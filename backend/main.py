"""
FastAPI application entry point for Single-Video Twin AI.

Serves both the REST API for video ingestion/chat and the static frontend UI.
Configured for deployment on Google Cloud Run with CORS support.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

# Load environment variables from .env file (local development)
# In production (Cloud Run), env vars are injected via deployment config
load_dotenv(dotenv_path="backend/.env")

app = FastAPI(
    title="Single-Video Twin API",
    description="Transform YouTube videos into conversational AI agents using RAG",
    version="1.0.0"
)

# CORS configuration for cross-origin requests
# Allows frontend (served from different origin in dev) to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register API routes
from backend.app.api.endpoints import router
app.include_router(router)

# Static file serving for frontend assets
# Must be mounted BEFORE catch-all routes to ensure proper routing precedence
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the main UI page."""
    return FileResponse('frontend/index.html')

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancer probes.
    
    Returns:
        dict: Status indicator for service health
    """
    return {"status": "healthy"}
