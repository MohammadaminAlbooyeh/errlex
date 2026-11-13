"""Language targets shipped with errlex."""

from __future__ import annotations

from collections.abc import Callable

from errlex.targets.base import Target
from errlex.targets.go_target import GoTarget
from errlex.targets.java_target import JavaTarget
from errlex.targets.python_target import PythonTarget
from errlex.targets.typescript_target import TypeScriptTarget

TargetFactory = Callable[[], Target]

TARGETS: dict[str, TargetFactory] = {
    "python": PythonTarget,
    "java": JavaTarget,
    "typescript": TypeScriptTarget,
    "go": GoTarget,
}


def get_target(name: str) -> Target:
    """Return a fresh target instance for ``name``."""
    try:
        factory = TARGETS[name]
    except KeyError:
        available = ", ".join(sorted(TARGETS))
        raise ValueError(f"unknown target {name!r} (available: {available})") from None
    return factory()


def available_targets() -> tuple[str, ...]:
    """Return the names of all built-in targets."""
    return tuple(TARGETS)


__all__ = [
    "GoTarget",
    "JavaTarget",
    "PythonTarget",
    "Target",
    "TargetFactory",
    "TARGETS",
    "TypeScriptTarget",
    "available_targets",
    "get_target",
]
