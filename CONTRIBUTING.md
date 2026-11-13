# Contributing to errlex

Thanks for taking the time to contribute.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Before opening a pull request

Run the same checks as CI:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

And verify the drift gate for every target:

```bash
for target in python java typescript go; do
  errlex check --target "$target" --spec tests/fixtures/sample_spec.py \
    --out "tests/fixtures/golden/$target"
done
```

## Changing generated output

Generated output is pinned by golden files under `tests/fixtures/golden/`.

1. Change the template or target implementation.
2. Regenerate the golden files:

   ```bash
   for target in python java typescript go; do
     errlex generate --target "$target" --spec tests/fixtures/sample_spec.py \
       --out "tests/fixtures/golden/$target"
   done
   ```

3. Review the golden diff carefully; it is the contract.
4. If the example service output changed, regenerate it too:

   ```bash
   errlex generate --target python \
     --spec examples/payment-service/errors_spec.py \
     --out examples/payment-service/python-api
   errlex generate --target java \
     --spec examples/payment-service/errors_spec.py \
     --out examples/payment-service/java-payment/src/main/java/com/example/errors
   ```

## Adding a target language

See [docs/adding-a-target-language.md](docs/adding-a-target-language.md). A new
target needs an implementation, a template, golden output, and tests.

## Commit messages

Use short, imperative subject lines (for example `add rust target`). Keep
unrelated changes in separate commits.
