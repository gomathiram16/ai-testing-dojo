# 🥋 Black Belt — Agent Showdown: Build It, Then Break It

**Goal:** wire a lightweight testing *agent* — a loop that generates tests, runs
them, reads the failures, and regenerates sharper tests — then set it loose on an
unseen module and watch where it excels and where it hallucinates.

**Time:** ~55 min (10 teach · 25 build/run · 15 showdown · 5 critique).

## Build / Break / Master — where each happens

- **BUILD** *(core, ~25 min)* — wire the one missing seam, `class LLMGenerator`,
  so the agent writes tests with a real model, then run the loop and watch it
  assemble: `--target cart` then `--generator llm`. Round 1 is a dumb happy-path
  test; round 2 sharpens using the failures. *(You complete and run the loop — the
  learning is in the loop, not in typing boilerplate.)*
- **BREAK — two senses:**
  - *The agent breaks the app* — `--target discounts` sets it loose on an unseen
    module and it surfaces the seeded negative-total bug.
  - *You break the agent* — the adversarial round (`injection_demo.py`, or
    `injection_live.py --naive`) hijacks the test-writing agent with a prompt
    injection hidden in product #11. A hijacked agent still "passes."
- **MASTER** *(critique + debrief)* — know where it adds value (tireless boundary
  probing) and where it fails (no sense of which risks matter; it can be
  hijacked); apply the defences (adversarial oracle, scan retrieved content,
  human-in-the-loop); and land on **accept / revise / override** — calibrated
  judgement, not hype or fear.

> One-liner: *build the loop and wire it to a real model; break things twice (the
> agent breaks an unseen module, then we break the agent with an injection); and
> master it by learning when to trust, audit, or override it.*

## The loop

```
        ┌──────────────┐
        │  generate    │  ← ask the model for tests (using your White Belt prompts)
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │  execute     │  ← run them against DojoShop (pytest)
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │  analyse     │  ← failing tests = bugs found; feed them back
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │ regenerate   │  ── repeat ──▶
        └──────────────┘
```

## Core — run the agent on a known module (25 min)

The agent runs **offline by default** (a deterministic mock stands in for the
model, so no keys are needed to see the loop work):

```
python belts/black/agent/dojo_agent.py --target cart
```

Watch it: round 1 is a happy-path test that passes and finds nothing; by round 2
it's probing boundaries and **surfacing real bugs**. That progression — dumb
first, sharper with feedback — is the whole point.

Then open `agent/dojo_agent.py` and find `class LLMGenerator` with its `TODO`.
That's the one seam attendees wire: swap the mock for a real model call (Claude Opus 5 / GPT-6, via the gateway)
using a White Belt prompt. (Everything else — execute, analyse, loop — is done.)

## Showdown — the unseen module (15 min)

Now point it at a module it has never seen:

```
python belts/black/agent/dojo_agent.py --target discounts
```

Watch it hunt. Somewhere in there is a seeded flaw (a discount that pushes the
total below zero). Does the agent find it? How many rounds does it take? See
`showdown.md` for what to watch and when to intervene.

## What you leave with

A working generate→execute→analyse→regenerate loop you built yourself, and — more
importantly — a felt sense of where an agent adds value (tireless, systematic
probing) and where it doesn't (it doesn't *know* which risks matter; you do).

## Files

- `agent/dojo_agent.py` — the runnable agent (mock generator + the LLM seam to wire)
- `showdown.md` — the showdown brief + observer/critique guide
