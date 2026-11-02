#!/usr/bin/env python3
"""Generate an AI test suite for DojoShop via the shared gateway (White Belt).

For the live room: attendees generate with one command and score with the next —
no personal ChatGPT/Claude account needed. Presets build each round's prompt.

  python belts/white/generate.py --preset naive   --model opus --out round1.py
  python belts/white/generate.py --preset spec     --model gpt  --out round2.py
  python belts/white/generate.py --preset context  --model opus --out round3.py
  python belts/white/generate.py --prompt-file my_prompt.txt    --out custom.py

Then:  python belts/white/score_prompt.py round3.py

(Solo practice with no gateway: paste a prompt into your own Claude/ChatGPT and
save the result instead — this script needs DOJO_API_BASE_URL / DOJO_API_KEY.)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from belts.common.llm_client import complete, gateway_configured  # noqa: E402

BASE_URL = "http://127.0.0.1:8000"


def openapi_spec() -> str:
    from app.main import app
    return json.dumps(app.openapi())


def context_doc() -> str:
    return (Path(__file__).parent / "context_doc.md").read_text(encoding="utf-8")


def build_prompt(preset: str) -> str:
    base = (f"Write a SINGLE pytest module (code only, no markdown fences) of API tests "
            f"for the e-commerce API at {BASE_URL}, using httpx against that base URL.")
    if preset == "naive":
        return "Write API tests for this e-commerce API."
    if preset == "spec":
        return (base + "\nUse ONLY the endpoints and fields in this OpenAPI spec; invent nothing.\n\n"
                + openapi_spec())
    if preset == "context":
        return (base + "\nBelow are the endpoints and the business rules & invariants. Write tests "
                "that FAIL if any invariant is violated; prioritise boundaries, error paths and "
                "access control.\n\nOPENAPI:\n" + openapi_spec() + "\n\nRULES:\n" + context_doc())
    raise SystemExit(f"unknown preset: {preset}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate an AI test suite via the gateway.")
    ap.add_argument("--preset", choices=["naive", "spec", "context"])
    ap.add_argument("--prompt-file")
    ap.add_argument("--model", default="opus", choices=["opus", "gpt", "gemini"])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not gateway_configured():
        raise SystemExit(
            "LLM gateway not set. In the room, add DOJO_API_BASE_URL and DOJO_API_KEY "
            "(a .env file works — see the slide). For solo practice, paste a prompt into "
            "your own Claude/ChatGPT and save the result instead."
        )

    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    elif args.preset:
        prompt = build_prompt(args.preset)
    else:
        raise SystemExit("give --preset or --prompt-file")

    code = complete(prompt, model=args.model,
                    system="You are an expert SDET. Output only a runnable pytest module.")
    m = re.search(r"```(?:python)?\n(.*?)```", code, re.S)
    code = m.group(1) if m else code
    Path(args.out).write_text(code, encoding="utf-8")
    print(f"wrote {args.out} ({len(code.splitlines())} lines)")
    print(f"score it:  python belts/white/score_prompt.py {args.out}")


if __name__ == "__main__":
    main()
