from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class OrderRequest(BaseModel):
    product_id: int
    count: int

class AnalyticsRequest(BaseModel):
    shop: int
    product_variation: int
    count: int
    original_price: str
    sale_price: str