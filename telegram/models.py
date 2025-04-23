from django.db import models

from receipt.models import Receipt
from django.utils.translation import gettext_lazy as _




class Status(models.TextChoices):
    IN_PROGRESS = 'in_progress', _('In progress')
    PROCESSED = 'processed', _('Processed')
    ERROR = 'error', _('Error')

class ReceiptStatusMessage(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='statuses')
    status = models.CharField(
        max_length=255,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        verbose_name=_('Status'),
    )
    chat_id = models.BigIntegerField()
    message_id = models.BigIntegerField()

    def update_telegram_message(self) -> None:
        from telegram.handlers.messages.photos import update_message
        update_message(receipt_status=self)

    def update_status_and_notify(self, new_status: Status):
        self.status = new_status
        self.save(update_fields=['status'])
        self.update_telegram_message()