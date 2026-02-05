# LMS AI Services

AI/ML services for the Learning Management System using LangGraph and RAG.

## Features

- **RAG Pipeline**: Question answering over internal documentation
- **Agentic AI**: LangGraph-based agent orchestration
- **Recommendations**: Personalized learning path suggestions
- **Vector Search**: Semantic search using Qdrant

## Getting Started

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your OpenAI API key and other configurations

# Start Qdrant (vector database)
docker run -p 6333:6333 qdrant/qdrant

# Start AI services
uvicorn main:app --reload --port 8001
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Embedding Documents

To embed your internal documentation:

```python
from src.rag.embeddings import DocumentEmbedder
from src.vector_store.client import VectorStoreClient

embedder = DocumentEmbedder()
vector_store = VectorStoreClient()

# Load and process documents
documents = embedder.load_documents("path/to/docs")
chunks = embedder.chunk_documents(documents)

# Embed and store
# ... (see full example in scripts/embed_docs.py)
```
