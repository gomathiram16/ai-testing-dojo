#!/usr/bin/env python3
"""One-command readiness check for the AI Testing Dojo.

Runs the whole tutorial end to end and prints a green/red report, so you (and
each attendee) can confirm the environment in one go:

    python verify_ready.py        # or:  make ready
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=str(ROOT),
                          capture_output=True, text=True)


# 1. dependencies
try:
    import fastapi, httpx, pytest, pydantic  # noqa: F401
    check("Dependencies import", True)
except Exception as e:  # noqa: BLE001
    check("Dependencies import", False, f"run: pip install -r requirements.txt ({e})")

# 2. app boots
try:
    from fastapi.testclient import TestClient
    from app.main import app
    r = TestClient(app).get("/products")
    check("App boots + GET /products", r.status_code == 200, f"{len(r.json())} products")
except Exception as e:  # noqa: BLE001
    check("App boots", False, str(e))

# 3. White Belt scorer
r = run("belts/white/score_prompt.py", "belts/white/examples/sample_context_output.py")
line = next((l.strip() for l in r.stdout.splitlines() if "Composite" in l), r.stderr[:80])
check("White Belt scorer runs", "Composite" in r.stdout, line)

# 4. Blue Belt AI suite
r = run("-m", "pytest", "belts/blue/ai_generated_suite/", "-q", "-p", "no:cacheprovider")
line = next((l for l in r.stdout.splitlines() if "passed" in l), "")
check("Blue Belt AI suite (13 pass)", "13 passed" in r.stdout, line)

# 5. Black Belt agent
r = run("belts/black/agent/dojo_agent.py", "--target", "discounts")
check("Black Belt agent finds bug", "defect detected" in r.stdout)

# 6. Prompt-injection oracle
r = run("belts/black/injection_demo.py")
check("Prompt-injection oracle fires", "prompt injection found" in r.stdout.lower())

# 7. Seeded-bug answer key (facilitator-only; solutions/ is excluded from the
#    shared/attendee repo, so skip gracefully when it isn't present)
if (ROOT / "solutions" / "test_seeded_bugs.py").exists():
    r = run("-m", "pytest", "solutions/test_seeded_bugs.py", "-q", "-p", "no:cacheprovider")
    check("Seeded-bug answer key (12 pass)", "12 passed" in r.stdout)
else:
    print("  (skipping seeded-bug answer key — solutions/ not present; normal in the attendee repo)")

# gateway status (informational, not a fail)
try:
    from belts.common.llm_client import gateway_configured
    gateway = gateway_configured()
except Exception:  # noqa: BLE001
    gateway = False

print("\nAI Testing Dojo — readiness check")
print("=" * 44)
all_ok = True
for name, ok, detail in results:
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {name}" + (f"  — {detail}" if detail else ""))
    all_ok = all_ok and ok
print(f"  [INFO] LLM gateway: {'configured' if gateway else 'not set (offline/mock mode — fine for practice)'}")
print("=" * 44)
print("READY ✅  all core checks passed." if all_ok else "NOT READY ❌  fix the FAIL lines above.")
sys.exit(0 if all_ok else 1)
