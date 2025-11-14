from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ShopSchema(BaseModel):
    id: str
    name: str
    about: Optional[str] = None
    profile: Optional[str] = None
    is_verified: bool
    is_active: bool


class ProductSchema(BaseModel):
    id: str
    shop_id: Optional[str] = None
    title: str
    about: Optional[str] = None
    on_sale: bool = False
    is_active: bool = True
    top_sale: bool = False
    top_popular: bool = False
    sku: Optional[str] = None
    created_at: Optional[str] = None


class ProductVariationSchema(BaseModel):
    id: str
    product_id: str
    size: Optional[str] = None
    color: Optional[str] = None
    count: int = 0
    amount: int = 0
    price: Optional[float] = None
    discount: Optional[float] = None