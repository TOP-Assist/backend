# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Components to be used for Dependency Injection."""

from typing import Annotated, cast

from fastapi import Depends, Request

from backend.translation.service import TranslationService


async def get_translation_service(
    request: Request,
) -> TranslationService:
    return cast(
        TranslationService,
        request.app.state.translation_service,
    )


TranslationServiceDep = Annotated[
    TranslationService,
    Depends(get_translation_service),
]
