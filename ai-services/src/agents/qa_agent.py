from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from ..rag.retriever import DocumentRetriever
from ..rag.generator import AnswerGenerator
from ..config import settings

class QAAgent:
    """Agent for handling Q&A using RAG pipeline"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.retriever = DocumentRetriever()
        self.generator = AnswerGenerator(self.llm)
        
        self.system_prompt = """You are a helpful AI assistant for an engineering platform learning system.
Your role is to answer questions about:
- Platform policies and guidelines
- Engineering tech stack and reference architectures
- Internal best practices, patterns, and playbooks

Always ground your answers in the provided documentation. If you cannot find relevant information
in the documentation, clearly state that you don't have that information.
Be concise, accurate, and helpful."""
    
    async def answer_question(
        self, 
        question: str, 
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Answer a question using RAG pipeline"""
        try:
            # Retrieve relevant documents
            retrieved_docs = await self.retriever.retrieve(question)
            
            # Generate answer with context
            answer = await self.generator.generate(
                question=question,
                context=retrieved_docs,
                history=history,
                system_prompt=self.system_prompt
            )
            
            return {
                "answer": answer["text"],
                "sources": answer["sources"],
                "confidence": answer["confidence"]
            }
        except Exception as e:
            return {
                "answer": f"I encountered an error: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
