# 🧭 Memory-aware Search Router

**AI assistants search the web for everything — generically and expensively.**
This one checks what it already knows about you first, then decides **whether** to search and **how** to search.

Built solo at **SearchHack (Telem AI Series)**, Sunnyvale, November 14, 2026.

## The problem

Today's assistants run the same web search for everyone, for every question:

- "What time do I usually run?" → a web search, even though the answer is about *you*.
- "Recommend a restaurant" → generic results, even though the assistant knows you're vegetarian, in Sunnyvale, with a $30 budget.

That wastes money and returns answers that aren't about you.

## How it works

```
question + user
      │
      ▼
 1. Mem0 ─────────── the user's relevant memories
      │
      ▼
 2. Planner (LLM) ── {"rota": "memoria" | "web" | "ambos",
      │                "motivo": "...",
      │                "consultas_web": [queries REWRITTEN with memory]}
      │
      ├── memoria → 0 web calls
      │
      ▼ web / ambos
 3. Telem search ─── auto-routing picks the best providers per query
      │               (we keep providers, latency, routing topic, trace id)
      ▼
 4. Tavily extract ─ clean markdown of the top 3 pages
      │
      ▼
 5. Combiner (LLM) ─ answer citing [M1].. (memory) and [W1].. (web)
```

**Example — same question, two users:** "Recommend a restaurant for dinner tonight"

| Alex (vegetarian, no car, $30) | Maria (steak lover, has a car, $100) |
|---|---|
| `vegetarian restaurants open for dinner in Sunnyvale CA under $30, peanut-free` | `quiet steakhouse restaurants Palo Alto CA dinner tonight with easy parking` |

### Why Telem

- **One call, many providers:** auto-routing (`auto_routing="accuracy"`) sends each personalized query to the providers that answer it best (exa, tavily, brave, parallel, …).
- **Observability:** every search returns the chosen providers, per-provider latency and status, the routing topic and an `interaction_id` trace. The UI shows all of it.
- **The router decides *whether* to search; Telem decides *where* to search.**

### Safety

- Web content is wrapped in `<web_source>` tags and treated as **untrusted data**: the answer prompt ignores any instructions found in pages (prompt-injection defense).
- Only **fictional** demo users (`search-hack`, `search-hack-maria`) and fictional memories.
- API keys live in `.env`, which is git-ignored.

## Run it

Requires Python 3.10+ (we use 3.12 via [uv](https://docs.astral.sh/uv/)).

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env          # then fill in the 4 API keys
.venv/bin/python seed.py      # load the fictional memories into Mem0
.venv/bin/streamlit run app.py
```

Keys: [OpenRouter](https://openrouter.ai), [Mem0](https://app.mem0.ai), [Tavily](https://tavily.com), [Telem](https://hack.telem.ai).

> **Note:** API keys issued at `hack.telem.ai` only work with `TELEM_BASE_URL=https://hack.telem.ai/api/router` (already in `.env.example`). The SDK default server answers `401 Invalid API key` for them.

Test each service on its own: `.venv/bin/python smoke_test.py telem | tavily | mem0`

## Files

| File | What it does |
|---|---|
| `app.py` | Streamlit UI |
| `pipeline.py` | Runs the 5 steps, timings and cost metrics |
| `planner.py` | Route + query rewriting (JSON with fallback to "ambos") |
| `combiner.py` | Cited answer, web content as untrusted data |
| `sources.py` | Mem0 search, Telem search, Tavily extract |
| `llm.py` | OpenAI SDK pointed at OpenRouter |
| `seed.py` | Fictional personas and memories |

## Stack

Python · Streamlit · [Telem](https://docs.telem.ai) · [Tavily](https://docs.tavily.com) · [Mem0](https://docs.mem0.ai) · OpenRouter (`anthropic/claude-haiku-5.5`)

## Limitations

- Cost savings are **estimates** from Telem's public price list (~$0.005 per provider call); the exact charge is in the Telem console.
- Web answers take ~10–20 s (several providers + page extraction).
- Mem0 processes writes asynchronously: new memories appear after a few seconds.
