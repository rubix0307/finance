import hashlib
from typing import Any
from uuid import uuid4
from django.core.files.base import ContentFile
from django.core.handlers.wsgi import WSGIRequest
from ninja import Router
from ninja.security import django_auth

from section.models import Section
from subscription.schemas import SubscriptionSchema, PlanSchema, PlanFeatureSchema, FeatureSchema
from subscription.services import SubscriptionManager
from .utils import fetch_image_bytes
from .schemas import UserSchema, UserUpdateSchema

router = Router()


@router.get("/me/", auth=django_auth, response=UserSchema)
def get_me(request: WSGIRequest) -> UserSchema:
    user = request.user
    user_subs = SubscriptionManager(user)

    return UserSchema(
        id=user.id,
        username=user.username,
        photo=user.photo,
        base_section=user.base_section.id,
        active_subs=[SubscriptionSchema(
            plan=PlanSchema(
                slug=sub.plan.slug,
                title=sub.plan.title,
                description=sub.plan.description,
                price_stars=sub.plan.price_stars,
                features=[PlanFeatureSchema(
                    feature=FeatureSchema(
                        code=p_feature.feature.code,
                        name=p_feature.feature.name,
                        description=p_feature.feature.description,
                    ),
                    limit=p_feature.limit,
                ) for p_feature in sub.plan.features.all()],
            ),
            started_at=str(sub.started_at),
            expires_at=str(sub.expires_at) if sub.expires_at else None,
        ) for sub in user_subs.active_subs]

    )

@router.post("/me/", response=UserSchema)
def update_me(
    request: WSGIRequest,
    data: UserUpdateSchema,
    **kwargs: dict[str, Any]
) -> UserSchema:
    user = request.user

    if data.photo:
        image_bytes, ext = fetch_image_bytes(data.photo)

        new_hash = hashlib.md5(image_bytes).hexdigest()
        old_hash = None
        if user.photo:
            try:
                user.photo.open('rb')
                old_hash = hashlib.md5(user.photo.read()).hexdigest()
                user.photo.close()
            except Exception:
                old_hash = None

        if new_hash != old_hash:
            filename = f"{uuid4()}.{ext}"
            user.photo.save(filename, ContentFile(image_bytes), save=False)

    if data.base_section:
        if isinstance(data.base_section, int):
            try:
                new_base_section = Section.objects.get(id=data.base_section)
                if new_base_section.memberships.filter(user=user).exists():
                    user.base_section = new_base_section
            except (Section.DoesNotExist, Exception):
                ...

    user.save()
    return UserSchema(
        id=user.id,
        username=user.username,
        photo=user.photo,
        base_section=user.base_section.id,
    )