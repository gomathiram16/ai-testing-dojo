"""AI-generated API test suite for DojoShop.

13 tests. Clean names. Good structure. Every single one passes.

THE PROMPT THAT PRODUCED THIS:
    "You are an experienced QA engineer. Here is the OpenAPI specification
     for DojoShop, a FastAPI e-commerce service:

       <paste the full output of GET http://127.0.0.1:8000/openapi.json>

     Write a comprehensive pytest suite for this API.
       - Use fastapi.testclient.TestClient, importing the app with
         `from app.main import app`.
       - Cover the products, carts and orders endpoints.
       - Use clear, descriptive test function names.
       - Assert status codes and the key response fields.
       - Group the tests by resource with comments.
     Return a single runnable test file."

Note what this prompt does NOT say: nothing about business rules or invariants,
nothing about invalid input, boundaries, illegal state changes or access
control, and no instruction to write tests that FAIL when a rule is violated.
That omission is the whole point — it produces a tidy, green, happy-path suite
that catches none of the 11 seeded bugs. (Contrast the White Belt context prompt
P09, which adds exactly those missing pieces.)

Your job in the Blue Belt: work out what it MISSES.
Run it first so you can see the wall of green:

    python -m pytest belts/blue/ai_generated_suite/ -v
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _new_cart() -> int:
    return client.post("/carts").json()["cart_id"]


# --- Products --------------------------------------------------------------
def test_list_products_returns_200():
    r = client.get("/products")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_products_not_empty():
    assert len(client.get("/products").json()) > 0


def test_product_has_expected_fields():
    product = client.get("/products").json()[0]
    for field in ("id", "name", "category", "price_cents", "stock"):
        assert field in product


def test_get_product_by_id():
    r = client.get("/products/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_product_with_unknown_id():
    r = client.get("/products/9999")
    assert r.status_code == 200


def test_filter_products_by_category():
    r = client.get("/products", params={"category": "Books"})
    assert r.status_code == 200
    assert all(p["category"] == "Books" for p in r.json())


# --- Carts -----------------------------------------------------------------
def test_create_cart():
    r = client.post("/carts")
    assert r.status_code == 200
    assert r.json()["status"] == "active"
    assert r.json()["items"] == []


def test_add_item_to_cart():
    cart_id = _new_cart()
    r = client.post(f"/carts/{cart_id}/items", json={"product_id": 8, "quantity": 1})
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1


def test_cart_total_matches_line_items():
    cart_id = _new_cart()
    client.post(f"/carts/{cart_id}/items", json={"product_id": 8, "quantity": 2})
    cart = client.get(f"/carts/{cart_id}").json()
    assert cart["total_cents"] == sum(i["subtotal_cents"] for i in cart["items"])


def test_remove_item_from_cart():
    cart_id = _new_cart()
    added = client.post(f"/carts/{cart_id}/items", json={"product_id": 8, "quantity": 1}).json()
    item_id = added["items"][0]["item_id"]
    r = client.delete(f"/carts/{cart_id}/items/{item_id}")
    assert r.status_code == 200
    assert r.json()["items"] == []


# --- Orders ----------------------------------------------------------------
def test_checkout_creates_order():
    cart_id = _new_cart()
    client.post(f"/carts/{cart_id}/items", json={"product_id": 9, "quantity": 1})
    r = client.post("/orders", json={"cart_id": cart_id})
    assert r.status_code == 200
    assert r.json()["status"] == "created"


def test_order_total_is_subtotal_plus_tax():
    cart_id = _new_cart()
    client.post(f"/carts/{cart_id}/items", json={"product_id": 8, "quantity": 1})
    order = client.post("/orders", json={"cart_id": cart_id}).json()
    assert order["total_cents"] == order["subtotal_cents"] + order["tax_cents"]


def test_get_order_by_id():
    cart_id = _new_cart()
    client.post(f"/carts/{cart_id}/items", json={"product_id": 8, "quantity": 1})
    order = client.post("/orders", json={"cart_id": cart_id}).json()
    r = client.get(f"/orders/{order['order_id']}")
    assert r.status_code == 200
    assert r.json()["order_id"] == order["order_id"]
