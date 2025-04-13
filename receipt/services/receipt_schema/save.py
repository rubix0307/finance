from datetime import datetime, date
from decimal import Decimal

from django.db import transaction

from currency.models import Currency
from receipt.services.receipt_schema.exceptions import MissingItemsError, MissingCurrencyError
from user.models import User
from receipt.models import Shop, Receipt, ReceiptItem, ReceiptItemCategory
from receipt.schemas import ReceiptSchema


class ReceiptSchemaService:
    def __init__(self, receipt_schema: ReceiptSchema, user: User):
        self.receipt_schema = receipt_schema
        self.receipt_data = receipt_schema.model_dump()
        self.user = user
        self.item_categories: dict[int, ReceiptItemCategory] = {}

        self._validate_required_fields()

    def _validate_required_fields(self) -> None:
        currency_code = self.receipt_data.get('currency')
        try:
            self.currency = Currency.objects.get(code=currency_code)
        except Currency.DoesNotExist:
            raise MissingCurrencyError()

        items = self.receipt_data.get("items")
        if not items or not isinstance(items, list) or len(items) == 0:
            raise MissingItemsError()

    def _preload_categories(self) -> None:
        category_ids = {item.category_id for item in self.receipt_schema.items}
        existing = ReceiptItemCategory.objects.filter(id__in=category_ids)
        self.item_categories = {cat.id: cat for cat in existing}

    def get_shop(self) -> Shop | None:
        shop_data = self.receipt_data.get('shop') or {}
        shop = None
        if shop_data.get('name'):
            shop = Shop.find_or_create(
                name=shop_data['name'],
                address=shop_data.get('address'),
                taxpayer_id=shop_data.get('taxpayer_id'),
            )
        return shop

    def get_date(self) -> date:
        date_str = self.receipt_data.get('date')
        time_str = self.receipt_data.get('time')

        if date_str and time_str:
            date_time_str = f"{date_str} {time_str}"
            fmt = "%d/%m/%Y %H:%M"
        elif date_str:
            date_time_str = date_str
            fmt = "%d/%m/%Y"
        else:
            return datetime.today().date()

        try:
            parsed_date = datetime.strptime(date_time_str, fmt)
        except ValueError:
            parsed_date = datetime.today()

        return parsed_date.date()

    def get_item_category(self, category_id: int) -> ReceiptItemCategory:
        category = self.item_categories.get(category_id)
        if not category:
            try:
                category = ReceiptItemCategory.objects.get(id=category_id)
            except ReceiptItemCategory.DoesNotExist:
                category, _ = ReceiptItemCategory.objects.get_or_create(id=-1, defaults={'name': 'Other'})
                self.item_categories[category_id] = category
        return category

    def save_receipt_items(self, receipt: Receipt) -> list[ReceiptItem]:
        self._preload_categories()

        receipt_items: list[ReceiptItem] = []
        for item_data in self.receipt_schema.items:
            receipt_items.append(ReceiptItem.objects.create(
                name=item_data.name,
                price=Decimal(item_data.price),
                category=self.get_item_category(item_data.category_id),
                receipt=receipt,
            ))
        return receipt_items

    def save(self) -> Receipt:
        receipt = Receipt.objects.create(
            shop=self.get_shop(),
            currency=self.currency,
            date=self.get_date(),
            owner=self.user,
        )
        self.save_receipt_items(receipt)
        return receipt

    def update_receipt_items(self, receipt: Receipt) -> list[ReceiptItem]:
        with transaction.atomic():
            ReceiptItem.objects.filter(receipt=receipt).delete()
            receipt_items = self.save_receipt_items(receipt=receipt)
        return receipt_items

    def update_receipt(self, receipt: Receipt) -> Receipt:
        receipt.shop = self.get_shop()
        receipt.currency = self.currency
        receipt.date = self.get_date()
        receipt.is_processed = True
        receipt.save(update_fields=['shop', 'currency', 'date', 'is_processed'])

        self.update_receipt_items(receipt)
        return receipt