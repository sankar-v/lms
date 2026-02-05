from typing import List, Dict, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from src.config import settings

class VectorStoreClient:
    """Client for vector database operations using PostgreSQL with pgvector"""
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    async def insert(self, documents: List[Dict]):
        """Insert documents with embeddings into vector store"""
        session = self.SessionLocal()
        try:
            for doc in documents:
                query = text("""
                    INSERT INTO document_embeddings (content, embedding, source, metadata)
                    VALUES (:content, :embedding, :source, :metadata)
                """)
                session.execute(query, {
                    "content": doc["text"],
                    "embedding": doc["embedding"],
                    "source": doc.get("source", ""),
                    "metadata": doc.get("metadata", {})
                })
            session.commit()
        finally:
            session.close()
    
    async def search(
        self, 
        query_embedding: List[float],
        top_k: int,
        threshold: float = 0.0
    ) -> List[Dict]:
        """Search for similar documents using cosine similarity"""
        session = self.SessionLocal()
        try:
            # Convert threshold to similarity score (1 - distance)
            # For cosine similarity: similarity = 1 - cosine_distance
            query = text("""
                SELECT 
                    content,
                    source,
                    metadata,
                    1 - (embedding <=> :embedding) as score
                FROM document_embeddings
                WHERE 1 - (embedding <=> :embedding) >= :threshold
                ORDER BY embedding <=> :embedding
                LIMIT :limit
            """)
            
            result = session.execute(query, {
                "embedding": str(query_embedding),
                "threshold": threshold,
                "limit": top_k
            })
            
            return [
                {
                    "text": row.content,
                    "source": row.source,
                    "metadata": row.metadata,
                    "score": float(row.score)
                }
                for row in result
            ]
        finally:
            session.close()
    
    async def search_with_filter(
        self,
        query_embedding: List[float],
        filters: Dict,
        top_k: int
    ) -> List[Dict]:
        """Search with metadata filtering"""
        session = self.SessionLocal()
        try:
            # Build filter conditions from filters dict
            filter_conditions = []
            params = {
                "embedding": str(query_embedding),
                "limit": top_k
            }
            
            for key, value in filters.items():
                filter_conditions.append(f"metadata->>'{key}' = :{key}")
                params[key] = value
            
            where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"
            
            query = text(f"""
                SELECT 
                    content,
                    source,
                    metadata,
                    1 - (embedding <=> :embedding) as score
                FROM document_embeddings
                WHERE {where_clause}
                ORDER BY embedding <=> :embedding
                LIMIT :limit
            """)
            
            result = session.execute(query, params)
            
            return [
                {
                    "text": row.content,
                    "source": row.source,
                    "metadata": row.metadata,
                    "score": float(row.score)
                }
                for row in result
            ]
        finally:
            session.close()
    
    def delete_all(self):
        """Delete all documents"""
        session = self.SessionLocal()
        try:
            query = text("DELETE FROM document_embeddings")
            session.execute(query)
            session.commit()
        finally:
            session.close()
