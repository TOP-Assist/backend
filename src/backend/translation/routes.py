"""HTTP route definitions for translation/text simplification functionality."""

from fastapi import APIRouter

from backend.translation.schemas import TranslationRequest, TranslationResult

router = APIRouter(prefix="/translation", tags=["translation"])


@router.post(
    "",
    responses={
        503: {"description": "The LLM provider could not process the request."},
    },
)
async def post_translation(request: TranslationRequest) -> TranslationResult:
    """
    Perform text simplification on the given text.
    """
    # TODO: Implement translation logic.
    raise NotImplementedError
