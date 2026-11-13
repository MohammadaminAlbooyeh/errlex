"""The error specification model.

An :class:`ErrorSpec` is the single source of truth for one error code. Every
target language is generated from a collection of these objects.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$")
_MIN_HTTP_STATUS = 100
_MAX_HTTP_STATUS = 599


@dataclass(frozen=True, slots=True)
class ErrorSpec:
    """A language-independent error definition.

    Attributes:
        code: Stable, screaming-snake-case identifier (for example
            ``PAYMENT_DECLINED``). This is the value that crosses service
            boundaries.
        http_status: HTTP status code associated with the error.
        retryable: Whether a client may safely retry the failed operation.
        message: Human-readable default message.
        description: Optional longer documentation for the error.
    """

    code: str
    http_status: int
    retryable: bool = False
    message: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not _CODE_PATTERN.match(self.code):
            raise ValueError(
                "code must be screaming snake case matching "
                f"{_CODE_PATTERN.pattern!r}, got {self.code!r}"
            )
        if isinstance(self.http_status, bool) or not isinstance(self.http_status, int):
            raise ValueError(f"http_status must be an int, got {self.http_status!r}")
        if not _MIN_HTTP_STATUS <= self.http_status <= _MAX_HTTP_STATUS:
            raise ValueError(
                f"http_status must be between {_MIN_HTTP_STATUS} and "
                f"{_MAX_HTTP_STATUS}, got {self.http_status}"
            )
        if not isinstance(self.retryable, bool):
            raise ValueError(f"retryable must be a bool, got {self.retryable!r}")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string")
        if not isinstance(self.description, str):
            raise ValueError(f"description must be a string, got {self.description!r}")
