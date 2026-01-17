"""FastAPI application for Anki card review web interface."""

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .routes import cards, anki, generate, files

# Global activity tracker for idle detection
_last_activity: float = time.time()

app = FastAPI(
    title="Anki Card Review API",
    description="Web interface for reviewing and adding Anki flashcards",
    version="0.1.0",
)

# CORS middleware for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
        # TODO: Parameterize this for production deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cards.router, prefix="/api/cards", tags=["cards"])
app.include_router(anki.router, prefix="/api/anki", tags=["anki"])
app.include_router(generate.router, prefix="/api", tags=["generation"])
app.include_router(files.router, prefix="/api/files", tags=["files"])


@app.middleware("http")
async def track_activity(request: Request, call_next):
    """Track last API activity for idle detection."""
    global _last_activity
    _last_activity = time.time()
    return await call_next(request)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/activity")
async def get_activity():
    """Return timestamp of last API activity for idle detection."""
    return {"last_activity": _last_activity}
