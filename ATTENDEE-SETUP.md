# 🔑 Attendee Setup — add your workshop API key (30 seconds)

*Do this once, at the start, so the AI belts can reach the model.*

At the start of the session you'll be given **three values**:

- a **URL**  (the gateway address)
- a **key**  (your session key for today)
- a **model name**

Put them in a file called **`.env`** in the `ai-testing-dojo` folder.

## Easiest way — in the editor (Codespaces / VS Code)

1. In the file list on the left, **right-click** the top `ai-testing-dojo` folder → **New File**.
2. Name it **exactly** `.env` — a dot, then `env`, with nothing before the dot.
3. Paste these three lines, filling in the values you were given, then **save** (**Cmd+S** on Mac, **Ctrl+S** on Windows):

```
DOJO_API_BASE_URL=<the URL you were given>
DOJO_API_KEY=<the key you were given>
```

> Only add a `DOJO_MODEL=...` line **if your facilitator gives you one.** Normally
> you leave it out, so the belts can use both Claude and GPT (the White Belt
> comparison). If you were handed three values including a model, add it.

That's it — the belts pick it up automatically. No restart needed.

## Or — one line in the Terminal

Paste this, replacing the three capitalised placeholders with your values:

```
printf 'DOJO_API_BASE_URL=%s\nDOJO_API_KEY=%s\nDOJO_MODEL=%s\n' "URL" "KEY" "MODEL" > .env
```

> Use this single `printf` line rather than a multi-line `cat <<'EOF'` — it pastes
> cleanly in one go and won't leave the terminal waiting for input.

## Check it worked

```
cat .env
```

You should see your three lines printed back. If a command later says
*"LLM gateway not configured"*, your `.env` is missing, in the wrong folder, or a
variable name is misspelled — it must be exactly `DOJO_API_BASE_URL`,
`DOJO_API_KEY`, `DOJO_MODEL`.

## Good to know

- `.env` is **git-ignored**, so your key is never committed or shared.
- The key is **for today only** and may be rate-limited — if you hit a limit, you
  can still do every belt on the offline/mock path.
- Keep the key to yourself; don't paste it into chat, screenshots, or the repo.
