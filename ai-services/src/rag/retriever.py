from typing import List, Dict
from src.vector_store.client import VectorStoreClient
from src.rag.embeddings import DocumentEmbedder
from src.config import settings

class DocumentRetriever:
    """Retrieves relevant documents from vector store"""
    
    def __init__(self):
        self.vector_store = VectorStoreClient()
        self.embedder = DocumentEmbedder()
    
    async def retrieve(self, query: str, top_k: int = None) -> List[Dict]:
        """Retrieve relevant documents for a query"""
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = await self.embedder.embed_text(query)
        
        # Search vector store
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            threshold=settings.SIMILARITY_THRESHOLD
        )
        
        return results
    
    async def retrieve_with_filter(
        self, 
        query: str, 
        filters: Dict,
        top_k: int = None
    ) -> List[Dict]:
        """Retrieve documents with metadata filtering"""
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        query_embedding = await self.embedder.embed_text(query)
        
        results = await self.vector_store.search_with_filter(
            query_embedding=query_embedding,
            filters=filters,
            top_k=top_k
        )
        
        return results
