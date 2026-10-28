# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Components to be used for Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from backend.infra.mongo import MongoDBDep
from backend.parlance.service import ParlanceService


async def get_parlance_service(db: MongoDBDep) -> ParlanceService:
    return ParlanceService(collection=db["parlance"])


ParlanceServiceDep = Annotated[
    ParlanceService,
    Depends(get_parlance_service),
]
