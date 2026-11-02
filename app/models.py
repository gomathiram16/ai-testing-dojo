"""Pydantic request/domain models for DojoShop."""
from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    category: str
    sku: str
    price_cents: int
    stock: int
    description: str = ""


class AddItemRequest(BaseModel):
    product_id: int
    quantity: int


class CreateOrderRequest(BaseModel):
    cart_id: int


class DiscountRequest(BaseModel):
    code: str
