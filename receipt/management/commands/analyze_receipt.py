from datetime import date

from django.core.management.base import BaseCommand
from ai.services.open_ai.service import OpenAIService
from currency.services import CurrencyRateService

from receipt.models import Receipt
from receipt.schemas import ReceiptSchema
from receipt.services.receipt_schema.save import ReceiptSchemaService


def process_receipt(receipt: Receipt) -> ReceiptSchema | None:
    ai = OpenAIService()
    return ai.analyze_receipt(receipt)

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        CurrencyRateService().save_rates()
        receipt = Receipt.objects.first()

        if receipt:
            schema = process_receipt(receipt)

            if schema:
                ReceiptSchemaService(receipt_schema=schema, user=receipt.owner).save()

            self.stdout.write(self.style.SUCCESS(f'Ответ от AI'))
