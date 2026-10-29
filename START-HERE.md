# 👋 Start Here — your 10-minute refresher

*Open this whenever you sit down and feel lost. It's a warm-up, not a lesson.*

## The big picture (read once)

You're building a **3-hour hands-on tutorial** that teaches testers *when to trust
AI-generated tests*. To teach that, you have a deliberately **broken pretend shop
called DojoShop** that people practise testing. **Everything is already built.**
Right now your only job is to get comfortable running it again.

## The map — your three belts

- 🥋 **White Belt** — *prompt the AI well and you get better tests.* You prove it with a score.
- 🥋 **Blue Belt** — *AI tests miss things.* You catch what they miss with a 6-point checklist.
- 🥋 **Black Belt** — *an AI agent that tests on its own.* You watch it hunt a bug.

## The refresher flow (4 steps)

Each step says **why** you're doing it, **what to type**, **what you'll see**, and **what it means**.

### Step 1 — Wake up the shop
- **Why:** DojoShop is the thing your attendees will test. Start by confirming it runs.
- **Do:**
  ```
  cd "/Users/gomathiramalingam/Desktop/Claude/Automation Star/Prep/ai-testing-dojo"
  source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
  uvicorn app.main:app
  ```
- **See:** the line `Application startup complete.` The terminal then looks frozen — **that's correct**, it means the shop is running.
- **Means:** your "system under test" is alive.

### Step 2 — Look at it two ways
- **Why:** attendees meet the shop two ways — as a **shopper** (the webpage) and as a **tester** (the API). They're the same thing underneath.
- **Do:** in a browser open **http://127.0.0.1:8000** (the shop), then **http://127.0.0.1:8000/docs** (the same thing as clickable buttons). When done, go back to Terminal and press **Ctrl + C** to stop.
- **See:** a little store with product tiles; and a list of API operations you can click "Try it out" on.
- **Means:** this is the "every click is an API call" bridge your tutorial is built on.

### Step 3 — Re-feel the White Belt "aha"
- **Why:** the heart of White Belt is that **how** you ask the AI matters more than **which** AI you use. The scorer turns that into a number so it's undeniable.
- **Do:**
  ```
  python belts/white/score_prompt.py belts/white/examples/sample_naive_output.py
  python belts/white/score_prompt.py belts/white/examples/sample_context_output.py
  ```
- **See:** about **9.8 / 25** for the first, **22.1 / 25** for the second.
- **Means:** same AI, a better prompt → roughly twice as good. *That gap is the entire White Belt.*

### Step 4 — Reload the big picture
- **Why:** so the three belts sit clearly in your head again.
- **Do:** open `AI-Testing-Dojo-Blueprint.md` and read just **§1** (the promise), **§3** (the run-of-show), and **§5–7** (the three belts).
- **See:** the four takeaways, the minute-by-minute plan, and each belt's goal.
- **Means:** you can now explain the whole tutorial in a couple of minutes.

## That's it 🎉

You didn't learn anything new — you dusted off what's already yours. When you're
ready, your next working session **re-walks the three belts properly**, one at a time.
