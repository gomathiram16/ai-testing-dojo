# 🥋 White Belt — Context Engineering

**Goal:** learn that *what you tell the AI* matters more than *which AI you use* —
and prove it with a number. You'll generate API tests three ways, measure the
hallucination rate and coverage of each, and build a scored prompt library.

**Time:** ~50 min (10 teach · 25 core · 8 critique · 7 optional stretch).
You work in pairs; report scores to the leaderboard.

## Setup (once)

```
pip install -r requirements.txt
make app            # DojoShop runs at http://127.0.0.1:8000  (spec at /openapi.json)
```

Keep the server running in one terminal; work in another. Your AI access is set
up either automatically (Codespaces secrets) or by the one-time `.env` step your
facilitator shares (see `ATTENDEE-SETUP.md`). No keys set up? Every round also
works offline on the provided example outputs.

## The three rounds

Each round: prompt two models (**Claude Opus 5** and **GPT-6**), save each result as a `.py` file, then
score it and log your best to the leaderboard.

```
python belts/white/score_prompt.py my_output.py          # static score (fast)
python belts/white/score_prompt.py my_output.py --run     # also execute under pytest
```

**Round 1 — Naive.** Use a baseline prompt (P01/P02 in `prompt_library.md`).
Note the hallucination rate and coverage. This is your floor.

**Round 2 — Structured.** Use a spec-grounded or role+format prompt
(P05–P07, P22–P23). Paste the OpenAPI spec from `/openapi.json`. Re-score.

**Round 3 — Context-engineered.** Add `context_doc.md` (the invariants + risk
notes) to your prompt (P08–P10). Re-score. Watch hallucination fall and coverage
and risk-targeting climb.

Record your **hallucination-rate drop from Round 1 → Round 3** — that delta is
the headline for the group debrief (target: a 40–60% reduction).

## Scoring

Five dimensions, 0–5 each, composite /25 — see `rubric.md`. Deterministic, so
the leaderboard is fair. Remember: a strong suite often *fails* against DojoShop
because it asserts the correct behaviour the app violates. That's a win, not a
bug in your tests.

## Stretch (optional, faster pairs)

- Try a **self-critique** prompt (P20/P21) and see if it beats your Round 3 score.
- Compare **Claude Opus 5 vs GPT-6** on the *same* prompt — who hallucinates less here?
- Get a suite to **100% route coverage** (hit the two routes the sample misses:
  `GET /carts/{id}` and `DELETE /carts/{id}/items/{item_id}`).

## What you leave with

Your forked, scored prompt library — reusable on your own APIs — plus a measured
feel for how much context engineering is worth.

## Files

- `prompt_library.md` — the **core** prompts for the 3 rounds (P01–P10)
- `prompt_library_advanced.md` — **stretch / go-deeper** prompts (P11–P23)
- `context_doc.md` — the invariants/risk doc for Round 3
- `rubric.md` — how scoring works
- `score_prompt.py` — the scorer
- `examples/` — a naive vs context-engineered sample output you can score right now

## How White Belt & Blue Belt relate

They both involve AI-generated tests, but they're **different jobs**:

- **White Belt = generate + score.** The scorer measures *hallucination* and *coverage* — is the AI writing real, broad tests? A suite can score **high here and still assert the wrong things**.
- **Blue Belt = audit a fixed, provided suite.** Everyone audits the *same* `belts/blue/ai_generated_suite/` (with a facilitator answer key), applying the heuristics to find what a green-looking suite still misses.

**Why they don't collide:** Blue Belt never audits an attendee's own White Belt output — it's a controlled exercise on a provided suite. So nothing an attendee prompts in White Belt can shortcut or spoil Blue Belt.

**The bridge:** the provided Blue suite passes **13/13, looks great, and catches 0 of 11 bugs**. High coverage ≠ catching bugs. White gets you a good-*looking* suite; Blue proves good-looking ≠ correct.
