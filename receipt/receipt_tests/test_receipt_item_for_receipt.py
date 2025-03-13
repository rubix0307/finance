from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from receipt.models import Receipt, ReceiptItem, Shop, Currency


class ReceiptItemModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test_user", password="password")
        self.shop = Shop.objects.create(name="Test Shop")
        self.currency = Currency.objects.create(code="USD")

        self.receipt = Receipt.objects.create(
            shop=self.shop,
            owner=self.user,
            currency=self.currency,
            date=now()
        )

    def test_create_receipt_item(self):
        """Creating ReceiptItem object and binding it to Receipt"""
        item = ReceiptItem.objects.create(
            name="Test Item",
            price=100.50,
            receipt=self.receipt
        )

        self.assertEqual(ReceiptItem.objects.count(), 1)
        self.assertEqual(item.receipt, self.receipt)
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.price, 100.50)

    def test_cascade_delete_receipt(self):
        """Cascading removal of Receipt -> ReceiptItem"""
        item1 = ReceiptItem.objects.create(name="Item 1", price=50.00, receipt=self.receipt)
        item2 = ReceiptItem.objects.create(name="Item 2", price=75.00, receipt=self.receipt)

        self.assertEqual(ReceiptItem.objects.filter(receipt=self.receipt).count(), 2)
        self.receipt.delete()
        self.assertEqual(ReceiptItem.objects.count(), 0)