from django.contrib.auth.models import AbstractUser
from django.db import models
from django.apps import apps


class User(AbstractUser):
    telegram_id = models.PositiveBigIntegerField(null=True, blank=True)
    base_section = models.ForeignKey("section.Section", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'user'

    def save(self, *args, **kwargs) -> None:  # type: ignore
        if not self.pk:
            super().save(*args, **kwargs)
            Section = apps.get_model('section', 'Section')
            section = Section.objects.create(name=f'Home')
            section.users.add(self)
            self.base_section = section
            self.save(update_fields=['base_section'])
        else:
            super().save(*args, **kwargs)