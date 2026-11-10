# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import logging
from typing import Callable, TypeVar

from pymongo.asynchronous.collection import AsyncCollection

from backend.validation.schemas import TranslationValidation, ValidationRequest
from backend.validation.validators.base import Validator


logger = logging.getLogger(__name__)

ValidatorType = TypeVar("ValidatorType", bound=type[Validator])

class ValidationService:
    """
    Service for validating a translation after it was generated.

    Each validator is registered to `self._registry` using the register decorator
    and a unique identifier ("name") before initialization.

    Upon initialization of the service, parametrized validators are initialized
    from resources/validator_config.json.
    """
    _registry: dict[str, ValidatorType] = {}

    @classmethod
    def register(cls) -> Callable[[ValidatorType], ValidatorType]:
        """Registry decorator, used to decorate validator metrics to include them in validation."""
        def decorator(validator_cls: ValidatorType) -> ValidatorType:
            name = validator_cls.__name__
            if not issubclass(validator_cls, Validator):
                logger.error(f"Validator {name} must be a subclass of Validator")

            cls._registry[name] = validator_cls
            return validator_cls

        return decorator

    def __init__(self, collection: AsyncCollection):
        self._collection = collection

        with open("src/backend/validation/resources/validator_config.json", "r") as f:
            validator_config = json.load(f)

        self.validators = {}
        for k, v in validator_config.items():
            validator_id = v.pop("validator_id")
            if validator_id not in self._registry:
                logging.error(f"Validator {validator_id} not found in registry.")
                continue
            validator_cls = self._registry[validator_id]
            self.validators[k] = validator_cls(validator_cls.parametrization(**v))

    async def run(self, request: ValidationRequest) -> TranslationValidation:
        results = {
            validator_name: await validator.run(request)
            for validator_name, validator in self.validators.items()
        }

        validation_result = TranslationValidation(
            results=results
        )

        result = await self._collection.insert_one(validation_result.model_dump())

        validation_result.inserted_id = str(result.inserted_id)
        return validation_result
