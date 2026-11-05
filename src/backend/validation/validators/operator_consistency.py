import re

from backend.validation.service import ValidationService
from backend.validation.validators.base import Validator
from nltk.tokenize import word_tokenize


@ValidationService.register("operator_consistency", enabled=True)
class OperatorConsistency(Validator):
    @staticmethod
    def _normalize_string(string: str) -> list[str]:
        no_ascii = re.sub(r"[^\w\s]", "", string)
        tokenized = word_tokenize(no_ascii, language="german")
        return [i.lower() for i in tokenized]

    @staticmethod
    def _operators_in_order(normalized_string: list[str], operators: list[str]) -> list[str]:
        return [i for i in normalized_string if i in operators]

    async def run(self, inp: str, out: str, operators: list[str]):
        inp_normalized = self._normalize_string(inp)
        out_normalized = self._normalize_string(out)

        # Keep order
        inp_ops = self._operators_in_order(inp_normalized, operators)
        out_ops = self._operators_in_order(out_normalized, operators)

        matches = []
        for i, inp_op in enumerate(inp_ops):
            if i >= len(out_ops):
                matches.append(False)
            else:
                matches.append(inp_op == out_ops[i])

        score = sum(matches) / len(matches)

        return {"score": score, "meta": {"matches": matches, "input_operators": inp_ops, "output_operators": out_ops}}
