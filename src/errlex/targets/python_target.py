"""Python target: emits one exception class per error code."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from errlex.spec import ErrorSpec
from errlex.targets.base import render_template


class PythonTarget:
    """Emit Python exception classes into a single ``errors.py`` module."""

    name = "python"

    def emit(self, specs: Sequence[ErrorSpec]) -> Mapping[str, str]:
        return {"errors.py": render_template("python.py.jinja", specs=specs)}
