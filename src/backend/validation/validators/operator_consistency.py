# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import copy
from itertools import zip_longest
from typing import Self

from typesafe_sdk import Choice, Noul, TypeSafeClient

from backend.analysis.executor import AnalysisExecutor
from backend.analysis.schemas import OperatorRequest, OperatorResult
from backend.validation.schemas import ValidationRequest, ValidationResult
from backend.validation.service import ValidationService
from backend.validation.validators.base import (
    Validator,
    ValidatorParametrization,
)


class OperatorConsistencyParametrization(ValidatorParametrization):
    preserve_order: bool = True
    use_decision_model: bool = True
    decision_model_threshold: float = 0.5


@ValidationService.register()
class OperatorConsistency(Validator):
    _parametrization = OperatorConsistencyParametrization

    def __init__(
        self,
        parametrization: OperatorConsistencyParametrization,
        analysis_executor: AnalysisExecutor,
    ):
        super().__init__(parametrization)
        self._analysis_executor = analysis_executor

        if self.parametrization.use_decision_model:
            base_url = "http://decision_model:8009"
            self._client = TypeSafeClient(
                base_url=base_url,
                api_key="local",
            )
        else:
            self._client = None

    async def run(self, request: ValidationRequest) -> ValidationResult:
        input_operators = await self._analysis_executor.get_operators(
            OperatorRequest(input=request.input_text)
        )
        output_operators = await self._analysis_executor.get_operators(
            OperatorRequest(input=request.output_text)
        )

        matches, confidences = await self._compare(
            input_operators, output_operators
        )

        max_operators = max(
            len(input_operators.operators), len(output_operators.operators)
        )
        score = sum(matches) / max_operators if max_operators > 0 else 0

        return ValidationResult(
            metric=self.__class__.__name__,
            parameters=self.parametrization.model_dump(),
            score=score,
            meta={
                "matches": matches,
                "confidences": confidences,
                "input_operators": input_operators.operators,
                "input_operators_lemmatized": input_operators.operators_lemmatized,
                "output_operators": output_operators.operators,
                "output_operators_lemmatized": output_operators.operators_lemmatized,
                "input_occurrences": [
                    occurrence.model_dump()
                    for occurrence in input_operators.occurrences
                ],
                "output_occurrences": [
                    occurrence.model_dump()
                    for occurrence in output_operators.occurrences
                ],
            },
        )

    @classmethod
    def create(
        cls,
        parametrization: OperatorConsistencyParametrization,
        analysis_executor: AnalysisExecutor,
    ) -> Self:
        return cls(parametrization, analysis_executor)

    async def _compare(
        self, inp: OperatorResult, out: OperatorResult
    ) -> tuple[list[bool], list[float] | None]:
        if self.parametrization.use_decision_model:
            assert self._client is not None, (
                "Specified to use decision model but no client found"
            )

        input_operators = (
            inp.operators
            if self.parametrization.use_decision_model
            else inp.operators_lemmatized
        )
        output_operators = (
            out.operators
            if self.parametrization.use_decision_model
            else out.operators_lemmatized
        )

        confidences = [] if self.parametrization.use_decision_model else None
        matches = []

        if self.parametrization.preserve_order:
            for inp_op, out_op in zip_longest(
                input_operators, output_operators, fillvalue=None
            ):
                if None in (inp_op, out_op):
                    matches.append(False)
                else:
                    if self.parametrization.use_decision_model:
                        confidence = self._decision_with_preserved_order(
                            inp_op, out_op
                        )
                        confidences.append(confidence)
                        matches.append(
                            confidence
                            > self.parametrization.decision_model_threshold
                        )
                    else:
                        matches.append(inp_op == out_op)
        else:
            if self.parametrization.use_decision_model:
                for inp_op in input_operators:
                    matched, confidence = self._decision_with_arbitrary_order(
                        inp_op, output_operators
                    )
                    confidences.append(confidence)
                    matches.append(matched is not None)
            else:
                output_operators_editable = copy.deepcopy(output_operators)
                for inp_op in input_operators:
                    try:
                        out_op_idx = output_operators_editable.index(inp_op)
                        output_operators_editable.pop(out_op_idx)
                        matches.append(True)
                    except ValueError:
                        matches.append(False)

        return matches, confidences

    def _decision_with_preserved_order(self, inp_op: str, out_op: str) -> float:
        response = self._client.system_one(
            state={
                "verb_1": inp_op,
                "verb_2": out_op,
            },
            questions={
                "same_infinitive": Noul(
                    instructions="Do both German verbs share the same infinitive?"
                )
            },
        )

        return response.answers["same_infinitive"].noul

    def _decision_with_arbitrary_order(
        self, inp_op: str, out_ops: list[str]
    ) -> tuple[str | None, float]:
        response = self._client.system_one(
            state={"verb": inp_op},
            questions={
                "match": Choice(
                    instructions="Which candidate shares the same infinitive? If there are several matches, select the earliest one.",
                    criteria={
                        **{verb: verb for verb in out_ops},
                        "no_match": "None of the candidates match.",
                    },
                )
            },
        )

        probabilities = response.answers["match"].probabilities

        matched_op = max(probabilities, key=probabilities.__getitem__)
        matched_probability = probabilities[matched_op]

        return (
            None if matched_op == "no_match" else matched_op,
            matched_probability,
        )
