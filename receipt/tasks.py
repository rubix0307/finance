from typing import TypedDict

import logging
from celery import shared_task, Task
from celery.exceptions import MaxRetriesExceededError

from ai.managers.schemes import ProcessPhotoResponse
from .models import Receipt
from .services import process_receipt_photo


logger = logging.getLogger(__name__)


class ProcessPhotoError(TypedDict):
    error: str


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 100},
    acks_late=True
)
def process_receipt_task(self: Task, receipt_pk: int) -> ProcessPhotoResponse | ProcessPhotoError:
    """
    Processes a receipt photo with retry logic.

    :param receipt_pk: pk of Receipt
    :param self: Celery Task instance.
    :return: ProcessPhotoResponse on success or ProcessPhotoError if retries fail.
    """
    try:
        receipt = Receipt.objects.get(pk=receipt_pk)
        response = process_receipt_photo(str(receipt.photo))
        if response is not None:
            return response
        else:
            return {"error": "Other error"}

    except Receipt.DoesNotExist:
        logger.error("Receipt not found")
        return {"error": "Receipt not found"}

    except MaxRetriesExceededError:
        logger.error(f"Task {self.request.id} failed after max retries")
        return {"error": "Max retries exceeded. Task failed permanently."}

    except Exception as e:
        logger.warning(f"Task {self.request.id} failed. Retrying... ({self.request.retries}/5)")
        try:
            raise self.retry(exc=e)  # Повторяем задачу
        except MaxRetriesExceededError:
            logger.error(f"Task {self.request.id} permanently failed after 5 attempts.")
            return {"error": "Permanent failure after max retries"}