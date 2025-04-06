from typing import Any, Literal, cast, TypeAlias

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.db import connection
from ninja import Router

from currency.models import Currency
from currency.schemas import CurrencySchema
from section.decorators import SectionRequired
from section.models import Section, SectionUser
from user.models import User
from .schemas import ChartPieSchema, ChartPieDataSchema, ExpensesSchema, ChartDataSchema, ExpensesDataSchema

router = Router(tags=["Charts"])
periods: TypeAlias = Literal['week', 'month', 'year']

def pie_chart(
        section: Section,
        period: periods,
        currency: Currency,
        **kwargs: dict[str, Any],
) -> ChartPieSchema:

    with open('chart/sql/pie.sql', 'r') as f:
        sql_query = f.read()

    params = {
        'section_id': int(section.id),
        'convert_currency_code': currency.code,
        'period': f'1 {period}s',
    }

    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    data_dicts = [dict(zip(columns, row)) for row in rows]

    return ChartPieSchema(
        chart_title=f'{period}',
        data=[ChartPieDataSchema.model_validate(item) for item in data_dicts]
    )

@router.get("{section_pk}/expenses/", response=ExpensesSchema)
@SectionRequired
def get_expenses(
        request: WSGIRequest,
        section_pk: int,
        chart_type: Literal['pie'],
        period: Literal[''] | periods,
        **kwargs: dict[str, Any],
) -> ExpensesSchema:
    if not period:
        period = 'week'

    section = cast(Section, kwargs.get('section'))
    user = cast(User, request.user)
    user_section = SectionUser.objects.get(section=section, user=user)

    return ExpensesSchema(
        period=period,
        currency=CurrencySchema(
            code=user_section.currency.code,
        ),
        expenses_data=ExpensesDataSchema(
            value=float(100),
            previous_value=None,
        ),
        chart_data=ChartDataSchema(
            type=chart_type,
            data=pie_chart(
                section=section,
                period=period,
                currency=user_section.currency,
            ),
        ),
    )