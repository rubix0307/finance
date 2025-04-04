from typing import Any

from django.core.handlers.wsgi import WSGIRequest
from django.db import connection
from ninja import Router

from section.decorators import SectionRequired
from section.models import Section
from .schemas import ChartPieSchema

router = Router(tags=["Charts"])


@router.get("{section_pk}/charts/pie/", response=list[ChartPieSchema])
@SectionRequired
def pie_chart(
        request: WSGIRequest,
        section_pk: int,
        **kwargs: dict[str, Any],
) -> list[ChartPieSchema]:
    section: Section = kwargs.get("section", Section.objects.get(pk=section_pk))

    with open('section/sql/pie.sql', 'r') as f:
        sql_query = f.read()

    params = {
        'section_id': int(section.id),
        'convert_currency_code': 'EUR',
        'interval': '700 weeks',
    }

    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    data_dicts = [dict(zip(columns, row)) for row in rows]

    return [ChartPieSchema.model_validate(item) for item in data_dicts]