from pydantic import BaseModel


class ShopSchema(BaseModel):
    id: str
    name: str