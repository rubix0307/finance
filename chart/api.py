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

class Expenses:
    def __init__(self, user: User, section: Section, period: periods, chart_type: Literal['pie']):
        self.user = user
        self.section = section
        self.user_section = SectionUser.objects.get(section=section, user=user)
        self.period = period
        self.chart_type = chart_type

    def get_currency(self) -> CurrencySchema:
        return CurrencySchema(
            code=self.user_section.currency.code,
        )

    def get_expenses_data(self) -> ExpensesDataSchema:
        with open('chart/sql/week_total.sql', 'r') as f:
            sql_query = f.read()

        params = {
            'section_id': int(self.section.id),
            'convert_currency_code': self.user_section.currency.code,
            'period': self.period,
        }

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()

        return ExpensesDataSchema(**rows[0][0])

    def get_chart_data(self) -> ChartDataSchema:
        return ChartDataSchema(
            type=self.chart_type,
            data=pie_chart(
                section=self.section,
                period=self.period,
                currency=self.user_section.currency,
            ),
        )

    def get_schema(self) -> ExpensesSchema:
        return ExpensesSchema(
            period=self.period,
            currency=self.get_currency(),
            expenses_data=self.get_expenses_data(),
            chart_data=self.get_chart_data(),
        )


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
        chart_title=None,
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

    return Expenses(
        user=user,
        section=section,
        period=period,
        chart_type=chart_type,
    ).get_schema()
