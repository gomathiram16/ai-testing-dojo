# Command Cheat-Sheet (plain English)

Everything you'll type happens in the **Terminal** — the text window where you
type instructions to the computer. Here's what each command means, so you can
explain it to attendees with confidence.

## The mental model (say this out loud to the room)

- **Terminal** — runs commands you type.
- **Python** — the language DojoShop is written in.
- **Virtual environment (`.venv`)** — a private box holding *this* project's
  packages, so they don't clash with anything else on the machine.
- **uvicorn** — the small web server that runs the app.
- **pytest** — the tool that runs the tests.

---

## 1. One-time setup (on a local computer only)

**macOS / Linux:**
```
cd "…/ai-testing-dojo"          # "change directory" — move into the project folder
python3 -m venv .venv           # create the private package box, named .venv
source .venv/bin/activate       # step into it — your prompt now shows (.venv)
pip install -r requirements.txt # install the packages the project needs
```

**Windows (PowerShell):**
```
cd "…\ai-testing-dojo"          # note the back-slashes in Windows paths
py -m venv .venv                # 'py' is the Windows Python launcher
.venv\Scripts\Activate.ps1      # step into it — your prompt now shows (.venv)
pip install -r requirements.txt
```
> On Windows, `python` usually works too; `py` is the safest launcher. If
> PowerShell blocks the activate script with an execution-policy error, run it
> once as `Set-ExecutionPolicy -Scope Process RemoteSigned` then activate again,
> **or** use `cmd` instead: `.venv\Scripts\activate.bat`.

> **In the workshop (GitHub Codespaces) none of this matters** — the Codespace is
> a **Linux machine in the browser**, identical for every attendee whatever their
> laptop is. Setup is already done; they skip straight to running things, and
> every command in sections 2–4 below is the same for everyone. See section 6 for
> the few host-side differences.

## 2. Run the shop

```
uvicorn app.main:app
```

Read it as: **uvicorn** (the server), run the app object named **`app`** that
lives inside **`app/main.py`**. That's exactly what `app.main:app` means —
`folder.file : the variable`.

