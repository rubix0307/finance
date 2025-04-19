import hashlib
from typing import Any
from uuid import uuid4

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.handlers.wsgi import WSGIRequest
from ninja import Router
from ninja.security import django_auth

from section.models import Section
from .utils import fetch_image_bytes
from .schemas import UserSchema, UserUpdateSchema

router = Router()


@router.get("/me/", auth=django_auth, response=UserSchema)
def get_me(request: WSGIRequest) -> UserSchema:
    user = request.user
    return UserSchema(
        id=user.id,
        username=user.username,
        photo=user.photo,
        base_section=user.base_section.id,
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