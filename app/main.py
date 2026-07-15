from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.database.database import create_tables
import app.models

from app.routers import home
from app.routers import auth
from app.routers import dashboard
from app.routers import resume
from app.routers import analysis
from app.routers import features

# Create Database Tables
create_tables()

app = FastAPI(
    title=settings.APP_NAME,
    description="Production Level AI Resume Analyzer",
    version=settings.APP_VERSION
)

# ------------------------------------
# Rate Limiter Setup
# ------------------------------------

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

# No Cache Middleware
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

# Static Files
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# Templates (Single Instance)
templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates

# Routers
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(resume.router)
app.include_router(analysis.router)
app.include_router(features.router)

# Health Check
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "project": settings.APP_NAME
    }