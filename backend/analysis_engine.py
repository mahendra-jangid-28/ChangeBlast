"""
ChangeBlast Analysis Engine
Performs static search across the sample repo to find blast radius of a proposed change.
"""
import os
import re
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

# ---- Patterns for "Replace User.id from Integer to UUID" ----
# These are the signals we search for in the codebase.

SIGNAL_PATTERNS = {
    "user_id_usage": [
        r"\buser_id\b",
        r"\bUser\.id\b",
        r"users\.id",
        r"User\.id",
        r"user\.id",
    ],
    "fk_integer": [
        r"ForeignKey\(['\"]users\.id",
        r"Integer.*ForeignKey",
        r"user_id.*Integer",
        r"user_id.*int",
    ],
    "api_route": [
        r"user_id.*int",
        r"/users/\{user_id\}",
        r"user_id: int",
        r"user_id=int",
    ],
    "auth_path": [
        r"session.*user_id",
        r"user_id.*session",
        r"token.*user",
        r"jwt.*user",
        r"build_user_jwt",
        r"get_user_from_token",
        r"create_session_token",
    ],
    "test_reference": [
        r"test.*user.*id",
        r"user.*id.*int",
        r"user_id.*==",
        r"isinstance.*int",
    ],
    "migration": [
        r"migration",
        r"ALTER TABLE",
        r"MIGRATION",
        r"migrate",
    ],
    "frontend": [
        r"userId",
        r"user\.id",
        r"user_id",
        r"profile.*userId",
    ],
    "db_model": [
        r"Integer.*primary_key",
        r"Column.*Integer",
        r"INTEGER.*PRIMARY KEY",
    ],
}

# Map file path patterns to categories
# ORDER MATTERS: more-specific patterns must come before broader ones.
CATEGORY_MAP = {
    # Frontend takes priority over api/ prefix
    "frontend_components": "frontend",
    "components": "frontend",
    ".jsx": "frontend",
    ".tsx": "frontend",
    # Tests
    "tests/": "tests",
    "test_": "tests",
    # Database
    "migrations/": "database",
    "migration": "database",
    "models.py": "database",
    "schema.py": "database",
    # Auth (subset of api, but keep explicit)
    "auth/": "api",
    "security.py": "api",
    # API routes
    "routes.py": "api",
    "api/": "api",
    # Generic frontend keyword
    "frontend": "frontend",
}

REPO_DIR = Path(__file__).parent / "sample_repo"


def _read_file_lines(filepath: Path) -> List[str]:
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()
    except Exception:
        return []


def _get_category(filepath: str) -> str:
    """Determine impact category from file path."""
    normalized = filepath.replace("\\", "/")
    for pattern, category in CATEGORY_MAP.items():
        if pattern in normalized:
            return category
    if normalized.endswith(".py"):
        return "code"
    return "code"


def _scan_file(filepath: Path, repo_root: Path) -> List[Dict]:
    """Scan a single file for all signal patterns. Returns list of findings."""
    lines = _read_file_lines(filepath)
    if not lines:
        return []

    rel_path = str(filepath.relative_to(repo_root)).replace("\\", "/")
    findings = []
    found_lines = set()

    all_patterns = []
    for pattern_group, patterns in SIGNAL_PATTERNS.items():
        for pattern in patterns:
            all_patterns.append((pattern_group, pattern))

    for lineno, line in enumerate(lines, 1):
        for pattern_group, pattern in all_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                if lineno not in found_lines:
                    found_lines.add(lineno)
                    findings.append({
                        "file": rel_path,
                        "line_start": lineno,
                        "line_end": lineno,
                        "line_content": line.strip(),
                        "pattern_group": pattern_group,
                        "category": _get_category(rel_path),
                    })
                break  # one finding per line is enough

    return findings


def scan_repository(repo_dir: Path = None) -> List[Dict]:
    """Walk the sample repo and collect all signal findings."""
    if repo_dir is None:
        repo_dir = REPO_DIR

    findings = []
    for filepath in repo_dir.rglob("*.py"):
        # Skip __pycache__
        if "__pycache__" in str(filepath):
            continue
        findings.extend(_scan_file(filepath, repo_dir))

    return findings


