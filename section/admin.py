from typing import cast

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count, QuerySet
from django.utils.translation import gettext_lazy as _
from .models import Section, SectionUser


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_count', 'owner')

    def get_queryset(self, request: WSGIRequest) -> QuerySet[Section]:
        qs = super().get_queryset(request)
        return qs.annotate(user_count=Count('memberships'))

    @admin.display(
        ordering='user_count',
        description=_('Count of users'),
    )
    def user_count(self, obj: Section) -> int:
        return getattr(obj, 'user_count', 0)



@admin.register(SectionUser)
class SectionUserAdmin(admin.ModelAdmin):
    list_display = ('section', 'user', 'user_section_name', 'currency')
