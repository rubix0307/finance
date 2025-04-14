from typing import Any

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from receipt.models import Receipt, ReceiptItem
from receipt import tasks


def update_receipt_data(modeladmin: admin.ModelAdmin, request: WSGIRequest, queryset: QuerySet[Receipt]) -> None:
    for receipt in queryset:
        tasks.update_receipt_data.delay(receipt_pk=receipt.pk, user_pk=request.user.pk)


class ReceiptItemInline(admin.TabularInline):  # type: ignore
    model = ReceiptItem
    extra = 0
    fields = ('id', 'name', 'category', 'price', 'currency')
    show_change_link = True
    readonly_fields = ('id', 'name', 'category', 'price', 'currency')
    can_delete = False

    def currency(self, obj: ReceiptItem) -> str:
        return str(obj.receipt.currency) if obj.receipt else '-'
    currency.short_description = 'Currency'


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin): # type: ignore
    list_display = ('id', 'photo', 'shop', 'owner', 'currency', 'date',)
    readonly_fields = ('photo_preview',)
    actions = [update_receipt_data]
    inlines = [ReceiptItemInline]

    def save_model(self, request: WSGIRequest, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)

    def photo_preview(self, obj: Receipt) -> str:
        if obj.photo:
            return mark_safe(
                f'<img id="photo_preview" src="{obj.photo.url}" style="width: 500; max-width: 100%; max-height: 1000px; object-fit: contain;" />')
        return '---'
    photo_preview.short_description = 'Preview'

    def change_view(self, request: WSGIRequest, object_id: str, form_url: str ='', extra_context: dict[str, Any] | None = None) -> HttpResponse:
        extra_context = extra_context or {}
        current_id = int(object_id)

        prev_obj = Receipt.objects.filter(id__lt=current_id).order_by('-id').first()
        next_obj = Receipt.objects.filter(id__gt=current_id).order_by('id').first()

        extra_context['prev_obj'] = prev_obj
        extra_context['next_obj'] = next_obj

        return super().change_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin): # type: ignore
    list_display = ('id', 'name', 'category', 'receipt', 'price', 'get_currency')
    list_filter = ('receipt', )

    def get_currency(self, obj: ReceiptItem) -> str:
        return str(obj.receipt.currency) if obj.receipt and obj.receipt.currency else "-"
    get_currency.short_description = 'Currency'

