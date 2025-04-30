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
    retry_kwargs={"max_retries": 2, "countdown": 10},
    acks_late=True,
    reject_on_worker_lost=True,
)
def update_receipt_data(self: Task, receipt_pk: int, user_pk: int) -> None | ProcessPhotoResponse | ProcessPhotoError:

    user = User.objects.get(pk=user_pk)
    receipt = Receipt.objects.get(pk=receipt_pk)
    receipt_status = receipt.statuses.order_by('-message_id').first()

    try:
        if receipt_status:
            receipt_status.update_status_and_notify(Status.IN_PROGRESS)
        else:
            receipt_status = None

        ai_service = OpenAIService()
        schema: ReceiptSchema | None = ai_service.analyze_receipt(receipt=receipt)

        if schema:
            new_status = Status.PROCESSED
            answer = ProcessPhotoResponse(status="success")
            user.subscription_manager.register('analyze_photo')
            ReceiptSchemaService(receipt_schema=schema, user=user).update_receipt(receipt)
        else:
            new_status = Status.ERROR
            answer = ProcessPhotoError(error='Receipt schema is not available')

        if receipt_status:
            receipt_status.update_status_and_notify(new_status)
    except Exception as ex:
        if receipt_status:
            receipt_status.update_status_and_notify(Status.ERROR)
        return None

    return answer


@shared_task(  # type: ignore
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 10},
    acks_late=True,
    reject_on_worker_lost=True,
)
def update_expenses_data_by_text(self: Task, receipt_pk: int, user_pk: int) -> bool:

    user = User.objects.get(pk=user_pk)
    receipt = Receipt.objects.get(pk=receipt_pk)
    receipt_status = receipt.statuses.order_by('-message_id').first()

    try:
        if receipt_status:
            receipt_status.update_status_and_notify(Status.IN_PROGRESS)
        else:
            receipt_status = None

        ai_service = OpenAIService()
        schema: ReceiptSchema | None = ai_service.analyze_user_expenses_by_text(receipt=receipt)

        if schema:
            new_status = Status.PROCESSED
            ReceiptSchemaService(
                receipt_schema=schema,
                user=user,
                currency=receipt.get_default_currency()
            ).update_receipt(receipt)
        else:
            new_status = Status.ERROR

        if receipt_status:
            receipt_status.update_status_and_notify(new_status)

    except Exception as ex:
        if receipt_status:
            receipt_status.update_status_and_notify(Status.ERROR)

    return bool(schema)