def build_evidence(findings: List[Dict]) -> List[Dict]:
    """Convert raw scan findings into structured evidence items."""
    evidence = []
    seen = set()

    relationship_map = {
        "user_id_usage": "direct_dependency",
        "fk_integer": "direct_dependency",
        "api_route": "exposes",
        "auth_path": "references",
        "test_reference": "tests",
        "migration": "migrates",
        "frontend": "references",
        "db_model": "direct_dependency",
    }

    desc_map = {
        "user_id_usage": "Directly references User.id (Integer) — must be updated to UUID",
        "fk_integer": "Declares Integer FK to users.id — requires schema migration",
        "api_route": "API route parameter typed as int — must accept UUID string",
        "auth_path": "Authentication path stores/reads user_id as Integer",
        "test_reference": "Test asserts or uses User.id as Integer — will fail after UUID change",
        "migration": "Database migration script referencing integer user schema",
        "frontend": "Frontend component renders user.id as integer",
        "db_model": "Database model defines id as Integer primary key",
    }

    for i, f in enumerate(findings):
        key = (f["file"], f["line_start"])
        if key in seen:
            continue
        seen.add(key)

        ev_id = f"ev_{str(i + 1).zfill(3)}"
        evidence.append({
            "id": ev_id,
            "source": f["category"],
            "file": f["file"],
            "line_start": f["line_start"],
            "line_end": f["line_end"],
            "relationship": relationship_map.get(f["pattern_group"], "references"),
            "description": desc_map.get(f["pattern_group"], "References User.id"),
            "line_content": f["line_content"],
        })

    return evidence


def classify_impact(evidence: List[Dict]) -> Dict[str, List[Dict]]:
    """Group evidence items by impact category."""
    impact = {
        "code": [],
        "api": [],
        "database": [],
        "frontend": [],
        "tests": [],
        "history": [],
    }

    for ev in evidence:
        cat = ev["source"]
        if cat in impact:
            impact[cat].append({
                "file": ev["file"],
                "line": ev["line_start"],
                "description": ev["description"],
                "evidence_id": ev["id"],
                "relationship": ev["relationship"],
            })
        else:
            impact["code"].append({
                "file": ev["file"],
                "line": ev["line_start"],
                "description": ev["description"],
                "evidence_id": ev["id"],
                "relationship": ev["relationship"],
            })

    # Add a history item describing the change intent
    impact["history"].append({
        "file": "models.py",
        "line": 13,
        "description": "User.id was originally introduced as Integer PK in migration 001",
        "evidence_id": "ev_history_001",
        "relationship": "references",
    })

    return impact


def calculate_risk(impact: Dict[str, List], evidence: List[Dict]) -> Dict:
    """
    Deterministic risk scoring:
    Public API affected        +3
    Database migration needed  +3
    Auth/security path touched +3
    10+ dependent files        +2
    Frontend/backend boundary  +2
    10+ affected tests         +1
    0-3 = LOW, 4-7 = MEDIUM, 8+ = HIGH
    """
    score = 0
    reasons = []

    # Count unique files
    all_files = set(ev["file"] for ev in evidence)
    api_items = impact.get("api", [])
    db_items = impact.get("database", [])
    auth_items = [ev for ev in evidence if ev.get("source") == "api" and
                  any(kw in ev["description"].lower() for kw in ["auth", "security", "session", "token", "jwt"])]
    test_items = impact.get("tests", [])
    frontend_items = impact.get("frontend", [])

    if len(api_items) > 0:
        score += 3
        reasons.append("Public API affected")

    if len(db_items) > 0:
        score += 3
        reasons.append("Database migration required")

    if len(auth_items) > 0:
        score += 3
        reasons.append("Auth/security path touched")

    if len(all_files) >= 10:
        score += 2
        reasons.append(f"{len(all_files)} dependent files affected")

    if len(frontend_items) > 0:
        score += 2
        reasons.append("Frontend/backend boundary crossed")

    if len(test_items) >= 10:
        score += 1
        reasons.append(f"{len(test_items)} tests affected")

    if score <= 3:
        level = "LOW"
    elif score <= 7:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {
        "level": level,
        "score": score,
        "reasons": reasons,
    }


def build_summary(impact: Dict, evidence: List[Dict]) -> Dict:
    """Build summary counts for the analysis."""
    all_files = set(ev["file"] for ev in evidence)
    direct = [ev for ev in evidence if ev["relationship"] == "direct_dependency"]
    indirect = [ev for ev in evidence if ev["relationship"] != "direct_dependency"]

    return {
        "direct_files": len(set(ev["file"] for ev in direct)),
        "indirect_files": len(set(ev["file"] for ev in indirect)),
        "api_contracts": len(impact.get("api", [])),
        "database_migrations": len(impact.get("database", [])),
        "tests_affected": len(impact.get("tests", [])),
    }


