from __future__ import annotations

from pathlib import Path

import pytest
from fixtures.sample_spec import REGISTRY

from errlex.diff import DriftDetected, assert_in_sync, check_output, format_drift
from errlex.targets import PythonTarget

TARGET = PythonTarget()


def _write_output(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for relative_path, content in TARGET.emit(REGISTRY.specs).items():
        (out_dir / relative_path).write_text(content, encoding="utf-8")


def test_fresh_output_has_no_drift(tmp_path: Path) -> None:
    _write_output(tmp_path)
    assert check_output(TARGET.name, TARGET.emit(REGISTRY.specs), tmp_path) == []


def test_hand_edited_output_is_detected(tmp_path: Path) -> None:
    _write_output(tmp_path)
    errors_py = tmp_path / "errors.py"
    errors_py.write_text(
        errors_py.read_text(encoding="utf-8") + "\n# hand-edited\n",
        encoding="utf-8",
    )

    drifts = check_output(TARGET.name, TARGET.emit(REGISTRY.specs), tmp_path)

    assert len(drifts) == 1
    assert drifts[0].has_drift
    assert not drifts[0].is_missing
    assert drifts[0].path == errors_py
    assert "drifted:" in format_drift(drifts)


def test_missing_output_is_detected(tmp_path: Path) -> None:
    drifts = check_output(TARGET.name, TARGET.emit(REGISTRY.specs), tmp_path)

    assert len(drifts) == 1
    assert drifts[0].is_missing
    assert drifts[0].has_drift
    assert "missing:" in format_drift(drifts)


def test_assert_in_sync_raises_with_drift_details(tmp_path: Path) -> None:
    _write_output(tmp_path)
    (tmp_path / "errors.py").write_text("stale\n", encoding="utf-8")

    with pytest.raises(DriftDetected) as exc_info:
        assert_in_sync(TARGET.name, TARGET.emit(REGISTRY.specs), tmp_path)

    assert len(exc_info.value.drifts) == 1
    assert exc_info.value.drifts[0].actual == "stale\n"
