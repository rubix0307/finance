from datetime import datetime
from decimal import Decimal
from typing import cast

from django.test import TestCase
from currency.models import Currency
from receipt.models import Receipt, ReceiptItem, ReceiptItemCategory, Shop
from receipt.schemes import ReceiptSchema
from receipt.services.receipt_schema.exceptions import MissingItemsError, MissingCurrencyError
from receipt.services.receipt_schema.save import ReceiptSchemaService
from user.models import User


class ReceiptSchemaServiceTest(TestCase):
    def setUp(self):
        self.currency = Currency.objects.create(code="USD")
        self.user = User.objects.create(username="testuser")
        self.category = ReceiptItemCategory.objects.create(name="Food")

    def get_valid_data(self, extra=None):
        """
        Returns the base dictionary for creating a ReceiptSchema
        extra - additional dictionary for overriding values
        """
        data = {
            "is_receipt": True,
            "shop": {"name": "Test Shop", "address": "Test Address", "taxpayer_id": "123456789"},
            "items": [
                {"name": "Item1", "price": 10.0, "category_id": self.category.id},
                {"name": "Item2", "price": 20.0, "category_id": self.category.id},
            ],
            "currency": "USD",
            "date": "01/03/2025",
            "time": "15:30",
        }
        if extra:
            data.update(extra)
        return data

    def test_missing_currency_raises_error(self):
        """Check that MissingCurrencyError is thrown if there is no currency"""
        data = self.get_valid_data(extra={"currency": "NON_EXISTENT"})
        receipt_schema = ReceiptSchema(**data)
        with self.assertRaises(MissingCurrencyError):
            ReceiptSchemaService(receipt_schema, self.user)

    def test_missing_items_raises_error(self):
        """Check that MissingItemsError is thrown if there are no items (empty list)"""
        data = self.get_valid_data(extra={"items": []})
        receipt_schema = ReceiptSchema(**data)
        with self.assertRaises(MissingItemsError):
            ReceiptSchemaService(receipt_schema, self.user)

    def test_get_shop_returns_none_when_no_shop_name(self):
        """If there is no store data in the data, the get_shop method should return None"""
        data = self.get_valid_data(extra={"shop": {}})
        receipt_schema = ReceiptSchema(**data)
        service = ReceiptSchemaService(receipt_schema, self.user)
        shop = service.get_shop()
        self.assertIsNone(shop)

    def test_get_shop_creates_shop_when_name_provided(self):
        """Given store data with a store name, the get_shop method should create (or find) the store"""
        data = self.get_valid_data()
        receipt_schema = ReceiptSchema(**data)
        service = ReceiptSchemaService(receipt_schema, self.user)

        shop = service.get_shop()
        self.assertIsNotNone(shop)

        shop = cast(Shop, shop)
        self.assertEqual(shop.name, "Test Shop")
        self.assertEqual(shop.address, "Test Address")
        self.assertEqual(shop.taxpayer_id, "123456789")

    def test_get_date_with_date_and_time(self):
        """Check that if date and time are present, the get_date method returns the correct date"""
        data = self.get_valid_data()
        receipt_schema = ReceiptSchema(**data)
        service = ReceiptSchemaService(receipt_schema, self.user)
        expected_date = datetime.strptime("01/03/2025 15:30", "%d/%m/%Y %H:%M").date()
        self.assertEqual(service.get_date(), expected_date)

    def test_get_date_with_date_only(self):
        """If only the date parameter is specified, get_date should parse the date correctly"""
        data = self.get_valid_data(extra={"time": None})
        receipt_schema = ReceiptSchema(**data)
        service = ReceiptSchemaService(receipt_schema, self.user)
        expected_date = datetime.strptime("01/03/2025", "%d/%m/%Y").date()
        self.assertEqual(service.get_date(), expected_date)

    def test_get_date_with_invalid_date(self):
        """
        If an invalid formatted string date/time is passed,
        get_date should return today's date.
        """
        data = self.get_valid_data(extra={"date": "invalid_date", "time": "invalid_time"})
        receipt_schema = ReceiptSchema(**data)
        service = ReceiptSchemaService(receipt_schema, self.user)
        today = datetime.today().date()
        self.assertEqual(service.get_date(), today)

    def test_get_item_category_existing(self):
        """
        If a category is present in the database, the get_item_category method should return it.
        For this purpose, we load categories beforehand.
        """
        data = self.get_valid_data(extra={"items": [{"name": "Item1", "price": 10.0, "category_id": self.category.id}]})
        receipt_schema = ReceiptSchema(**data)
        service = ReceiptSchemaService(receipt_schema, self.user)
        service._preload_categories()
        category = service.get_item_category(self.category.id)
        self.assertEqual(category, self.category)

    def test_get_item_category_existing_no_preload(self):
        """
        If a category is present in the database, the get_item_category method should return it
        """
        data = self.get_valid_data(extra={"items": [{"name": "Item1", "price": 10.0, "category_id": self.category.id}]})
        receipt_schema = ReceiptSchema(**data)
        service = ReceiptSchemaService(receipt_schema, self.user)
        category = service.get_item_category(self.category.id)
        self.assertEqual(category, self.category)

    def test_get_item_category_not_existing(self):
        """
        If no category is found, the get_item_category method should return the category 'Other'
        with id=-1, creating it if necessary
        """
        non_existing_category_id = 9999
        data = self.get_valid_data(extra={"items": [{"name": "Item1", "price": 10.0, "category_id": non_existing_category_id}]})
        receipt_schema = ReceiptSchema(**data)
        service = ReceiptSchemaService(receipt_schema, self.user)
        # Убеждаемся, что категории с данным id нет в базе
        with self.assertRaises(ReceiptItemCategory.DoesNotExist):
            ReceiptItemCategory.objects.get(id=non_existing_category_id)
        category = service.get_item_category(non_existing_category_id)
        self.assertEqual(category.id, -1)
        self.assertEqual(category.name, "Other")

    def test_save_receipt_items(self):
        """Check that the save_receipt_items method creates ReceiptItem objects associated with the passed Receipt"""
        data = self.get_valid_data()
        receipt_schema = ReceiptSchema(**data)
        service = ReceiptSchemaService(receipt_schema, self.user)

        receipt = Receipt.objects.create(
            shop=None,
            currency=self.currency,
            date=service.get_date(),
            owner=self.user,
        )
        items = service.save_receipt_items(receipt)
        self.assertEqual(len(items), 2)
        self.assertEqual(ReceiptItem.objects.filter(receipt=receipt).count(), 2)

        for item_obj, item_data in zip(items, receipt_schema.items):
            self.assertEqual(item_obj.name, item_data.name)
            self.assertEqual(item_obj.price, Decimal(str(item_data.price)))
            self.assertEqual(item_obj.receipt, receipt)

    def test_save_creates_receipt_and_items(self):
        """The save method should create a Receipt with store, currency, date, owner and related items"""
        shop_data = {"name": "Test Shop", "address": "Test Address", "taxpayer_id": "123456789"}
        data = self.get_valid_data(extra={"shop": shop_data, "items": [
            {"name": "Item1", "price": 10.0, "category_id": self.category.id},
        ]})
        receipt_schema = ReceiptSchema(**data)
        service = ReceiptSchemaService(receipt_schema, self.user)
        receipt = service.save()

        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.owner, self.user)
        self.assertEqual(receipt.currency, self.currency)
        expected_date = datetime.strptime("01/03/2025 15:30", "%d/%m/%Y %H:%M").date()
        self.assertEqual(receipt.date, expected_date)

        self.assertIsNotNone(receipt.shop)
        self.assertEqual(receipt.shop.name, "Test Shop")

        self.assertEqual(ReceiptItem.objects.filter(receipt=receipt).count(), 1)