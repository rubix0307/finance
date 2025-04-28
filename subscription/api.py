from django.core.handlers.wsgi import WSGIRequest
from ninja import Router
from ninja.security import django_auth

from .models import Plan
from .schemas import PlanSchema, PlanFeatureSchema, FeatureSchema

router = Router(auth=django_auth)

@router.get("/", response=list[PlanSchema])
def get_plans(request: WSGIRequest) -> list[PlanSchema]:
    return [PlanSchema(
        slug=plan.slug,
        title=plan.title,
        description=plan.description,
        price_stars=plan.price_stars,
        link=plan.link,
        features=[PlanFeatureSchema(
            feature=FeatureSchema(
                code=p_feature.feature.code,
                name=p_feature.feature.name,
                description=p_feature.feature.description,
            ),
            limit=p_feature.limit,
        ) for p_feature in plan.features.all()],
    ) for plan in Plan.objects.filter(is_active=True, translations__link__isnull=False)]