# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from typing import Callable, TypeVar, Any, Optional

from backend.validation.schemas import ValidationResult, TranslationValidation
from pymongo.asynchronous.collection import AsyncCollection
from backend.validation.validators.base import Validator

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
            for validator_name, (validator, enabled) in self._registry.items() if enabled
        }
        self._collection = collection

    async def run(self, inp: str, out: str, meta: Optional[dict[str, Any]] = None) -> TranslationValidation:
        results = {
            validator_name: await validator.run(inp, out, meta)
            for validator_name, validator in self.validators.items()
        }

        validation_result = TranslationValidation(
            results=results
        )

        result = await self._collection.insert_one(validation_result.model_dump())

        validation_result.inserted_id = str(result.inserted_id)
        return validation_result
