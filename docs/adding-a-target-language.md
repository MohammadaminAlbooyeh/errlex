# Adding a target language

Adding a language is additive: implement the `Target` protocol, add a Jinja2
template, register the target, and pin its output with a golden file.

## The Target protocol

```python
# src/errlex/targets/base.py
class Target(Protocol):
    name: ClassVar[str]

    def emit(self, specs: Sequence[ErrorSpec]) -> Mapping[str, str]:
        ...
```

`emit` returns a mapping of relative file paths to file contents. A target may
emit one file for the whole taxonomy (Python, TypeScript, Go) or one file per
error code (Java).

Paths must be relative. The CLI writes them beneath the user-provided `--out`
directory and creates parent directories as needed.

## Step 1: write the template

Create `templates/<language>.<ext>.jinja`. Templates receive the context passed
by the target implementation. The Python target, for example, receives
`specs=Sequence[ErrorSpec]`, while Java receives one `spec` and a `package`.

Shared filters are registered in `base.py`:

| Filter        | Example                              |
| ------------- | ------------------------------------ |
| `pascal_case` | `PAYMENT_DECLINED` → `PaymentDeclined` |
| `snake_case`  | `PaymentDeclined` → `payment_declined` |
| `json_string` | `value` → `"value"` with escaping    |

## Step 2: implement the target

```python
# src/errlex/targets/rust_target.py
from collections.abc import Mapping, Sequence

from errlex.spec import ErrorSpec
from errlex.targets.base import render_template


class RustTarget:
    name = "rust"

    def emit(self, specs: Sequence[ErrorSpec]) -> Mapping[str, str]:
        return {"errors.rs": render_template("rust.rs.jinja", specs=specs)}
```

## Step 3: register it

```python
# src/errlex/targets/__init__.py
from errlex.targets.rust_target import RustTarget

TARGETS = {
    "python": PythonTarget,
    "java": JavaTarget,
    "typescript": TypeScriptTarget,
    "go": GoTarget,
    "rust": RustTarget,
}
```

The CLI derives its `--target` choices from `TARGETS`, so no CLI change is
needed.

## Step 4: add a golden file and tests

1. Add `tests/fixtures/golden/rust/errors.rs`.
2. Add `tests/test_rust_target.py`, mirroring the other target tests.
3. Generate the golden output:

   ```bash
   errlex generate --target rust --spec tests/fixtures/sample_spec.py \
     --out tests/fixtures/golden/rust
   ```

4. Confirm the drift gate passes:

   ```bash
   errlex check --target rust --spec tests/fixtures/sample_spec.py \
     --out tests/fixtures/golden/rust
   ```

## Design guidance

- Match the host language's conventions for naming, visibility, and error
  handling. Do not build a lowest-common-denominator shim.
- Keep output deterministic: preserve registry order and avoid timestamps.
- Emit a "do not edit" header. The drift check is what protects the file, but
  the header tells humans why hand edits will be rejected.
- Render literals through `json_string` (or a language-specific escaper) rather
  than concatenating raw quotes into templates.
- Add comments only where the generated code benefits from them.
