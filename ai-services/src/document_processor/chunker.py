"""Text chunking strategies for document processing."""

import re
from typing import List
import logging

from .models import Document, DocumentChunk

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunk documents into smaller pieces for embedding."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None,
    ):
        """
        Initialize document chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to split on (in priority order)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or [
            "\n\n",  # Double newline (paragraphs)
            "\n",    # Single newline
            ". ",    # Sentences
            "! ",
            "? ",
            "; ",
            ": ",
            ", ",
            " ",     # Words
            "",      # Characters
        ]
    
    def chunk(self, document: Document) -> List[DocumentChunk]:
        """
        Chunk a document into smaller pieces.
        
        Args:
            document: Document to chunk
            
        Returns:
            List of document chunks
        """
        chunks = self._split_text(document.content)
        
        result = []
        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                content=chunk_text.strip(),
                document_id=document.document_id,
                chunk_index=i,
                metadata=document.metadata,
                start_char=0,  # Could be calculated if needed
                end_char=len(chunk_text),
            )
            result.append(chunk)
        
        logger.info(
            f"Chunked document {document.document_id} into {len(result)} chunks"
        )
        return result
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks using recursive character splitting.
        
        This implements a smart chunking algorithm that:
        1. Tries to split on paragraph boundaries first
        2. Falls back to sentences if paragraphs are too large
        3. Falls back to words/characters as last resort
        """
        # Start with the highest priority separator
        return self._split_text_recursive(text, self.separators)
    
    def _split_text_recursive(
        self, text: str, separators: List[str]
    ) -> List[str]:
        """Recursively split text with different separators."""
        if not text:
            return []
        
        # Use the first separator
        separator = separators[0] if separators else ""
        
        if separator:
            splits = text.split(separator)
        else:
            # If no separator, split by characters
            splits = list(text)
        
        # Merge splits into chunks
        chunks = []
        current_chunk = []
        current_length = 0
        
        for split in splits:
            split_length = len(split)
            
            # If adding this split would exceed chunk size
            if current_length + split_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = separator.join(current_chunk) if separator else "".join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap
                overlap_text = self._create_overlap(chunks[-1], separator)
                current_chunk = [overlap_text] if overlap_text else []
                current_length = len(overlap_text)
            
            # Add split to current chunk
            if split:  # Don't add empty strings
                current_chunk.append(split)
                current_length += split_length + len(separator)
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = separator.join(current_chunk) if separator else "".join(current_chunk)
            chunks.append(chunk_text)
        
        # If we have chunks that are still too large and more separators available
        if separators and any(len(chunk) > self.chunk_size for chunk in chunks):
            # Recursively split large chunks with next separator
            result = []
            for chunk in chunks:
                if len(chunk) > self.chunk_size and len(separators) > 1:
                    result.extend(
                        self._split_text_recursive(chunk, separators[1:])
                    )
                else:
                    result.append(chunk)
            return result
        
        return chunks
    
    def _create_overlap(self, text: str, separator: str) -> str:
        """Create overlap text from the end of previous chunk."""
        if len(text) <= self.chunk_overlap:
            return text
        
        # Take last chunk_overlap characters
        overlap = text[-self.chunk_overlap:]
        
        # Try to start at a clean separator boundary
        if separator and separator in overlap:
            parts = overlap.split(separator)
            # Skip the first partial part
            overlap = separator.join(parts[1:])
        
        return overlap
    
    def chunk_batch(self, documents: List[Document]) -> List[List[DocumentChunk]]:
        """
        Chunk multiple documents.
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List of chunk lists (one per document)
        """
        return [self.chunk(doc) for doc in documents]
