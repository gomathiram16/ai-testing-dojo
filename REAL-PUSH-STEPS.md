# 🚀 Real push — the dojo to GitHub + Codespaces (with answer keys hidden)

You've done the practice run, so the mechanics are familiar. This adds the one
thing that matters for the real repo: **`solutions/` and `facilitator/` must never
reach the shared repo.** Run commands in **your own Terminal**; `<you>` = your
GitHub username.

Repo folder: `…/Automation Star/Prep/ai-testing-dojo`

---

## How the hiding works (read once)

- `.gitignore` excludes `solutions/`, `facilitator/`, and `belts/black/generated/`.
  Because they're ignored, `git add .` never stages them, so they're **never
  committed and never in history**. (A separate branch would NOT hide them —
  branches are visible and history still leaks. `.gitignore` is the clean way.)
- You keep the full copy **locally** on your Mac as your facilitator master.
- `verify_ready.py` skips the answer-key check when `solutions/` is absent, so the
  attendee repo still reports **READY**.
- Optional: keep a **private** full backup repo too (Part 7).

---

## Part 1 — sanitise-check locally (prove the hide works BEFORE pushing)

```
cd "/Users/gomathiramalingam/Desktop/Claude/Automation Star/Prep/ai-testing-dojo"
cat .gitignore
```
- [ ] `.gitignore` lists `solutions/`, `facilitator/`, `belts/black/generated/`.

```
git init
git add .
git status
```
- [ ] **CRITICAL CHECK:** `git status` lists `app/`, `belts/`, `README.md`,
      `START-HERE.md`, `ATTENDEE-SETUP.md`, `COMMANDS.md`, `Makefile`,
      `verify_ready.py`, `requirements.txt`, `.devcontainer/`, `.gitignore` …
      and **NOT** `solutions/` or `facilitator/`. If you see either of those,
      stop — the `.gitignore` isn't taking effect; tell me.

```
git commit -m "AI Testing Dojo — attendee repo"
```

> Double-check nothing is tracked that shouldn't be:
> ```
> git ls-files | grep -E "solutions/|facilitator/"
> ```
> This must print **nothing**. (Empty = good.)

---

## Part 2 — create the repo and push

For a room of ~60 who each launch their own Codespace, a **public** repo is
simplest (anyone with the link can open one). It's safe because the answer keys
are excluded.

```
gh repo create ai-testing-dojo --public --source=. --remote=origin --push
```
- [ ] It prints the repo URL and pushes.

> If it says *"remote origin already exists"*: `git remote remove origin`, then
> `git remote add origin https://github.com/<you>/ai-testing-dojo.git`, then
> `git branch -M main && git push -u origin main`.
> Prefer private instead? Use `--private` — but then each attendee needs access,
> which isn't practical for 60 people; public is the usual choice for a workshop.

---

## Part 3 — confirm nothing leaked (do this, every time)

1. Open the repo on github.com and **look at the file list**.
   - [ ] You see `app/`, `belts/`, the READMEs — and **no `solutions/`, no `facilitator/`**.
2. Try the direct URLs (they should 404):
   - `https://github.com/<you>/ai-testing-dojo/tree/main/solutions` → **404** ✅
   - `https://github.com/<you>/ai-testing-dojo/tree/main/facilitator` → **404** ✅
3. Check history didn't capture them earlier:
   - On GitHub, the repo's commit list → your single commit → confirm only intended files.

If any answer-key file is visible, the safest fix is to delete the repo
(`gh repo delete ai-testing-dojo --yes`), fix `.gitignore`, and re-push from a
clean `git init` — because removing a file later leaves it in history.

---

## Part 4 — turn on Prebuilds (fast launches for ~30)

Repo → **Settings → Codespaces → Set up prebuild** → for `main` → save.
- [ ] Prebuild configured (so attendees don't wait for a container build).

---

## Part 5 — add the Codespaces secrets

Repo → **Settings → Secrets and variables → Codespaces → New repository secret**,
add three (values from `facilitator/api_gateway.md`):
- [ ] `DOJO_API_BASE_URL`
- [ ] `DOJO_API_KEY`  (a capped **virtual** key, not a real provider key)
- [ ] `DOJO_MODEL`

> **Public-repo caveat (test this in the friend dry run!):** repo Codespaces
> secrets reach codespaces created by users with access. For a **public** repo and
> **external** attendees, a codespace may be created on a fork where your secrets
> don't apply — in which case they won't auto-receive the key. If your friend's
> run (a non-collaborator account) shows "LLM gateway not configured", switch to
> the **attendee `.env` method** (`ATTENDEE-SETUP.md`) — that always works. This
> is exactly what the PM dry run is for.

---

## Part 6 — test a fresh launch yourself (incognito)

- [ ] Repo → **Code → Codespaces → Create codespace on main** → wait for build.
- [ ] `echo $DOJO_API_BASE_URL` → prints your gateway URL (secret injected).
- [ ] `make check` (or `python verify_ready.py`) → **READY** (it skips the
      answer-key check — that's expected; `solutions/` isn't in this repo).
- [ ] `uvicorn app.main:app` → open forwarded port 8000 → shop loads.
- [ ] One real belt command works end to end (e.g. the agent with `--generator llm`).

---

## Part 7 (optional) — private full backup of everything

So your facilitator materials live in the cloud too (with answers):
```
cd "/Users/gomathiramalingam/Desktop/Claude/Automation Star/Prep/ai-testing-dojo"
# temporarily allow the two folders for THIS private repo only:
gh repo create ai-testing-dojo-facilitator --private
git remote add facilitator https://github.com/<you>/ai-testing-dojo-facilitator.git
git add -f solutions/ facilitator/     # -f overrides .gitignore, just here
git commit -m "facilitator master (private)"
git push facilitator main
# then UNSTAGE them from the public remote tracking going forward:
git rm -r --cached solutions/ facilitator/
git commit -m "keep solutions/facilitator out of the public remote"
```
> Simpler alternative: just keep your local folder as the master and skip Part 7.
> Only do this if you want a cloud backup of the answer keys.

---

## What attendees end up seeing

`app/`, `belts/` (White/Blue/Black, minus `solutions/`), `README.md`,
`START-HERE.md`, `ATTENDEE-SETUP.md`, `COMMANDS.md` — everything they need to do
all three belts, and **nothing that reveals the seeded bugs or the answer keys.**
