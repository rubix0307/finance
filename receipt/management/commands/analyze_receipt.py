from django.core.management.base import BaseCommand
from ai.services.open_ai.service import OpenAIService
import concurrent.futures

def process_receipt(image_path):
    ai = OpenAIService()
    return ai.analyze_receipt(image_path)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('image_path', type=str, help='Путь к изображению чека')

    def handle(self, *args, **kwargs):
        image_path = kwargs['image_path']

        self.stdout.write(self.style.SUCCESS(f'Запуск анализа чека: {image_path}'))

        try:
            max_workers = 10
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(process_receipt, [image_path]*max_workers))

            self.stdout.write(self.style.SUCCESS(f'Ответ от AI'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при анализе: {e}'))