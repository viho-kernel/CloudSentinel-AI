import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import Counter, Histogram

# Prometheus Metrics Definitions
HTTP_REQUESTS_TOTAL = Counter(
    "cloudsentinel_http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status_code", "environment"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "cloudsentinel_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint", "environment"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

VULNERABILITIES_DETECTED_TOTAL = Counter(
    "cloudsentinel_vulnerabilities_detected_total",
    "Total vulnerabilities discovered by the scanner engine",
    ["severity", "iac_type", "rule_id"]
)

AI_REMEDIATIONS_TOTAL = Counter(
    "cloudsentinel_ai_remediations_total",
    "Total AI remediations requested and generated",
    ["status"]
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces OWASP-recommended HTTP security response headers."""
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com fonts.googleapis.com fonts.gstatic.com; "
            "img-src 'self' data: https:;"
        )
        return response

class MetricsMiddleware(BaseHTTPMiddleware):
    """Measures latency and request counts for Prometheus observability."""
    def __init__(self, app, environment: str):
        super().__init__(app)
        self.environment = environment

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        endpoint = request.url.path

        # Ignore noisy health check and metrics polling from bloating duration histograms
        if endpoint in ["/metrics", "/healthz"]:
            return await call_next(request)

        try:
            response = await call_next(request)
            status_code = str(response.status_code)
        except Exception as exc:
            status_code = "500"
            raise exc from None
        finally:
            duration = time.time() - start_time
            method = request.method
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                environment=self.environment
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                endpoint=endpoint,
                environment=self.environment
            ).observe(duration)

        return response
