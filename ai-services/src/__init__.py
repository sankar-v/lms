"""RAG Pipeline - Production-ready document ingestion and search."""

__version__ = "1.0.0"

from .ingestion import IngestionOrchestrator
from .embeddings import EmbeddingService
from .vector_store.client import VectorStoreClient
from .document_processor import (
    DocumentLoader,
    DocumentChunker,
    Document,
    DocumentChunk,
    DocumentType,
)

__all__ = [
    "IngestionOrchestrator",
    "EmbeddingService",
    "VectorStoreClient",
    "DocumentLoader",
    "DocumentChunker",
    "Document",
    "DocumentChunk",
    "DocumentType",
]
