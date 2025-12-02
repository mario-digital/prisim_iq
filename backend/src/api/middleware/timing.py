"""Request timing middleware."""

import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware that adds X-Process-Time header to responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add processing time header to response."""
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        # Add timing header
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        return response

