from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from src.agents.orchestrator import AgentOrchestrator
from src.config import settings

app = FastAPI(
    title="LMS AI Services",
    description="AI Services for LMS - RAG and Recommendations",
    version="1.0.0"
)

orchestrator = AgentOrchestrator()

class ChatRequest(BaseModel):
    question: str
    conversation_history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    confidence: float = 0.0

class RecommendationRequest(BaseModel):
    user_id: int

class RecommendationResponse(BaseModel):
    recommendations: List[Dict]
    reasoning: str

@app.get("/")
async def root():
    return {"message": "LMS AI Services is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat questions using RAG pipeline"""
    result = await orchestrator.handle_chat(
        question=request.question,
        history=request.conversation_history
    )
    return result

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Generate personalized learning recommendations"""
    result = await orchestrator.handle_recommendations(user_id=request.user_id)
    return result

@app.post("/embed")
async def embed_documents(documents: List[str]):
    """Embed documents for vector search"""
    # TODO: Implement document embedding
    return {"message": f"Embedded {len(documents)} documents"}
