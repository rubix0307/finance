from ninja import Schema

class PlanSchema(Schema):
    slug: str
    title: str
    description: str | None
    price_stars: int | None
    features: list['PlanFeatureSchema']

class FeatureSchema(Schema):
    code: str
    name: str
    description: str | None

class PlanFeatureSchema(Schema):
    feature: FeatureSchema
    limit: int | None

class SubscriptionSchema(Schema):
    plan: PlanSchema
    started_at: str
    expires_at: str | None