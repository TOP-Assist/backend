# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""HTTP route definitions for parlance word functionality."""

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException

from backend.parlance.deps import ParlanceServiceDep
from backend.parlance.errors import ParlanceNotFoundError
from backend.parlance.schemas import ParlanceWord

router = APIRouter(prefix="/parlance", tags=["parlance"])


@router.get(
    "",
    responses={
        404: {
            "description": "Could not find any parlance for the given domain."
        }
    },
)
async def get_parlance(
    service: ParlanceServiceDep,
    domain: str,
    min_freq: int = 0,
) -> list[ParlanceWord]:
    """
    Get a list of words (defined by their lemma and part-of-speech tag) that are
    considered parlance in a given domain.
    """
    try:
        return await service.get_parlance(domain, min_freq)
    except ParlanceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Could not find any parlance for the given domain.",
        ) from exc


@router.get("/domains")
def get_domains(request: Request) -> list[str]:
    """
    Get a list of all domains for which we currently provide curated parlance
    information.
    """
    return request.app.state.domains
