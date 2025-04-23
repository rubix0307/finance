from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet

from telegram.models import ReceiptStatusMessage


def update_telegram_message(modeladmin: admin.ModelAdmin, request: WSGIRequest, queryset: QuerySet[ReceiptStatusMessage]) -> None:
    for status_data in queryset:
        status_data.update_telegram_message()

@admin.register(ReceiptStatusMessage)
class ReceiptStatusMessageAdmin(admin.ModelAdmin): # type: ignore
    list_display = ('id', 'receipt', 'status', 'chat_id', 'message_id',)
    actions = [update_telegram_message]