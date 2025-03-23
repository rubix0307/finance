from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from ai.services.open_ai.service import OpenAIService
import concurrent.futures

from receipt.schemes import ReceiptSchema
from receipt.services.receipt_schema.save import ReceiptSchemaService


def process_receipt(image_path):
    ai = OpenAIService()
    return ai.analyze_receipt(image_path)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('image_path', type=str, help='Путь к изображению чека')

    def handle(self, *args, **kwargs):
        User = get_user_model()
        image_path = kwargs['image_path']

        self.stdout.write(self.style.SUCCESS(f'Запуск анализа чека: {image_path}'))

        try:
            # max_workers = 1
            # with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            #     results = list(executor.map(process_receipt, [image_path]*max_workers))
            # schema = results[0]

            # schema = ReceiptSchema(**{
            #     'currency': 'EUR',
            #     'date': '15/03/2025',
            #     'is_receipt': True,
            #     'items': [
            #           {'category_id': 4, 'name': 'Xiaomi Electric Shaver S301 Z3', 'price': 39.99}
            #     ],
            #     'shop': {
            #           'address': 'Via Portico 71, Orio al Serio 24050',
            #           'name': 'Xiaomi Store Oriocenter',
            #           'taxpayer_id': '10298480962'
            #     },
            #     'time': '19:25'}
            # )
            process_receipt(image_path)
            ReceiptSchemaService(receipt_schema=schema, user=User.objects.first()).save()

            self.stdout.write(self.style.SUCCESS(f'Ответ от AI'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при анализе: {e}'))