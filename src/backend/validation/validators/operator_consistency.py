from typing import Any, Optional

import spacy

from backend.validation.schemas import ValidationResult
from backend.validation.service import ValidationService
from backend.validation.validators.base import Validator
from HanTa import HanoverTagger as ht

NAME = "operator_consistency"

@ValidationService.register(NAME, enabled=True)
class OperatorConsistency(Validator):
    _registry_name = NAME
    _tokenizer = spacy.blank("de")
    _tagger = ht.HanoverTagger("morphmodel_ger.pgz")

    def __init__(self):
        # TODO
        self._full_operator_list: list[str] = ["analysieren"]

    def _normalize_string(self, string: str) -> list[str]:
        tokens = [t.text for t in self._tokenizer(string) if not (t.is_punct or t.is_space)]
        if not tokens:
            return []
        return [lemma.lower() for _, lemma, _ in self._tagger.tag_sent(tokens)]

    @staticmethod
    def _operators_in_order(normalized_string: list[str], operators: list[str]) -> list[str]:
        return [i for i in normalized_string if i in operators]

    async def run(self, inp: str, out: str, meta: Optional[dict[str, Any]]) -> ValidationResult:
        if meta is not None and meta.get("operators"):
            operators = meta["operators"]
        else:
            operators = self._full_operator_list

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

        out = ValidationResult(
            metric=self._registry_name,
            score=score,
            meta = {
                "matches": matches,
                "input_operators": inp_ops,
                "output_operators": out_ops
            }
        )

        return out
