from typing import TypeVar, Any, cast, ClassVar
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.apps import apps
from django.db.models import Value, BooleanField, QuerySet


T = TypeVar('T', bound='User')

class CustomUserManager[T](UserManager[T]):
    def create_user(self, **extra_fields: Any) -> T:
        user = self.model(**extra_fields)
        user.set_password(extra_fields.get('password'))
        user.save()
        return cast(T, user)

    def create_superuser(self, **extra_fields: Any) -> T:
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(**extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    base_section = models.ForeignKey('section.Section', on_delete=models.SET_NULL, null=True, blank=True)
    photo = models.ImageField(upload_to='users/', null=True, blank=True, max_length=1024)

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = []

    objects: ClassVar[CustomUserManager['User']] = CustomUserManager()
    class Meta:
        db_table = 'user'

    def __str__(self) -> str:
        return f'User: {self.pk} {self.username}'

    def save(self, is_new: bool = False, *args, **kwargs) -> None:  # type: ignore
        if not self.pk or is_new:
            super().save(*args, **kwargs)
            Section = apps.get_model('section', 'Section')
            SectionUser = apps.get_model('section', 'SectionUser')
            Currency = apps.get_model('currency', 'Currency')

            section = Section.objects.create(
                name='Home',
                owner=self,
            )
            default_currency = Currency.objects.get(code='USD')

            SectionUser.objects.create(
                section=section,
                user=self,
                currency=default_currency,
            )

            self.base_section = section
            self.save(update_fields=['base_section'])
        else:
            super().save(*args, **kwargs)

    def get_sections(self) -> QuerySet:
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