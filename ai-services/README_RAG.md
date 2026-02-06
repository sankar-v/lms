# RAG Pipeline Quick Start

## 🎯 Overview

Production-ready RAG pipeline for ingesting, embedding, and searching unstructured documents using PostgreSQL + pgVector.

**Key Features:**
- ✅ Multi-format support (PDF, MD, TXT, HTML, DOCX)
- ✅ Smart text chunking with overlap
- ✅ Async batch embedding generation
- ✅ pgVector for efficient similarity search
- ✅ 3 usage modes: SDK, CLI, REST API
- ✅ Background processing for large jobs
- ✅ Comprehensive CRUD operations

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ai-services
uv pip install -r requirements.txt
```

### 2. Setup Environment

Create `.env`:
```bash
OPENAI_API_KEY=your-key-here
DATABASE_URL=postgresql://lms_user:lms_password@localhost:5432/lms_db
```

### 3. Start Services

```bash
# Start PostgreSQL
cd ../infrastructure/docker
docker-compose up postgres -d

# Start AI services API (optional)
cd ../../ai-services
uvicorn main:app --reload --port 8001
```

### 4. Ingest Documents

#### Option A: CLI (Easiest)
```bash
# Ingest single file
python -m src.cli ingest ../docs/README.md --category documentation

# Ingest directory
python -m src.cli ingest ../docs --pattern "*.md" --recursive

# List documents
python -m src.cli list

# Search
python -m src.cli search "deployment guide" --top-k 5
```

#### Option B: Python SDK
```python
import asyncio
from src.ingestion import IngestionOrchestrator

async def main():
    orchestrator = IngestionOrchestrator()
    
    # Ingest file
    task = await orchestrator.ingest_document(
        "../docs/README.md",
        metadata_overrides={"category": "docs"}
    )
    print(f"Ingested {task.processed_chunks} chunks")
    
    await orchestrator.close()

asyncio.run(main())
```

#### Option C: REST API
```bash
# Upload file
curl -X POST "http://localhost:8001/documents/upload" \
  -F "file=@../docs/README.md" \
  -F "category=documentation"

# Search
curl -X POST "http://localhost:8001/documents/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "How to deploy?", "top_k": 5}'
```

## 📖 Usage Examples

### Example 1: Ingest Documentation

```python
from src.ingestion import IngestionOrchestrator

orchestrator = IngestionOrchestrator(
    chunk_size=1000,
    chunk_overlap=200
)

# Ingest all markdown files
tasks = await orchestrator.ingest_directory(
    "../docs",
    pattern="*.md",
    recursive=True,
    metadata_overrides={
        "category": "documentation",
        "tags": ["internal"]
    }
)

print(f"Ingested {len(tasks)} documents")
```

### Example 2: Semantic Search

```python
from src.embeddings import EmbeddingService
from src.vector_store.client import VectorStoreClient

embedding_service = EmbeddingService()
vector_store = VectorStoreClient()

# Search
query_embedding = await embedding_service.embed("How to deploy?")
results = await vector_store.search(
    query_embedding=query_embedding,
    top_k=5,
    threshold=0.7
)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['text'][:200]}...")
```

### Example 3: Document Management

```bash
# List all documents
python -m src.cli list

# Get document info
python -m src.cli info <document_id>

# Delete document
python -m src.cli delete <document_id>

# View statistics
python -m src.cli stats
```

## 🏗️ Architecture

```
Document → Loader → Chunker → Embeddings → pgVector
```

**Components:**
- `DocumentLoader`: Multi-format file parsing
- `DocumentChunker`: Smart text splitting with overlap
- `EmbeddingService`: Batch embedding generation (OpenAI)
- `VectorStoreClient`: PostgreSQL + pgVector operations
- `IngestionOrchestrator`: End-to-end pipeline coordination

## 📊 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Load PDF (10 pages) | ~1s | PyPDF2 |
| Chunk 5000 words | ~0.1s | Recursive split |
| Embed 100 chunks | ~2s | OpenAI batch |
| Search | ~50ms | IVFFlat index |

## 🔧 Configuration

### Chunking Settings

```python
orchestrator = IngestionOrchestrator(
    chunk_size=1000,        # Max chars per chunk
    chunk_overlap=200,      # Overlap between chunks
    embedding_batch_size=100  # API batch size
)
```

**Recommendations:**
- Small docs: chunk_size=500, overlap=100
- Medium docs: chunk_size=1000, overlap=200
- Large docs: chunk_size=1500, overlap=300

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...

# Optional (with defaults)
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
```

## 📚 CLI Reference

```bash
# Ingest
python -m src.cli ingest <path> [--pattern "*.md"] [--category docs] [--tags tag1 tag2]

# List
python -m src.cli list [--limit 50] [--offset 0]

# Info
python -m src.cli info <document_id>

# Delete
python -m src.cli delete <document_id>
python -m src.cli delete <source_path> --source

# Search
python -m src.cli search "<query>" [--top-k 5] [--threshold 0.7]

# Stats
python -m src.cli stats
```

## 🌐 API Reference

API documentation: `http://localhost:8001/docs`

**Key Endpoints:**
- `POST /documents/upload` - Upload single file
- `POST /documents/ingest` - Ingest directory
- `GET /documents/tasks/{id}` - Check task status
- `POST /documents/search` - Semantic search
- `GET /documents/` - List documents
- `DELETE /documents/{id}` - Delete document

## 🧪 Testing

Run the demo:
```bash
python examples/rag_demo.py
```

## 🐛 Troubleshooting

**PostgreSQL connection failed**
```bash
docker-compose up postgres -d
docker ps | grep postgres
```

**OpenAI rate limit**
- Reduce `embedding_batch_size` to 50
- Check your API quota

**Import errors**
```bash
uv pip install -r requirements.txt
```

**Slow search**
- Rebuild index with more lists
- Add metadata filters

## 📖 Full Documentation

See [RAG_PIPELINE.md](../../docs/RAG_PIPELINE.md) for:
- Detailed architecture
- Advanced usage patterns
- Performance tuning
- API reference
- Troubleshooting guide

## 🎯 Next Steps

1. **Ingest your data**: `python -m src.cli ingest <path>`
2. **Test search**: `python -m src.cli search "<query>"`
3. **Start API**: `uvicorn main:app --reload`
4. **Integrate**: Use SDK in your application

## 🤝 Contributing

To add a new file format:
1. Add loader to `DocumentLoader`
2. Update `DocumentType` enum
3. Add to `_loaders` dict
4. Test with sample files
