from typing import Optional

from ninja import Schema, Field
from pydantic import BaseModel

from currency.schemas import CurrencySchema
from datetime import date



class SectionReceiptItemCategorySchema(Schema):
    id: int
    name: str

class SectionReceiptItemSchema(Schema):
    id: int
    name: str
    price: float
    category: SectionReceiptItemCategorySchema

class SectionReceiptShopSchema(Schema):
    id: int
    name: Optional[str] = None
    address: Optional[str] = None
    taxpayer_id: Optional[str] = None

class SectionReceiptSchema(Schema):
    id: int
    photo: str | None
    currency: CurrencySchema
    date: date | None
    items: list[SectionReceiptItemSchema]
    shop: Optional[SectionReceiptShopSchema] = None

class SectionUserSchema(Schema):
    id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    photo: Optional[str]
    currency: Optional[CurrencySchema]
    is_owner: bool


class MemberUpdateSchema(BaseModel):
    currency: Optional[str] = None

class SectionUpdateSchema(BaseModel):
    name: Optional[str] = None

class SectionMemberMiniSchema(Schema):
    id: int
    currency: CurrencySchema

class SectionMemberDeleteSchema(Schema):
    status: int

class SectionMiniSchema(Schema):
    id: int
    name: str

class SectionSchema(SectionMiniSchema):
    is_base: bool
    users: list[SectionUserSchema]

class ReceiptPaginationSchema(Schema):
    total: int
    page: int
    size: int
    pages: int
    results: list[SectionReceiptSchema]

class ErrorResponse(Schema):
    message: str

