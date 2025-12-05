from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

app = FastAPI(title="Single-Video Twin API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.app.api.endpoints import router

app.include_router(router)

# Mount static files BEFORE defining routes
# This ensures /static/* is matched before the root catch-all
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse('frontend/index.html')

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
