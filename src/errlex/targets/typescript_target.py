"""TypeScript target: emits an error enum plus typed error classes."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from errlex.spec import ErrorSpec
from errlex.targets.base import render_template


class TypeScriptTarget:
    """Emit a TypeScript ``errors.ts`` module."""

    name = "typescript"

    def emit(self, specs: Sequence[ErrorSpec]) -> Mapping[str, str]:
        return {"errors.ts": render_template("typescript.ts.jinja", specs=specs)}
