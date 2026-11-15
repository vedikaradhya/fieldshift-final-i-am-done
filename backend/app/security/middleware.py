"""HTTP security controls suitable for the local API profile.

Rate limiting is intentionally process-local. Production must use the documented
Redis-backed limiter so multiple API processes share the same counters.
"""
from collections import defaultdict, deque
from time import monotonic
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), camera=(), microphone=()"
        response.headers["Cross-Origin-Resource-Policy"] = "same-site"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RequestLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_bytes: int = 1_000_000):
        super().__init__(app); self.max_bytes = max_bytes
    async def dispatch(self, request: Request, call_next) -> Response:
        length = request.headers.get("content-length")
        if length and int(length) > self.max_bytes:
            return JSONResponse({"detail": "Request body too large"}, status_code=413)
        return await call_next(request)


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, attempts: int = 8, window_seconds: int = 60):
        super().__init__(app); self.attempts = attempts; self.window_seconds = window_seconds; self.events: dict[str, deque[float]] = defaultdict(deque)
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path.endswith(("/auth/login", "/auth/register", "/auth/forgot-password")):
            host = request.client.host if request.client else "unknown"
            now, bucket = monotonic(), self.events[host]
            while bucket and bucket[0] <= now - self.window_seconds: bucket.popleft()
            if len(bucket) >= self.attempts:
                return JSONResponse({"detail": "Too many authentication attempts. Try again shortly."}, status_code=429, headers={"Retry-After": str(self.window_seconds)})
            bucket.append(now)
        return await call_next(request)
