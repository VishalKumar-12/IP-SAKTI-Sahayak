# IP-SAKTI Sahayak

**AI-Powered Multilingual Ayurveda IPR & Regulatory Assistant**

> This README currently covers **Phase 1 — Frontend UI (mock data)** only.
> Backend, RAG, embeddings, database and multilingual/Bhashini integration
> are implemented in later phases and will extend this document.

## Authentication & Chat History (PostgreSQL)

The backend now includes user accounts and persistent chat history, backed by PostgreSQL.

### What was added
- **Sign up / Log in** — `POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/auth/me`. Passwords are hashed with Werkzeug's `generate_password_hash`; sessions use JWT access tokens (`Flask-JWT-Extended`).
- **Protected chat** — `POST /api/chat` now requires an `Authorization: Bearer <token>` header. Every request creates or continues a `Conversation` and stores both the user's message and the assistant's answer as `Message` rows.
- **Chat history endpoints**:
  - `GET /api/chat/conversations` — list the logged-in user's conversations (most recent first).
  - `GET /api/chat/conversations/<id>` — full message history for one conversation.
  - `DELETE /api/chat/conversations/<id>` — delete a conversation and its messages.
- **Frontend** — new `pages/login.html` and `pages/signup.html`, a shared `js/auth.js` (token storage, route guarding, navbar login/logout state), and the chat sidebar (`pages/chat.html` + `js/chat.js`) now lists real conversations from the database instead of hard-coded examples, lets you reopen or delete a past conversation, and carries a `conversation_id` on every message so replies land in the right thread.

### Database schema
Three tables (see `backend/models.py`):
- `users` — id, name, email (unique), password_hash, created_at
- `conversations` — id, user_id (FK), title, created_at, updated_at
- `messages` — id, conversation_id (FK), role (`user`/`assistant`), content, citations (JSON), confidence, classification, language, created_at

### Setup
1. Install the new dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a PostgreSQL database (the app does **not** create the database itself, only the tables):
   ```bash
   createdb ipsakti_sahayak
   ```
3. Set the connection details in `.env` (defaults shown; override as needed):
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=ipsakti_sahayak
   DB_USER=postgres
   DB_PASSWORD=postgres
   JWT_SECRET_KEY=change-this-secret-in-production
   JWT_ACCESS_TOKEN_EXPIRES=604800
   ```
   Alternatively set a single `DATABASE_URL` (e.g. `postgresql+psycopg2://user:pass@host:5432/dbname`), which takes priority.
4. Create the tables (also happens automatically the first time the Flask app starts, via `db.create_all()`):
   ```bash
   python -m scripts.init_db
   ```
5. Run the backend as usual:
   ```bash
   python -m backend.app
   ```
6. Open `frontend/pages/signup.html` to create an account, then use the chat page — you'll be redirected to `login.html` if you're not signed in.

> **Note:** `JWT_SECRET_KEY` must be set to a strong, random value in production — the default is only for local development.

## What's built so far

