from pydantic import BaseModel

class IngestRequest(BaseModel):
    url: str

class IngestResponse(BaseModel):
    message: str
    video_id: str

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
