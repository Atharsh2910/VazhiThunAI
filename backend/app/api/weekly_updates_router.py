"""
Weekly Updates Router
======================
New isolated router — registered in main.py alongside the existing routers.
Does NOT modify any existing router.

Endpoint:
    GET /api/v1/weekly-updates?career_path=Data%20Scientist

Returns APIResponse-shaped JSON consistent with the rest of the project.
All errors are caught and returned as graceful failure responses — never crashes.
"""

import uuid
import logging
from typing import Dict, Any

from fastapi import APIRouter, Query

from app.schemas.base import APIResponse, MetaResponse, ErrorResponse
from app.services.weekly_updates_service import get_weekly_updates

logger = logging.getLogger(__name__)

weekly_updates_router = APIRouter()


@weekly_updates_router.get(
    "/weekly-updates",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get weekly career updates for a given career path",
    tags=["Weekly Updates"],
)
def get_weekly_updates_endpoint(
    career_path: str = Query(
        default="Machine Learning Engineer",
        description="The learner's target career path (e.g. 'Data Scientist')",
        min_length=2,
        max_length=200,
    )
):
    """
    Fetch recent, relevant industry updates for the specified career path.

    - Calls GNews API for real recent articles (last 7 days)
    - Filters and ranks by relevance
    - Uses Groq to generate 2-3 sentence summaries + "why it matters"
    - Results cached per career path for 6 hours

    Returns structured update objects or a graceful error if the external API
    is unavailable.
    """
    request_id = str(uuid.uuid4())

    try:
        data = get_weekly_updates(career_path=career_path)

        return APIResponse(
            success=True,
            data=data,
            meta=MetaResponse(request_id=request_id),
        )

    except RuntimeError as e:
        # Expected: missing API key, GNews unavailable, etc.
        logger.warning(f"Weekly updates unavailable for '{career_path}': {e}")
        return APIResponse(
            success=False,
            data={
                "career_path": career_path,
                "period": "",
                "updates": [],
            },
            error=ErrorResponse(
                code="WEEKLY_UPDATES_UNAVAILABLE",
                message=str(e),
            ),
            meta=MetaResponse(request_id=request_id),
        )

    except Exception as e:
        # Unexpected errors — log fully but never expose internals to client
        logger.exception(f"Unexpected error in weekly-updates for '{career_path}': {e}")
        return APIResponse(
            success=False,
            data={
                "career_path": career_path,
                "period": "",
                "updates": [],
            },
            error=ErrorResponse(
                code="INTERNAL_ERROR",
                message="Weekly updates are temporarily unavailable. Please try again later.",
            ),
            meta=MetaResponse(request_id=request_id),
        )
