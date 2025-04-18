from ninja import Router, Schema

class UserSchema(Schema):
    id: int
    username: str | None
    photo: str | None

class UserUpdateSchema(Schema):
    photo: str
