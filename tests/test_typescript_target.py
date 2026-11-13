from __future__ import annotations

from pathlib import Path

from fixtures.sample_spec import REGISTRY

from errlex.targets import TypeScriptTarget

GOLDEN = Path(__file__).parent / "fixtures" / "golden" / "typescript" / "errors.ts"


def test_typescript_target_matches_golden() -> None:
    generated = TypeScriptTarget().emit(REGISTRY.specs)
    assert generated == {"errors.ts": GOLDEN.read_text(encoding="utf-8")}


def test_typescript_output_contains_enum_and_class() -> None:
    content = TypeScriptTarget().emit(REGISTRY.specs)["errors.ts"]
    assert 'PAYMENT_DECLINED = "PAYMENT_DECLINED",' in content
    assert "export class PaymentDeclinedError extends ErrlexError" in content
    assert "httpStatus: 402" in content
