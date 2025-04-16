from typing import Iterable

from django.contrib.auth import get_user_model
from django.db import models
from currency.models import Currency
from user.models import User


class Section(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(
        get_user_model(), through='SectionUser', related_name='sections', blank=True
    )
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_section'
    )

    def add_members(self, user_objs: Iterable[User], currency: Currency | None = None) -> None:
        if not currency:
            currency = Currency.objects.get(code='USD')

        for user in user_objs:
            if not self.memberships.filter(user=user).exists():
                SectionUser.objects.create(section=self, user=user, currency=currency)

    class Meta:
        db_table = 'section'

    def __str__(self) -> str:
        return self.name


class SectionUser(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    user_section_name = models.CharField(max_length=255, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'section')
        db_table = 'section_user'

    def __str__(self) -> str:
        return f'{self.user} in {self.section}'