- Open **http://127.0.0.1:8000** → the shop. `127.0.0.1` = *this computer*; `:8000` = the "door" (port) it listens on.
- Open **http://127.0.0.1:8000/docs** → the same API as clickable buttons.
- Press **`Ctrl + C`** to stop it.
- Optional: add `--reload --reload-dir app` to auto-restart when you edit code in
  the `app` folder. (We limit it to `app` so it doesn't watch `.venv` and loop.)

## 3. Run the tests

```
pytest                                  # run every test
python -m pytest                        # exactly the same, spelled out
pytest belts/blue/ai_generated_suite/ -v   # just these tests, verbose
```

`-v` = verbose (list each test). `-q` = quiet (just the summary).

## 4. Score a prompt (White Belt)

```
python belts/white/score_prompt.py my_output.py          # score a generated test file
python belts/white/score_prompt.py my_output.py --run    # also run it under pytest
```

`python <script.py>` simply means "run this Python file."

---

## What attendees actually type

In the workshop, setup is pre-done, so attendees really only use **three**
commands: start the app (`uvicorn app.main:app`), run tests (`pytest …`), and
score prompts (`python …/score_prompt.py …`). Keep your explanation to those
three and you'll never lose the room.

---

## 5. Reading the pytest output (explain this to the room)

When you run `pytest -v`, the terminal prints a block like this. Here's what
every part means, so you can narrate it with confidence.

### The header — "what am I running, and with what?"

```
platform darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0 -- /…/.venv/bin/python
cachedir: .pytest_cache
rootdir: /…/ai-testing-dojo
plugins: anyio-4.14.2
collected 13 items
```

- **`platform darwin`** — "darwin" is just the internal name for **macOS**. (On Windows you'd see `win32`; on Linux, `linux`.) Nothing to do with evolution.
- **`Python 3.13.5, pytest-9.1.1, pluggy-1.6.0`** — the versions in play. **pluggy** is the small plug-in engine pytest uses internally; you'll never touch it directly.
- **`-- /…/.venv/bin/python`** — the **exact Python being used**: the one inside the project's `.venv` (our private package box). Proof the tests are running in the right environment. First line to check if anything looks odd.
- **`cachedir: .pytest_cache`** — a hidden folder where pytest remembers things between runs (e.g. which tests failed last time). Harmless.
- **`rootdir`** — the **project root** pytest is working from; it anchors all the test paths below.
- **`plugins: anyio-4.14.2`** — pytest add-ons currently installed. `anyio` arrived with FastAPI and registers itself automatically; we don't use it directly.
- **`collected 13 items`** — pytest **scanned and counted the tests before running them**. Good sanity check: expected 13, got 13.

### The results — and that percentage

```
…test_list_products_returns_200 PASSED [  7%]
…test_get_order_by_id            PASSED [100%]
```

- **`PASSED`** — the test ran and all its assertions held. (Other outcomes: `FAILED`, `ERROR`, `SKIPPED`, `XFAIL`.)
- **The `[ 7% ] … [100%]`** — this is a **progress bar**: how far through the run pytest is, **not a score or a confidence level**. 1 of 13 done ≈ 7%, 13 of 13 = 100%.

> **Say this to the room:** `100%` means *100% of the tests have finished running* — **not** 100% correct. All 13 passed, the bar hit 100%, and the suite still catches **zero** of the real bugs. Passing ≠ correct.

### The warnings summary — "it worked, but take note"

```
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is
deprecated; install `httpx2` instead.
```

- A **warning is not a failure** — every test still passed. It's a heads-up from a library: the current way FastAPI's test client wires `starlette` + `httpx` together is **deprecated** ("still works, but will be removed one day — switch eventually").
- It's about **library versions, not your tests or the app.** Safe to ignore for the workshop; a one-line dependency bump fixes it later.
- The `.venv/lib/.../testclient.py:1` just names the file that raised it.
- The closing **`-- Docs: https://docs.pytest.org/...capture-warnings.html`** is pytest's standard footer on managing warnings — not specific to your run.

### One-line summary (say it out loud)

> *"Mac, the project's own Python, 13 tests found, all 13 passed — the percentages are just the progress bar reaching 100%, and the warning is a library version note, not a test problem."*

---

## 6. Windows & other machines (cross-platform notes)

**Read this first — the reassurance:** the tutorial runs in **GitHub Codespaces**,
which is a **Linux computer running in the browser**. So the attendee's laptop
being Windows, Mac, or Linux **makes no difference to anything they type** —
their terminal inside the Codespace is Linux for everyone. `uvicorn app.main:app`,
`python -m pytest …`, `python belts/white/score_prompt.py …` are **identical** on
every machine. You do **not** need a separate Windows script set for the workshop.

The OS only matters in two situations: (a) someone runs the project **locally**
instead of in the Codespace, and (b) a few **host-side conveniences** (clipboard,
shortcuts). Here are those differences.

### Command equivalents

| Task | macOS / Linux | Windows (PowerShell) | In Codespaces |
|------|---------------|----------------------|----------------|
| Create venv | `python3 -m venv .venv` | `py -m venv .venv` | already done |
| Activate venv | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` | already active |
| Run Python | `python3` / `python` | `py` / `python` | `python` |
| Start the shop | `uvicorn app.main:app` | *same* | *same* |
| Run tests | `python -m pytest …` | *same* | *same* |
| Score a prompt | `python belts/white/score_prompt.py …` | *same* | *same* |
| Stop the server | `Ctrl + C` | `Ctrl + C` | `Ctrl + C` |
| New terminal | `` Ctrl+`  `` | `` Ctrl+`  `` | `` Ctrl+`  `` |
| Paste clipboard → file | `pbpaste > out.py` | `Get-Clipboard > out.py` | paste into the editor, or `Get-Clipboard`/`xclip` |

### Things to call out to Windows users

- **Paths use back-slashes**: `belts\white\score_prompt.py` on a local Windows shell. Inside the Codespace (Linux) it's forward-slashes `belts/white/...` like everyone else.
- **Saving a model's output to a file**: in the Codespace, the simplest route for *everyone* is to **paste into a new file in the editor** and save — no clipboard command needed. That sidesteps `pbpaste` vs `Get-Clipboard` entirely.
- **`python3` may not exist on Windows** — it's just `python` or `py` there. In the Codespace, `python` works for all.
- **The `platform` line in pytest output** reads `darwin` on a Mac, `win32` on Windows, `linux` in a Codespace — all normal, just names the OS.

### The bottom line for the day

> Tell the room once: *"You're all working on the same Linux machine in the
> browser, so every command on screen works exactly as shown no matter what
> laptop you brought."* Then you never have to branch your instructions live.
