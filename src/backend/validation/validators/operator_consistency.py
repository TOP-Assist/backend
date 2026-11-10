from itertools import zip_longest

from limes.analyzers.de import GermanAnalyzer
from limes.parsers import SpacyParser
from pydantic import BaseModel

from backend.analysis.service import AnalysisService
from backend.validation.schemas import ValidationResult, ValidationRequest
from backend.validation.service import ValidationService
from backend.validation.validators.base import Validator


class OperatorConsistencyParametrization(BaseModel):
    preserve_order: bool = True

@ValidationService.register()
class OperatorConsistency(Validator):
    # TODO: Use from context
    _analyzer = AnalysisService(
        parser=SpacyParser(model="de_dep_news_trf"),
        analyzer=GermanAnalyzer()
    )

    parametrization = OperatorConsistencyParametrization

    def __init__(self, parametrization: OperatorConsistencyParametrization):
        self.preserve_order = parametrization.preserve_order

    async def run(self, request: ValidationRequest) -> ValidationResult:
        input_operators = self._analyzer.get_operators(request.input_text)
        output_operators = self._analyzer.get_operators(request.output_text)

        if self.preserve_order:
            matches = [
                inp_op == out_op
                for inp_op, out_op
                in zip_longest(input_operators, output_operators, fillvalue=None)
            ]

        else:
            matches = []
            for inp_op in input_operators:
                try:
                    out_op_idx = output_operators.index(inp_op)
                    output_operators.pop(out_op_idx)
                    matches.append(True)
                except ValueError:
                    matches.append(False)

        score = sum(matches) / len(matches) if len(matches) > 0 else 0

        return ValidationResult(
            metric=self.__class__.__name__,
            parameters=vars(self),
            score=score,
            meta = {
                "matches": matches,
                "input_operators": input_operators,
                "output_operators": output_operators,
            }
        )
