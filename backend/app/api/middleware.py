"""ASGI middleware that logs one line per HTTP request.

Standard library `logging`, not a request-logging framework, is enough here: one
INFO/WARNING/ERROR line per request with method, path, status, duration and a
request id is all a small API needs, and it keeps the request log in the same
format and destination as every other log line (see app/core/logging.py).
"""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

logger = logging.getLogger("app.http")

_REQUEST_ID_HEADER = "X-Request-ID"


async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Log the request/response and attach a request id for tracing.

    The request id is read from an incoming `X-Request-ID` header if the client (or
    a load balancer) already set one, otherwise generated here; either way it's
    echoed back in the response header and exposed via `request.state.request_id`
    so an exception handler can log the same id against a failure.
    """
    request_id = request.headers.get(_REQUEST_ID_HEADER, str(uuid.uuid4()))
    request.state.request_id = request_id
    client_host = request.client.host if request.client else "-"
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "%s %s %s -> unhandled exception (%.1fms) [%s]",
            client_host,
            request.method,
            request.url.path,
            duration_ms,
            request_id,
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    response.headers[_REQUEST_ID_HEADER] = request_id

    log = logger.info
    if response.status_code >= 500:
        log = logger.error
    elif response.status_code >= 400:
        log = logger.warning

    log(
        "%s %s %s -> %d (%.1fms) [%s]",
        client_host,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response
