# 💥 ChangeBlast

> **See the blast radius before you change the code.**

ChangeBlast is a full-stack developer tool that analyzes a proposed code change **before** it is implemented and shows everything it will affect — impacted files, API contracts, database migrations, tests, risk level, and a step-by-step change plan.

Built as a hackathon MVP.

---

## 🔗 Live Demo

| Service | URL |
|---|---|
| **Frontend** | https://changeblast.vercel.app |
| **Backend API** | https://changeblast-api.onrender.com |
| **API Docs** | https://changeblast-api.onrender.com/docs |

> **Demo change:** *"Replace User.id from Integer to UUID"* — try it on the live site.

---

## ✨ Features

- **Blast Radius Analysis** — Submit any proposed change in plain English; get back every file, API, and table it touches
- **Evidence-backed findings** — Every impact item links to a real file + line number from the repository
- **Deterministic risk scoring** — No LLM involved in the score; six transparent signals produce a LOW / MEDIUM / HIGH rating
- **Impact Explorer** — Six tabs (Code · API · Database · Frontend · Tests · History) with expandable evidence
- **SVG blast radius graph** — Radial node/edge visualization with hover tooltips, zero external dependencies
- **Ordered change plan** — Phased step-by-step guide generated directly from what was found
- **Live progress** — Animated step tracker while the backend analyzes in the background

---

## 🏗 Architecture

```
Browser (React + Vite)
       │  POST /api/v1/analysis   → queued (202)
       │  GET  /api/v1/analysis/{id}/status  (poll 800ms)
       │  GET  /api/v1/analysis/{id}         (full result)
       ▼
FastAPI backend (Uvicorn)
       │
       ├── background task → analysis_engine.run_analysis()
       │       ├── scan_repository()      — regex scan of sample_repo/
       │       ├── build_evidence()       — structured findings
       │       ├── classify_impact()      — sort into 6 categories
       │       ├── calculate_risk()       — deterministic score
       │       ├── build_summary()        — numeric counts
       │       ├── build_graph()          — nodes + edges
       │       └── build_change_plan()    — ordered steps
       │
       └── .store/  ← JSON file store (one file per analysis)
```

**Deployment:**
- Frontend → Vercel (static build, `VITE_API_URL` env var points to backend)
- Backend → Render (Python web service, `uvicorn backend.main:app`)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ · FastAPI · Uvicorn |
| Analysis engine | Custom static scan (regex, no LLM) |
| Storage | JSON file store (zero-config) |
| Frontend | React 18 · Vite 5 |
| Graph | Pure SVG — no external graph library |
| Styling | Vanilla CSS custom properties (dark theme) |
| Deploy | Vercel (frontend) · Render (backend) |

---

## 📁 Project Structure

```
CHANGEBLAST/
├── backend/
│   ├── main.py                 # FastAPI app — 3 API endpoints + file store
│   ├── analysis_engine.py      # Full pipeline: scan → evidence → risk → plan
│   ├── requirements.txt        # fastapi, uvicorn
│   └── sample_repo/            # Seeded e-commerce codebase (demo target)
│       ├── models.py           # User, Order, Payment, UserSession models
│       ├── users/              # User service + Pydantic schemas
│       ├── orders/             # Order service
│       ├── payments/           # Payment service
│       ├── auth/               # Auth & JWT utilities
│       ├── api/                # REST route definitions + frontend components
│       ├── migrations/         # SQL migration scripts
│       └── tests/              # Pytest test suite
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # All screens + components (single file)
│   │   └── index.css           # All styles (dark theme)
│   ├── index.html
│   ├── vite.config.js          # Dev server — proxies /api → backend
│   └── package.json
├── start.bat                   # Windows one-click launcher
├── start.ps1                   # PowerShell launcher
└── README.md
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+  (`python --version`)
- Node.js 18+  (`node --version`)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --port 8000 --reload
```

- API base: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

- App: `http://localhost:5173`
- The Vite dev server proxies all `/api` requests to `localhost:8000`

### One-click (Windows)

```
start.bat
```

---

## 🎬 Running the Demo

1. Open `http://localhost:5173` (or the live Vercel URL)
2. Click **"Analyze a Change"**
3. Click the demo pill: **"Replace User.id from Integer to UUID"**
4. Click **"Analyze Blast Radius"**
5. Watch the animated progress → results Dashboard

**Expected output:**
| Field | Value |
|---|---|
| Risk level | 🔴 HIGH |
| Score | 14 |
| Reasons | Public API affected · DB migration required · Auth/security touched · 12 files · Frontend boundary · 38 tests |
| Evidence | 150+ findings |
| Impact tabs | Code (32) · API (36) · Database (35) · Frontend (9) · Tests (38) · History (1) |
| Graph | 14 nodes · 13 edges |
| Change plan | 7 ordered steps |

---

## 🔌 API Reference

### `POST /api/v1/analysis`
Submit a proposed change. Returns `analysis_id` immediately (202).

```json
{ "text": "Replace User.id from Integer to UUID", "repo": "sample-ecommerce" }
```

### `GET /api/v1/analysis/{id}/status`
Poll until `status` is `completed` or `failed`.

### `GET /api/v1/analysis/{id}`
Full result — summary, risk, impact, evidence, graph, change plan.

### `GET /api/v1/health`
Health check → `{ "status": "ok", "service": "changeblast" }`

---

## ⚙️ Risk Scoring

Fully deterministic — no LLM involved in the score calculation:

| Signal | +Points |
|---|---|
| Public API affected | +3 |
| Database migration needed | +3 |
| Auth / security path touched | +3 |
| 10+ dependent files | +2 |
| Frontend / backend boundary crossed | +2 |
| 10+ tests affected | +1 |

`0–3` → **LOW** · `4–7` → **MEDIUM** · `8+` → **HIGH**

---

## 📸 Screenshots

> _Add screenshots here after recording the demo._

| Home | Analysis Form | Dashboard |
|---|---|---|
| ![home](docs/screenshot-home.png) | ![form](docs/screenshot-form.png) | ![dashboard](docs/screenshot-dashboard.png) |

---

## 🏁 Hackathon Note

This is a **hackathon MVP**. The static analysis engine targets a seeded sample e-commerce repository. In a production version, it would support real repository ingestion, multi-language AST parsing, and a persistent database.