# White Belt — Prompt Scoring Rubric

`score_prompt.py` rates a generated test suite on five dimensions, 0–5 each, for
a **composite out of 25**. It is deterministic, so pairs can be ranked fairly on
the leaderboard. Higher is better.

| Dimension | 0 | 3 | 5 | How it's measured |
|-----------|---|---|---|-------------------|
| **Hallucination** (inverse) | Most calls hit routes/fields the API doesn't have | Some invented calls | No hallucinated calls | `(1 − hallucinated_calls / total_calls) × 5`, from static analysis of the paths the tests call vs the real routes |
| **Coverage** | Barely touches the API | ~half the routes | Most real routes exercised | `(real (method,route) pairs hit / total) × 5` |
| **Assertions** | No real assertions | ~1 per test | ≥2 meaningful asserts per test | assertion density (`asserts / test`), capped at 5 |
| **Executability** | Doesn't parse | — | Parses and (with `--run`) collects & runs | AST parse; with `--run`, pytest actually executes it |
| **Risk targeting** | Ignores high-risk areas | Hits orders **or** probes boundaries | Hits orders/access-control **and** probes boundaries (0, negatives, large values) | presence of high-risk routes + boundary literals |

## How to read it

- A **naive** prompt typically lands ~8–12/25: it hallucinates endpoints, covers little, and only checks `status_code == 200`.
- A **context-engineered** prompt typically lands ~20–24/25: real routes only, boundary and access-control probes, invariant-based assertions.
- The jump between them is the White Belt lesson — and you'll have *measured* it yourself.

## Note on "failing" tests

A high-quality suite will often **fail** when run against DojoShop. That's
correct: DojoShop is buggy, and good tests assert the *right* behaviour. `--run`
treats "ran but some failed" as executable (the tests did their job) — it only
penalises suites that can't run at all.

## Leaderboard

Report your best composite per round to the shared sheet. Track your own
**hallucination-rate drop** from Round 1 (naive) to Round 3 (context) — that
delta is the headline number for the debrief.
