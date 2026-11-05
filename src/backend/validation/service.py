# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later
import uuid
from typing import Callable, TypeVar

from backend.validation.schemas import ValidationResult, TranslationValidation
from pymongo.asynchronous.collection import AsyncCollection
from backend.validation.validators.base import Validator, ValidatorResult

ValidatorType = TypeVar("ValidatorType", bound=type[Validator])

class ValidationService:
    """Service for validating a translation after it was generated."""
    _registry: dict[str, tuple[ValidatorType, bool]] = {}

    @classmethod
    def register(cls, name: str, enabled: bool) -> Callable[[ValidatorType], ValidatorType]:
        """Registry decorator, used to decorate validator metrics to include them in validation."""
        def decorator(validator_cls: ValidatorType) -> ValidatorType:
            if name in cls._registry:
                raise ValueError(f"Validator {name} already registered")
            if not issubclass(validator_cls, Validator):
                raise TypeError(f"Validator {name} must be a subclass of Validator")

            cls._registry[name] = (validator_cls, enabled)
            return validator_cls

        return decorator

    def __init__(self, collection: AsyncCollection):
        self.validators: dict[str, Validator] = {
            validator_name: validator()
            for validator_name, (validator, enabled) in self._registry.values() if enabled
        }
        self._collection = collection

    async def run(self, inp: str, out: str) -> str:
        results = {}
        for validator_name, validator in self.validators.items():
            score, meta = await validator.run(inp, out)
            validator_result = ValidationResult(metric=validator_name, score=score, meta=meta)
            results[validator_name] = validator_result

        validation_result = TranslationValidation(
            translation_id=uuid.uuid4().hex,
            results=results
        )

        result = await self._collection.insert_one(validation_result.model_dump())
        return result.inserted_id