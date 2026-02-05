from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from src.config import settings

class VectorStoreClient:
    """Client for vector database operations (Qdrant)"""
    
    def __init__(self):
        self.client = QdrantClient(
            host=settings.VECTOR_DB_HOST,
            port=settings.VECTOR_DB_PORT
        )
        self.collection_name = settings.VECTOR_DB_COLLECTION
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
    
    async def insert(self, documents: List[Dict]):
        """Insert documents with embeddings into vector store"""
        points = []
        for i, doc in enumerate(documents):
            point = PointStruct(
                id=doc.get("id", i),
                vector=doc["embedding"],
                payload={
                    "text": doc["text"],
                    "source": doc.get("source", ""),
                    "metadata": doc.get("metadata", {})
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    async def search(
        self, 
        query_embedding: List[float],
        top_k: int,
        threshold: float = 0.0
    ) -> List[Dict]:
        """Search for similar documents"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=threshold
        )
        
        return [
            {
                "text": hit.payload["text"],
                "source": hit.payload["source"],
                "metadata": hit.payload.get("metadata", {}),
                "score": hit.score
            }
            for hit in results
        ]
    
    async def search_with_filter(
        self,
        query_embedding: List[float],
        filters: Dict,
        top_k: int
    ) -> List[Dict]:
        """Search with metadata filtering"""
        # TODO: Implement filter construction based on filters dict
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        
        return [
            {
                "text": hit.payload["text"],
                "source": hit.payload["source"],
                "metadata": hit.payload.get("metadata", {}),
                "score": hit.score
            }
            for hit in results
        ]
    
    def delete_collection(self):
        """Delete the collection"""
        self.client.delete_collection(collection_name=self.collection_name)
