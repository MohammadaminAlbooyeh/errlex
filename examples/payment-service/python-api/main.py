"""Minimal FastAPI service consuming errlex-generated Python errors."""

from __future__ import annotations

from errors import PaymentDeclinedError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="example payment service")


@app.exception_handler(PaymentDeclinedError)
async def payment_declined_handler(
    request: Request, exc: PaymentDeclinedError
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "code": exc.code,
            "message": str(exc),
            "retryable": exc.retryable,
        },
    )


@app.post("/payments")
async def create_payment() -> dict[str, str]:
    raise PaymentDeclinedError()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
