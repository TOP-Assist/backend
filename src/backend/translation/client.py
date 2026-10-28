# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Module for clients that handle communication with LLM inference providers."""

from abc import ABC

from openai import (
    APIConnectionError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
)
from pydantic import ValidationError

from backend.translation.errors import (
    TranslationOutputError,
    TranslationProviderError,
    TranslationTimeoutError,
    TranslationUnavailableError,
)
from backend.translation.schemas import LLMAnswer


class TranslationClient(ABC):
    """An abstract base which all LLM client implementations should follow."""

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> LLMAnswer: ...


class OpenAICompatibleTranslationClient:
    def __init__(
        self,
        sdk: AsyncOpenAI,
        *,
        model: str,
        temperature: float = 0.0,
    ) -> None:
        self._sdk = sdk
        self._model = model
        self._temperature = temperature

    async def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> LLMAnswer:
        try:
            completion = await self._sdk.chat.completions.create(
                model=self._model,
                temperature=self._temperature,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": input_text},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "LLMAnswer",
                        "strict": True,
                        "schema": LLMAnswer.model_json_schema(),
                    },
                },
            )
        except APITimeoutError as exc:
            raise TranslationTimeoutError(
                "The translation provider timed out"
            ) from exc
        except APIConnectionError as exc:
            raise TranslationUnavailableError(
                "Cannot connect to the translation provider"
            ) from exc
        except APIResponseValidationError as exc:
            raise TranslationOutputError(
                "The provider returned an invalid response envelope"
            ) from exc
        except APIStatusError as exc:
            if exc.status_code == 429 or exc.status_code >= 500:
                raise TranslationUnavailableError(
                    "The translation provider is temporarily unavailable"
                ) from exc

            raise TranslationProviderError(
                "The translation provider rejected the request"
            ) from exc

        if not completion.choices:
            raise TranslationOutputError("The provider returned no completion")

        choice = completion.choices[0]
        message = choice.message

        if message.refusal:
            raise TranslationOutputError(
                "The provider declined to generate a translation"
            )

        if choice.finish_reason != "stop":
            raise TranslationOutputError(
                "The provider did not complete the translation normally"
            )

        if not message.content:
            raise TranslationOutputError(
                "The provider returned no translation content"
            )

        try:
            answer = LLMAnswer.model_validate_json(
                message.content,
                strict=True,
            )
        except ValidationError as exc:
            raise TranslationOutputError(
                "The translation does not match the expected schema"
            ) from exc

        if not answer.title.strip() or not answer.optimized.strip():
            raise TranslationOutputError(
                "The translation contains empty required content"
            )

        return answer
