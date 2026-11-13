# errlex documentation

`errlex` generates native error types for multiple languages from one Python
specification, and enforces that the generated code never drifts from that
specification.

## Mental model

There are three pieces:

1. **A spec** — a Python file containing `ErrorSpec` objects collected in a
   `Registry`. This is the source of truth.
2. **A target** — a language emitter that turns the registry into files using a
   Jinja2 template.
3. **A drift check** — a command that regenerates the output in memory and
   compares it byte-for-byte with committed files.

The invariant is simple: for every target, `generate(spec)` must equal the files
committed in the repository.

## Install

```bash
pip install errlex
```

## Generate

```bash
errlex generate \
  --target python \
  --spec examples/payment-service/errors_spec.py \
  --out examples/payment-service/python-api
```

`--out` is always a directory. The target decides the file names inside it. Java
emits one file per exception, so point `--out` at the package directory.

## Check

```bash
errlex check \
  --target java \
  --spec examples/payment-service/errors_spec.py \
  --out examples/payment-service/java-payment/src/main/java/com/example/errors
```

Exit codes:

- `0` — generated output matches the spec.
- `1` — at least one file drifted or is missing.
- `2` — invalid CLI usage.

## Library API

```python
from errlex import ErrorSpec, Registry, generate

REGISTRY = Registry(
    [
        ErrorSpec(code="NOT_FOUND", http_status=404, message="Resource not found."),
    ]
)

files = generate(REGISTRY, "typescript")
assert "errors.ts" in files
```

Custom targets only need to implement `emit(specs) -> Mapping[str, str]`.

## Guides

- [Writing a spec](writing-a-spec.md)
- [Adding a target language](adding-a-target-language.md)
- [CI drift check](ci-drift-check.md)
