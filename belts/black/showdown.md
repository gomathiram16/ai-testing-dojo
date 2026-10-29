# Black Belt — The Showdown (observer & critique guide)

The agent attacks the **unseen discounts module**. Your pair doesn't just watch —
you observe, critique, and decide when to step in.

```
python belts/black/agent/dojo_agent.py --target discounts --rounds 3
```

## What's really happening

The discounts module applies percentage codes (`SAVE10`, `HALF`, or `PCT<n>`).
It has a seeded flaw: **it never checks that the percentage is ≤ 100**, so a code
like `PCT200` drives the order total **negative**. A happy-path test sails past
it; only a boundary probe catches it.

Round by round you should see the loop go from "all green, nothing here" to
"🐛 found a bug" once it starts testing beyond 100%.

## Watch for — where agents shine

- **Tireless enumeration.** It'll try boundary after boundary without getting bored.
- **Fast feedback.** Generate → run → read failures in seconds.

## Watch for — where agents mislead

- **False confidence.** Round 1 passes and *looks* thorough. Passing ≠ correct (your Blue Belt lesson).
- **Wrong oracle.** An agent may assert what the code *does*, not what it *should* — locking in the bug.
- **Missing the risk.** It has no idea that "money going negative" is catastrophic. It treats every boundary as equal. You don't.

## When to intervene

- If it stalls on happy paths, feed it a White Belt heuristic-primed prompt (P15–P17).
- If it "fixes" a test by loosening the assertion, stop it — that's the agent gaming the loop.
- Ask your pair: *would you ship on the strength of what this agent produced? What would you still check by hand?*

## The takeaway line

An agent is a superb **junior** tester: fast, tireless, literal. It multiplies a
skilled human and endangers an unskilled one. The context engineering (White) and
the audit instinct (Blue) are exactly what turn its output from a liability into
leverage.
