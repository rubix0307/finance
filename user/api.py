import hashlib
from typing import Any
from uuid import uuid4

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.handlers.wsgi import WSGIRequest
from ninja import Router
from ninja.security import django_auth

from .schemas import UserSchema, UserUpdateSchema

router = Router()

@router.get("/me/", auth=django_auth, response=UserSchema)
def get_me(request: WSGIRequest) -> UserSchema:
    return request.user

@router.post("/me/", response=UserSchema)
def update_me(
    request: WSGIRequest,
    data: UserUpdateSchema,
    **kwargs: dict[str, Any]
) -> UserSchema:
    user = request.user
    try:
        if data.photo:
            resp = requests.get(data.photo)
            resp.raise_for_status()

            content_type = resp.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                soup = BeautifulSoup(resp.text, 'html.parser')
                img = soup.find('img')
                if not img or not img.get('src'):
                    raise ValueError("Не удалось найти <img> на странице Telegram")
                image_url = img['src']
                resp2 = requests.get(image_url)
                resp2.raise_for_status()
                image_bytes = resp2.content
                ext = image_url.split('.')[-1].split('?')[0] or 'jpg'
            else:
                image_bytes = resp.content
                ext = data.photo.split('.')[-1].split('?')[0] or 'jpg'

            new_hash = hashlib.md5(image_bytes).hexdigest()
            old_hash = None
            if user.photo:
                try:
                    user.photo.open('rb')
                    old_content = user.photo.read()
                    user.photo.close()
                    old_hash = hashlib.md5(old_content).hexdigest()
                except Exception:
                    old_hash = None

            if new_hash != old_hash:
                filename = f"{uuid4()}.{ext}"
                user.photo.save(filename, ContentFile(image_bytes), save=False)

        user.save()
    finally:
        return user