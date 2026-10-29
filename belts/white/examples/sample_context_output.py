"""Sample output from a CONTEXT-ENGINEERED prompt (library prompt P09, risk-primed).

THE PROMPT THAT PRODUCED THIS:
    "Spec:
       <paste GET /openapi.json>
     Business rules & invariants:
       <paste belts/white/context_doc.md>
     Write pytest tests (httpx, http://127.0.0.1:8000) that would FAIL if any
     invariant is violated — prioritise boundaries, error paths and access control."

Same model as the naive one — only the prompt changed. Result: real routes only,
boundary + access-control probes, assertions grounded in the rules. Several tests
FAIL against DojoShop on purpose (a good prompt catches bugs). Scores ~22.1 / 25.

Run:   python belts/white/score_prompt.py belts/white/examples/sample_context_output.py
Live:  python belts/white/generate.py --preset context --model opus --out r3.py   (needs the gateway)
"""
import httpx

BASE_URL = "http://127.0.0.1:8000"


def _new_cart() -> int:
    return httpx.post(f"{BASE_URL}/carts").json()["cart_id"]


def test_list_products_returns_list():
    r = httpx.get(f"{BASE_URL}/products")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_valid_product():
    r = httpx.get(f"{BASE_URL}/products/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_missing_product_is_404():
    r = httpx.get(f"{BASE_URL}/products/9999")
    assert r.status_code == 404


def test_zero_quantity_rejected():
    cart = _new_cart()
    r = httpx.post(f"{BASE_URL}/carts/{cart}/items", json={"product_id": 8, "quantity": 0})
    assert r.status_code in (400, 422)


def test_negative_quantity_rejected():
    cart = _new_cart()
    r = httpx.post(f"{BASE_URL}/carts/{cart}/items", json={"product_id": 8, "quantity": -1})
    assert r.status_code in (400, 422)


def test_order_is_owner_scoped():
    cart = _new_cart()
    httpx.post(f"{BASE_URL}/carts/{cart}/items", json={"product_id": 8, "quantity": 1})
    order = httpx.post(f"{BASE_URL}/orders", json={"cart_id": cart}, headers={"X-User": "alice"}).json()
    r = httpx.get(f"{BASE_URL}/orders/{order['order_id']}", headers={"X-User": "bob"})
    assert r.status_code in (403, 404)
