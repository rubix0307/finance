from typing import Optional

from ninja import Schema, Field
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
    username: str
    currency: Optional[CurrencySchema]
    is_owner: bool
    receipt_feed_size: Optional[int]

class SectionSchema(Schema):
    id: int
    name: str
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

