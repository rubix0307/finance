from django.core.handlers.wsgi import WSGIRequest
from ninja import Router, Schema
from django.db.models import Value, BooleanField, Q, QuerySet
from ninja.security import django_auth

from currency.models import Currency
from currency.schemas import CurrencySchema
from section.models import SectionUser, Section
from user.models import User
from .models import Section


def get_user_sections(user: User) -> QuerySet[Section]:
    owned_sections = Section.objects.filter(owner=user).annotate(
        is_owner=Value(True, output_field=BooleanField())
    )

    participant_sections = Section.objects.filter(
        memberships__user=user
    ).exclude(owner=user).annotate(
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






class SectionUserSchema(Schema):
    id: int
    username: str
    currency: CurrencySchema
    is_owner: bool

class SectionSchema(Schema):
    id: int
    name: str
    is_base: bool
    users: list[SectionUserSchema]



router = Router()

@router.get("/", auth=django_auth, response=list[SectionSchema])
def get_sections_menu(request: WSGIRequest) -> list[SectionSchema]:
    user = request.user
    sections = get_user_sections(user)

    return [
        SectionSchema(
            id=section.id,
            name=section.name,
            is_base=(section.id == user.base_section_id),
            users=[
                SectionUserSchema(
                    id=membership.user.id,
                    username=membership.user.username,
                    currency=CurrencySchema(
                        id=membership.currency.id,
                        code=membership.currency.code
                    ) if membership.currency else None,
                    is_owner=(section.owner_id == membership.user.id)
                )
                for membership in section.memberships.all()
            ]
        )
        for section in sections
    ]
