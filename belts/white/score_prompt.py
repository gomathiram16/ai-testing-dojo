#!/usr/bin/env python3
"""score_prompt.py — score an AI-generated API test suite (White Belt).

Given a Python test file produced by an LLM from one of your prompts, this
scores it against the *real* DojoShop API on five rubric dimensions and prints
a 0-25 composite. It is deterministic, so you can compare prompting strategies
fairly on a leaderboard.

What it measures
  * Hallucination  — API paths the test calls that the API does not have.
  * Coverage       — real (method, route) pairs the test exercises.
  * Assertions     — assertion density (a proxy for assertion quality).
  * Executability  — does the file parse (and, with --run, pass under pytest)?
  * Risk targeting — does it hit high-risk areas (orders, access control) and
                     probe boundaries (0, negatives, large values)?

Usage
  python belts/white/score_prompt.py <test_file.py>
  python belts/white/score_prompt.py <test_file.py> --run          # also run pytest
  python belts/white/score_prompt.py <test_file.py> --json         # machine output
  python belts/white/score_prompt.py <test_file.py> --include-unseen
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from app.main import app  # noqa: E402

HTTP_METHODS = {"get", "post", "put", "delete", "patch", "options", "head"}
UNSEEN_ROUTE = "/orders/{order_id}/discount"
HIGH_RISK = {("post", "/orders"), ("get", "/orders/{order_id}")}


# --------------------------------------------------------------------------- #
# Real routes from the app
# --------------------------------------------------------------------------- #
def real_routes(include_unseen: bool = False) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for route in app.routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if not methods or not path:
            continue
        if path.startswith("/openapi") or path.startswith("/docs") or path.startswith("/redoc"):
            continue
        if path == "/" or path.startswith("/static"):  # storefront UI, not an API route
            continue
        if not include_unseen and path == UNSEEN_ROUTE:
            continue
        for method in methods:
            m = method.lower()
            if m in HTTP_METHODS:
                pairs.add((m, path))
    return pairs


# --------------------------------------------------------------------------- #
# Path helpers
# --------------------------------------------------------------------------- #
def _segments(path: str) -> list[str]:
    path = path.split("?")[0]
    return [s for s in path.strip("/").split("/") if s != ""]


def _is_wild(seg: str) -> bool:
    return seg == "{}" or (seg.startswith("{") and seg.endswith("}"))


def compatible(ref_path: str, tmpl_path: str) -> bool:
    a, b = _segments(ref_path), _segments(tmpl_path)
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if _is_wild(x) or _is_wild(y):
            continue
        if x != y:
            return False
    return True


def _literalize(node: ast.AST) -> str | None:
    """Reconstruct a URL string from an AST node, using {} for dynamic bits."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):  # f-string
        out = ""
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                out += value.value
            else:
                out += "{}"
        return out
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _literalize(node.left)
        right = _literalize(node.right)
        return (left if left is not None else "{}") + (right if right is not None else "{}")
    return None


def _to_api_path(raw: str | None) -> str | None:
    if raw is None:
        return None
    # strip scheme + host
    import re

    raw = re.sub(r"^https?://[^/]+", "", raw)
    raw = raw.split("?")[0]
    if not raw.startswith("/"):
        idx = raw.find("/")
        if idx == -1:
            return None
        raw = raw[idx:]
    return raw


# --------------------------------------------------------------------------- #
# Static analysis of the generated test file
# --------------------------------------------------------------------------- #
class Analysis:
    def __init__(self) -> None:
        self.parsed = True
        self.syntax_error = ""
        self.calls: set[tuple[str, str]] = set()   # (method, path)
        self.test_funcs = 0
        self.asserts = 0
        self.has_boundary = False


def analyse(source: str) -> Analysis:
    a = Analysis()
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:  # unparseable = biggest possible red flag
        a.parsed = False
        a.syntax_error = f"{exc.msg} (line {exc.lineno})"
        return a

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
            a.test_funcs += 1
        if isinstance(node, ast.Assert):
            a.asserts += 1
        if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
            if node.value == 0 or node.value > 1000:
                a.has_boundary = True
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            a.has_boundary = True  # a negative literal
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            method = node.func.attr.lower()
            if method in HTTP_METHODS and node.args:
                path = _to_api_path(_literalize(node.args[0]))
                if path:
                    a.calls.add((method, path))
    return a


