# DojoShop — Context Document (White Belt)

Paste this into the AI **alongside** your prompt in the context-engineering
round. It describes how DojoShop is *supposed* to behave. Good context makes the
model generate tests that assert the right invariants — which means those tests
will catch the bugs DojoShop actually contains.

## System overview

DojoShop is a small e-commerce API. A shopper browses products, builds a cart,
checks out to create an order, and can apply a discount code to an order. All
money is in **integer cents**. Callers are identified by an optional `X-User`
request header (default `guest`).

## Endpoints & contracts

| Method | Path | Purpose | Key rules |
|--------|------|---------|-----------|
| GET | `/products` | List products; optional `?category=` | Filtering must be consistent (case-insensitive) with the full list |
| GET | `/products/{id}` | One product | **404** if the id does not exist |
| POST | `/carts` | Create a cart | Returns `cart_id`, status `active`, empty items, total 0 |
| GET | `/carts/{id}` | Read a cart | `total_cents` must equal the sum of line `subtotal_cents` |
| POST | `/carts/{id}/items` | Add `{product_id, quantity}` | `quantity >= 1`; product must exist; max **10** distinct lines; cart must be `active` |
| DELETE | `/carts/{id}/items/{item_id}` | Remove a line | Cart total must be recomputed afterward |
| POST | `/orders` | Checkout `{cart_id}` | Cart must be **non-empty**; quantities must not exceed **stock**; tax is 20% of subtotal, **rounded** to the nearest cent; checkout marks the cart `checked_out` |
| GET | `/orders/{id}` | Read an order | Only the **owner** (matching `X-User`) may read it; otherwise 403/404 |
| POST | `/orders/{id}/discount` | Apply `{code}` | Percentage must be within **0–100**; total must never go negative |

## Invariants (assert these)

1. **Money is non-negative.** No cart or order total is ever below zero.
2. **Totals are consistent.** A cart's `total_cents` equals the sum of its line subtotals, at all times (including after a delete).
3. **Quantities are positive integers** (`>= 1`). Zero and negatives are rejected.
4. **Stock is respected.** You cannot order more of a product than its `stock`.
5. **Tax rounds** to the nearest cent (half-up), never truncates.
6. **State is legal.** You cannot check out an empty cart, nor modify a cart after checkout.
7. **Access is scoped.** A caller can only read their own orders.
8. **Missing resources 404.** Unknown product/cart/order ids return 404, not 200-with-null.
9. **Discounts are bounded.** 0 ≤ percentage ≤ 100.

## Risk priorities (test these first)

- **Money & discounts** — wrong totals or negative prices are the costliest failures.
- **Access control** — reading another user's order is a security defect.
- **Stock** — overselling has real-world consequences.
- **Boundaries** — quantity 0 / negative / max, cart at the line limit, tax rounding edges.

## Seed data notes

Product ids `1`–`10` exist. Product `5` (HTC One Mini) has `stock: 0`. Prices
range from a `999`-cent book to a `249900`-cent laptop. Categories include
`Computers`, `Electronics`, `Apparel`, `Books`, `Gift Cards`.
