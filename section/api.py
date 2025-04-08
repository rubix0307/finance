from datetime import date
from typing import cast, Any
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db import connection
from ninja import Router
from ninja.errors import HttpError
from ninja.security import django_auth
from currency.schemas import CurrencySchema
from chart.api import router as charts_router
from user.models import User
from .decorators import SectionRequired
from .models import Section
from .schemas import SectionSchema, SectionUserSchema, SectionReceiptSchema, SectionReceiptItemSchema, \
    SectionReceiptItemCategorySchema, ReceiptPaginationSchema, SectionReceiptShopSchema, SectionMiniSchema, \
    SectionUpdateSchema

router = Router()
router.add_router("/", charts_router)

@router.get("/", response=list[SectionSchema])
def get_sections(request: WSGIRequest) -> list[SectionSchema]:
    user = cast(User, request.user)
    sections = user.get_sections()

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
                        code=membership.currency.code
                    ),
                    is_owner=(section.owner_id == membership.user.id),
                )
                for membership in section.memberships.all()
            ],
        )
        for section in sections
    ]

@router.post("/{section_pk}/", response=SectionMiniSchema)
@SectionRequired
def update_section(
    request: WSGIRequest,
    section_pk: int,
    data: SectionUpdateSchema,
    **kwargs: dict[str, Any]
) -> SectionMiniSchema:
    section = Section.objects.get(pk=section_pk)

    update_fields = []

    if data.name is not None:
        section.name = data.name
        update_fields.append('name')

    if update_fields:
        section.save(update_fields=update_fields)

    return SectionMiniSchema.from_orm(section)

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

    paginator = Paginator(section.receipts.all().order_by('id'), size)


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