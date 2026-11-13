"""Drift detection: compare freshly generated output with committed files.

The core guarantee of errlex is that generated code always matches the spec it
was generated from. This module implements the comparison used by the CLI and
by CI.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Drift:
    """One generated file that does not match its committed counterpart."""

    target: str
    path: Path
    expected: str
    actual: str | None

    @property
    def is_missing(self) -> bool:
        return self.actual is None

    @property
    def has_drift(self) -> bool:
        return self.actual != self.expected


class DriftDetected(AssertionError):
    """Raised when one or more generated files have drifted."""

    def __init__(self, drifts: list[Drift]) -> None:
        self.drifts = tuple(drifts)
        if len(drifts) == 1:
            message = f"generated output for target {drifts[0].target!r} is out of date"
        else:
            message = f"generated output for {len(drifts)} files is out of date"
        super().__init__(message)


def check_output(
    target: str,
    generated: Mapping[str, str],
    out_dir: Path,
) -> list[Drift]:
    """Compare ``generated`` files against the same paths under ``out_dir``."""
    drifts: list[Drift] = []
    for relative_path, expected in generated.items():
        path = out_dir / relative_path
        actual = path.read_text(encoding="utf-8") if path.is_file() else None
        drift = Drift(target=target, path=path, expected=expected, actual=actual)
        if drift.has_drift:
            drifts.append(drift)
    return drifts


def assert_in_sync(target: str, generated: Mapping[str, str], out_dir: Path) -> None:
    """Raise :class:`DriftDetected` if any generated file is stale or missing."""
    drifts = check_output(target, generated, out_dir)
    if drifts:
        raise DriftDetected(drifts)


def format_drift(drifts: list[Drift]) -> str:
    """Render a human-readable drift report for CLI output."""
    lines: list[str] = []
    for drift in drifts:
        if drift.is_missing:
            lines.append(f"missing: {drift.path}")
            continue
        lines.append(f"drifted: {drift.path}")
    return "\n".join(lines)
