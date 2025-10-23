from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

from sqlalchemy import DateTime

class ProductBase(BaseModel):
    shop_id: Optional[UUID] = Field(None, description="ID of the shop, added by middleware")
    title: str = Field(..., max_length=100)
    about: Optional[str] = Field(None, max_length=1000)
    on_sale: bool = False
    is_active: bool = True
    top_sale: bool = False
    top_popular: bool = False
    sku: Optional[str] = Field(None, max_length=50)
    base_price: float = Field(..., gt=0)

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: UUID
    created_at: datetime

    categories: List["Category"] = []

    class Config:
        from_attributes = True

from .category import Category  # Circular import resolution