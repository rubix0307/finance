from django.http import JsonResponse
from .tasks import process_receipt_task

def process_receipt_view(request, receipt_pk=123):
    # Постановка задачи в очередь
    process_receipt_task.delay(receipt_pk=receipt_pk)
    return JsonResponse({"status": "Задача поставлена в очередь"})