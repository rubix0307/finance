from typing import Any

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import ForeignKey

from section.models import Section
from user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'first_name', 'last_name')


    def formfield_for_foreignkey(self, db_field: ForeignKey, request: WSGIRequest, **kwargs: dict[str, Any]) -> Any:
        if db_field.name == "base_section":
            obj_id = request.resolver_match.kwargs.get("object_id")
            if obj_id:
                try:
                    user = User.objects.get(pk=obj_id)
                    kwargs["queryset"] = user.sections.all()
                except User.DoesNotExist:
                    kwargs["queryset"] = Section.objects.none()
            else:
                kwargs["queryset"] = Section.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
