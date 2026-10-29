# White Belt — Prompt Library · Core (the 3 rounds)

The **10 core prompts (P01–P10)** for the three timed rounds. Start here. For
stretch and "go-deeper" strategies (few-shot, chain-of-thought, heuristic-primed,
self-critique, format-constrained), see **`prompt_library_advanced.md`**.

Use the **same prompt with two models — Claude Opus 5 and GPT-6** (Gemini 3.x
optional) — to compare them, then score the output with `score_prompt.py`.
Placeholders:

- `{BASE_URL}` → `http://127.0.0.1:8000`
- `{OPENAPI}` → paste the spec from `GET /openapi.json` (or the `/docs` schema)
- `{CONTEXT_DOC}` → paste `belts/white/context_doc.md`

Typical composite scores are noted as a rough guide — measure your own.

---

## 1 · Naive baseline (the control) — ~8–12/25   ·   *Round 1*

**P01.** `Write API tests for this e-commerce API at {BASE_URL}.`

**P02.** `Generate pytest tests for a shopping cart REST API.`

> Purpose: establish your floor. Expect hallucinated routes and status-only asserts.

## 2 · Role-primed — ~10–14/25   ·   *optional warm-up*

**P03.** `You are a senior SDET. Write thorough pytest API tests for the service at {BASE_URL} (products, carts, orders).`

**P04.** `Act as a security-minded QA engineer. Write API tests for {BASE_URL}, paying attention to error handling and access control.`

## 3 · Spec-grounded — ~15–19/25   ·   *Round 2*

**P05.** `Here is the OpenAPI spec:\n{OPENAPI}\nWrite pytest tests using httpx against {BASE_URL}. Only call endpoints defined in the spec.`

**P06.** `Using ONLY the routes and schemas in this OpenAPI spec, write pytest tests. Do not invent endpoints or fields.\n{OPENAPI}`

**P07.** `From this OpenAPI spec, produce one pytest test per operation (path+method), asserting status codes and response shape.\n{OPENAPI}`

## 4 · Context-doc-augmented — ~20–24/25   ·   *Round 3*

**P08.** `Here is how the system should behave:\n{CONTEXT_DOC}\nWrite pytest tests (httpx, {BASE_URL}) that assert these invariants. Prefer testing the rules over the happy path.`

**P09.** `Spec:\n{OPENAPI}\nBusiness rules & invariants:\n{CONTEXT_DOC}\nWrite tests that would FAIL if any invariant is violated.`

**P10.** `Using the invariants below, write tests that check money is never negative, totals stay consistent, stock is respected, and orders are owner-scoped.\n{CONTEXT_DOC}`

---

### How to use in the rounds

1. **Round 1 — naive:** P01 (or P02). Note the low score and the hallucinations.
2. **Round 2 — spec-grounded:** P05–P07, pasting the OpenAPI spec. Re-score.
3. **Round 3 — context-engineered:** P08–P10, adding `context_doc.md`. Re-score,
   then **adapt it yourself** — this is where the skill (and the leaderboard) lives.
4. Run each in **Claude Opus 5** *and* **GPT-6**, save each output as a `.py` file,
   score it (`python belts/white/score_prompt.py your_output.py`), and log your best.

*Faster pairs / stretch → move to `prompt_library_advanced.md`.*
*(Models are served via the gateway; confirm exact versions before the event — they change monthly.)*
