# 💥 ChangeBlast

> **See the blast radius before you change the code.**

ChangeBlast is a full-stack developer tool that analyzes a proposed code change *before* it is implemented and shows everything it will affect across a repository — impacted files, API contracts, database migrations, tests, risk level, and a step-by-step change plan.

Built as a hackathon MVP.

---

## ✨ What it does

1. You describe a proposed change in plain English (e.g. *"Replace User.id from Integer to UUID"*)
2. ChangeBlast scans the repository using static analysis
3. It finds every affected file, API route, database table, test, and frontend component
4. It calculates a deterministic risk score and explains why
5. It generates an ordered change plan you can follow immediately

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI · Uvicorn |
| Analysis | Custom static scan engine (no LLM required) |
| Storage | JSON file store (zero-config, session-persistent) |
| Frontend | React 18 · Vite |
| Graph | Pure SVG (no external graph library) |
| Styling | Vanilla CSS custom properties |

---

## 📁 Folder Structure

```
CHANGEBLAST/
├── backend/
│   ├── main.py                 # FastAPI app — API endpoints & background tasks
│   ├── analysis_engine.py      # Core pipeline: scan → evidence → risk → plan
│   ├── requirements.txt        # Python dependencies
│   └── sample_repo/            # Seeded e-commerce codebase (the demo target)
│       ├── models.py           # SQLAlchemy models: User, Order, Payment, UserSession
│       ├── users/              # User service + Pydantic schemas
│       ├── orders/             # Order service
│       ├── payments/           # Payment service
│       ├── auth/               # Auth & security utilities
│       ├── api/                # REST route definitions
│       ├── migrations/         # Database migration scripts
│       └── tests/              # Pytest test suite
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # All screens + components (single file)
│   │   └── index.css           # All styles
│   ├── index.html
│   ├── vite.config.js          # Dev server with /api proxy to backend
│   └── package.json
├── start.bat                   # Windows one-click launcher
├── start.ps1                   # PowerShell launcher
└── README.md
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --port 8000 --reload
```

Backend runs at **http://localhost:8000**
Swagger docs at **http://localhost:8000/docs**

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173** (proxies `/api` to the backend automatically)

### One-click (Windows)

```
start.bat
```

---

## 🎬 Primary Demo

1. Open **http://localhost:5173**
2. Click **"Analyze a Change"**
3. Click the demo pill → *"Replace User.id from Integer to UUID"*
4. Hit **"Analyze Blast Radius"**
5. Watch progress → Dashboard

**Expected result:**
- 🔴 Risk: **HIGH** (score 12)
- Reasons: *Public API affected · Database migration required · Auth/security path touched*
- 150+ evidence findings across code, API, DB, frontend, and tests
- 6-step ordered change plan

---

## 🔌 API Contract

### `POST /api/v1/analysis`

Submit a proposed change for analysis.

**Request:**
```json
{
  "text": "Replace User.id from Integer to UUID",
  "repo": "sample-ecommerce"
}
```

**Response (202 Accepted):**
```json
{
  "analysis_id": "cb_9492e010",
  "status": "queued"
}
```

---

### `GET /api/v1/analysis/{analysis_id}`

Retrieve the full analysis result once `status` is `completed`.

**Response (200 OK):**
```json
{
  "analysis_id": "cb_9492e010",
  "status": "completed",
  "request": { "text": "Replace User.id from Integer to UUID" },
  "summary": {
    "direct_files": 11,
    "indirect_files": 8,
    "api_contracts": 45,
    "database_migrations": 35,
    "tests_affected": 38
  },
  "risk": {
    "level": "HIGH",
    "score": 12,
    "reasons": [
      "Public API affected",
      "Database migration required",
      "Auth/security path touched",
      "12 dependent files affected",
      "38 tests affected"
    ]
  },
  "impact": {
    "code": [ { "file": "users/service.py", "line": 11, "description": "...", "evidence_id": "ev_001" } ],
    "api": [],
    "database": [],
    "frontend": [],
    "tests": [],
    "history": []
  },
  "graph": {
    "nodes": [ { "id": "core_user_id", "label": "User.id", "category": "core" } ],
    "edges": [ { "source": "core_user_id", "target": "db_users", "relationship": "migrates" } ]
  },
  "change_plan": [
    { "order": 1, "area": "database", "title": "Update database schema", "description": "..." }
  ],
  "evidence": [
    { "id": "ev_001", "source": "code", "file": "users/service.py", "line_start": 11, "line_end": 11,
      "relationship": "direct_dependency", "description": "Directly references User.id (Integer)" }
  ]
}
```

### `GET /api/v1/analysis/{analysis_id}/status`

Lightweight status poll: `queued` → `analyzing` → `completed` | `failed`

---

## ⚙️ Risk Scoring

Deterministic — no LLM involved in the score:

| Signal | Points |
|---|---|
| Public API affected | +3 |
| Database migration needed | +3 |
| Auth/security path touched | +3 |
| 10+ dependent files | +2 |
| Frontend/backend boundary crossed | +2 |
| 10+ affected tests | +1 |

`0–3 = LOW` · `4–7 = MEDIUM` · `8+ = HIGH`

---

## 🏁 Hackathon Note

This is a **hackathon MVP** — built for a single working demo. The static analysis targets the `sample_repo/` directory (a seeded e-commerce codebase). In a production version, this would be replaced with a real repo ingestion pipeline, multi-language AST parsing, and a proper database.
