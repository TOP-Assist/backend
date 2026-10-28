# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""HTTP route definitions for translation/text simplification functionality."""

import logging

from fastapi import APIRouter, HTTPException

from backend.translation.deps import TranslationServiceDep
from backend.translation.errors import (
    TranslationOutputError,
    TranslationProviderError,
    TranslationTimeoutError,
    TranslationUnavailableError,
)
from backend.translation.schemas import TranslationRequest, TranslationResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/translation", tags=["translation"])


@router.post(
    "",
    responses={
        502: {"description": "LLM provider failure."},
        503: {"description": "LLM temporarily unavailable."},
        504: {"description": "LLM provider timed out."},
    },
)
async def post_translation(
    body: TranslationRequest,
    service: TranslationServiceDep,
) -> TranslationResult:
    try:
        return await service.translate(
            body.text,
            barriers=body.barriers,
            parlance_words=body.parlance_words,
        )
    except TranslationTimeoutError as exc:
        logger.warning("Translation provider timed out.")
        raise HTTPException(
            status_code=504,
            detail={
                "code": "translation_timeout",
                "message": "The translation provider timed out.",
            },
        ) from exc
    except TranslationUnavailableError as exc:
        logger.warning("Translation provider unavailable.")
        raise HTTPException(
            status_code=503,
            detail={
                "code": "translation_unavailable",
                "message": "Translation is temporarily unavailable.",
            },
        ) from exc
    except TranslationOutputError as exc:
        logger.error("Translation provider returned unusable output.")
        raise HTTPException(
            status_code=502,
            detail={
                "code": "translation_invalid_output",
                "message": "The provider returned an unusable translation.",
            },
        ) from exc
    except TranslationProviderError as exc:
        logger.error("Translation provider rejected the backend request.")
        raise HTTPException(
            status_code=502,
            detail={
                "code": "translation_provider_error",
                "message": "The LLM provider could not fulfill the request.",
            },
        ) from exc