A complete, responsive, production-styled frontend using plain **HTML5 + CSS3 + Vanilla JavaScript** (no frameworks, per the project's strict stack requirement). Every page is fully navigable and works against a **mock API layer** (`frontend/js/api.js`), so the whole experience — including AI answers, ABS analysis, TKDL indicators, and citations — can be explored before the Flask/RAG backend exists.

### Pages
| Page | Path | Purpose |
|---|---|---|
| Home | `frontend/index.html` | Hero, features, how-it-works, India/International frameworks |
| AI Assistant | `frontend/pages/chat.html` | Chat UI with mock source-grounded answers, confidence, citations |
| ABS Helper | `frontend/pages/abs.html` | Access & Benefit-Sharing considerations form + result |
| TKDL Helper | `frontend/pages/tkdl.html` | Traditional-knowledge / prior-art indicator search |
| Sources | `frontend/pages/sources.html` | Browsable, filterable knowledge-source library |
| About | `frontend/pages/about.html` | Project explanation, RAG/citation/safety principles |

### Key UI elements implemented
- Sticky responsive navbar with language selector, jurisdiction selector, hamburger menu on mobile
- Hero section with an AI workflow visual (Question → Analysis → RAG Search → Sources → Answer)
- Six feature cards, a 5-step "how it works" timeline, India/International framework cards
- Full chat interface: sidebar with quick actions & recent questions, message thread, typing indicator, answer card (Answer / Why This Matters / Relevant Considerations / Sources / Confidence / Disclaimer), mic/attach/send controls, copy/helpful/not-helpful actions
- ABS Helper form → result card with access, benefit-sharing, traditional-knowledge and framework fields
- TKDL Helper search → result card with relevance, source, confidence, and an explicit notice that restricted TKDL contents are never scraped or reproduced
- Sources page with search + category/jurisdiction/type filters
- Confidence meter (score, level badge, progress bar) reused across chat, ABS and TKDL
- Loading, typing, error, empty-results and low-confidence/abstention states
- Accessibility: semantic HTML, ARIA labels, visible focus states, skip link, keyboard-friendly composer

## Folder structure (Phase 1)

```
IP-SAKTI-Sahayak/
├── frontend/
│   ├── index.html
│   ├── pages/
│   │   ├── chat.html
│   │   ├── abs.html
│   │   ├── tkdl.html
│   │   ├── sources.html
│   │   └── about.html
│   ├── css/
│   │   ├── style.css        # design tokens, navbar, hero, home sections, footer
│   │   ├── chat.css         # chat sidebar / thread / composer
│   │   ├── components.css   # forms, result cards, confidence, source cards, states
│   │   └── responsive.css   # 1024 / 768 / 480 / 320 breakpoints
│   ├── js/
│   │   ├── app.js           # nav toggle, jurisdiction sync, chat sidebar toggle
│   │   ├── api.js           # mock API layer (Phase 2 will add real fetch calls)
│   │   ├── chat.js          # chat page behavior
│   │   ├── abs.js           # ABS Helper page behavior
│   │   ├── tkdl.js          # TKDL Helper page behavior
│   │   ├── sources.js       # Sources page behavior
│   │   ├── language.js      # language selection, kept separate from UI
│   │   └── voice.js         # mic input via Web Speech API
│   └── assets/
│       ├── images/  (placeholder — add project imagery here)
│       ├── icons/   (placeholder)
│       └── logo/    (placeholder)
├── README.md
└── .gitignore
```

`backend/`, `data/`, `scripts/`, `evaluation/` and `docs/` will be added starting Phase 2.

## Design language

- **Colors:** deep green (`#1F4B3F`) for trust/authority, saffron/orange (`#E07B2D`) as accent, warm off-white background (`#F6F5EF`), dark text (`#1B2420`)
- **Type:** `Fraunces` (serif) for headings — conveys institutional gravitas — paired with `Work Sans` (sans-serif) for body/UI text
- Rounded cards with restrained shadows (no heavy glassmorphism, no overused gradients)
- Subtle Ayurveda-inspired dot/leaf motif in the hero background

## How to run the frontend locally

The frontend is fully static — no build step and no server-side code required for Phase 1.

### Option A — Open directly
Double-click `frontend/index.html`, or open it from your browser with **File → Open**.

> Note: on some browsers, `fetch`/module features can behave inconsistently under the `file://` protocol. If you notice anything odd, use Option B below.

### Option B — Serve locally (recommended)
From the project root:

```bash
cd IP-SAKTI-Sahayak/frontend
python3 -m http.server 8080
```

Then open:

```
http://localhost:8080/
```

Alternatively, with Node.js installed:

```bash
cd IP-SAKTI-Sahayak/frontend
npx serve .
```

### Try it out
- Home → click **Ask IP-SAKTI** to open the chat
- Chat → try the pre-filled example question, or click a **Quick Action** in the sidebar
- ABS Helper → fill the form and click **Analyze ABS Considerations**
- TKDL Helper → search for a herb or formulation (e.g. "Ashwagandha") and click **Check Traditional Knowledge**
- Sources → search/filter the mock document library
- Resize the browser (or use dev tools' device toolbar) to confirm responsiveness at 320px, 375px, 768px, 1024px and 1440px

All responses right now come from `frontend/js/api.js` in **mock mode** (`MOCK_MODE = true`), simulating network latency — no backend, Pinecone, or database connection is required yet.

## Next phase

**Phase 2** will build the Flask backend (`backend/app.py`, `/api/health`, `/api/chat`, `/api/sources`) and connect it to this frontend by flipping `MOCK_MODE` to `false` in `api.js`.



---
title: IP-SAKTI Embedding Service
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 6.0.0
app_file: app.py
python_version: 3.12
---

# IP-SAKTI Embedding Service

Embedding service for IP-SAKTI Sahayak.

Model:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Embedding dimension: 384