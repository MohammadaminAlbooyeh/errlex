"""Java target: emits one exception class per error code."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from errlex.spec import ErrorSpec
from errlex.targets.base import pascal_case, render_template

DEFAULT_PACKAGE = "com.example.errors"
_PACKAGE_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")


class JavaTarget:
    """Emit one ``*Exception.java`` file per error code."""

    name = "java"

    def __init__(self, package: str = DEFAULT_PACKAGE) -> None:
        if not _PACKAGE_PATTERN.match(package):
            raise ValueError(f"invalid Java package name: {package!r}")
        self.package = package

    def emit(self, specs: Sequence[ErrorSpec]) -> Mapping[str, str]:
        return {
            f"{pascal_case(spec.code)}Exception.java": render_template(
                "java.java.jinja", spec=spec, package=self.package
            )
            for spec in specs
        }
