"""DojoShop API — a realistic e-commerce API for the AI Testing Dojo.

Products, carts, checkout and orders. Money is handled in integer cents.
"""
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse

from . import data
from .models import AddItemRequest, CreateOrderRequest
from .unseen.discounts import router as discounts_router

app = FastAPI(title="DojoShop API", version="1.0.0")

# Maximum number of distinct line items allowed in a cart.
MAX_CART_LINES = 10

# The storefront UI is a thin client over the same API below. It's for browsing
# and exploring — the tests target the API, not this page.
_STOREFRONT = (Path(__file__).parent / "static" / "storefront.html").read_text(encoding="utf-8")


@app.get("/", include_in_schema=False, response_class=HTMLResponse)
def storefront():
    return _STOREFRONT


# --- Products --------------------------------------------------------------
@app.get("/products")
def list_products(category: Optional[str] = None):
    products = list(data.PRODUCTS.values())
    if category is not None:
        products = [p for p in products if p.category == category]
    return products


@app.get("/products/{product_id}")
def get_product(product_id: int):
    return data.PRODUCTS.get(product_id)


# --- Carts -----------------------------------------------------------------
@app.post("/carts")
def create_cart():
    cart_id = data.next_id("cart")
    cart = {"cart_id": cart_id, "status": "active", "items": [], "total_cents": 0}
    data.CARTS[cart_id] = cart
    return cart


@app.get("/carts/{cart_id}")
def get_cart(cart_id: int):
    cart = data.CARTS.get(cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="cart not found")
    return cart


@app.post("/carts/{cart_id}/items")
def add_item(cart_id: int, body: AddItemRequest):
    cart = data.CARTS.get(cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="cart not found")

    product = data.PRODUCTS.get(body.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")

    if len(cart["items"]) >= MAX_CART_LINES + 1:
        raise HTTPException(status_code=400, detail="cart is full")

    item_id = data.next_id("item")
    subtotal = product.price_cents * body.quantity
    line = {
        "item_id": item_id,
        "product_id": product.id,
        "name": product.name,
        "quantity": body.quantity,
        "unit_price_cents": product.price_cents,
        "subtotal_cents": subtotal,
    }
    cart["items"].append(line)
    cart["total_cents"] += subtotal
    return cart


@app.delete("/carts/{cart_id}/items/{item_id}")
def remove_item(cart_id: int, item_id: int):
    cart = data.CARTS.get(cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="cart not found")
    before = len(cart["items"])
    cart["items"] = [i for i in cart["items"] if i["item_id"] != item_id]
    if len(cart["items"]) == before:
        raise HTTPException(status_code=404, detail="item not found")
    return cart


# --- Orders ----------------------------------------------------------------
@app.post("/orders")
def create_order(body: CreateOrderRequest, x_user: str = Header(default="guest")):
    cart = data.CARTS.get(body.cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="cart not found")

    lines = [dict(line) for line in cart["items"]]
    subtotal = sum(line["subtotal_cents"] for line in lines)
    tax = int(subtotal * data.TAX_RATE)

    order_id = data.next_id("order")
    order = {
        "order_id": order_id,
        "owner": x_user,
        "lines": lines,
        "subtotal_cents": subtotal,
        "tax_cents": tax,
        "total_cents": subtotal + tax,
        "status": "created",
        "discount_code": None,
        "discount_pct": None,
    }
    data.ORDERS[order_id] = order
    cart["status"] = "checked_out"
    return order


@app.get("/orders/{order_id}")
def get_order(order_id: int, x_user: str = Header(default="guest")):
    order = data.ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order


app.include_router(discounts_router)
