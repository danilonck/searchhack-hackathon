# Pitch — Memory-aware Search Router (3 min)

~420 spoken words. Times are cumulative. **[Bold brackets]** = what to show.

---

## 0:00 – 0:25 · Hook and problem

> Every AI assistant today does the same thing: you ask a question, it searches the web. Always. For everyone.
>
> Ask "what time do I usually run?" — it searches the web. Ask "recommend a restaurant" — it returns the same generic list it gives everybody, even though it *knows* you're vegetarian and on a $30 budget.
>
> That's wasted money on every call, and answers that aren't about you.

## 0:25 – 0:45 · Customer

> Our customer is any team shipping an AI assistant or agent that searches the web: travel and concierge apps, personal assistants, support copilots. They pay per search, per provider, per token — and their users want answers that feel personal.

## 0:45 – 1:05 · Solution

> We built a memory-aware search router. Before searching, it reads what it remembers about the user, in Mem0, and decides two things:
> **whether** to search at all, and **how** to search — rewriting the query with the user's context.
> When it does search, Telem's auto-router sends that personalized query to the best providers, and Tavily extracts clean page content. The answer cites every source.

## 1:05 – 2:20 · Demo

**[Alex selected · click "What time do I usually go running?"]**
> Personal question. Route: memory only. Zero web searches, about three seconds. Watch the sidebar: one search avoided.

**[Click "Who won the last Warriors game?"]**
> A world question. Route: web only. Under the hood you see exactly what Telem did: which providers it picked, each one's latency, and a trace id.

**[Click "Recommend a restaurant for dinner tonight"]**
> Now both. Left: what the user typed. Right: what we actually searched — vegetarian, Sunnyvale, under thirty dollars, peanut-free. Every claim is cited: M for memory, W for web.

**[Switch user to Maria — same question reruns]**
> Same words, different person. Maria loves steak, has a car, spends up to a hundred. Now we search for a quiet steakhouse in Palo Alto with easy parking. Same question, opposite search.

## 2:20 – 2:40 · Why Telem is essential

> We decide *whether* to search. Telem decides *where*. Its auto-routing picks the right providers for each personalized query in one call, and its observability lets us show — and price — every step. Without Telem we'd be hard-coding one provider, or paying for all of them.

> And it's FinOps by design: memory questions cost zero web calls, and web questions send one query to a small allow-list that Telem routes within. On our demo set that's about sixty percent cheaper than always searching — with the same cited answers.

## 2:40 – 3:00 · Business and close

> Business model: a drop-in layer for assistant builders, priced per routed query — cheaper than the searches it avoids.
> And with Telem Monitors, one click keeps watching that personalized search for you.
>
> Search less. Search smarter. Search for *you*. Thank you.

---

## Slides (3–4)

1. **Title** — "Memory-aware Search Router · Search less. Search smarter. Search for you." Your name, SearchHack (Telem AI Series).
2. **Problem → Solution** — Left: "Assistants search everything, the same way, for everyone." Right: the 5-step flow (Mem0 → Planner → Telem → Tavily → cited answer).
3. **Same question, two people** — the Alex vs. Maria table of rewritten queries (from the README).
4. **Why Telem + business** — auto-routing + observability; customer = AI assistant builders; priced per routed query; also built: Telem Monitors.

## Q&A prep

- **"How much do you really save?"** — Estimated from Telem's price list: unoptimized, one search fanned out to ~8 providers (~$0.04). We skip search when memory answers and cap web searches to 1 query over 3 allowed providers: ~$0.08 vs ~$0.22 on the 5 demo questions (−62%). Exact charges are in the Telem console.
- **"What if the planner is wrong?"** — It falls back to searching everything, so the worst case is today's behavior.
- **"Prompt injection from web pages?"** — Page content is wrapped as untrusted data; the answer prompt ignores instructions inside it.
- **"Why not just always search?"** — Cost, latency (3 s vs. ~15 s) and relevance: a generic search can't know your diet or budget.
- **"Privacy?"** — Memory is per user; the demo uses only fictional users.
