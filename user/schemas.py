from typing import Optional

from ninja import Router, Schema

from subscription.schemas import SubscriptionSchema


class UserSchema(Schema):
    id: int
    username: str | None
    photo: str | None
    base_section: int | None
    active_subs: list[SubscriptionSchema]

class UserUpdateSchema(Schema):
    photo: Optional[str] = None
    base_section: Optional[int] = None