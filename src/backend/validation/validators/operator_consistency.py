# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import copy
from itertools import zip_longest
from typing import Self

from backend.analysis.executor import AnalysisExecutor
from backend.analysis.schemas import OperatorRequest
from backend.validation.schemas import ValidationRequest, ValidationResult
from backend.validation.service import ValidationService
from backend.validation.validators.base import (
    Validator,
    ValidatorParametrization,
)


class OperatorConsistencyParametrization(ValidatorParametrization):
    preserve_order: bool = True


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

    async def run(self, request: ValidationRequest) -> ValidationResult:
        input_analysis = await self._analysis_executor.get_operators(
            OperatorRequest(input=request.input_text)
        )
        output_analysis = await self._analysis_executor.get_operators(
            OperatorRequest(input=request.output_text)
        )

        input_operators = input_analysis.operators
        output_operators = output_analysis.operators

        if self.parametrization.preserve_order:
            matches = [
                inp_op == out_op
                for inp_op, out_op in zip_longest(
                    input_operators, output_operators, fillvalue=None
                )
            ]

        else:
            matches = []
            # Preserve output operators for returning result
            output_operators_editable = copy.deepcopy(output_operators)
            for inp_op in input_operators:
                try:
                    out_op_idx = output_operators_editable.index(inp_op)
                    output_operators_editable.pop(out_op_idx)
                    matches.append(True)
                except ValueError:
                    matches.append(False)

        max_operators = max(len(input_operators), len(output_operators))
        score = sum(matches) / max_operators if max_operators > 0 else 0

        return ValidationResult(
            metric=self.__class__.__name__,
            parameters=self.parametrization.model_dump(),
            score=score,
            meta={
                "matches": matches,
                "input_operators": input_operators,
                "output_operators": output_operators,
                "input_occurrences": [
                    occurrence.model_dump()
                    for occurrence in input_analysis.occurrences
                ],
                "output_occurrences": [
                    occurrence.model_dump()
                    for occurrence in output_analysis.occurrences
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
