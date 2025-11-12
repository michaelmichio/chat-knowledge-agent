from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import get_settings
from core.logger import logger
from core.exceptions import register_exception_handlers
from domain.documents.routes import router as docs_router

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)

# --- CORS setup
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register global error handler
register_exception_handlers(app)

app.include_router(docs_router)

# --- Root endpoint (health check)
@app.get("/health")
def health_check():
    logger.info("Health check pinged")
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}
