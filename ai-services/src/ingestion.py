"""Ingestion pipeline orchestrator."""

import asyncio
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import logging
import uuid

from .document_processor import DocumentLoader, DocumentChunker, Document
from .embeddings import EmbeddingService
from .vector_store.client import VectorStoreClient
from .document_processor.models import IngestionTask, ProcessingStatus

logger = logging.getLogger(__name__)


class IngestionOrchestrator:
    """
    Orchestrates the end-to-end document ingestion pipeline.
    
    Workflow:
    1. Load document from file
    2. Chunk document into smaller pieces
    3. Generate embeddings for chunks
    4. Store chunks and embeddings in vector database
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_batch_size: int = 100,
    ):
        """
        Initialize ingestion orchestrator.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            embedding_batch_size: Batch size for embedding generation
        """
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.embedding_service = EmbeddingService(
            batch_size=embedding_batch_size
        )
        self.vector_store = VectorStoreClient()
        self._tasks: Dict[str, IngestionTask] = {}
    
    async def ingest_document(
        self,
        file_path: str,
        metadata_overrides: Optional[Dict] = None,
        task_id: Optional[str] = None,
    ) -> IngestionTask:
        """
        Ingest a single document through the full pipeline.
        
        Args:
            file_path: Path to document file
            metadata_overrides: Additional metadata to add/override
            task_id: Optional task ID for tracking
            
        Returns:
            IngestionTask with status and progress
        """
        # Create task
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        task = IngestionTask(
            task_id=task_id,
            document_path=file_path,
            status=ProcessingStatus.PENDING,
        )
        self._tasks[task_id] = task
        
        try:
            task.status = ProcessingStatus.PROCESSING
            logger.info(f"Starting ingestion of {file_path}")
            
            # Step 1: Load document
            logger.info(f"Loading document: {file_path}")
            document = self.loader.load(
                file_path,
                **(metadata_overrides or {})
            )
            
            # Step 2: Chunk document
            logger.info(f"Chunking document: {document.document_id}")
            chunks = self.chunker.chunk(document)
            task.total_chunks = len(chunks)
            
            # Step 3: Generate embeddings
            logger.info(
                f"Generating embeddings for {len(chunks)} chunks"
            )
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_service.embed_batch(
                chunk_texts,
                show_progress=True,
            )
            
            # Step 4: Prepare documents for vector store
            vector_docs = []
            for chunk, embedding in zip(chunks, embeddings):
                vector_docs.append({
                    "content": chunk.content,
                    "embedding": embedding,
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.chunk_id,
                    "source": chunk.metadata.source,
                    "metadata": chunk.metadata.to_dict(),
                })
            
            # Step 5: Insert into vector store
            logger.info(f"Inserting {len(vector_docs)} chunks into vector store")
            inserted_count = await self.vector_store.insert(vector_docs)
            
            task.processed_chunks = inserted_count
            task.status = ProcessingStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            logger.info(
                f"Successfully ingested {file_path}: "
                f"{inserted_count} chunks"
            )
            
        except Exception as e:
            task.status = ProcessingStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            logger.error(f"Failed to ingest {file_path}: {e}", exc_info=True)
            raise
        
        return task
    
    async def ingest_directory(
        self,
        directory_path: str,
        pattern: str = "*.*",
        recursive: bool = True,
        metadata_overrides: Optional[Dict] = None,
    ) -> List[IngestionTask]:
        """
        Ingest all documents in a directory.
        
        Args:
            directory_path: Path to directory
            pattern: File pattern to match (e.g., "*.pdf")
            recursive: Whether to search recursively
            metadata_overrides: Metadata to add to all documents
            
        Returns:
            List of ingestion tasks
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find matching files
        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))
        
        logger.info(
            f"Found {len(files)} files matching pattern '{pattern}' "
            f"in {directory_path}"
        )
        
        # Ingest files concurrently (with semaphore to limit parallelism)
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent ingestions
        
        async def ingest_with_limit(file_path: Path):
            async with semaphore:
                try:
                    return await self.ingest_document(
                        str(file_path),
                        metadata_overrides=metadata_overrides,
                    )
                except Exception as e:
                    logger.error(f"Failed to ingest {file_path}: {e}")
                    return None
        
        tasks = await asyncio.gather(
            *[ingest_with_limit(f) for f in files],
            return_exceptions=True,
        )
        
        # Filter out failed tasks
        successful_tasks = [t for t in tasks if isinstance(t, IngestionTask)]
        
        logger.info(
            f"Completed directory ingestion: "
            f"{len(successful_tasks)}/{len(files)} successful"
        )
        
        return successful_tasks
    
    def get_task_status(self, task_id: str) -> Optional[IngestionTask]:
        """Get status of an ingestion task."""
        return self._tasks.get(task_id)
    
    def list_tasks(self) -> List[IngestionTask]:
        """List all ingestion tasks."""
        return list(self._tasks.values())
    
    async def delete_document(self, document_id: str) -> int:
        """
        Delete a document from the vector store.
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            Number of chunks deleted
        """
        return self.vector_store.delete_by_document_id(document_id)
    
    async def delete_by_source(self, source: str) -> int:
        """
        Delete documents by source path.
        
        Args:
            source: Source path
            
        Returns:
            Number of chunks deleted
        """
        return self.vector_store.delete_by_source(source)
    
    def get_stats(self) -> Dict:
        """Get ingestion statistics."""
        return {
            "total_documents": self.vector_store.get_document_count(),
            "total_tasks": len(self._tasks),
            "completed_tasks": len([
                t for t in self._tasks.values()
                if t.status == ProcessingStatus.COMPLETED
            ]),
            "failed_tasks": len([
                t for t in self._tasks.values()
                if t.status == ProcessingStatus.FAILED
            ]),
            "pending_tasks": len([
                t for t in self._tasks.values()
                if t.status in [ProcessingStatus.PENDING, ProcessingStatus.PROCESSING]
            ]),
        }
    
    async def close(self):
        """Close all connections."""
        await self.embedding_service.close()
