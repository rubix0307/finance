from django.contrib.auth import get_user_model
from django.db import models
from currency.models import Currency


class Section(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(
        get_user_model(), through='SectionUser', related_name='sections', blank=True
    )
    owner = models.OneToOneField(
        get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_section"
    )

    class Meta:
        db_table = 'section'

    def __str__(self) -> str:
        return self.name


class SectionUser(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'section')
        db_table = 'section_user'

    def __str__(self) -> str:
        return f"{self.user} in {self.section}"
