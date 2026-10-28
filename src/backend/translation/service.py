# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Service class for translation/text simplification functionality."""

from collections.abc import Sequence

from backend.analysis.schemas import BarrierTokenHighlight
from backend.translation.client import TranslationClient
from backend.translation.schemas import TranslationResult, TranslationStrategy
from backend.translation.strategies import default


class TranslationService:
    def __init__(
        self,
        client: TranslationClient,
        *,
        prompt_variant: str = "default",
    ) -> None:
        self._client = client
        # Resolve prompts up front so a misconfigured variant fails at startup.
        self._default_prompt = default.get_prompt(prompt_variant)

    async def translate(
        self,
        text: str,
        *,
        barriers: Sequence[BarrierTokenHighlight] | None = None,
        parlance_words: Sequence[str] | None = None,
        strategy: TranslationStrategy = TranslationStrategy.DEFAULT,
    ) -> TranslationResult:
        match strategy:
            case TranslationStrategy.DEFAULT:
                instructions = default.prepare(
                    self._default_prompt,
                    barriers=barriers or (),
                    parlance_words=parlance_words or (),
                )

        response = await self._client.generate(
            instructions=instructions,
            input_text=text,
        )

        return TranslationResult(
            title=response.title,
            optimized=response.optimized,
            explanation=response.explanation,
            answer=response.answer,
            strategy_used=strategy,
        )
