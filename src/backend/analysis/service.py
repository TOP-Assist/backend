"""Service class for text analysis functionality."""

from limes import Sentence, Text
from limes.analyzers.base import BaseAnalyzer
from limes.parsers import Parser
from limes.protocols import TokenProtocol

from backend.analysis.schemas import (
    AnalysisResult,
    BarrierDescription,
    BarrierTokenHighlight,
    TokenHighlight,
)
from backend.parlance.schemas import ParlanceWord


class AnalysisService:
    def __init__(self, parser: Parser, analyzer: BaseAnalyzer) -> None:
        self._parser = parser
        self._analyzer = analyzer

    def get_barrier_definitions(self) -> list[BarrierDescription]:
        """
        Retrieve a static list of barrier definitions for all barriers supported
        by the registered analyzer.
        """
        return [
            BarrierDescription(
                title=barrier.title,
                description=barrier.description,
            )
            for barrier in self._analyzer.supported_barriers
        ]

    def analyze(
        self,
        text: str,
        *,
        check_barriers: bool = True,
        parlance_words: list[ParlanceWord] | None = None,
    ) -> AnalysisResult:
        """
        Analyze a given text for either barriers, parlance words, or both.
        """
        if not check_barriers and parlance_words is None:
            raise ValueError("At least one analysis operation is required")

        barriers: list[BarrierTokenHighlight] | None = (
            [] if check_barriers else None
        )
        parlance: list[TokenHighlight] | None = (
            [] if parlance_words is not None else None
        )

        # No parsing is needed for an empty-lexicon-only request.
        if not check_barriers and not parlance_words:
            return AnalysisResult(
                text=text,
                barriers=barriers,
                parlance=parlance,
            )

        analyzed = Text(
            raw=text,
            parser=self._parser,
            analyzer=self._analyzer,
        )

        search_from = 0
        next_barrier_number = 1

        for sentence in analyzed.sentences:
            sentence_text = str(sentence)
            start = text.find(sentence_text, search_from)

            if start < 0:
                raise RuntimeError("Cannot align sentence with input")

            search_from = start + len(sentence_text)

            if barriers is not None:
                findings, next_barrier_number = self._find_barriers(
                    sentence,
                    sentence_start=start,
                    first_barrier_number=next_barrier_number,
                )
                barriers.extend(findings)

            if parlance is not None and parlance_words:
                parlance.extend(
                    self._find_parlance(
                        sentence,
                        sentence_start=start,
                        words=parlance_words,
                    )
                )

        return AnalysisResult(
            text=text,
            barriers=barriers,
            parlance=parlance,
        )

    def _find_barriers(
        self,
        sentence: Sentence,
        *,
        sentence_start: int,
        first_barrier_number: int,
    ) -> tuple[list[BarrierTokenHighlight], int]:
        """Return token highlights and the next available barrier number."""
        highlights: list[BarrierTokenHighlight] = []
        next_number = first_barrier_number
        sentence_text = str(sentence)

        for barrier in sentence.barriers or ():
            if barrier.affected_tokens is None:
                continue

            occurrence: list[BarrierTokenHighlight] = []

            for token in sorted(
                barrier.affected_tokens,
                key=lambda item: item.i,
            ):
                position = self._locate_token(
                    token,
                    sentence_text=sentence_text,
                    sentence_start=sentence_start,
                )
                if position is None:
                    continue

                start, end = position
                occurrence.append(
                    BarrierTokenHighlight(
                        title=barrier.title,
                        description=barrier.description,
                        suggestion=barrier.suggested_improvement,
                        barrier_number=next_number,
                        start=start,
                        end=end,
                        token=str(token),
                    )
                )

            if occurrence:
                highlights.extend(occurrence)
                next_number += 1

        return highlights, next_number

    def _find_parlance(
        self,
        sentence: Sentence,
        *,
        sentence_start: int,
        words: list[ParlanceWord],
    ) -> list[TokenHighlight]:
        """Return unique matching token spans in source order."""
        highlights: dict[tuple[int, int], TokenHighlight] = {}
        sentence_text = str(sentence)

        for word in words:
            matches = sentence.find(
                word=word.word,
                pos=word.pos_tag,
            )

            for token in matches or ():
                position = self._locate_token(
                    token,
                    sentence_text=sentence_text,
                    sentence_start=sentence_start,
                )
                if position is None:
                    continue

                start, end = position
                highlights[position] = TokenHighlight(
                    start=start,
                    end=end,
                    token=str(token),
                )

        return [highlights[position] for position in sorted(highlights)]

    @staticmethod
    def _locate_token(
        token: TokenProtocol,
        *,
        sentence_text: str,
        sentence_start: int,
    ) -> tuple[int, int] | None:
        """Convert a sentence-local token offset to a text-global span."""
        token_text = str(token)

        # Preserves the old application's highlighting policy.
        if not any(character.isalpha() for character in token_text):
            return None

        local_start = token._token.idx  # pyright: ignore[reportAttributeAccessIssue]
        local_end = local_start + len(token_text)

        if (
            sentence_start < 0
            or local_start < 0
            or local_end > len(sentence_text)
            or sentence_text[local_start:local_end] != token_text
        ):
            raise RuntimeError("Cannot align analyzed token with input")

        return (
            sentence_start + local_start,
            sentence_start + local_end,
        )
