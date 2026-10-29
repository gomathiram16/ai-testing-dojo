# The AI Testing Dojo — DojoShop

A deliberately buggy e-commerce API for the AutomationSTAR 2026 tutorial
**"The AI Testing Dojo: Build, Break & Master Agents."**

DojoShop models a real store (products, cart, checkout, orders, discounts) but
carries a controlled set of seeded bugs. Across three belts you will:

- **White Belt** — generate AI test suites against it and measure hallucination.
- **Blue Belt** — audit AI-generated suites with six testing heuristics.
- **Black Belt** — build an agent that hunts bugs in an unseen module.

## Run it

```
pip install -r requirements.txt
make app        # then open in a browser:
                #   http://127.0.0.1:8000/       the DojoShop storefront — browse & click
                #   http://127.0.0.1:8000/docs   the API, click-to-call (Swagger UI)
make test       # runs the test suite
```

The storefront is a thin UI over the same API — handy for exploring the shop.
The tutorial's testing targets the **API**, not the page.

## Endpoints

- Products: `GET /products`, `GET /products/{id}`
- Carts: `POST /carts`, `GET /carts/{id}`, `POST /carts/{id}/items`, `DELETE /carts/{id}/items/{item_id}`
- Orders: `POST /orders`, `GET /orders/{id}`
- Discounts (Black Belt / unseen): `POST /orders/{id}/discount`

Orders are associated with a caller via the optional `X-User` header.

> **Attendees:** please don't open `solutions/` — that's the facilitator answer key.
