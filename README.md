# RosaBot 🌹

An AI staff assistant for **India Rosa**, a restaurant in Montreal. RosaBot helps
waiters, runners, and bartenders during service — looking up menu items, cocktail
specs, ingredients, and possible allergens through a simple chat interface.

It is built as an **agent with function-calling tools**, not a vector-database
chatbot. The menu lives in structured JSON, and the language model reaches it
through a small set of deterministic Python tools — so answers are precise
(exact ounces, exact ingredients) rather than fuzzy approximations.

---

## Why function-calling instead of RAG

The menu is structured data: exact measurements, specific ingredients, strict
allergen information. Vector embeddings are good at "find something similar in
meaning," but poor at "give me the *exact* ingredients of this *specific* item."
Loading the whole menu into the prompt, meanwhile, is slow and expensive.

So RosaBot keeps the menu in JSON and exposes three tools. The model decides
which tool to call, the tool returns a small precise snippet, and the model
answers from that. No vector store, no prompt bloat, fully debuggable.

## Architecture

```
Browser (index.html)
        │  POST /chat
        ▼
FastAPI backend (app/main.py)
        │
        ▼
LangChain agent (app/agent/) ── system prompt + 3 tools
        │
        ▼
Menu tools (app/tools/) ── thin wrappers over the repository
        │
        ▼
MenuRepository (app/data/) ── loads + normalizes the JSON menus
```

### The three tools

| Tool | Purpose | Example question |
|------|---------|------------------|
| `search_menu_items` | Full details of one specific item | "Does the Pisco Sour have egg?" |
| `get_menu_summary` | Lightweight list (names + categories) | "What cocktails do you have?" |
| `filter_by_dietary` | Items without a flagged allergen | "Anything without dairy?" |

## Allergen handling

Allergen information comes from two layers, with the safer one winning:

1. **Kitchen-curated lists** (`allergy_guide.json`) — authoritative. Where the
   kitchen has listed an allergen, that is used directly.
2. **Keyword inference** — a fallback that scans ingredient names to catch
   anything the curated lists did not mention (e.g. egg white in cocktails).

Every allergen flag records its **source** (`curated` vs `inferred`) so RosaBot
can speak with appropriate confidence. **No answer is ever presented as a safety
guarantee** — every dietary response carries a disclaimer telling staff to
confirm with the kitchen.

## Project structure

```
RosaV2/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI app + /chat endpoint
│   │   ├── config.py            settings + .env loading
│   │   ├── agent/               LangChain agent + system prompt
│   │   ├── tools/               the 3 tools + Pydantic schemas
│   │   ├── data/                MenuRepository + JSON menus
│   │   └── models/              request/response models
│   ├── tests/                   pytest suite (repository + tools)
│   ├── requirements.txt
│   └── .env                     OPENAI_API_KEY=... (not committed)
└── index.html                   single-file chat frontend
```

## Running locally

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows  (use: source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

Create `backend/.env`:

```
OPENAI_API_KEY=sk-your-key-here
```

Start the server:

```bash
uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000`. Interactive docs (try it in the
browser, no frontend needed): `http://localhost:8000/docs`.

### 2. Frontend

From the project root, serve the page:

```bash
python -m http.server 5500
```

Open `http://localhost:5500` and chat with RosaBot.

## Running the tests

```bash
cd backend
python -m pytest -v
```

## Configuration

Set these in `backend/.env` (all optional except the API key):

| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENAI_API_KEY` | — | required |
| `ROSABOT_MODEL` | `gpt-4o-mini` | which model to use |
| `ROSABOT_TEMPERATURE` | `0.2` | low = grounded, consistent |
| `ROSABOT_ORIGINS` | `*` | allowed CORS origins |

## Notes & limitations

- **Conversation memory** is in-memory and resets when the server restarts.
  Swap `InMemorySaver` for a `SqliteSaver` in `app/agent/rosabot_agent.py` to
  persist it.
- **Allergen detection** is only as complete as the curated guide plus the
  keyword list. It is a staff aid, not a certified allergen database.
- Built as a student prototype to demonstrate an applied AI use case in
  restaurant operations.