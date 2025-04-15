from ninja import Router, Schema

class UserSchema(Schema):
    id: int
    username: str | None
