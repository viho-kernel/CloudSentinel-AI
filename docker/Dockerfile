# ==============================================================
# CloudSentinel AI - Production Hardened Multi-Stage Dockerfile
# Follows CIS Docker Benchmark 4.1, 4.6 & OWASP Container Security
# ==============================================================

# Stage 1: Build & Dependency Resolution
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies safely
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Minimal Distroless/Slim Production Runtime
FROM python:3.12-slim AS runtime

# Security: Set working directory
WORKDIR /app

# Security: Create non-root system user and group (UID/GID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -d /app appuser

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application source code
COPY --chown=appuser:appgroup app /app/app

# Security: Switch to unprivileged non-root user
USER 10001:10001

# Expose microservice port (GCP Cloud Run standard)
EXPOSE 8080

# Production Healthcheck Probe (CIS Docker Benchmark 4.6)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')" || exit 1

# Launch production server via Uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
