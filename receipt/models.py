from typing import Optional, cast, Annotated, Iterable

from django.contrib.postgres.search import TrigramSimilarity
from django.db import models
from django.db.models.base import ModelBase
from parler.models import TranslatableModel, TranslatedFields

from currency.models import Currency
from section.models import Section
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
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True, related_name='receipts')
    date = models.DateTimeField(null=True)
    date_last_update = models.DateTimeField(auto_now=True, null=True, blank=True)
    date_add = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    input_text = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.pk}'

    def save(
        self,
        do_analyze_photo: bool = False,
        do_analyze_input_text: bool = False,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        from . import tasks

        self.section = self.owner.base_section
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if do_analyze_photo:
            self.refresh_from_db()
            tasks.update_receipt_data.delay(receipt_pk=self.pk, user_pk=self.owner.pk)

        if do_analyze_input_text:
            self.refresh_from_db()
            tasks.update_expenses_data_by_text(receipt_pk=self.pk, user_pk=self.owner.pk)

    def get_default_currency(self) -> Currency | None:
        try:
            return self.section.memberships.get(user=self.owner).currency
        except Exception:
            return None

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


class ReceiptItemCategory(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
    )
    color = models.CharField(max_length=34, default='#ffffff')

    def __str__(self):
        return f'{self.safe_translation_getter("name", any_language=True)}'

    class Meta:
        db_table = "receipt_item_category"