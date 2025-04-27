from ninja import Schema

class PlanSchema(Schema):
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

