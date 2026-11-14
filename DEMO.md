# Demo script (3 min walkthrough)

Before recording: `.venv/bin/streamlit run app.py`, open http://localhost:8501, start with **Alex** selected.
Run every question once before recording so you know the timings (web answers take ~10–20 s; cut the wait in the video).

| # | User | Question (click the example button) | Expected route | What it proves |
|---|---|---|---|---|
| 1 | Alex | What time do I usually go running, and how far? | 🧠 Memory only | **0 web searches**, ~3 s. The "Web searches avoided" counter goes up. |
| 2 | Alex | Who won the last Golden State Warriors game? | 🌐 Web only | Fresh world facts. Open "Under the hood": Telem picked the providers, per-provider latency, trace id. |
| 3 | Alex | Recommend a restaurant for dinner tonight | 🧠 + 🌐 | Query **rewritten with memory**: vegetarian, Sunnyvale, under $30, peanut-free. Answer cites [M#] and [W#]. |
| 4 | **Maria** | (same question stays in the box; switch user in the sidebar) | 🧠 + 🌐 | **Same question, opposite search**: quiet steakhouse in Palo Alto, easy parking, under $100. |
| 5 | Maria → Alex | Will I need a jacket for my morning run tomorrow? | 🧠 + 🌐 | Memory supplies place + time (Alex 6:30 am in Sunnyvale vs. Maria 6 pm ride in Palo Alto). Different forecasts, different advice. |

Backup question (memory + web): "What should I get my sister for her birthday?" (Alex: Ana loves design books → current design book picks).

## Talking points while it runs

- **Step 1:** "Most assistants would have searched the web here. We didn't: it's about *you*."
- **Step 2:** "When it's about the world, Telem's auto-router picks the best providers for the query, and we see exactly what ran."
- **Step 3–4:** "Memory doesn't just answer — it changes **how** we search. Same words, two people, two different searches."
- **Close:** point at the sidebar: searches avoided and estimated savings.

## If something breaks

- Planner fails → the app falls back to "Memory + Web" automatically (yellow warning).
- A page can't be extracted → the answer uses Telem's snippet ("⚠️ snippet only").
- Memories missing → re-run `.venv/bin/python seed.py` and wait ~1 min.
