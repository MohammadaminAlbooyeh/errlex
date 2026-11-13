from __future__ import annotations

from pathlib import Path

import pytest
from fixtures.sample_spec import REGISTRY

from errlex.targets import JavaTarget

GOLDEN = (
    Path(__file__).parent
    / "fixtures"
    / "golden"
    / "java"
    / "PaymentDeclinedException.java"
)


def test_java_target_matches_golden() -> None:
    generated = JavaTarget().emit(REGISTRY.specs)
    assert generated == {
        "PaymentDeclinedException.java": GOLDEN.read_text(encoding="utf-8")
    }


def test_java_target_honours_package_option() -> None:
    generated = JavaTarget(package="com.acme.payments").emit(REGISTRY.specs)
    content = generated["PaymentDeclinedException.java"]
    assert content.startswith("package com.acme.payments;")
    assert 'public static final String CODE = "PAYMENT_DECLINED";' in content
    assert "public static final int HTTP_STATUS = 402;" in content


def test_java_target_rejects_invalid_package() -> None:
    with pytest.raises(ValueError, match="invalid Java package name"):
        JavaTarget(package="com.acme.payments;")
