"""Shared specification used by the golden-file tests."""

from __future__ import annotations

from errlex import ErrorSpec
from errlex.registry import Registry

PAYMENT_DECLINED = ErrorSpec(
    code="PAYMENT_DECLINED",
    http_status=402,
    retryable=False,
    message="The payment was declined by the processor.",
)

REGISTRY = Registry([PAYMENT_DECLINED])
