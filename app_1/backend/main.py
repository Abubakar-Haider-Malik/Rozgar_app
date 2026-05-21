"""
Service Marketplace — FastAPI Application Entry Point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.routers.api import router
from backend.static_ui import HTML_CONTENT

app = FastAPI(
    title="Service Marketplace",
    description="AI-powered service orchestration for Pakistan's informal economy",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend dev server and production domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routes under /api/v1 (Must be before static mount)
app.include_router(router, prefix="/api/v1", tags=["Service Marketplace"])

@app.get("/")
async def root():
    return HTMLResponse(content=HTML_CONTENT)
