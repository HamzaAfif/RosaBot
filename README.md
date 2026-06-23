# RosaBot 🌹

A full-stack AI assistant I built for the restaurant where I work part-time as a
busser in Montreal. During busy shifts I kept noticing the same problems — new
staff struggling to learn a large menu, people unsure about allergens, bartenders
double-checking cocktail specs mid-rush. So I built RosaBot: a chat assistant that
knows the entire India Rosa menu and answers staff questions instantly, in French
or English.

It's a real tool solving a real problem I see every shift, built as a portfolio
project while doing my Master's in Software Engineering at UQAM.

> **🌹 Live demo:** https://rosa-bot.vercel.app
> **Stack:** React · Tailwind · FastAPI · LangChain · OpenAI

---

## What it does

- **Menu lookups** — "What's in the Butter Chicken?" returns exact ingredients.
- **Cocktail specs** — exact ounces, method, and glassware for bartenders.
- **Allergen checks** — "Anything without dairy?" with a safety-first approach.
- **Bilingual** — staff ask in English or French; the menu data is in French.
- **Typo-tolerant** — "poulet au boeur" still finds "Poulet au beurre."
- **Remembers context** — ask a follow-up ("what about nuts?") and it knows
  what you mean.

## The interesting engineering decision: tools, not RAG

The obvious way to build a menu chatbot today is RAG — embed the menu into a
vector database and retrieve "similar" chunks. I deliberately didn't do that, and
understanding *why* was the most valuable part of this project.

A menu is **structured, exact data**: 1.75 oz of pisco, egg white present or not,
this specific allergen. Vector search is good at "find something similar in
meaning" but bad at "give me the *exact* ingredients of this *specific* dish" — it
can return a cocktail that merely *looks* similar and hand back the wrong recipe.

So instead, the menu stays as structured JSON, and the language model reaches it
through **function-calling tools** — small, deterministic Python functions it
calls when it needs precise data. No vector store, no fuzzy approximations, no
loading the whole menu into the prompt. The model picks a tool, the tool returns
a tiny exact snippet, and the answer is built from that. It's cheaper, faster, and
fully debuggable — if it ever answers wrong, I can trace exactly which tool was
called and why.

This is the kind of judgment I'm proud of: choosing the right pattern for the data
instead of reaching for the trendy default.

## Does it actually work? I measured it.

Most projects stop at "it seemed fine when I tried it." I wanted a real number, so
I built an automated evaluation suite: a fixed set of real staff questions, graded
against known-correct facts, with every run traced in LangSmith for latency and
cost.

The first run scored **44%**. Investigating the failures surfaced real bugs; a
whole dessert section missing from the searchable data, and a dietary
misclassification (a dairy dish listed as vegan). After fixing them, accuracy rose
to **81%** — a measured, documented improvement, not a vibe.

**→ Full write-up: [EVAL_REPORT.md](EVAL_REPORT.md)**; method, baseline, what
failed, what I fixed, and the before/after numbers.

That measure → find failures → fix → re-measure loop is the difference between a
demo and a system.

## How it's built

```
React + Tailwind frontend
        │  POST /chat
        ▼
FastAPI backend
        │
        ▼
LangChain agent  ──  system prompt + 3 tools + conversation memory
        │
        ▼
3 menu tools  ──  thin wrappers over the data layer
        │
        ▼
MenuRepository  ──  loads + normalizes 3 messy JSON menu files into one clean shape
```

The layering is deliberate — the repository is the *only* code that touches the
JSON, the tools wrap the repository, the agent calls the tools, the API wraps the
agent. Each layer has one job, so swapping the JSON for a real database later means
changing one file and nothing else.

### The three tools

| Tool | What it's for | Example |
|------|---------------|---------|
| `search_menu_items` | Details of one specific item | "Does the Pisco Sour have egg?" |
| `get_menu_summary` | Lightweight list of everything | "What cocktails do you have?" |
| `filter_by_dietary` | Items without a given allergen | "Anything without dairy?" |

## Allergens: built to be safe, not just clever

Allergens are the one place a restaurant tool can't bluff. RosaBot uses two layers:

1. **Kitchen-curated lists** — authoritative facts the kitchen provided.
2. **Keyword inference** — a fallback that scans ingredient names to catch what
   the curated lists missed (like egg white hiding in a cocktail).

Every allergen flag records its **source**, so the bot can say "the kitchen lists
this as containing nuts" (high confidence) vs "I detected possible dairy" (lower
confidence). And it **never** tells staff a dish is "safe" — every dietary answer
carries a disclaimer to confirm with the kitchen. That restraint was a conscious
design choice: an AI guessing wrong about an allergy is the one failure that
actually matters.

## Tech stack

**Frontend:** React, Vite, Tailwind CSS
**Backend:** FastAPI, Python
**AI:** LangChain agent (`create_agent`), OpenAI, in-memory conversation
checkpointer
**Testing:** pytest (data layer + tools)
**Deployment:** Frontend on Vercel, backend containerized and hosted on Railway

## Running it locally

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```
Create `backend/.env`:
```
OPENAI_API_KEY=sk-your-key-here
```
Run it:
```bash
uvicorn app.main:app --reload    # API at localhost:8000, docs at /docs
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev                      # app at localhost:5173
```

**Tests:**
```bash
cd backend
python -m pytest -v
```

## What I learned

- Why function-calling beats RAG for structured data — and being able to defend
  that choice.
- Designing an agent with tools, schemas, and a system prompt that enforces real
  safety rules.
- Building a clean layered backend where each part has one responsibility.
- Learning React from scratch — state, components, props, hooks — to build the
  frontend myself.
- Deploying a real full-stack app: containerizing the backend, wiring environment
  variables, and connecting two separately-hosted services.
- Handling the unglamorous-but-essential parts: error handling, conversation
  memory, bilingual + typo-tolerant search, keeping secrets out of version
  control.

## Honest limitations

- Conversation memory is in-memory and resets on restart (swap in `SqliteSaver`
  to persist).
- Allergen detection is a staff *aid*, not a certified database; only as complete
  as the curated lists plus keyword coverage.
- Built as a student prototype, but designed with production paths in mind.

---

*Built by Hamza — Master's student in Software Engineering, UQAM. This started as
a problem I noticed on the restaurant floor and became a project I'm genuinely
proud of.*