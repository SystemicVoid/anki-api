"""FastAPI application for Anki card review web interface."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import cards, anki

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


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
