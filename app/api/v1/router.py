"""
API v1 — top-level router.

New endpoint routers should be imported here and included with a prefix and
a list of tags so they appear correctly in the OpenAPI docs.

Example:
    from app.api.v1.endpoints import analysis
    router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
"""

from fastapi import APIRouter

router = APIRouter()

# ── Endpoint routers ──────────────────────────────────────────────────────────
# TODO: include endpoint routers as they are implemented.
# router.include_router(some_router, prefix="/some-resource", tags=["some-resource"])
