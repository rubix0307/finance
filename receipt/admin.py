from django.contrib import admin

from receipt.models import Receipt


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin): # type: ignore
    list_display = ('id', )

