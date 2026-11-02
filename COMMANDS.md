# AI Testing Dojo — Attendee Guide

Everything you need for the day, in order: setup first, then the three belts.

The commands run in the **Terminal inside your Codespace** (the panel at the
bottom of the screen). The Codespace is a Linux computer in your browser, so these
commands are the same whatever laptop you brought: Windows, Mac or Linux.

> **Tip — no copy-paste?** Highlight a command in this file, press
> **Ctrl+Shift+P** (Mac: **Cmd+Shift+P**) and choose
> **Terminal: Run Selected Text In Active Terminal**.

---

## 0. Create your Codespace

1. Sign in to **github.com** with a **personal** account.
2. Open `https://codespaces.new/gomathiram16/ai-testing-dojo`
3. Under **Recommended secrets**, type the three values from the **Miro board**:
   `OPENROUTER_BASE_URL`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`.
4. Click **Create codespace** and wait for the Terminal to appear.

## 1. Check you're set up (once, at the start)

**Check everything is installed**
```
make check
```
You should see `deps ok` and `app import ok`.

**Check your AI key**
```
python -c "from belts.common.llm_client import gateway_configured as g; print('AI key OK' if g() else 'NO KEY')"
```
- **AI key OK** → go to step 2.
- **NO KEY** (usually means the boxes in step 0 were left empty — no need to
  start again) → create a file called `.env` in the top `ai-testing-dojo` folder
  (right-click the folder → **New File** → name it exactly `.env`), paste the
  three lines from the Miro board, save, and run the check again:
  ```
  OPENROUTER_BASE_URL=<from the Miro board>
  OPENROUTER_API_KEY=<from the Miro board>
  OPENROUTER_MODEL=<from the Miro board>
  ```
  Still no key? Carry on. Every belt has an offline option.

  The key is for **today only** and has a spending limit. `.env` is git-ignored,
  so it's never committed. Don't paste the key into chat or screenshots.

## 2. Start the shop

```
make app
```
Leave this terminal running. Click **Open in Browser** on the port 8000 pop-up
to see DojoShop (add `/docs` to the address for the clickable API).
Press **Ctrl+C** to stop it.

Open a **second terminal** (the **+** in the terminal panel) for everything below.

---

## 3. ⚪ White Belt — Context Engineering

Same AI, three prompts. Generate a test suite each way, then score it:

```
python belts/white/generate.py --preset naive   --out round1.py
python belts/white/score_prompt.py round1.py
```
```
python belts/white/generate.py --preset spec    --out round2.py
python belts/white/score_prompt.py round2.py
```
```
python belts/white/generate.py --preset context --out round3.py
python belts/white/score_prompt.py round3.py
```

Add `--run` to a score command to also run the tests:
`python belts/white/score_prompt.py round3.py --run`

**Offline (no AI key):** score the ready-made examples
```
python belts/white/score_prompt.py belts/white/examples/sample_naive_output.py
python belts/white/score_prompt.py belts/white/examples/sample_context_output.py
```

Write your best score on the **leaderboard**.

> **Prefer another AI (Claude, Gemini, ChatGPT)?** Keep `make app` running.
> 1. Open your AI chat and use a prompt from `belts/white/prompt_library.md`
>    (Round 1: P01/P02 · Round 2: P05–P07 · Round 3: P08–P10).
>    For the API spec, run this and copy the contents of `openapi.json`:
>    `curl -s http://127.0.0.1:8000/openapi.json > openapi.json`
> 2. Save **only the code** from the reply as `belts/white/Claude_round1.py`
>    (or `Gemini_round1.py`, `GPT_round1.py`).
> 3. Score it: `python belts/white/score_prompt.py belts/white/Claude_round1.py`
>    (add `--run` to also run the tests).
>
> Compare the same prompt across different AIs, and log your best on the leaderboard.

---

## 4. 🔵 Blue Belt — Audit the AI

Run the AI-written test suite:
```
python -m pytest belts/blue/ai_generated_suite/ -v
```
All 13 pass. Now audit them with the **Heuristics Checklist** and log gaps on
your copy of the **Audit Worksheet** (links on the Miro board, also in
`belts/blue/`). 1 point per real gap → leaderboard.

**Reading the output:** `PASSED [ 7%] … [100%]` is a progress bar (how many
tests have run), **not** a score. 100% means "all finished", not "all correct".
A yellow *warning* is a library version note, not a failed test.

---

## 5. ⚫ Black Belt — Build & Break an Agent

**Watch the agent loop** (generate → run → analyse → regenerate), offline:
```
python belts/black/agent/dojo_agent.py --target cart
```

**Run it with the real AI** — round 1 starts simple, later rounds get sharper:
```
python belts/black/agent/dojo_agent.py --target cart --generator llm --staged --show
```

**Showdown — the hidden discounts module:**
```
python belts/black/agent/dojo_agent.py --target discounts
```
```
python belts/black/agent/dojo_agent.py --target discounts --generator llm --staged --show
```

**Break the agent — prompt injection:**
```
python belts/black/injection_demo.py
```
```
python belts/black/injection_live.py --naive --run
```

Options: `--show` prints the generated tests and results;
`--save-dir belts/black/generated` saves each round to a file.

---

## Something not working?

| You see | Do this |
|---|---|
| `NO KEY` / "LLM gateway not configured" | Create the `.env` file (step 1), or use the offline commands |
| `make: command not found` | Use `python verify_ready.py` and `uvicorn app.main:app` instead |
| `no tests collected` | Check you typed the path exactly; run from the `ai-testing-dojo` folder |
| Port 8000 page won't open | Open the **Ports** tab next to Terminal and click the globe icon on 8000 |
| Codespace won't start | Pair with a neighbour |

---

## Appendix — running on your own laptop instead (optional)

Only needed if you **can't use Codespaces**. You need Python 3.12+ installed.
This is the only place Mac and Windows differ: creating and entering the
project's private package box (`.venv`). After that, every command above is the
same.

**Mac / Linux**
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**
```
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If PowerShell blocks the activate step, run
`Set-ExecutionPolicy -Scope Process RemoteSigned` once, then activate again.
If `make` isn't available on Windows, use `uvicorn app.main:app` to start the
shop and `python verify_ready.py` to check setup.
