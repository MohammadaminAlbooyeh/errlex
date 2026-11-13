from __future__ import annotations

from pathlib import Path

from fixtures.sample_spec import REGISTRY

from errlex.targets import GoTarget

GOLDEN = Path(__file__).parent / "fixtures" / "golden" / "go" / "errors.go"


def test_go_target_matches_golden() -> None:
    generated = GoTarget().emit(REGISTRY.specs)
    assert generated == {"errors.go": GOLDEN.read_text(encoding="utf-8")}


def test_go_output_contains_error_variable() -> None:
    content = GoTarget().emit(REGISTRY.specs)["errors.go"]
    assert "ErrPaymentDeclined = &Error{" in content
    assert 'Code:       "PAYMENT_DECLINED",' in content
    assert "HTTPStatus: 402," in content
