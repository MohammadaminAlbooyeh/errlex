"""Go target: emits typed error variables implementing ``error``."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from errlex.spec import ErrorSpec
from errlex.targets.base import render_template


class GoTarget:
    """Emit a Go ``errors.go`` file with one error variable per code."""

    name = "go"

    def emit(self, specs: Sequence[ErrorSpec]) -> Mapping[str, str]:
        return {"errors.go": render_template("go.go.jinja", specs=specs)}
