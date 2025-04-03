from django.contrib.auth.models import AbstractUser
from django.db import models
from django.apps import apps
from django.db.models import Value, BooleanField


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

    def get_sections(self):
        Section = apps.get_model('section', 'Section')
        owned_sections = Section.objects.filter(owner=self).annotate(
            is_owner=Value(True, output_field=BooleanField())
        )

        participant_sections = Section.objects.filter(
            memberships__user=self
        ).exclude(owner=self).annotate(
            is_owner=Value(False, output_field=BooleanField())
        )

        sections = (owned_sections | participant_sections).order_by(
            '-is_owner', 'id'
        ).select_related('owner') \
            .prefetch_related(
            'users',
            'memberships',
            'memberships__user',
            'memberships__currency'
        ).distinct()

        return sections