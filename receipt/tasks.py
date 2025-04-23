from typing import TypedDict

import logging
from celery import shared_task, Task
from celery.exceptions import MaxRetriesExceededError

from ai.managers.schemas import ProcessPhotoResponse, ProcessPhotoError
from ai.services.open_ai.service import OpenAIService
from telegram.models import ReceiptStatusMessage, Status

from .schemas import ReceiptSchema
from user.models import User
from receipt.services.receipt_schema.save import ReceiptSchemaService
from .models import Receipt

logger = logging.getLogger(__name__)


@shared_task(  # type: ignore
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 100},
    acks_late=True
)
def update_receipt_data(self: Task, receipt_pk: int, user_pk: int) -> None | ProcessPhotoResponse | ProcessPhotoError:

    try:
        user = User.objects.get(pk=user_pk)
        receipt = Receipt.objects.get(pk=receipt_pk)
        receipt_status = receipt.statuses.order_by('-message_id').first()
        if receipt_status:
            receipt_status.update_status_and_notify(Status.IN_PROGRESS)
        else:
            receipt_status = None

        ai_service = OpenAIService()
        schema: ReceiptSchema | None = ai_service.analyze_receipt(receipt=receipt)

        if schema:
            new_status = Status.PROCESSED
            answer = ProcessPhotoResponse(status="success")
            ReceiptSchemaService(receipt_schema=schema, user=user).update_receipt(receipt)
        else:
            new_status = Status.ERROR
            answer = ProcessPhotoError(error='Receipt schema is not available')

        if receipt_status:
            receipt_status.update_status_and_notify(new_status)

        return answer

    except Receipt.DoesNotExist:
        logger.error("Receipt not found")
        return {"error": "Receipt not found"}

    except User.DoesNotExist:
        logger.error("User does not exist")
        return {"error": "User does not exist"}

    except MaxRetriesExceededError:
        logger.error(f"Task {self.request.id} failed after max retries")
        return {"error": "Max retries exceeded. Task failed permanently."}

    except Exception as e:
        logger.warning(f"Task {self.request.id} failed. Retrying... ({self.request.retries}/5)")
        try:
            raise self.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error(f"Task {self.request.id} permanently failed after 5 attempts.")
            return {"error": "Permanent failure after max retries"}
