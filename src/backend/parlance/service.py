# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Service class for parlance functionality."""

import logging

from pymongo.asynchronous.collection import AsyncCollection

from backend.parlance.errors import ParlanceNotFoundError
from backend.parlance.schemas import ParlanceWord

logger = logging.getLogger(__name__)


class ParlanceService:
    """Business logic for interacting with parlance data."""

    def __init__(self, collection: AsyncCollection):
        self._collection = collection

    async def get_parlance(
        self, domain: str, min_freq: int
    ) -> list[ParlanceWord]:
        """
        Retrieve all parlance words for a domain that match the frequency
        criterion.

        Raises
        ------
        ParlanceNotFoundError: If no parlance is found for the given domain.
        """
        query = {
            "domain": domain,
            "frequency": {"$gte": min_freq},
        }
        projection = {"_id": 0, "lemma": 1, "pos": 1}
        logger.debug("Running query %s against database.", query)
        entries = [
            ParlanceWord(word=doc["lemma"], pos_tag=doc["pos"])
            async for doc in self._collection.find(query, projection)
        ]
        if not entries:
            raise ParlanceNotFoundError(domain)
        return entries
