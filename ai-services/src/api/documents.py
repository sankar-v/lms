"""FastAPI routes for document ingestion."""

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import tempfile
from pathlib import Path
import logging

from ..ingestion import IngestionOrchestrator
from ..document_processor.models import ProcessingStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

# Global orchestrator instance
orchestrator = IngestionOrchestrator()


class IngestionRequest(BaseModel):
    """Request model for directory ingestion."""
    directory_path: str
    pattern: str = "*.*"
    recursive: bool = True
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class IngestionResponse(BaseModel):
    """Response model for ingestion tasks."""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response model for task status."""
    task_id: str
    status: str
    document_path: str
    total_chunks: int
    processed_chunks: int
    progress_percentage: float
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class DocumentInfo(BaseModel):
    """Document information response."""
    document_id: str
    source: str
    chunk_count: int
    created_at: Optional[str] = None
    metadata: dict


class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    top_k: int = 5
    threshold: float = 0.7
    filters: Optional[dict] = None


class SearchResult(BaseModel):
    """Search result model."""
    content: str
    source: str
    score: float
    metadata: dict


@router.post("/upload", response_model=IngestionResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: Optional[str] = None,
    tags: Optional[str] = None,
):
    """
    Upload and ingest a document asynchronously.
    
    The document will be processed in the background, and you can check
    the status using the returned task_id.
    """
    try:
        # Save uploaded file to temp directory
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Parse tags if provided
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        
        metadata_overrides = {}
        if category:
            metadata_overrides["category"] = category
        if tag_list:
            metadata_overrides["tags"] = tag_list
        
        # Create background task
        import uuid
        task_id = str(uuid.uuid4())
        
        async def ingest_task():
            try:
                await orchestrator.ingest_document(
                    tmp_path,
                    metadata_overrides=metadata_overrides,
                    task_id=task_id,
                )
            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)
        
        background_tasks.add_task(ingest_task)
        
        return IngestionResponse(
            task_id=task_id,
            status="processing",
            message=f"Document '{file.filename}' is being processed",
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_directory(
    background_tasks: BackgroundTasks,
    request: IngestionRequest,
):
    """
    Ingest all documents from a directory asynchronously.
    
    The ingestion will be processed in the background.
    """
    try:
        import uuid
        task_id = str(uuid.uuid4())
        
        metadata_overrides = {}
        if request.category:
            metadata_overrides["category"] = request.category
        if request.tags:
            metadata_overrides["tags"] = request.tags
        
        async def ingest_task():
            await orchestrator.ingest_directory(
                request.directory_path,
                pattern=request.pattern,
                recursive=request.recursive,
                metadata_overrides=metadata_overrides,
            )
        
        background_tasks.add_task(ingest_task)
        
        return IngestionResponse(
            task_id=task_id,
            status="processing",
            message=f"Directory '{request.directory_path}' is being processed",
        )
        
    except Exception as e:
        logger.error(f"Directory ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the status of an ingestion task."""
    task = orchestrator.get_task_status(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status.value,
        document_path=task.document_path,
        total_chunks=task.total_chunks,
        processed_chunks=task.processed_chunks,
        progress_percentage=task.progress_percentage,
        error_message=task.error_message,
        created_at=task.created_at.isoformat(),
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.get("/tasks", response_model=List[TaskStatusResponse])
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """List all ingestion tasks."""
    tasks = orchestrator.list_tasks()
    
    if status:
        tasks = [t for t in tasks if t.status.value == status]
    
    return [
        TaskStatusResponse(
            task_id=t.task_id,
            status=t.status.value,
            document_path=t.document_path,
            total_chunks=t.total_chunks,
            processed_chunks=t.processed_chunks,
            progress_percentage=t.progress_percentage,
            error_message=t.error_message,
            created_at=t.created_at.isoformat(),
            completed_at=t.completed_at.isoformat() if t.completed_at else None,
        )
        for t in tasks
    ]


@router.get("/", response_model=List[DocumentInfo])
async def list_documents(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List documents in the vector store."""
    docs = orchestrator.vector_store.list_documents(limit=limit, offset=offset)
    
    return [
        DocumentInfo(
            document_id=doc["document_id"],
            source=doc["source"],
            chunk_count=0,  # Would need separate query
            created_at=doc.get("created_at"),
            metadata=doc.get("metadata", {}),
        )
        for doc in docs
    ]


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document_info(document_id: str):
    """Get information about a specific document."""
    info = orchestrator.vector_store.get_document_info(document_id)
    
    if not info:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentInfo(**info)


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the vector store."""
    count = await orchestrator.delete_document(document_id)
    
    if count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "message": f"Successfully deleted document {document_id}",
        "chunks_deleted": count,
    }


@router.delete("/source/{source:path}")
async def delete_by_source(source: str):
    """Delete documents by source path."""
    count = await orchestrator.delete_by_source(source)
    
    if count == 0:
        raise HTTPException(status_code=404, detail="No documents found for source")
    
    return {
        "message": f"Successfully deleted documents from source {source}",
        "chunks_deleted": count,
    }


@router.post("/search", response_model=List[SearchResult])
async def search_documents(request: SearchRequest):
    """Search for documents using semantic similarity."""
    from ..embeddings import EmbeddingService
    
    try:
        # Generate query embedding
        embedding_service = EmbeddingService()
        query_embedding = await embedding_service.embed(request.query)
        
        # Search
        if request.filters:
            results = await orchestrator.vector_store.search_with_filter(
                query_embedding=query_embedding,
                filters=request.filters,
                top_k=request.top_k,
            )
        else:
            results = await orchestrator.vector_store.search(
                query_embedding=query_embedding,
                top_k=request.top_k,
                threshold=request.threshold,
            )
        
        await embedding_service.close()
        
        return [
            SearchResult(
                content=r["text"],
                source=r["source"],
                score=r["score"],
                metadata=r.get("metadata", {}),
            )
            for r in results
        ]
        
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_stats():
    """Get ingestion statistics."""
    return orchestrator.get_stats()
