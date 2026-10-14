from fastapi import FastAPI
from api.v1.router import router as v1_router
from core.config import settings
from core.logging import configure_logging
from core.lifespan import lifespan
from middleware import AccessLogMiddleware

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME, 
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.include_router(v1_router)
app.add_middleware(AccessLogMiddleware)