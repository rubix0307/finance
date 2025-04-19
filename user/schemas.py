from typing import Optional

from ninja import Router, Schema

class UserSchema(Schema):
    id: int
    username: str | None
    photo: str | None
    base_section: int | None

class UserUpdateSchema(Schema):
    photo: Optional[str] = None
    base_section: Optional[int] = None