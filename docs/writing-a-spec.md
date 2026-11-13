# Writing a spec

A spec is an ordinary Python module. It defines `ErrorSpec` objects and exports
them in a `Registry`.

```python
# errors_spec.py
from errlex import ErrorSpec, Registry

PAYMENT_DECLINED = ErrorSpec(
    code="PAYMENT_DECLINED",
    http_status=402,
    retryable=False,
    message="The payment was declined by the processor.",
    description="The processor rejected the charge; do not retry without new details.",
)

RATE_LIMITED = ErrorSpec(
    code="RATE_LIMITED",
    http_status=429,
    retryable=True,
    message="Too many requests; retry after the indicated delay.",
)

REGISTRY = Registry([PAYMENT_DECLINED, RATE_LIMITED])
```

## Fields

| Field         | Type   | Required | Rules                                                  |
| ------------- | ------ | -------- | ------------------------------------------------------ |
| `code`        | `str`  | yes      | `SCREAMING_SNAKE_CASE`; unique within the registry     |
| `http_status` | `int`  | yes      | Between 100 and 599                                     |
| `retryable`   | `bool` | no       | Defaults to `False`                                     |
| `message`     | `str`  | yes      | Non-empty default message                               |
| `description` | `str`  | no       | Longer documentation emitted where the target supports it |

## How the CLI finds specs

The CLI loads the file given by `--spec` and looks for, in order:

1. A `Registry` exported as `REGISTRY` or `registry`.
2. An iterable of specs exported as `SPECS` or `specs`.
3. Every `ErrorSpec` instance defined at module level.

Exporting `REGISTRY` explicitly is recommended because it makes ordering and
membership obvious.

## Rules of thumb

- **Codes are forever.** Treat a code as part of the wire contract. Renaming one
  is a breaking change for every service that already handles it.
- **One code, one meaning.** Do not reuse a code for a different condition, even
  if the HTTP status is similar.
- **HTTP status is a hint, not the contract.** The code is what clients should
  branch on.
- **Messages are defaults.** Services may override a message when raising, but
  the generated default should still be useful in logs.

## Validation errors

`ErrorSpec` validates eagerly:

```python
ErrorSpec(code="payment_declined", http_status=402, message="...")
# ValueError: code must be screaming snake case ...
```

`Registry` rejects duplicate codes:

```python
Registry([PAYMENT_DECLINED, PAYMENT_DECLINED])
# DuplicateErrorCode: duplicate error code: PAYMENT_DECLINED
```
