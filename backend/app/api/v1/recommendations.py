from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.config import settings
import httpx

router = APIRouter()

@router.get("/user/{user_id}")
async def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """Get personalized learning recommendations for a user"""
    try:
        # Call AI service for recommendations
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/recommendations",
                json={"user_id": user_id}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/feedback")
async def submit_feedback(user_id: int, module_id: int, rating: int):
    """Submit feedback on a recommendation"""
    # Store feedback for improving recommendations
    return {"message": "Feedback recorded", "user_id": user_id, "module_id": module_id}
