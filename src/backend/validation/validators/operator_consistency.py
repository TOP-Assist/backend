from typing import Any, Optional

from limes.analyzers.de import GermanAnalyzer
from limes.parsers import SpacyParser

from backend.analysis.service import AnalysisService
from backend.validation.schemas import ValidationResult
from backend.validation.service import ValidationService
from backend.validation.validators.base import Validator

NAME = "operator_consistency"

@ValidationService.register(NAME, enabled=True)
class OperatorConsistency(Validator):
    # TODO: Worker Queue Pattern?
    _registry_name = NAME

    _analyzer = AnalysisService(
        # TODO: Use from context
        parser=SpacyParser(model="de_dep_news_trf"),
        analyzer=GermanAnalyzer()
    )

    async def run(self, inp: str, out: str, meta: Optional[dict[str, Any]]) -> ValidationResult:
        input_operators = self._analyzer.get_operators(inp)
        output_operators = self._analyzer.get_operators(out)

        matches = []
        for i, inp_op in enumerate(input_operators):
            if i >= len(out):
                matches.append(False)
            else:
                matches.append(inp_op == output_operators[i])

        score = sum(matches) / len(matches)

        return ValidationResult(
            metric=self._registry_name,
            score=score,
            meta = {
                "matches": matches,
                "input_operators": input_operators,
                "output_operators": output_operators
            }
        )
