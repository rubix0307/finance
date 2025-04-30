from typing import Optional

from ninja import Schema
from pydantic import Field


class PlanSchema(Schema):
    slug: str
    title: str
    description: Optional[str]
    price_stars: Optional[int]
    link: Optional[str]
    features: list['PlanFeatureSchema']

class FeatureSchema(Schema):
    code: str
    name: str
    description: Optional[str]

class PlanFeatureSchema(Schema):
    feature: FeatureSchema
    limit: int | None
    remaining: Optional[int] = Field(default=None)

class SubscriptionSchema(Schema):
    plan: PlanSchema
    started_at: str
    expires_at: Optional[str]