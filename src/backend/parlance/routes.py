"""HTTP route definitions for parlance word functionality."""

from fastapi import APIRouter

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
def get_parlance(domain: str, min_freq: int = 0) -> list[ParlanceWord]:
    """
    Get a list of words (defined by their lemma and part-of-speech tag) that are
    considered parlance in a given domain.
    """
    # TODO: Implement Parlance-Getting function.
    raise NotImplementedError


@router.get("/domains")
def get_domains() -> list[str]:
    """
    Get a list of all domains for which we currently provide curated parlance
    information.
    """
    # TODO: Implement Domain-Getting function.
    raise NotImplementedError
