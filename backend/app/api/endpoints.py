"""
API endpoints for video ingestion and conversational chat.

Provides RESTful interface for:
- POST /ingest: Process YouTube video and store transcript
- POST /chat: Query ingested video content via RAG pipeline
"""

from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import IngestRequest, IngestResponse, ChatRequest, ChatResponse
from backend.app.services.ingestion import IngestionService
from backend.app.services.rag_service import RAGService

router = APIRouter()

# Singleton service instances for POC
# Production: Consider dependency injection or session-based instances
ingestion_service = IngestionService()
rag_service = RAGService()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_video(request: IngestRequest):
    """
    Extract and store YouTube video transcript for semantic search.
    
    Process flow:
        1. Validate YouTube URL format
        2. Fetch transcript using yt-dlp
        3. Split into semantic chunks
        4. Generate embeddings and store in vector database
        
    Args:
        request: IngestRequest containing YouTube URL
        
    Returns:
        IngestResponse with success message and video ID
        
    Raises:
        HTTPException 500: If transcript extraction or storage fails
        
    Note:
        This overwrites any previously ingested video (single-video limitation).
        For multi-video support, implement session-based vector stores.
    """
    try:
        # Extract transcript and chunk for optimal retrieval
        chunks = ingestion_service.process_video(request.url)
        
        # Store chunks in vector database with embeddings
        rag_service.ingest_chunks(chunks)
        
        # Extract video ID for response tracking
        video_id = ingestion_service._extract_video_id(request.url)
        
        return IngestResponse(
            message="Video ingested successfully", 
            video_id=video_id or "unknown"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Answer user questions using RAG over ingested video transcript.
    
    Process flow:
        1. Validate that video has been ingested
        2. Perform semantic search for relevant chunks
        3. Generate context-grounded answer via LLM
        4. Return answer in speaker's tone
        
    Args:
        request: ChatRequest containing user question
        
    Returns:
        ChatResponse with AI-generated answer
        
    Raises:
        HTTPException 400: If no video has been ingested yet
        
    Note:
        Answers are strictly grounded in transcript context to prevent hallucination.
        System prompt enforces first-person perspective matching video speaker.
    """
    # Validate that vector store has been populated
    if not rag_service.vector_store_service.vector_store:
        raise HTTPException(
            status_code=400, 
            detail="No video ingested. Please ingest a video first."
        )
    
    # Execute RAG pipeline: retrieve + generate
    answer = rag_service.ask_question(request.question)
    
    return ChatResponse(answer=answer)
