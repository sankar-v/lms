from typing import List, Dict, Optional
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from src.config import settings

logger = logging.getLogger(__name__)


class VectorStoreClient:
    """Client for vector database operations using PostgreSQL with pgvector"""
    
    def __init__(self):
        self.engine = create_engine(
            settings.DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
    
    async def insert(
        self,
        documents: List[Dict],
        batch_size: int = 100,
    ) -> int:
        """
        Insert documents with embeddings into vector store.
        
        Args:
            documents: List of dicts with 'content', 'embedding', 'document_id', 'chunk_id', 'metadata'
            batch_size: Number of documents to insert per batch
            
        Returns:
            Number of documents inserted
        """
        session = self.SessionLocal()
        inserted_count = 0
        
        try:
            # Process in batches for better performance
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                for doc in batch:
                    query = text("""
                        INSERT INTO document_embeddings 
                        (content, embedding, document_id, chunk_id, source, metadata)
                        VALUES (:content, :embedding, :document_id, :chunk_id, :source, :metadata)
                        ON CONFLICT (chunk_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata,
                            updated_at = CURRENT_TIMESTAMP
                    """)
                    session.execute(query, {
                        "content": doc["content"],
                        "embedding": doc["embedding"],
                        "document_id": doc.get("document_id", ""),
                        "chunk_id": doc.get("chunk_id", ""),
                        "source": doc.get("source", ""),
                        "metadata": doc.get("metadata", {})
                    })
                    inserted_count += 1
                
                session.commit()
                logger.info(f"Inserted batch {i // batch_size + 1}, total: {inserted_count}")
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting documents: {e}")
            raise
        finally:
            session.close()
        
        return inserted_count
    
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
            logger.info("Deleted all documents from vector store")
        finally:
            session.close()
    
    def delete_by_document_id(self, document_id: str) -> int:
        """
        Delete all chunks for a specific document.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            Number of chunks deleted
        """
        session = self.SessionLocal()
        try:
            query = text("""
                DELETE FROM document_embeddings
                WHERE document_id = :document_id
            """)
            result = session.execute(query, {"document_id": document_id})
            session.commit()
            deleted_count = result.rowcount
            logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
            return deleted_count
        finally:
            session.close()
    
    def delete_by_source(self, source: str) -> int:
        """
        Delete all documents from a specific source.
        
        Args:
            source: Source path to delete
            
        Returns:
            Number of documents deleted
        """
        session = self.SessionLocal()
        try:
            query = text("""
                DELETE FROM document_embeddings
                WHERE source = :source
            """)
            result = session.execute(query, {"source": source})
            session.commit()
            deleted_count = result.rowcount
            logger.info(f"Deleted {deleted_count} chunks from source {source}")
            return deleted_count
        finally:
            session.close()
    
    def get_document_count(self) -> int:
        """Get total number of document chunks."""
        session = self.SessionLocal()
        try:
            query = text("SELECT COUNT(*) as count FROM document_embeddings")
            result = session.execute(query)
            return result.fetchone().count
        finally:
            session.close()
    
    def list_documents(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        List documents with pagination.
        
        Args:
            limit: Maximum number of documents to return
            offset: Number of documents to skip
            
        Returns:
            List of document metadata
        """
        session = self.SessionLocal()
        try:
            query = text("""
                SELECT DISTINCT document_id, source, metadata, created_at
                FROM document_embeddings
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            result = session.execute(query, {"limit": limit, "offset": offset})
            
            return [
                {
                    "document_id": row.document_id,
                    "source": row.source,
                    "metadata": row.metadata,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
                for row in result
            ]
        finally:
            session.close()
    
    def get_document_info(self, document_id: str) -> Optional[Dict]:
        """
        Get information about a specific document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document info or None if not found
        """
        session = self.SessionLocal()
        try:
            query = text("""
                SELECT 
                    document_id,
                    source,
                    metadata,
                    COUNT(*) as chunk_count,
                    MIN(created_at) as created_at
                FROM document_embeddings
                WHERE document_id = :document_id
                GROUP BY document_id, source, metadata
            """)
            result = session.execute(query, {"document_id": document_id})
            row = result.fetchone()
            
            if not row:
                return None
            
            return {
                "document_id": row.document_id,
                "source": row.source,
                "metadata": row.metadata,
                "chunk_count": row.chunk_count,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
        finally:
            session.close()
