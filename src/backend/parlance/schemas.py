# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Object definitions for parlance functionality."""

from limes import PartOfSpeechTag
from pydantic import BaseModel


class ParlanceWord(BaseModel):
    """
    A word that holds special meaning in the given domain of the text.
    """

    word: str
    pos_tag: PartOfSpeechTag
