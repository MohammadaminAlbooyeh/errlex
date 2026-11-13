# CI drift check

The drift check is errlex's core guarantee: generated code always matches the
spec it was generated from, in every target language, at the same time.

`errlex check` regenerates output in memory and compares it byte-for-byte with
the committed files. It never writes to disk. If a file was hand-edited, is
stale, or is missing, the command exits with status `1`.

## Check one target

```bash
errlex check \
  --target python \
  --spec errors_spec.py \
  --out src/payments
```

## Check every target

```bash
for target in python java typescript go; do
  errlex check \
    --target "$target" \
    --spec errors_spec.py \
    --out "generated/$target" || exit 1
done
```

For Java, `--out` is the package directory, for example
`src/main/java/com/acme/errors`.

## GitHub Actions

```yaml
name: errors

on:
  push:
    branches: [main]
  pull_request:

jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - name: Check generated errors
        run: |
          set -e
          for target in python java typescript go; do
            errlex check \
              --target "$target" \
              --spec errors_spec.py \
              --out "generated/$target"
          done
```

## What failure means

A non-zero exit prints each offending path as `drifted:` or `missing:`. Fix it
by regenerating and committing the result:

```bash
errlex generate --target python --spec errors_spec.py --out src/payments
git add src/payments/errors.py
git commit -m "regenerate errors from spec"
```

Do not manually patch generated files. If the generated output is wrong, change
the template or the spec, then regenerate.

## Why not check only on release?

Drift compounds. A hand edit made in January is much more expensive to reconcile
in June, after other services have started depending on the edited behavior.
Running the check on every pull request keeps the invariant true at every commit
rather than discovering the mismatch at deploy time.

## Local pre-commit hook (optional)

```bash
#!/bin/sh
set -e
for target in python java typescript go; do
  errlex check --target "$target" --spec errors_spec.py --out "generated/$target"
done
```
