from typing import Optional, cast, Annotated, Iterable

from django.contrib.postgres.search import TrigramSimilarity
from django.db import models
from django.db.models.base import ModelBase

from currency.models import Currency
from user.models import User
from .common import get_photo_upload_path

class Shop(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    address = models.CharField(max_length=1024, blank=True, null=True)
    taxpayer_id = models.CharField(max_length=1024, blank=True, null=True)

    objects = models.Manager()

    def __str__(self) -> str:
        return f'{self.name}{f"- {self.address}" if self.address else ""}'

    @classmethod
    def find_or_create(cls,
        name: str,
        address: Optional[str] = None,
        taxpayer_id: str | None = None,
        similarity: Annotated[float, 'from 0 to 1.0'] = 0.7
    ) -> 'Shop':
        normalized_name = name.strip().lower()

        if taxpayer_id:
            similar_shop = cls.objects.annotate(
                similarity=TrigramSimilarity('name', normalized_name)
            ).filter(
                taxpayer_id=taxpayer_id,
                similarity__gte=0.95
            ).order_by('-similarity').first()
            if similar_shop:
                return cast(Shop, similar_shop)

        else:
            similar_shop = cls.objects.annotate(
                similarity=TrigramSimilarity('name', normalized_name)
            ).filter(
                taxpayer_id__isnull=True,
                similarity__gte=similarity
            ).order_by('-similarity').first()
            if similar_shop:
                return cast(Shop, similar_shop)

        shop, _ = cls.objects.get_or_create(
            name=name,
            taxpayer_id=taxpayer_id,
            defaults={"address": address}
        )
        return cast(Shop, shop)

    class Meta:
        db_table = 'shop'

class Receipt(models.Model):
    photo = models.ImageField(upload_to=get_photo_upload_path, null=True, blank=True, max_length=1024)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(null=True)

    def __str__(self) -> str:
        return f'{self.pk}'

    def save(
        self,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        from . import tasks

        is_new = self.pk is None
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if is_new:
            self.refresh_from_db()
            tasks.update_receipt_data.delay(receipt_pk=self.pk, user_pk=self.owner.pk)

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