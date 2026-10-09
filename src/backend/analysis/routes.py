"""HTTP route definitions for text analysis functionality."""

from fastapi import APIRouter, HTTPException

from backend.analysis.deps import AnalysisExecutorDep
from backend.analysis.errors import AnalysisBusyError
from backend.analysis.schemas import (
    AnalysisRequest,
    AnalysisResult,
    BarrierDescription,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post(
    "",
    responses={
        503: {"description": "Analysis workers are currently at capacity."}
    },
)
async def post_analysis(
    executor: AnalysisExecutorDep,
    body: AnalysisRequest,
) -> AnalysisResult:
    try:
        return await executor.analyze(
            body.text,
            body.parlance_words,
            body.check_barriers,
        )
    except AnalysisBusyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Analysis is currently at capacity. Please retry.",
        ) from exc


@router.get("/barriers")
def get_barrier_definitions(
    executor: AnalysisExecutorDep,
) -> list[BarrierDescription]:
    return executor.get_barrier_definitions()
