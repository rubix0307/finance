from typing import Optional, cast, Annotated

from django.contrib.postgres.search import TrigramSimilarity
from django.db import models

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
