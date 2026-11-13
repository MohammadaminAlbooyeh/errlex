"""Collection and validation of :class:`~errlex.spec.ErrorSpec` objects."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from errlex.spec import ErrorSpec


class DuplicateErrorCode(ValueError):
    """Raised when two specs declare the same error code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"duplicate error code: {code}")


class Registry:
    """An ordered, validated collection of error specs.

    Registration order is preserved, so generated output is deterministic.
    """

    def __init__(self, specs: Iterable[ErrorSpec] | None = None) -> None:
        self._specs: dict[str, ErrorSpec] = {}
        if specs is not None:
            self.register_all(specs)

    def register(self, spec: ErrorSpec) -> ErrorSpec:
        """Add one spec, rejecting duplicate codes."""
        if not isinstance(spec, ErrorSpec):
            raise TypeError(f"expected ErrorSpec, got {type(spec).__name__}")
        if spec.code in self._specs:
            raise DuplicateErrorCode(spec.code)
        self._specs[spec.code] = spec
        return spec

    def register_all(self, specs: Iterable[ErrorSpec]) -> None:
        """Add several specs, rejecting duplicates across the whole batch."""
        for spec in specs:
            self.register(spec)

    def get(self, code: str) -> ErrorSpec:
        """Return the spec for ``code`` or raise :class:`KeyError`."""
        return self._specs[code]

    @property
    def specs(self) -> tuple[ErrorSpec, ...]:
        """The registered specs in registration order."""
        return tuple(self._specs.values())

    @property
    def codes(self) -> tuple[str, ...]:
        """The registered codes in registration order."""
        return tuple(self._specs)

    def validate(self) -> None:
        """Validate every spec and the uniqueness invariant.

        Specs are validated on construction, so this is mostly useful after
        deserializing specs from another source in the future.
        """
        seen: set[str] = set()
        for spec in self._specs.values():
            ErrorSpec.__post_init__(spec)
            if spec.code in seen:
                raise DuplicateErrorCode(spec.code)
            seen.add(spec.code)

    def __iter__(self) -> Iterator[ErrorSpec]:
        return iter(self._specs.values())

    def __len__(self) -> int:
        return len(self._specs)

    def __contains__(self, code: object) -> bool:
        return code in self._specs

    def __repr__(self) -> str:
        return f"Registry({list(self._specs.values())!r})"
