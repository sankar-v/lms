"""Document models for processing."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"
    HTML = "html"
    DOCX = "docx"
    UNKNOWN = "unknown"


class ProcessingStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DocumentMetadata:
    """Metadata for a document."""
    source: str  # File path or URL
    document_type: DocumentType
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    file_size: Optional[int] = None  # in bytes
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    custom_metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "source": self.source,
            "document_type": self.document_type.value,
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "file_size": self.file_size,
            "tags": self.tags,
            "category": self.category,
            **self.custom_metadata,
        }


@dataclass
class Document:
    """Represents a loaded document."""
    content: str
    metadata: DocumentMetadata
    document_id: Optional[str] = None

    def __post_init__(self):
        if self.document_id is None:
            # Generate ID from source path
            import hashlib
            self.document_id = hashlib.md5(
                self.metadata.source.encode()
            ).hexdigest()


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""
    content: str
    document_id: str
    chunk_index: int
    metadata: DocumentMetadata
    start_char: int = 0
    end_char: int = 0
    
    @property
    def chunk_id(self) -> str:
        """Generate unique chunk ID."""
        return f"{self.document_id}_chunk_{self.chunk_index}"


@dataclass
class IngestionTask:
    """Represents a document ingestion task."""
    task_id: str
    document_path: str
    status: ProcessingStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_chunks: int = 0
    processed_chunks: int = 0
    error_message: Optional[str] = None
    
    @property
    def progress_percentage(self) -> float:
        """Calculate processing progress."""
        if self.total_chunks == 0:
            return 0.0
        return (self.processed_chunks / self.total_chunks) * 100
