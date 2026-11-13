"""Shared error taxonomy for the example payment services."""

from __future__ import annotations

from errlex import ErrorSpec, Registry

PAYMENT_DECLINED = ErrorSpec(
    code="PAYMENT_DECLINED",
    http_status=402,
    retryable=False,
    message="The payment was declined by the processor.",
    description="The processor rejected the charge; do not retry without new payment details.",
)

PAYMENT_METHOD_EXPIRED = ErrorSpec(
    code="PAYMENT_METHOD_EXPIRED",
    http_status=402,
    retryable=False,
    message="The payment method has expired.",
)

RATE_LIMITED = ErrorSpec(
    code="RATE_LIMITED",
    http_status=429,
    retryable=True,
    message="Too many requests; retry after the period indicated by Retry-After.",
)

REFUND_FAILED = ErrorSpec(
    code="REFUND_FAILED",
    http_status=502,
    retryable=True,
    message="The refund could not be completed by the upstream processor.",
)

REGISTRY = Registry(
    [
        PAYMENT_DECLINED,
        PAYMENT_METHOD_EXPIRED,
        RATE_LIMITED,
        REFUND_FAILED,
    ]
)
