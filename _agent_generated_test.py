from fastapi.testclient import TestClient
from app.main import app
from app import data
client = TestClient(app)

def _order():
    data.reset()
    c = client.post('/carts').json()['cart_id']
    client.post(f'/carts/{c}/items', json={'product_id': 2, 'quantity': 1})
    return client.post('/orders', json={'cart_id': c}).json()['order_id']

def _cart():
    data.reset()
    return client.post('/carts').json()['cart_id']

def test_discount_reduces_total():
    oid = _order()
    r = client.post(f'/orders/{oid}/discount', json={'code': 'SAVE10'})
    assert r.status_code == 200
    assert r.json()['total_cents'] > 0
