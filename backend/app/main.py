from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

app.include_router(health_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Incident Memory API",
        "docs": "/docs",
        "health": "/health",
    }
