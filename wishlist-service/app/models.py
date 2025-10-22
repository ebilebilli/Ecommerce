from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Wishlist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    product_variation_id: int = Field(index=True)
    shop_id: int = Field(default=1, index=True)  # Default 1, çünki hər məhsulun mağazası var
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Eyni user eyni product'u eyni shop-da iki dəfə əlavə edə bilməz
    class Config:
        unique_together = [('user_id', 'product_variation_id', 'shop_id')]

# API Schemas
class WishlistCreate(SQLModel):
    user_id: int
    product_variation_id: int
    shop_id: int = 1  # Default dəyər

class WishlistResponse(SQLModel):
    id: int
    user_id: int
    product_variation_id: int
    shop_id: int
    created_at: datetime