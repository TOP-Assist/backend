# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Components to be used for Dependency Injection."""

from typing import Annotated

from fastapi import Depends, Request

from backend.analysis.executor import AnalysisExecutor
from backend.validation.service import ValidationService
from backend.infra.mongo import MongoDBDep

def get_analysis_executor(request: Request) -> AnalysisExecutor:
    return request.app.state.analysis_executor

async def get_validation_service(
    db: MongoDBDep,
    analysis_executor: Annotated[AnalysisExecutor, Depends(get_analysis_executor)]
) -> ValidationService:
    return ValidationService(
        collection=db["validation"],
        analysis_executor=analysis_executor
    )


ValidationServiceDep = Annotated[
    ValidationService,
    Depends(get_validation_service),
]
