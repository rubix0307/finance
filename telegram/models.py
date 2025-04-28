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
        update_message(user=self.receipt.owner, receipt_status=self)

    def update_status_and_notify(self, new_status: Status):
        self.status = new_status
        self.save(update_fields=['status'])
        self.update_telegram_message()


class PreCheckoutLog(models.Model):
    user_id = models.BigIntegerField()
    pre_checkout_query_id = models.CharField(max_length=255)
    invoice_payload = models.TextField()
    total_amount = models.PositiveIntegerField()
    currency = models.CharField(max_length=10)
    date = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PreCheckout {self.pre_checkout_query_id} by {self.user_id}"

class PaymentStatus(models.TextChoices):
    SUCCESSFUL = 'successful', _('Successful')

class Payment(models.Model):
    user_id = models.BigIntegerField()
    chat_id = models.BigIntegerField()
    currency = models.CharField(max_length=10)
    invoice_payload = models.TextField()
    total_amount = models.PositiveIntegerField()
    telegram_payment_charge_id = models.CharField(max_length=255, unique=True)
    provider_payment_charge_id = models.CharField(max_length=255)

    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.SUCCESSFUL)
    subscription_expiration_date = models.PositiveIntegerField(null=True, blank=True)
    is_first_recurring = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment {self.telegram_payment_charge_id} ({self.status})"
