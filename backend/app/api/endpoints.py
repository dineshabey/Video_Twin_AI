from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import IngestRequest, IngestResponse, ChatRequest, ChatResponse
from backend.app.services.ingestion import IngestionService
from backend.app.services.rag_service import RAGService

router = APIRouter()

# Global Services (singleton for this POC)
ingestion_service = IngestionService()
rag_service = RAGService()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_video(request: IngestRequest):
    try:
        chunks = ingestion_service.process_video(request.url)
        rag_service.ingest_chunks(chunks)
        
        # Extract video ID for response (optional, can be improved)
        video_id = ingestion_service._extract_video_id(request.url)
        return IngestResponse(message="Video ingested successfully", video_id=video_id or "unknown")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not rag_service.vector_store_service.vector_store:
        raise HTTPException(status_code=400, detail="No video ingested. Please ingest a video first.")
    
    answer = rag_service.ask_question(request.question)
    return ChatResponse(answer=answer)
