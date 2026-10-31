#!/usr/bin/env python3
"""DojoShop testing agent — generate -> execute -> analyse -> regenerate.

A minimal agentic testing loop for the Black Belt. It runs fully offline by
default using a deterministic MockGenerator, so you can watch the loop work with
no API keys. Point it at a module: it generates tests, runs them, reads the
failures as "bugs found", and regenerates more targeted tests each round.

    python belts/black/agent/dojo_agent.py --target discounts   # the Showdown (unseen module)
    python belts/black/agent/dojo_agent.py --target cart        # a known module
    python belts/black/agent/dojo_agent.py --target discounts --rounds 3

To use a real model instead of the mock, implement LLMGenerator.generate()
(see the TODO) and run with --generator llm.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))  # so 'app' and 'belts.common' import when run as a script

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMISE THE ON-SCREEN TEXT HERE — edit these strings freely to re-word the
# agent's output. The {things in braces} are filled in automatically, so keep
# those tokens (and their spelling) as they are; everything else is yours.
# ─────────────────────────────────────────────────────────────────────────────
MSG_HEADER   = "\nDojoShop testing agent  |  target: {target}  |  generator: {gen}"
MSG_RULE      = "-" * 60                        # the divider line
MSG_SAVED     = "   Saved generated tests to: {path}"
MSG_ROUND     = "\nRound {n}: {total} test(s) generated  |  {passed} passed, {failed} failed  |  {verdict}"
VERDICT_BUG   = "defect detected"
VERDICT_GREEN = "no defect found"
VERDICT_NONE  = "no tests collected (model output was not a runnable test module; re-run with --show to see why)"
MSG_REVEALED  = "      Revealed by: {name}"
MSG_FINISHED  = "Run complete after {rounds} round(s). Defects surfaced: {count}"
MSG_BUG_ITEM  = "   - {name}"
# Shown only on the discounts target when at least one defect was found:
MSG_SEEDED    = "\nNote: the negative-total defect is the seeded flaw in the unseen discounts module."
MSG_EXCELS    = "\nStrength: systematically probing boundaries the happy path skips."
MSG_NEEDS_YOU = "Limitation: it does not know which boundaries matter — that judgement is yours.\n"

# Every generated test file starts with this: a client plus two helpers.
HEADER = """from fastapi.testclient import TestClient
from app.main import app
from app import data
client = TestClient(app)

def _order():
    data.reset()
    c = client.post('/carts').json()['cart_id']
    client.post(f'/carts/{c}/items', json={'product_id': 2, 'quantity': 1})
    return client.post('/orders', json={'cart_id': c}).json()['order_id']

def _cart():
    data.reset()
    return client.post('/carts').json()['cart_id']
"""

# The MockGenerator's "thinking": progressively sharper tests per round.
PLAYBOOK = {
    "discounts": [
        HEADER + """
def test_discount_reduces_total():
    oid = _order()
    r = client.post(f'/orders/{oid}/discount', json={'code': 'SAVE10'})
    assert r.status_code == 200
    assert r.json()['total_cents'] > 0
""",
        HEADER + """
def test_discount_never_makes_total_negative():
    oid = _order()
    r = client.post(f'/orders/{oid}/discount', json={'code': 'PCT200'})
    assert r.status_code in (400, 422) or r.json()['total_cents'] >= 0
""",
        HEADER + """
def test_discount_percent_is_bounded_0_to_100():
    for code, should_ok in [('PCT0', True), ('PCT100', True), ('PCT101', False)]:
        oid = _order()
        r = client.post(f'/orders/{oid}/discount', json={'code': code})
        if should_ok:
            assert r.json()['total_cents'] >= 0
        else:
            assert r.status_code in (400, 422)
""",
    ],
    "cart": [
        HEADER + """
def test_add_item_ok():
    c = _cart()
    r = client.post(f'/carts/{c}/items', json={'product_id': 8, 'quantity': 2})
    assert r.status_code == 200
