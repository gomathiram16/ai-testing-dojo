# White Belt — Prompt Library · Advanced (stretch & go-deeper)

The **13 advanced prompts (P11–P23)** — more involved strategies that tend to score
higher. Reach for these in the **stretch round**, if you're a faster pair, or when
you take this home to your own APIs. Start from the core (`prompt_library.md`) first.

Same placeholders as the core file:
`{BASE_URL}` → `http://127.0.0.1:8000` · `{OPENAPI}` → the `/openapi.json` spec ·
`{CONTEXT_DOC}` → `belts/white/context_doc.md`.

---

## 5 · Few-shot — ~16–20/25

**P11.** `Follow this example's style and rigour, then cover the rest of the API at {BASE_URL}.\n\nExample:\n\ndef test_missing_product_is_404():\n    r = httpx.get(f"{BASE_URL}/products/9999")\n    assert r.status_code == 404`

**P12.** `Here are two good tests (a boundary test and an access-control test). Write ~10 more in the same spirit for {BASE_URL}.\n[paste 2 exemplars]`

## 6 · Plan-then-generate (CoT) — ~18–22/25

**P13.** `First, list the test conditions you would cover for {BASE_URL} (happy path, boundaries, errors, state, access). Then write the pytest code for each.`

**P14.** `Think step by step: enumerate every endpoint, its inputs, and its failure modes. Produce a checklist, then implement it as pytest tests.`

## 7 · Heuristic-primed — ~20–24/25

**P15.** `Write pytest tests for {BASE_URL} that explicitly apply boundary-value analysis and equivalence partitioning to quantity, cart size, and product ids.`

**P16.** `Generate tests that check state transitions: empty-cart checkout, adding items after checkout, and re-reading a cart after delete.`

**P17.** `Write metamorphic and consistency tests: filtering products by category two ways should agree; a cart total should equal the sum of its lines.`

## 8 · Negative / edge-focused — ~17–21/25

**P18.** `Write pytest tests for {BASE_URL} that focus on invalid input and error paths: negative/zero quantity, unknown ids, empty payloads, over-limit carts.`

**P19.** `Prioritise boundaries and failure modes over happy paths. For each endpoint, write at least one test that should return a 4xx.`

## 9 · Self-critique / refine — ~21–24/25

**P20.** `Write pytest tests for {BASE_URL}. Then critique your own tests for hallucinated endpoints, missing boundaries, and weak assertions, and output an improved version.`

**P21.** `Draft tests, then check each call against this spec and delete or fix any endpoint or field not present:\n{OPENAPI}\nOutput only the corrected suite.`

## 10 · Format-constrained — ~16–20/25

**P22.** `Write pytest tests using httpx against {BASE_URL}. Rules: one behaviour per test; test names describe the behaviour; every test has at least two assertions; no print statements; only real endpoints.`

**P23.** `Output a single runnable pytest file. Use a BASE_URL constant, a helper to create a cart, and group tests by resource. No markdown, code only.`

---

### When to reach for these

- **Self-critique (P20/P21)** — often the single biggest jump; great to beat your Round 3 score.
- **Heuristic-primed (P15–P17)** — explicitly aim the AI at the testing techniques; very strong.
- **Plan-then-generate (P13/P14)** — good when coverage is your weak spot.
- **Few-shot / format-constrained** — tidy, consistent output; good for "back-home" reuse.

Score the same way: `python belts/white/score_prompt.py your_output.py`, and log your best.
