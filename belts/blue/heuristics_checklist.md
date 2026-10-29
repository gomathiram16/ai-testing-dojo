# The Quality-Gate Heuristics (6 + 1 bonus)

A repeatable process for auditing **any** AI-generated test suite. Work through
the six heuristics in order, then the 2026 bonus (#7, AI-specific). For each, ask
the questions, and log every gap you find on the worksheet.

This is the artifact you take home — it works on any AI testing tool, not just
this one.

---

## 1 · Equivalence Partitioning
*Group inputs that should behave the same way. Has the suite tested one from each group?*

- For each input, what are the **valid**, **invalid**, and **special** groups?
- Does the suite test any *invalid* input at all, or only well-formed data?
- Are unknown/missing IDs tested as well as existing ones?

🚩 **Red flag:** every test uses realistic, valid, happy-path data.

## 2 · Boundary Analysis
*Bugs cluster at the edges. Has the suite gone to the edges?*

- For every number: what happens at **zero**, at **negative**, at **one**, at the **maximum**, and at **maximum + 1**?
- Are there limits (list sizes, quantities, lengths) that are never pushed?
- Is anything tested *just past* where it should be rejected?

🚩 **Red flag:** quantities are always 1 or 2; no test ever expects a 4xx.

## 3 · State-Transition Oracle
*Objects move through states. Are the illegal moves blocked?*

- What states can this thing be in, and which transitions are **legal**?
- What happens if you repeat an action, or do it **out of order**?
- Can you still modify something after it's been finalised?

🚩 **Red flag:** every test runs one clean sequence, start to finish, once.

## 4 · Risk-Based Prioritisation
*Test hardest where failure hurts most. Is the effort in the right place?*

- Where would a bug cost real **money**, leak **data**, or break **trust**?
- Is access control tested — can one user reach another user's data?
- Count the tests: are they spread evenly, or weighted toward the risky areas?

🚩 **Red flag:** twelve tests on reading products, none on permissions.

## 5 · Metamorphic Relations
*Some relationships must hold between operations, even when you don't know the exact answer.*

- If I do X then undo X, does the system return to where it started?
- If I ask the **same question two different ways**, do I get the same answer?
- Does changing the order of operations change the result when it shouldn't?

🚩 **Red flag:** every test checks a single call in isolation.

## 6 · Consistency Oracles
*The system must agree with itself.*

- Does a **read after a write** reflect the change?
- Do the parts sum to the whole (do line items add up to the total)?
- Is the same value reported identically everywhere it appears?
- **Is the assertion actually capable of failing?**

🚩 **Red flag:** an assertion that restates the implementation instead of the
requirement — it will pass no matter how wrong the answer is.

## 7 · Adversarial Oracle *(2026 bonus — AI-specific)*
*Can untrusted content steer the system — or an AI acting on it?*

- Does any API response carry **free text the system will later trust** (names, descriptions, notes)?
- If an AI reads that content as context, could hidden instructions in it **hijack** the AI — an *indirect prompt injection*?
- Do the tests (or the agent) **blindly trust** returned content instead of scanning it?
- Would a hijacked agent's run still *pass*, hiding the attack? (It usually does — functional tests don't catch it.)

🚩 **Red flag:** the system echoes user-supplied text into places an AI reads, and nothing scans it. Try `belts/black/injection_round.md` to see it live. (OWASP LLM01.)

---

## Using the gate

For each heuristic, record: *what did the suite check, what did it miss, and
what's the risk of that gap?* A suite that passes 100% and clears zero
heuristics is worse than no suite at all — it manufactures false confidence.
