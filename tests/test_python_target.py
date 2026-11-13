from __future__ import annotations

from pathlib import Path

from fixtures.sample_spec import REGISTRY

from errlex import generate
from errlex.targets import PythonTarget

GOLDEN = Path(__file__).parent / "fixtures" / "golden" / "python" / "errors.py"


def test_python_target_matches_golden() -> None:
    generated = PythonTarget().emit(REGISTRY.specs)
    assert generated == {"errors.py": GOLDEN.read_text(encoding="utf-8")}


def test_public_generate_function_uses_target() -> None:
    assert generate(REGISTRY, "python") == PythonTarget().emit(REGISTRY.specs)


def test_generated_python_is_executable() -> None:
    source = PythonTarget().emit(REGISTRY.specs)["errors.py"]
    namespace: dict[str, object] = {}
    exec(compile(source, "errors.py", "exec"), namespace)  # noqa: S102

    errors = namespace["ERRORS"]
    assert isinstance(errors, dict)
    error_class = errors["PAYMENT_DECLINED"]
    instance = error_class()

    assert instance.code == "PAYMENT_DECLINED"
    assert instance.http_status == 402
    assert instance.retryable is False
    assert str(instance) == "The payment was declined by the processor."