""",
        HEADER + """
def test_reject_zero_and_negative_quantity():
    c = _cart()
    r0 = client.post(f'/carts/{c}/items', json={'product_id': 8, 'quantity': 0})
    rn = client.post(f'/carts/{c}/items', json={'product_id': 8, 'quantity': -1})
    assert r0.status_code in (400, 422)
    assert rn.status_code in (400, 422)
""",
        HEADER + """
def test_cart_total_consistent_after_delete():
    c = _cart()
    add = client.post(f'/carts/{c}/items', json={'product_id': 2, 'quantity': 1}).json()
    item_id = add['items'][0]['item_id']
    client.delete(f'/carts/{c}/items/{item_id}')
    cart = client.get(f'/carts/{c}').json()
    assert cart['total_cents'] == sum(i['subtotal_cents'] for i in cart['items'])
""",
    ],
}


class MockGenerator:
    """Deterministic stand-in for an LLM: returns sharper tests as it gets feedback."""
    name = "mock"

    def generate(self, target: str, findings: list[str], round_idx: int) -> str:
        rounds = PLAYBOOK.get(target, PLAYBOOK["cart"])
        return rounds[min(round_idx, len(rounds) - 1)]


class LLMGenerator:
    """Real-model generator via the shared Dojo LLM gateway (OpenAI-compatible).

    Needs DOJO_API_BASE_URL and DOJO_API_KEY (Codespaces secrets pointing at the
    LiteLLM gateway). Falls back with a clear message if unset, so the mock path
    always works for offline practice. See facilitator/api_gateway.md."""
    name = "llm"

    # When staged=True, the per-round objective escalates so a strong model shows
    # the dumb->sharper progression (set by main() from --staged).
    staged = False

    # Round-by-round objectives for staged mode, PER TARGET. Round 1 is deliberately
    # shallow; each later round unlocks more. Rounds beyond the list reuse the last.
    STAGE_OBJECTIVES = {
        "discounts": [
            "THIS ROUND: write ONLY happy-path tests — valid discount codes (e.g. SAVE10, "
            "HALF, PCT30) on a normal order, asserting status 200 and the discounted total. "
            "Do NOT test invalid input, boundaries, error paths, or percentages over 100.",
            "THIS ROUND: add BOUNDARY and INVALID-INPUT tests — zero, negative percentages, "
            "values just over 100 (PCT101, PCT150), unknown codes and unknown orders. Assert "
            "the API should reject bad input and must never produce a negative total.",
            "THIS ROUND: go ADVERSARIAL — very large percentages, malformed codes, and "
            "INVARIANT checks (the order total must never go below zero; a rejected code must "
            "not mutate the order).",
        ],
        "cart": [
            "THIS ROUND: write ONLY happy-path tests — create a cart, add a valid item with a "
            "normal quantity (e.g. 1 or 2), and assert the cart contents and total. Do NOT "
            "test invalid quantities, stock limits, deletion, or error paths.",
            "THIS ROUND: add BOUNDARY and INVALID-INPUT tests — quantity of zero, negative "
            "quantity, adding to a non-existent cart or product, and quantities that exceed "
            "available stock. Assert the API should reject bad input.",
            "THIS ROUND: go ADVERSARIAL and check INVARIANTS — the cart total must always "
            "equal the sum of its line items (especially AFTER deleting an item), quantities "
            "must be >= 1, and stock limits must hold.",
        ],
        "default": [
            "THIS ROUND: write ONLY simple happy-path tests on valid inputs. Do NOT test "
            "invalid input, boundaries, or error paths.",
            "THIS ROUND: add BOUNDARY and INVALID-INPUT tests — zero, negatives, values past "
            "the limits, and unknown ids. Assert the API should reject bad input.",
            "THIS ROUND: go ADVERSARIAL and check INVARIANTS that must always hold.",
        ],
    }

    # Exact fixture setup per target — so even a small/cheap model builds valid
    # state instead of guessing endpoints or hard-coding tax-inclusive totals.
    SETUP_RECIPE = {
        "discounts": (
            "FIXTURE — to get an order to discount, use EXACTLY this at the start of each test "
            "(do not invent other ways to make an order):\n"
            "    data.reset()\n"
            "    cart_id = client.post('/carts').json()['cart_id']\n"
            "    client.post(f'/carts/{cart_id}/items', json={'product_id': 2, 'quantity': 1})\n"
            "    order_id = client.post('/orders', json={'cart_id': cart_id}).json()['order_id']\n"
            "Then POST /orders/{order_id}/discount with {'code': ...}.\n"
            "MONEY: integer cents, INCLUDING 20% tax. Do NOT hard-code exact totals. Assert "
            "INVARIANTS instead: total_cents >= 0; a valid code lowers the total vs no discount; "
            "an invalid/unknown code returns 400; an unknown order_id returns 404."
        ),
        "cart": (
            "FIXTURE — to get a cart, use EXACTLY:\n"
            "    data.reset()\n"
            "    cart_id = client.post('/carts').json()['cart_id']\n"
            "Add items with POST /carts/{cart_id}/items json={'product_id': 8, 'quantity': N}.\n"
            "MONEY: integer cents incl. 20% tax. Do NOT hard-code totals. Assert INVARIANTS: "
            "the cart total_cents equals the sum of line subtotal_cents; quantity 0 or negative "
            "is rejected (400/422)."
        ),
    }

    def generate(self, target: str, findings: list[str], round_idx: int) -> str:
        from belts.common.llm_client import complete, gateway_configured
        if not gateway_configured():
            raise RuntimeError(
                "LLM gateway not configured. Run with --generator mock, or set "
                "DOJO_API_BASE_URL and DOJO_API_KEY (see facilitator/api_gateway.md)."
            )
        # Give the model the module actually under test, so it writes direct tests
        # instead of trying to introspect the schema. 'cart' etc. live in main.py
        # (pass it whole — it's small); 'discounts' etc. live in app/unseen/.
        app_src = (REPO_ROOT / "app" / "main.py").read_text(encoding="utf-8")[:6000]
        mod_path = REPO_ROOT / "app" / "unseen" / f"{target}.py"
        target_src = mod_path.read_text(encoding="utf-8")[:3500] if mod_path.exists() else ""
        feedback = ("\nAlso build on these prior failing tests: " + ", ".join(findings)) if findings else ""

        if self.staged:
            objectives = self.STAGE_OBJECTIVES.get(target, self.STAGE_OBJECTIVES["default"])
            objective = objectives[min(round_idx, len(objectives) - 1)]
        else:
            objective = ("Probe boundaries, invalid input and error paths — zero, negatives, "
                         "values just past the limits, and unknown ids/codes.")
        setup = self.SETUP_RECIPE.get(target, "")

        prompt = (
            f"Write ONE pytest module that tests the '{target}' area of this FastAPI app.\n"
            "RULES (follow exactly):\n"
            "- Output ONLY Python code. No explanation, no markdown fences.\n"
            "- Start with: from fastapi.testclient import TestClient; from app.main import app; "
            "from app import data; client = TestClient(app).\n"
            "- At the START of every test call data.reset() to get a clean state.\n"
            "- Write SIMPLE, DIRECT tests that call concrete endpoints with concrete values.\n"
            "- Do NOT introspect the OpenAPI schema. Do NOT write dynamic/meta/helper-heavy code.\n"
            "- Name every test function test_*. Keep the whole module short.\n"
            f"- {objective}\n"
            + (f"\n{setup}\n" if setup else "")
            + f"{feedback}\n\n"
            f"app/main.py (excerpt):\n{app_src}\n\n"
            + (f"app/unseen/{target}.py (the module UNDER TEST — target your tests here):\n{target_src}\n"
               if target_src else "")
        )
        code = complete(prompt, model="opus", max_tokens=4000,
                        system="You are an expert SDET. Output only a runnable pytest module, no prose.")
        return _extract_code(code)


def _extract_code(text: str) -> str:
    """Pull runnable Python out of a model reply (strip fences / leading prose)."""
    if not text:
        return ""
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    # No fence: drop any prose before the first import/def line.
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith(("import ", "from ", "def ", "class ")):
            return "\n".join(lines[i:]).strip()
    return text.strip()


def run_tests(code: str) -> dict:
    """Execute a generated test module against DojoShop and read the results."""
    fd, path = tempfile.mkstemp(prefix="dojo_agent_", suffix=".py")
    with os.fdopen(fd, "w") as f:
        f.write(code)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", path, "-q", "-rf", "--tb=no", "-p", "no:cacheprovider"],
            cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    out = result.stdout
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", out)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", out)) else 0
    errors = int(m.group(1)) if (m := re.search(r"(\d+) error", out)) else 0
    failing = re.findall(r"FAILED \S+::(\S+)", out)
    raw = out + (("\n--- stderr ---\n" + result.stderr) if result.stderr.strip() else "")
    return {"passed": passed, "failed": failed, "errors": errors,
            "failing": failing, "raw": raw}


def main() -> None:
    ap = argparse.ArgumentParser(description="DojoShop testing agent (generate→execute→analyse→regenerate).")
    ap.add_argument("--target", default="discounts", help="module to attack: 'discounts' (unseen) or 'cart'")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--generator", choices=["mock", "llm"], default="mock")
    ap.add_argument("--show", action="store_true",
                    help="print the generated test code and the pytest output each round")
    ap.add_argument("--save-dir", default=None,
                    help="write each round's generated tests to this folder to inspect/run later")
    ap.add_argument("--staged", action="store_true",
                    help="(llm only) escalate the prompt per round so a strong model shows the "
                         "dumb round 1 -> sharper round 2/3 progression")
    args = ap.parse_args()

    gen = MockGenerator() if args.generator == "mock" else LLMGenerator()
    if args.generator == "llm":
        gen.staged = args.staged
    print(MSG_HEADER.format(target=args.target, gen=gen.name))
    print(MSG_RULE)

    bugs: list[str] = []
    findings: list[str] = []
    for r in range(args.rounds):
        code = gen.generate(args.target, findings, r)          # 1. generate

        if args.save_dir:                                      # persist for inspection
            d = Path(args.save_dir); d.mkdir(parents=True, exist_ok=True)
            fpath = d / f"{args.target}_round{r + 1}.py"
            fpath.write_text(code, encoding="utf-8")
            print(MSG_SAVED.format(path=fpath))
        if args.show:
            print(f"\n----- generated tests (round {r + 1}) -----")
            print(code.strip() or "(model returned EMPTY output)")
            print("----- end generated tests -----")

        res = run_tests(code)                                  # 2. execute
        newly = [f for f in res["failing"] if f not in bugs]   # 3. analyse
        bugs.extend(newly)
        total = res["passed"] + res["failed"]
        if total == 0:
            verdict = VERDICT_NONE
        else:
            verdict = VERDICT_BUG if res["failed"] else VERDICT_GREEN
        print(MSG_ROUND.format(n=r + 1, total=total,
                               passed=res["passed"], failed=res["failed"], verdict=verdict))
        for f in newly:
            print(MSG_REVEALED.format(name=f))
        if args.show:
            print("\n----- pytest output -----")
            print(res["raw"].strip())
            print("----- end pytest output -----")
        findings = res["failing"]                              # 4. regenerate with feedback

    print("\n" + MSG_RULE)
    print(MSG_FINISHED.format(rounds=args.rounds, count=len(bugs)))
    for b in bugs:
        print(MSG_BUG_ITEM.format(name=b))
    if args.target == "discounts" and bugs:
        print(MSG_SEEDED)
    print(MSG_EXCELS)
    print(MSG_NEEDS_YOU)


if __name__ == "__main__":
    main()
