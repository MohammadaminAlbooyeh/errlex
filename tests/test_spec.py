from __future__ import annotations

import pytest

from errlex import DuplicateErrorCode, ErrorSpec, Registry


def test_valid_spec() -> None:
    spec = ErrorSpec(
        code="PAYMENT_DECLINED",
        http_status=402,
        retryable=False,
        message="The payment was declined by the processor.",
    )

    assert spec.code == "PAYMENT_DECLINED"
    assert spec.http_status == 402
    assert spec.retryable is False


@pytest.mark.parametrize("code", ["", "payment_declined", "PAYMENT-DECLINED", "1PAYMENT"])
def test_invalid_code_is_rejected(code: str) -> None:
    with pytest.raises(ValueError, match="code must be screaming snake case"):
        ErrorSpec(code=code, http_status=400, message="bad")


@pytest.mark.parametrize("status", [0, 99, 600, 1000, True])
def test_invalid_http_status_is_rejected(status: object) -> None:
    with pytest.raises(ValueError, match="http_status"):
        ErrorSpec(code="BAD_STATUS", http_status=status, message="bad")  # type: ignore[arg-type]


def test_empty_message_is_rejected() -> None:
    with pytest.raises(ValueError, match="message"):
        ErrorSpec(code="NO_MESSAGE", http_status=500, message="")


def test_non_boolean_retryable_is_rejected() -> None:
    with pytest.raises(ValueError, match="retryable"):
        ErrorSpec(code="BAD_RETRY", http_status=500, retryable="yes", message="bad")  # type: ignore[arg-type]


def test_registry_preserves_order_and_rejects_duplicates() -> None:
    first = ErrorSpec(code="FIRST_ERROR", http_status=400, message="first")
    second = ErrorSpec(code="SECOND_ERROR", http_status=409, message="second")
    registry = Registry([first, second])

    assert registry.codes == ("FIRST_ERROR", "SECOND_ERROR")
    assert registry.get("FIRST_ERROR") is first
    assert "SECOND_ERROR" in registry
    assert len(registry) == 2

    with pytest.raises(DuplicateErrorCode) as exc_info:
        registry.register(ErrorSpec(code="FIRST_ERROR", http_status=400, message="again"))
    assert exc_info.value.code == "FIRST_ERROR"


def test_registry_rejects_non_spec_values() -> None:
    registry = Registry()
    with pytest.raises(TypeError, match="expected ErrorSpec"):
        registry.register("NOT_A_SPEC")  # type: ignore[arg-type]


def test_registry_validate_is_idempotent() -> None:
    registry = Registry([ErrorSpec(code="ONLY_ERROR", http_status=400, message="only")])
    registry.validate()
    assert registry.codes == ("ONLY_ERROR",)
