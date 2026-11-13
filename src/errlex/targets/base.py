"""The target protocol and shared Jinja2 rendering helpers."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from typing import ClassVar, Protocol, runtime_checkable

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from errlex.spec import ErrorSpec


@runtime_checkable
class Target(Protocol):
    """A language emitter.

    A target renders every registered spec into one or more files. The returned
    mapping is keyed by a path relative to the user-supplied output directory.
    """

    name: ClassVar[str]

    def emit(self, specs: Sequence[ErrorSpec]) -> Mapping[str, str]:
        """Render ``specs`` into ``{relative_path: file_contents}``."""
        ...


def pascal_case(value: str) -> str:
    """Convert ``PAYMENT_DECLINED`` to ``PaymentDeclined``."""
    parts = re.split(r"[^A-Za-z0-9]+", value)
    return "".join(part[:1].upper() + part[1:].lower() for part in parts if part)


def snake_case(value: str) -> str:
    """Convert ``PaymentDeclined`` to ``payment_declined``."""
    spaced = re.sub(r"(?<!^)(?=[A-Z])", "_", value)
    return re.sub(r"[^A-Za-z0-9]+", "_", spaced).strip("_").lower()


def json_string(value: object) -> str:
    """Render a value as a JSON string literal usable in most target languages."""
    return json.dumps(value, ensure_ascii=False)


def _template_candidates() -> list[Path]:
    candidates: list[Path] = []
    configured = os.environ.get("ERRLEX_TEMPLATES_DIR")
    if configured:
        candidates.append(Path(configured))
    candidates.append(Path(__file__).resolve().parent.parent / "templates")
    candidates.append(Path(__file__).resolve().parents[3] / "templates")
    return candidates


@lru_cache(maxsize=1)
def get_environment() -> Environment:
    """Return the shared Jinja2 environment, loading templates lazily."""
    for candidate in _template_candidates():
        if candidate.is_dir():
            environment = Environment(
                loader=FileSystemLoader(str(candidate)),
                autoescape=False,
                keep_trailing_newline=True,
                trim_blocks=True,
                lstrip_blocks=True,
                undefined=StrictUndefined,
            )
            environment.filters["pascal_case"] = pascal_case
            environment.filters["snake_case"] = snake_case
            environment.filters["json_string"] = json_string
            return environment
    searched = ", ".join(str(path) for path in _template_candidates())
    raise RuntimeError(f"could not locate the errlex templates directory (searched: {searched})")


def render_template(name: str, **context: object) -> str:
    """Render ``name`` from the templates directory with ``context``."""
    return get_environment().get_template(name).render(**context)
