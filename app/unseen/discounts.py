"""Discounts module — the 'unseen' module used in the Black Belt showdown.

Codes:
  * fixed codes: SAVE10 (10%), SAVE25 (25%), HALF (50%)
  * dynamic codes: PCT<n> applies n percent, e.g. PCT30 -> 30%
"""
import re

from fastapi import APIRouter, HTTPException

from .. import data
from ..models import DiscountRequest

router = APIRouter()

FIXED_CODES = {"SAVE10": 10.0, "SAVE25": 25.0, "HALF": 50.0}


def resolve_pct(code: str):
    normalized = code.strip().upper()
    match = re.fullmatch(r"PCT(\d+)", normalized)
    if match:
        return float(match.group(1))
    return FIXED_CODES.get(normalized)


@router.post("/orders/{order_id}/discount")
def apply_discount(order_id: int, body: DiscountRequest):
    order = data.ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")

    pct = resolve_pct(body.code)
    if pct is None:
        raise HTTPException(status_code=400, detail="invalid discount code")

    discount_cents = int(order["subtotal_cents"] * pct / 100)
    new_subtotal = order["subtotal_cents"] - discount_cents
    tax = int(new_subtotal * data.TAX_RATE)

    order["discount_code"] = body.code
    order["discount_pct"] = pct
    order["tax_cents"] = tax
    order["total_cents"] = new_subtotal + tax
    return order
