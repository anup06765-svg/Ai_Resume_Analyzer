from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.database.database import create_tables
import app.models

from app.routers import home
from app.routers import auth
from app.routers import dashboard
from app.routers import resume
from app.routers import analysis

# Create Database Tables
create_tables()

app = FastAPI(
    title="AI Resume Analyzer",
    description="Production Level AI Resume Analyzer",
    version="2.0"
)

# Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"
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

# Uploaded Files
app.mount(
    "/uploads",
    StaticFiles(directory="app/uploads"),
    name="uploads"
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

# Health Check
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "project": "AI Resume Analyzer"
    }