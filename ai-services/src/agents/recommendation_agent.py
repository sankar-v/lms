from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from src.config import settings
import httpx

class RecommendationAgent:
    """Agent for generating personalized learning recommendations"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.system_prompt = """You are an AI learning advisor for an engineering platform.
Your role is to recommend personalized learning paths based on:
- User's current role and skills
- Learning history and progress
- Available modules and their prerequisites
- Best practices for skill development

Provide thoughtful, sequenced recommendations that build upon existing knowledge."""
    
    async def generate_recommendations(self, user_id: int) -> Dict[str, Any]:
        """Generate personalized learning recommendations for a user"""
        try:
            # Fetch user data from backend
            user_data = await self._fetch_user_data(user_id)
            progress_data = await self._fetch_progress_data(user_id)
            available_modules = await self._fetch_available_modules()
            
            # Use LLM to analyze and recommend
            recommendations = await self._analyze_and_recommend(
                user_data=user_data,
                progress=progress_data,
                modules=available_modules
            )
            
            return {
                "recommendations": recommendations["modules"],
                "reasoning": recommendations["reasoning"]
            }
        except Exception as e:
            return {
                "recommendations": [],
                "reasoning": f"Error generating recommendations: {str(e)}"
            }
    
    async def _fetch_user_data(self, user_id: int) -> Dict:
        """Fetch user profile data from backend"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.BACKEND_API_URL}/api/v1/users/{user_id}")
            return response.json()
    
    async def _fetch_progress_data(self, user_id: int) -> List[Dict]:
        """Fetch user's learning progress from backend"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.BACKEND_API_URL}/api/v1/progress/user/{user_id}")
            return response.json()
    
    async def _fetch_available_modules(self) -> List[Dict]:
        """Fetch available learning modules from backend"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.BACKEND_API_URL}/api/v1/modules/")
            return response.json()
    
    async def _analyze_and_recommend(
        self,
        user_data: Dict,
        progress: List[Dict],
        modules: List[Dict]
    ) -> Dict[str, Any]:
        """Use LLM to analyze user state and recommend modules"""
        # TODO: Implement LLM-based recommendation logic
        # For now, return placeholder
        return {
            "modules": modules[:3],  # Top 3 modules
            "reasoning": "Based on your role and current progress"
        }
