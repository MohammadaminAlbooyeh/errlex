"""errlex: one error taxonomy, many languages."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from errlex.registry import DuplicateErrorCode, Registry
from errlex.spec import ErrorSpec
from errlex.targets import Target, get_target

__version__ = "0.1.0"

__all__ = [
    "DuplicateErrorCode",
    "ErrorSpec",
    "Registry",
    "Target",
    "__version__",
    "generate",
]


def generate(
    specs: Registry | Iterable[ErrorSpec],
    target: str | Target = "python",
) -> Mapping[str, str]:
    """Generate code for ``target`` from ``specs``.

    Args:
        specs: A :class:`Registry` or an iterable of :class:`ErrorSpec`.
        target: A built-in target name (``python``, ``java``, ``typescript``,
            ``go``) or a custom object implementing the :class:`Target`
            protocol.

    Returns:
        A mapping of relative file paths to generated file contents.
    """
    registry = specs if isinstance(specs, Registry) else Registry(specs)
    emitter = get_target(target) if isinstance(target, str) else target
    return emitter.emit(registry.specs)
