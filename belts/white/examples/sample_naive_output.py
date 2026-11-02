"""Sample output from a NAIVE prompt (library prompt P01).

THE PROMPT THAT PRODUCED THIS:
    "Write API tests for this e-commerce API at http://127.0.0.1:8000."

That's the whole prompt — no spec, no rules. Illustrative of the result: a
hallucinated singular /product route, an invented /checkout endpoint, shallow
status-only assertions, and thin coverage. Scores ~9.8 / 25.

Run:   python belts/white/score_prompt.py belts/white/examples/sample_naive_output.py
Live:  python belts/white/generate.py --preset naive --model opus --out r1.py   (needs the gateway)
"""
import httpx

BASE_URL = "http://127.0.0.1:8000"


def test_get_products():
    r = httpx.get(f"{BASE_URL}/products")
    assert r.status_code == 200


def test_get_single_product():
    r = httpx.get(f"{BASE_URL}/product/1")  # hallucinated: route is /products/{id}
    assert r.status_code == 200


def test_checkout():
    r = httpx.post(f"{BASE_URL}/checkout", json={})  # hallucinated: no such route
    assert r.status_code == 200
