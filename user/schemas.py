from ninja import Router, Schema

class UserSchema(Schema):
    id: int
    username: str | None
    photo: str | None
    base_section: int | None

class UserUpdateSchema(Schema):
    base_section: int | None
