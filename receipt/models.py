from typing import Optional, cast, Annotated, Any, LiteralString, Protocol, runtime_checkable

from django.contrib.auth import get_user_model
from django.contrib.postgres.search import TrigramSimilarity
from django.db import models

from currency.models import Currency
from .common import get_photo_upload_path


class Shop(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    address = models.CharField(max_length=1024, blank=True, null=True)

    objects = models.Manager()

    def __str__(self) -> str:
        return f'{self.name}{f'- {self.address}' if self.address else ''}'

    @classmethod
    def find_or_create(cls, name: str, address: Optional[str] = None, similarity: Annotated[float, 'from 0 to 1.0'] = 0.7) -> 'Shop':
        """
        Quickly search for a similar store. If not found, create a new one.
        Similarity search via TrigramSimilarity (PostgreSQL) is used.
        """

        normalized_name = name.strip().lower()
        similar_shop = cls.objects.annotate(
            similarity=TrigramSimilarity('name', normalized_name)
        ).filter(similarity__gt=similarity).order_by('-similarity').first()

        if similar_shop:
            return cast(Shop, similar_shop)

        shop, _ = cls.objects.get_or_create(name=name, defaults={"address": address})
        return cast(Shop, shop)

    class Meta:
        db_table = 'shop'


class Receipt(models.Model):
    photo = models.ImageField(upload_to=get_photo_upload_path, null=True, blank=True, max_length=1024)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField()

    def __str__(self) -> str:
        return f'{self.pk}'

    class Meta:
        db_table = 'receipt'


class ReceiptItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    category = models.ForeignKey('ReceiptItemCategory', on_delete=models.SET_NULL, null=True, blank=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')

    class Meta:
        db_table = 'receipt_item'
        ordering = ['id']


class ReceiptItemCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'receipt_item_category'