def build_graph(impact: Dict, evidence: List[Dict]) -> Dict:
    """Build a simple node/edge graph for visualization."""
    nodes = []
    edges = []
    node_ids = set()

    # Core node — the change itself
    nodes.append({
        "id": "core_user_id",
        "label": "User.id",
        "category": "core",
        "description": "Integer → UUID (proposed change)",
    })
    node_ids.add("core_user_id")

    # DB node
    nodes.append({
        "id": "db_users",
        "label": "users table",
        "category": "database",
        "description": "Primary key column changes type",
    })
    edges.append({"source": "core_user_id", "target": "db_users", "relationship": "migrates"})
    node_ids.add("db_users")

    # Add nodes for each unique file in evidence
    for ev in evidence:
        node_id = ev["file"].replace("/", "_").replace(".", "_")
        if node_id not in node_ids:
            node_ids.add(node_id)
            cat = ev["source"]
            nodes.append({
                "id": node_id,
                "label": ev["file"].split("/")[-1],
                "category": cat,
                "description": ev["description"],
                "file": ev["file"],
            })

        edge_rel = ev["relationship"]
        edges.append({
            "source": "core_user_id",
            "target": node_id,
            "relationship": edge_rel,
        })

    # Deduplicate edges
    seen_edges = set()
    deduped_edges = []
    for e in edges:
        key = (e["source"], e["target"])
        if key not in seen_edges:
            seen_edges.add(key)
            deduped_edges.append(e)

    return {"nodes": nodes, "edges": deduped_edges}


def build_change_plan(impact: Dict, risk: Dict) -> List[Dict]:
    """Generate an ordered, phased change plan."""
    plan = []
    order = 1

    plan.append({
        "order": order,
        "area": "database",
        "title": "Update database schema",
        "description": "Create a migration that adds a UUID column to the users table, backfills all existing rows, then updates all foreign key columns (orders.user_id, payments.user_id, user_sessions.user_id) to reference the new UUID. Run migration on staging first.",
    })
    order += 1

    if impact.get("api"):
        plan.append({
            "order": order,
            "area": "api",
            "title": "Update API routes and schemas",
            "description": "Change all route path parameters from `int` to `str` (UUID). Update Pydantic schemas: UserResponse.id, UserCreate, UserUpdate. Update OpenAPI spec and notify API consumers.",
        })
        order += 1

    plan.append({
        "order": order,
        "area": "code",
        "title": "Update service layer",
        "description": "Change `get_user_by_id`, `update_user`, `delete_user` to accept `str` UUID instead of `int`. Update all FK references in OrderService and PaymentService.",
    })
    order += 1

    if impact.get("api") and any("auth" in item["description"].lower() or "session" in item["description"].lower()
                                  for item in impact["api"]):
        plan.append({
            "order": order,
            "area": "api",
            "title": "Update auth/session handling",
            "description": "Update `create_session_token`, `get_user_from_token`, and `build_user_jwt_payload` to use UUID string instead of Integer. The JWT 'sub' claim format changes from '42' to '550e8400-...'.",
        })
        order += 1

    if impact.get("frontend"):
        plan.append({
            "order": order,
            "area": "frontend",
            "title": "Update frontend components",
            "description": "Update UserCard, OrderHistory, and UserProfileLink to treat userId as a string UUID. Remove any parseInt() calls. Update URL patterns that rely on numeric user IDs.",
        })
        order += 1

    if impact.get("tests"):
        plan.append({
            "order": order,
            "area": "tests",
            "title": "Update and run test suite",
            "description": "Update all test fixtures from integer user IDs (e.g. user.id = 42) to UUID format. Fix `isinstance(user.id, int)` assertions. Re-run the full test suite and confirm green.",
        })
        order += 1

    plan.append({
        "order": order,
        "area": "code",
        "title": "Deploy and verify",
        "description": "Deploy in order: database migration → backend → frontend. Monitor error logs for any Integer/UUID type mismatch errors. Verify auth flows, order creation, and payment processing end-to-end.",
    })

    return plan


def run_analysis(change_text: str, analysis_id: str) -> Dict:
    """
    Full analysis pipeline. Returns the complete response contract.
    """
    # 1. Scan repo
    raw_findings = scan_repository()

    # 2. Build evidence
    evidence = build_evidence(raw_findings)

    # 3. Classify impact
    impact = classify_impact(evidence)

    # 4. Risk scoring
    risk = calculate_risk(impact, evidence)

    # 5. Summary
    summary = build_summary(impact, evidence)

    # 6. Graph
    graph = build_graph(impact, evidence)

    # 7. Change plan
    change_plan = build_change_plan(impact, risk)

    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "request": {"text": change_text},
        "summary": summary,
        "risk": risk,
        "impact": impact,
        "graph": graph,
        "change_plan": change_plan,
        "evidence": evidence,
    }
