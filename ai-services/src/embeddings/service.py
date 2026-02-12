"""Embedding service for generating vector embeddings."""

import asyncio
from typing import List, Optional
import logging
from openai import AsyncOpenAI

from ..config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using OpenAI."""
    
    def __init__(
        self,
        model: str = None,
        batch_size: int = 100,
        max_retries: int = 3,
    ):
        """
        Initialize embedding service.
        
        Args:
            model: OpenAI embedding model name
            batch_size: Number of texts to embed in one batch
            max_retries: Maximum number of retry attempts
        """
        self.model = model or settings.EMBEDDING_MODEL
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        embeddings = await self.embed_batch([text])
        return embeddings[0]
    
    async def embed_batch(
        self,
        texts: List[str],
        show_progress: bool = False,
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with batching.
        
        Args:
            texts: List of texts to embed
            show_progress: Whether to log progress
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            if show_progress:
                logger.info(
                    f"Embedding batch {i // self.batch_size + 1}/"
                    f"{(len(texts) - 1) // self.batch_size + 1}"
                )
            
            # Embed batch with retries
            batch_embeddings = await self._embed_with_retry(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    async def _embed_with_retry(self, texts: List[str]) -> List[List[float]]:
        """Embed texts with exponential backoff retry."""
        for attempt in range(self.max_retries):
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                )
                
                # Extract embeddings in order
                embeddings = [item.embedding for item in response.data]
                return embeddings
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to generate embeddings after {self.max_retries} attempts: {e}")
                    raise
                
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(
                    f"Embedding attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
        
        return []
    
    async def close(self):
        """Close the client connection."""
        await self.client.close()
