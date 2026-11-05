# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Components to be used for Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from backend.validation.service import ValidationService
from backend.infra.mongo import MongoDBDep


async def get_validation_service(db: MongoDBDep) -> ValidationService:
    return ValidationService(collection=db["validation"])


ValidationServiceDep = Annotated[
    ValidationService,
    Depends(get_validation_service),
]
