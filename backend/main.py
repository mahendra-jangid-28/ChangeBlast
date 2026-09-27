"""
ChangeBlast API — FastAPI application
"""
import uuid
import json
import time
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from analysis_engine import run_analysis

# ---- Storage (simple JSON file store) ----

STORE_DIR = Path(__file__).parent / ".store"
STORE_DIR.mkdir(exist_ok=True)


def _store_path(analysis_id: str) -> Path:
    return STORE_DIR / f"{analysis_id}.json"


def save_analysis(data: dict) -> None:
    with open(_store_path(data["analysis_id"]), "w") as f:
        json.dump(data, f, default=str)


def load_analysis(analysis_id: str) -> Optional[dict]:
    path = _store_path(analysis_id)
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def update_status(analysis_id: str, status: str) -> None:
    data = load_analysis(analysis_id)
    if data:
        data["status"] = status
        save_analysis(data)


# ---- FastAPI App ----

app = FastAPI(
    title="ChangeBlast API",
    description="See the blast radius before you change the code.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Request/Response Models ----

class AnalysisRequest(BaseModel):
    text: str
    repo: Optional[str] = "sample-ecommerce"


# ---- Background worker ----

def _run_analysis_task(analysis_id: str, change_text: str):
    """Run analysis in background, update status on completion."""
    try:
        update_status(analysis_id, "analyzing")
        time.sleep(0.5)  # Brief pause to show "analyzing" state in UI
        result = run_analysis(change_text, analysis_id)
        result["status"] = "completed"
        save_analysis(result)
    except Exception as e:
        stub = load_analysis(analysis_id)
        if stub:
            stub["status"] = "failed"
            stub["error"] = str(e)
            save_analysis(stub)


# ---- Routes ----

@app.post("/api/v1/analysis", status_code=202)
async def create_analysis(payload: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Submit a proposed change for analysis.
    Returns immediately with analysis_id; use GET to poll for results.
    """
    analysis_id = f"cb_{uuid.uuid4().hex[:8]}"

    # Save initial stub so GET works immediately
    stub = {
        "analysis_id": analysis_id,
        "status": "queued",
        "request": {"text": payload.text},
        "summary": {},
        "risk": {},
        "impact": {"code": [], "api": [], "database": [], "frontend": [], "tests": [], "history": []},
        "graph": {"nodes": [], "edges": []},
        "change_plan": [],
        "evidence": [],
    }
    save_analysis(stub)

    background_tasks.add_task(_run_analysis_task, analysis_id, payload.text)

    return {"analysis_id": analysis_id, "status": "queued"}


@app.get("/api/v1/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Retrieve analysis by ID. Returns full result when status=completed."""
    data = load_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    return data


@app.get("/api/v1/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """Lightweight status check endpoint."""
    data = load_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    return {
        "analysis_id": analysis_id,
        "status": data["status"],
    }


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "changeblast"}


# ---- Serve React frontend (production) ----
FRONTEND_BUILD = Path(__file__).parent.parent / "frontend" / "dist"
if FRONTEND_BUILD.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_BUILD / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        index = FRONTEND_BUILD / "index.html"
        if index.exists():
            return FileResponse(str(index))
        raise HTTPException(status_code=404, detail="Frontend not built")
