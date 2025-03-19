from pydantic import BaseModel, Field
from typing import List, Optional


class ShopSchema(BaseModel):
    name: Optional[str] = Field(None)
    address: Optional[str] = Field(None)
    taxpayer_id: Optional[str] = Field(None)


class ItemSchema(BaseModel):
    name: str = Field(...)
    price: float = Field(...)
    category_id: int = Field(...)


class ReceiptSchema(BaseModel):
    is_receipt: bool = Field(...)
    shop: ShopSchema
    items: List[ItemSchema]
    date: Optional[str] = Field(None)
    time: Optional[str] = Field(None)
    currency: str = Field(...)