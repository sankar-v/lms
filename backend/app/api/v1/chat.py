from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.core.config import settings
import httpx

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    conversation_history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    confidence: float = 0.0

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a question to the RAG-based Q&A assistant"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/chat",
                json={
                    "question": request.question,
                    "conversation_history": [msg.dict() for msg in request.conversation_history]
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.get("/history/{user_id}")
async def get_chat_history(user_id: int):
    """Get chat history for a user"""
    # TODO: Implement chat history retrieval
    return {"user_id": user_id, "messages": []}
