# 🥋 Blue Belt — Heuristic Auditing: Catching What AI Misses

**Goal:** AI-generated tests pass. They even look good. But they silently miss
boundaries, assert the wrong invariants, and overfit to happy paths. This belt
gives you a systematic way to catch that — a quality gate you can reuse on any
AI testing tool.

**Time:** ~50 min (10 teach · 25 bug hunt · 8 critique · 7 optional stretch).

## The setup

You've been handed `ai_generated_suite/test_dojoshop_ai.py` — 13 tests an LLM
produced from the OpenAPI spec. Run it:

```
python -m pytest belts/blue/ai_generated_suite/ -v
```

**All 13 pass.** Thirteen green ticks. Ship it?

DojoShop contains **11 known bugs** in the areas this suite covers — including a
security hole and a money error. Your job is to find out how many the suite
actually catches.

## The bug hunt (core, 25 min)

Work in pairs. Open `heuristics_checklist.md` and go through the six heuristics
**in order** — then the 2026 bonus (#7, the Adversarial Oracle) — auditing the AI
suite against each one. Log every gap on `audit_worksheet.md`.

For each heuristic ask: *what did the suite check, what did it miss, and how
much does that gap matter?*

Two questions worth asking about every single assertion:

1. **Is this asserting the requirement, or just restating the code?**
2. **Could this assertion ever fail?**

Score yourself: **1 point per genuine gap found.** Report to the leaderboard.

## Group critique (8 min)

We'll put the answer key on screen and compare. Expect a moment of discomfort —
the suite's real bug-catching score is lower than anyone guesses.

## Stretch (optional, 7 min)

Pick the two gaps you think are most dangerous and **write the missing tests**.
Run them — they should fail, because they're finally asserting the right thing.
A failing test that catches a real bug beats a passing test that doesn't.

## What you leave with

A filled-in 6-heuristic quality gate (plus the 2026 Adversarial-Oracle bonus): a repeatable audit process you can run
against any AI-generated suite on Monday morning, grounded in established
testing theory rather than vibes.

## Files

- `ai_generated_suite/test_dojoshop_ai.py` — the suite under audit
- `heuristics_checklist.md` — the six heuristics **+ the 2026 bonus (#7, Adversarial Oracle)** + probing questions (your takeaway)
- `audit_worksheet.md` — where you log findings

## How White Belt & Blue Belt relate

They both involve AI-generated tests, but they're **different jobs**:

- **White Belt = generate + score.** Its scorer measures *hallucination* and *coverage* — a suite can score high and still assert the wrong things.
- **Blue Belt = audit a fixed, provided suite.** Everyone audits the *same* `ai_generated_suite/` (with the answer key in `solutions/`), applying the heuristics to find what a green-looking suite misses.

**Why they don't collide:** Blue Belt never audits an attendee's own White Belt output — it's a controlled exercise on *this* provided suite. Nothing an attendee prompts in White Belt can shortcut or spoil it.

**The bridge:** this suite passes **13/13, looks great, and catches 0 of 11 bugs** — high coverage ≠ catching bugs. If a sharp pair's White Belt prompt genuinely catches a bug, surface it as the bridge in action.
