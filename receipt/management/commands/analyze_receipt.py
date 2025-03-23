from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from ai.services.open_ai.service import OpenAIService
import concurrent.futures

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
            max_workers = 1
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(process_receipt, [image_path]*max_workers))

            ReceiptSchemaService(receipt_schema=results[0], user=User.objects.first()).save()

            self.stdout.write(self.style.SUCCESS(f'Ответ от AI'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при анализе: {e}'))