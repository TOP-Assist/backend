# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

from fastapi import APIRouter, HTTPException

from backend.validation.deps import ValidationServiceDep
from backend.validation.schemas import TranslationValidation, ValidationRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/validation", tags=["validation"])


@router.post("")
async def post_validation(
    body: ValidationRequest,
    service: ValidationServiceDep,
) -> TranslationValidation:
    try:
        return await service.run(body)
    except Exception as e:  # TODO: Less generic
        logger.warning(f"An error occurred: {e}")
        raise HTTPException(status_code=404, detail="An error occured") from e
