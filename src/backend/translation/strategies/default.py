# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections.abc import Sequence
from importlib.resources import files
from string import Formatter

from backend.analysis.schemas import BarrierTokenHighlight

# One file per prompt variant, selected via the `LLM_PROMPT_VARIANT` setting.
# Files are sent verbatim, so keep `{barriers}` and `{parlance_words}` intact
# and double any literal braces. To revise a prompt without losing the old
# one, add a new file (e.g. `qwen3-v2.md`) and point the setting at it.
_PROMPT_DIR = files("backend.translation") / "prompts" / "default"
_PROMPT_SUFFIX = ".md"
_PLACEHOLDERS = frozenset({"barriers", "parlance_words"})


def _available_variants() -> list[str]:
    return sorted(
        entry.name.removesuffix(_PROMPT_SUFFIX)
        for entry in _PROMPT_DIR.iterdir()
        if entry.is_file() and entry.name.endswith(_PROMPT_SUFFIX)
    )


def get_prompt(variant: str) -> str:
    """Load the prompt for `variant` after validating its placeholders."""
    variants = _available_variants()
    if variant not in variants:
        raise ValueError(
            f"Unknown prompt variant '{variant}' for the default strategy. "
            f"Available: {variants}"
        )

    prompt = (_PROMPT_DIR / f"{variant}{_PROMPT_SUFFIX}").read_text(
        encoding="utf-8"
    )

    try:
        placeholders = {
            name
            for _, name, _, _ in Formatter().parse(prompt)
            if name is not None
        }
    except ValueError as exc:
        raise ValueError(
            f"Prompt variant '{variant}' is not a valid format string"
        ) from exc

    if placeholders != _PLACEHOLDERS:
        raise ValueError(
            f"Prompt variant '{variant}' must use exactly the placeholders "
            f"{sorted(_PLACEHOLDERS)}, found {sorted(placeholders)}"
        )

    return prompt


def prepare(
    prompt: str,
    *,
    barriers: Sequence[BarrierTokenHighlight] = (),
    parlance_words: Sequence[str] = (),
) -> str:
    """Populate the prompt's placeholders."""
    return prompt.format(
        barriers=_format_barrier_suggestions(barriers),
        parlance_words=(
            ", ".join(parlance_words)
            if parlance_words
            else "Keine Fachbegriffe identifiziert."
        ),
    )


def _format_barrier_suggestions(
    barriers: Sequence[BarrierTokenHighlight],
) -> str:
    """Preserve the original barrier-formatting behavior."""
    suggestions = [
        (
            f"{index + 1}. Wort {barrier.token} ist ein {barrier.title}. "
            "Diese Sprachbarriere kann wie folgt entfernt werden: "
            f"{barrier.suggestion}"
        )
        for index, barrier in enumerate(barriers)
        if barrier.title != "Langer Satz"
    ]

    return (
        "\n".join(suggestions).strip()
        if suggestions
        else "Keine Sprachbarrieren identifiziert."
    )
