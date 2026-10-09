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
    ) -> None:
        self._client = client

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
