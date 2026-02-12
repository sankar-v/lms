from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import Graph, StateGraph
from .qa_agent import QAAgent
from .recommendation_agent import RecommendationAgent

class AgentOrchestrator:
    """Orchestrates LangGraph agents for chat and recommendations"""
    
    def __init__(self):
        self.qa_agent = QAAgent()
        self.recommendation_agent = RecommendationAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> Graph:
        """Build the LangGraph workflow"""
        # TODO: Implement LangGraph workflow
        # This will define the agent routing and state management
        pass
    
    async def handle_chat(
        self, 
        question: str, 
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Route chat questions to QA agent"""
        return await self.qa_agent.answer_question(question, history)
    
    async def handle_recommendations(self, user_id: int) -> Dict[str, Any]:
        """Route recommendation requests to recommendation agent"""
        return await self.recommendation_agent.generate_recommendations(user_id)
    
    def _determine_agent(self, query: str) -> str:
        """Determine which agent should handle the query"""
        # Simple routing logic - can be enhanced with LLM
        recommendation_keywords = ["recommend", "suggest", "what should i learn", "next"]
        if any(keyword in query.lower() for keyword in recommendation_keywords):
            return "recommendation"
        return "qa"
