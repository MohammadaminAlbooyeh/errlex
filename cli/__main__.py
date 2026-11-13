"""Command line entry point for errlex."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from types import ModuleType
from typing import Any

from errlex import __version__
from errlex.diff import check_output, format_drift
from errlex.registry import Registry
from errlex.spec import ErrorSpec
from errlex.targets import Target, available_targets, get_target
from errlex.targets.java_target import JavaTarget


def _load_spec_module(path: Path) -> ModuleType:
    resolved = path.resolve()
    if not resolved.is_file():
        raise SystemExit(f"spec file not found: {path}")
    digest = hashlib.sha1(str(resolved).encode()).hexdigest()[:12]
    module_name = f"_errlex_spec_{digest}"
    spec = importlib.util.spec_from_file_location(module_name, resolved)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load spec module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    parent = str(resolved.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - surface a clean CLI error
        raise SystemExit(f"failed to execute spec file {path}: {exc}") from exc
    return module


def _coerce_registry(module: ModuleType) -> Registry:
    for attribute in ("REGISTRY", "registry", "SPECS", "specs"):
        value: Any = getattr(module, attribute, None)
        if isinstance(value, Registry):
            return value
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            specs = tuple(item for item in value if isinstance(item, ErrorSpec))
            if specs:
                return Registry(specs)
    specs = tuple(value for value in vars(module).values() if isinstance(value, ErrorSpec))
    if not specs:
        raise SystemExit(
            "no error specs found; export REGISTRY, a list of specs, "
            "or at least one ErrorSpec instance"
        )
    return Registry(specs)


def _load_registry(path: Path) -> Registry:
    return _coerce_registry(_load_spec_module(path))


def _make_target(name: str, package: str | None) -> Target:
    if package is not None:
        if name != "java":
            raise SystemExit("--package is only supported for the java target")
        return JavaTarget(package=package)
    return get_target(name)


def _generate(args: argparse.Namespace) -> tuple[Registry, Target, dict[str, str]]:
    registry = _load_registry(args.spec)
    target = _make_target(args.target, args.package)
    generated = dict(target.emit(registry.specs))
    return registry, target, generated


def _cmd_generate(args: argparse.Namespace) -> int:
    _registry, target, generated = _generate(args)
    args.out.mkdir(parents=True, exist_ok=True)
    for relative_path, content in generated.items():
        destination = args.out / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        print(f"wrote {destination}")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    _registry, target, generated = _generate(args)
    drifts = check_output(target.name, generated, args.out)
    if drifts:
        print(format_drift(drifts), file=sys.stderr)
        print(
            f"\n{len(drifts)} generated file(s) are out of date for target "
            f"{target.name!r}. Run 'errlex generate' and commit the result.",
            file=sys.stderr,
        )
        return 1
    print(f"{target.name}: generated output is in sync ({len(generated)} file(s))")
    return 0


def _cmd_targets(_args: argparse.Namespace) -> int:
    for name in available_targets():
        print(name)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="errlex",
        description="Generate native error types from a single Python specification.",
    )
    parser.add_argument("--version", action="version", version=f"errlex {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="generate error types")
    _add_common_arguments(generate)
    generate.set_defaults(func=_cmd_generate)

    check = subparsers.add_parser("check", help="fail if committed output has drifted")
    _add_common_arguments(check)
    check.set_defaults(func=_cmd_check)

    targets = subparsers.add_parser("targets", help="list built-in targets")
    targets.set_defaults(func=_cmd_targets)

    return parser


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target", required=True, choices=available_targets())
    parser.add_argument("--spec", required=True, type=Path, help="path to the Python spec file")
    parser.add_argument("--out", required=True, type=Path, help="output directory")
    parser.add_argument(
        "--package",
        default=None,
        help="Java package name (only valid with --target java)",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler: Any = args.func
    result: int = handler(args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
