import os
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.core.config import settings
from app.core.security import SecurityHeadersMiddleware, MetricsMiddleware
from app.api.routes import router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Cloud Security & DevSecOps Platform powered by Google Gemini",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. Add Security & Observability Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(MetricsMiddleware, environment=settings.ENVIRONMENT)

# 2. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Mount Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 4. Prometheus Metrics Endpoint
@app.get("/metrics", tags=["SRE & Observability"])
async def prometheus_metrics():
    """Prometheus scraper endpoint exposing SRE Golden Signals and scan counters."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# 5. Root Web Dashboard
@app.get("/", include_in_schema=False)
async def serve_dashboard():
    """Serves the primary DevSecOps Cyber Dashboard."""
    index_file = os.path.join(static_dir, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    return Response(content=html_content, media_type="text/html")

# 6. Include API Routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