# --------------------------------------------------------------------------- #
# Optional: run under pytest against a live server
# --------------------------------------------------------------------------- #
def run_pytest(test_file: Path, base_url: str) -> dict:
    import socket

    def _free_port() -> int:
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    port = _free_port()
    env = dict(os.environ, BASE_URL=f"http://127.0.0.1:{port}")
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(port)],
        cwd=str(REPO_ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        # wait for the server to accept connections
        for _ in range(50):
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-q"],
            cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
        )
        return {"returncode": result.returncode, "output": result.stdout.strip().splitlines()[-1:] if result.stdout else []}
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #
def score(a: Analysis, routes: set[tuple[str, str]], ran: dict | None) -> dict:
    referenced = a.calls
    total_ref = len(referenced)
    hallucinated = {
        (m, p) for (m, p) in referenced
        if not any(rm == m and compatible(p, rp) for (rm, rp) in routes)
    }
    halluc_rate = (len(hallucinated) / total_ref) if total_ref else 1.0

    covered = {
        (rm, rp) for (rm, rp) in routes
        if any(m == rm and compatible(p, rp) for (m, p) in referenced)
    }
    coverage = (len(covered) / len(routes)) if routes else 0.0

    density = a.asserts / a.test_funcs if a.test_funcs else 0.0

    risk_hits = len([r for r in HIGH_RISK if r in covered])
    risk_score = min(5.0, (risk_hits / len(HIGH_RISK)) * 3 + (2 if a.has_boundary else 0))

    if not a.parsed:
        exec_score = 0.0
    elif ran is not None:
        exec_score = 5.0 if ran["returncode"] in (0, 1) else 1.0  # 1 = tests ran but some failed (expected vs buggy app)
    else:
        exec_score = 5.0 if (a.test_funcs and total_ref) else 2.0

    dims = {
        "hallucination": round((1 - halluc_rate) * 5, 1),
        "coverage": round(coverage * 5, 1),
        "assertions": round(min(5.0, density * 2.5), 1),
        "executability": round(exec_score, 1),
        "risk_targeting": round(risk_score, 1),
    }
    composite = round(sum(dims.values()), 1)
    return {
        "composite": composite,
        "max": 25,
        "dimensions": dims,
        "hallucination_rate_pct": round(halluc_rate * 100, 1),
        "coverage_pct": round(coverage * 100, 1),
        "test_functions": a.test_funcs,
        "assertions": a.asserts,
        "endpoints_referenced": sorted(f"{m.upper()} {p}" for m, p in referenced),
        "hallucinated_endpoints": sorted(f"{m.upper()} {p}" for m, p in hallucinated),
        "uncovered_routes": sorted(f"{m.upper()} {p}" for m, p in (routes - covered)),
        "syntax_error": a.syntax_error,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Score an AI-generated API test suite.")
    ap.add_argument("test_file", type=Path)
    ap.add_argument("--run", action="store_true", help="also run the tests under pytest")
    ap.add_argument("--include-unseen", action="store_true", help="score against the unseen discount route too")
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = ap.parse_args()

    source = args.test_file.read_text(encoding="utf-8")
    a = analyse(source)
    routes = real_routes(include_unseen=args.include_unseen)
    ran = run_pytest(args.test_file, args.base_url) if (args.run and a.parsed) else None
    result = score(a, routes, ran)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    d = result["dimensions"]
    print(f"\n  DojoShop White Belt — prompt score: {args.test_file.name}")
    print("  " + "-" * 52)
    print(f"  Composite            {result['composite']:>5} / 25")
    print(f"    Hallucination      {d['hallucination']:>5} / 5   ({result['hallucination_rate_pct']}% of calls hallucinated)")
    print(f"    Coverage           {d['coverage']:>5} / 5   ({result['coverage_pct']}% of routes hit)")
    print(f"    Assertions         {d['assertions']:>5} / 5   ({result['assertions']} asserts / {result['test_functions']} tests)")
    print(f"    Executability      {d['executability']:>5} / 5")
    print(f"    Risk targeting     {d['risk_targeting']:>5} / 5")
    if result["hallucinated_endpoints"]:
        print("  Hallucinated calls:  " + ", ".join(result["hallucinated_endpoints"]))
    if result["uncovered_routes"]:
        print("  Not covered:         " + ", ".join(result["uncovered_routes"]))
    if result["syntax_error"]:
        print("  SYNTAX ERROR:        " + result["syntax_error"])
    print()


if __name__ == "__main__":
    main()
