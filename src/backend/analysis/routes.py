"""HTTP route definitions for text analysis functionality."""

from fastapi import APIRouter

from backend.analysis.schemas import (
    AnalysisRequest,
    AnalysisResult,
    BarrierDescription,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("")
async def post_analysis(request: AnalysisRequest) -> AnalysisResult:
    """Perform barrier analysis on the provided text."""
    # TODO: Implement analysis logic.
    raise NotImplementedError


@router.get("/barriers")
def get_barrier_definitions() -> list[BarrierDescription]:
    """Get all available linguistic barriers from the analyzer."""
    # TODO: Implement barrier-getting logic.
    raise NotImplementedError
