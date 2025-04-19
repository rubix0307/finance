from datetime import date
from typing import cast, Any
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db import connection
from django.http import HttpResponse
from ninja import Router
from ninja.errors import HttpError
from ninja.security import django_auth

import section
from currency.models import Currency
from currency.schemas import CurrencySchema
from chart.api import router as charts_router
from user.models import User
from .decorators import SectionRequired
from .models import Section, SectionUser
from .schemas import SectionSchema, SectionUserSchema, SectionReceiptSchema, SectionReceiptItemSchema, \
    SectionReceiptItemCategorySchema, ReceiptPaginationSchema, SectionReceiptShopSchema, SectionMiniSchema, \
    SectionUpdateSchema, SectionMemberMiniSchema, MemberUpdateSchema

router = Router(auth=django_auth)
router.add_router("/", charts_router)

@router.get("/", response=list[SectionSchema], auth=django_auth)
def get_sections(request: WSGIRequest) -> list[SectionSchema]:
    user = cast(User, request.user)
    sections = user.get_sections()

    sections_data = []
    for section in sections:
        memberships = section.memberships.all()
        user_as_member = list(filter(lambda m: m.user.id == user.id, memberships))[0]

        sections_data.append(SectionSchema(
            id=section.id,
            name=user_as_member.user_section_name or section.name,
            is_base=(section.id == user.base_section_id),
            users=[
                SectionUserSchema(
                    id=member.user.id,
                    username=member.user.username,
                    first_name=member.user.first_name,
                    last_name=member.user.last_name,
                    photo=member.user.photo,
                    currency=CurrencySchema(
                        code=member.currency.code
                    ),
                    is_owner=(section.owner_id == member.user.id),
                )
                for member in section.memberships.all()
            ],
        ))

    return sections_data

@router.post("/{section_pk}/", response=SectionMiniSchema)
@SectionRequired
def update_section(
    request: WSGIRequest,
    section_pk: int,
    data: SectionUpdateSchema,
    **kwargs: dict[str, Any]
) -> SectionMiniSchema:

    section: Section = cast(Section, kwargs.get('section'))

    update_fields = []
    new_name = None
    if data.name is not None:
        if not request.user.id == section.owner.id:
            user_as_member = SectionUser.objects.get(user=request.user, section=section)
            user_as_member.user_section_name = data.name
            user_as_member.save()
            new_name = user_as_member.user_section_name
        else:
            section.name = data.name
            new_name = section.name
            update_fields.append('name')

    if update_fields:
        section.save(update_fields=update_fields)

    return SectionMiniSchema(
        id=section.id,
        name=new_name or section.name,
    )

@router.post("/{section_pk}/memberships/{member_pk}/", response=SectionMemberMiniSchema)
@SectionRequired
def update_section_member(
    request: WSGIRequest,
    section_pk: int,
    member_pk: int,
    data: MemberUpdateSchema,
    **kwargs: dict[str, Any]
) -> SectionMemberMiniSchema:
    if not request.user.pk == member_pk:
        raise HttpError(403, 'Member editing is forbidden for you')

    section: Section = cast(Section, kwargs.get('section'))
    member = section.memberships.get(user=request.user)

    update_fields = []

    if data.currency is not None:
        try:
            member.currency = Currency.objects.get(code=data.currency[:3])
            update_fields.append('currency')
        except Currency.DoesNotExist:
            raise HttpError(404, 'Selected currency not found')

    if update_fields:
        member.save(update_fields=update_fields)

    return SectionMemberMiniSchema(
        id=member.user.id,
        currency=CurrencySchema(code=member.currency.code),
    )

@router.post("/{section_pk}/memberships/{member_pk}/delete")
@SectionRequired
def delete_section_member(
    request: WSGIRequest,
    section_pk: int,
    member_pk: int,
    **kwargs: dict[str, Any]
) -> HttpResponse:
    section: Section = cast(Section, kwargs.get('section'))

    if request.user != section.owner and request.user.pk == member_pk:
        ...
    elif request.user == section.owner and request.user.pk != member_pk:
        ...
    else:
        raise HttpError(403, 'Member editing is forbidden for you')

    section.memberships.filter(user_id=member_pk).delete()
    return HttpResponse(status=200)

@router.get("/{section_pk}/receipts/", response=ReceiptPaginationSchema)
@SectionRequired
def get_section_receipts(
        request: WSGIRequest,
        section_pk: int,
        page: int = 1,
        size: int = 10,
        **kwargs: dict[str, Any],
    ) -> ReceiptPaginationSchema:
    section = Section.objects.get(pk=section_pk)

    if not (section.users.filter(pk=request.user.pk).exists() or section.owner == request.user):
        raise HttpError(403, "Доступ запрещён")

    if size > 50:
        size = 50

    paginator = Paginator(section.receipts.filter(is_processed=True).order_by('-date'), size)


    try:
        current_page = paginator.page(page)
    except Exception:
        raise HttpError(404, "Страница не найдена")

    receipts = [
        SectionReceiptSchema(
            id=r.id,
            currency=CurrencySchema(
                code=r.currency.code
            ),
            photo=r.photo.url,
            date=date(year=r.date.year, month=r.date.month, day=r.date.day),
            items=[
                SectionReceiptItemSchema(
                    id=i.id,
                    name=i.name,
                    price=float(i.price),
                    category=SectionReceiptItemCategorySchema(
                        id=i.category.id,
                        name=i.category.name,
                    ),
                )
                for i in r.items.all()
            ],
            shop=SectionReceiptShopSchema(
                id=r.shop.id,
                name=r.shop.name,
                address=r.shop.address,
                taxpayer_id=r.shop.taxpayer_id,
            ) if r.shop else None
        )
        for r in current_page.object_list
    ]

    return ReceiptPaginationSchema(
        total=paginator.count,
        page=page,
        size=size,
        pages=paginator.num_pages,
        results=receipts,
    )