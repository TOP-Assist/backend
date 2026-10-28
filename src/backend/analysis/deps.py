# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Components to be used for Dependency Injection."""

from typing import Annotated, cast

from fastapi import Depends, Request

from backend.analysis.executor import AnalysisExecutor


async def get_analysis_executor(
    request: Request,
) -> AnalysisExecutor:
    return cast(
        AnalysisExecutor,
        request.app.state.analysis_executor,
    )


AnalysisExecutorDep = Annotated[
    AnalysisExecutor,
    Depends(get_analysis_executor),
]
