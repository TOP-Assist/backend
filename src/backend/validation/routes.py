

import logging

from backend.validation.deps import ValidationServiceDep
from backend.validation.schemas import ValidationRequest, TranslationValidation

from fastapi import APIRouter, HTTPException


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/validation", tags=["validation"])

@router.post(
    ""
)
async def post_validation(
    body: ValidationRequest,
    service: ValidationServiceDep,
) -> TranslationValidation:
    # TODO: Do we want to control metrics per-prompt? If not, this is not needed.
    assert body.selected_validators == "all",\
        "Selecting a subset of validators is not supported yet."

    try:
        return await service.run(body.input_text, body.output_text)
    except Exception as e: # TODO: Less generic
        logger.warning(f"An error occured: {e}")
        raise HTTPException(status_code=404, detail="An error occured") from e