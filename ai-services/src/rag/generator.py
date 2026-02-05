from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

class AnswerGenerator:
    """Generates answers using LLM with retrieved context"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    async def generate(
        self,
        question: str,
        context: List[Dict],
        history: List[Dict[str, str]],
        system_prompt: str
    ) -> Dict[str, Any]:
        """Generate an answer using RAG"""
        
        # Format context
        context_text = self._format_context(context)
        
        # Build messages
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history
        for msg in history[-5:]:  # Keep last 5 messages
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # Add current question with context
        prompt = f"""Based on the following documentation, please answer the question.

Documentation:
{context_text}

Question: {question}

Answer:"""
        
        messages.append(HumanMessage(content=prompt))
        
        # Generate response
        response = await self.llm.ainvoke(messages)
        
        # Extract sources
        sources = [doc.get("source", "unknown") for doc in context]
        
        return {
            "text": response.content,
            "sources": list(set(sources)),
            "confidence": self._calculate_confidence(context)
        }
    
    def _format_context(self, context: List[Dict]) -> str:
        """Format retrieved documents into a single context string"""
        formatted = []
        for i, doc in enumerate(context, 1):
            text = doc.get("text", "")
            source = doc.get("source", "unknown")
            formatted.append(f"[Document {i}] (Source: {source})\n{text}\n")
        return "\n".join(formatted)
    
    def _calculate_confidence(self, context: List[Dict]) -> float:
        """Calculate confidence score based on retrieval results"""
        if not context:
            return 0.0
        
        # Use average similarity score as confidence
        scores = [doc.get("score", 0.0) for doc in context]
        return sum(scores) / len(scores) if scores else 0.0
