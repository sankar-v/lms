# RAG Pipeline Documentation

## Overview

The RAG (Retrieval-Augmented Generation) pipeline is a comprehensive, production-ready system for ingesting, embedding, and searching unstructured documents using PostgreSQL with pgVector.

## Architecture

```
┌─────────────────┐
│ Document Input  │
│ (PDF/MD/TXT/    │
│  HTML/DOCX)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Document Loader │
│ - Multi-format  │
│ - Metadata      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Text Chunker   │
│ - Smart split   │
│ - Overlap       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Embedding Svc   │
│ - OpenAI API    │
│ - Batching      │
│ - Retry logic   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vector Store    │
│ PostgreSQL +    │
│ pgVector        │
└─────────────────┘
```

## Features

### ✅ Document Processing
- **Multi-format support**: PDF, Markdown, Plain Text, HTML, DOCX
- **Metadata extraction**: File info, custom tags, categories
- **Error handling**: Graceful fallbacks for encoding issues

### ✅ Smart Chunking
- **Recursive splitting**: Paragraphs → Sentences → Words → Characters
- **Configurable overlap**: Maintain context between chunks
- **Boundary-aware**: Respects natural text boundaries

### ✅ Embedding Generation
- **Async/await**: Non-blocking operations
- **Batch processing**: Efficient API usage
- **Retry logic**: Exponential backoff for failures
- **Progress tracking**: Monitor large ingestion jobs

### ✅ Vector Storage
- **CRUD operations**: Insert, search, delete, list
- **Metadata filtering**: Search within categories
- **Deduplication**: Upsert on conflict (chunk_id)
- **Pagination**: Efficient data retrieval

### ✅ Usage Modes

#### 1. **Python SDK** (Programmatic)
```python
from src.ingestion import IngestionOrchestrator

orchestrator = IngestionOrchestrator()

# Ingest single file
task = await orchestrator.ingest_document(
    "docs/guide.pdf",
    metadata_overrides={"category": "documentation", "tags": ["guide"]}
)

# Ingest directory
tasks = await orchestrator.ingest_directory(
    "docs/",
    pattern="*.md",
    recursive=True
)
```

#### 2. **CLI Tool** (Command-line)
```bash
# Ingest single file
python -m src.cli ingest docs/guide.pdf --category documentation --tags guide tutorial

# Ingest directory
python -m src.cli ingest docs/ --pattern "*.md" --category docs

# List documents
python -m src.cli list --limit 10

# Search
python -m src.cli search "How to deploy?" --top-k 5

# Delete
python -m src.cli delete <document_id>

# Stats
python -m src.cli stats
```

#### 3. **REST API** (Async)
```bash
# Upload file
curl -X POST "http://localhost:8001/documents/upload" \
  -F "file=@docs/guide.pdf" \
  -F "category=documentation"

# Check task status
curl "http://localhost:8001/documents/tasks/{task_id}"

# Search
curl -X POST "http://localhost:8001/documents/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "How to deploy?", "top_k": 5}'

# List documents
curl "http://localhost:8001/documents/?limit=50"

# Delete document
curl -X DELETE "http://localhost:8001/documents/{document_id}"
```

## Installation

### 1. Install Dependencies

```bash
cd ai-services
uv pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgresql://lms_user:lms_password@localhost:5432/lms_db
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 3. Start Database

```bash
cd ../infrastructure/docker
docker-compose up postgres -d
```

### 4. Initialize Schema

The schema is automatically created when Docker starts. To manually run:

```bash
docker exec -i lms_postgres psql -U lms_user -d lms_db < ../../database/init.sql
```

## Usage Examples

### Example 1: Ingest Documentation

```python
import asyncio
from src.ingestion import IngestionOrchestrator

async def main():
    orchestrator = IngestionOrchestrator(
        chunk_size=1000,
        chunk_overlap=200,
        embedding_batch_size=100
    )
    
    # Ingest all markdown files from docs directory
    tasks = await orchestrator.ingest_directory(
        directory_path="../../docs",
        pattern="*.md",
        recursive=True,
        metadata_overrides={
            "category": "documentation",
            "tags": ["internal", "engineering"]
        }
    )
    
    print(f"Ingested {len(tasks)} documents")
    
    # Get stats
    stats = orchestrator.get_stats()
    print(f"Total documents: {stats['total_documents']}")
    
    await orchestrator.close()

asyncio.run(main())
```

### Example 2: Search Documents

```python
import asyncio
from src.embeddings import EmbeddingService
from src.vector_store.client import VectorStoreClient

async def main():
    embedding_service = EmbeddingService()
    vector_store = VectorStoreClient()
    
    # Generate query embedding
    query = "How do I deploy to production?"
    query_embedding = await embedding_service.embed(query)
    
    # Search
    results = await vector_store.search(
        query_embedding=query_embedding,
        top_k=5,
        threshold=0.7
    )
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Source: {result['source']}")
        print(f"   Content: {result['text'][:200]}...")
    
    await embedding_service.close()

asyncio.run(main())
```

### Example 3: CLI Workflow

```bash
# 1. Ingest your documentation
python -m src.cli ingest ../docs --pattern "*.md" --category documentation

# 2. Check what was ingested
python -m src.cli list

# 3. Search for specific content
python -m src.cli search "authentication" --top-k 3

# 4. Get detailed info about a document
python -m src.cli info <document_id>

# 5. View statistics
python -m src.cli stats
```

### Example 4: API Integration

Start the API server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Upload a document:
```python
import requests

# Upload file
with open("guide.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8001/documents/upload",
        files={"file": f},
        data={"category": "guides", "tags": "tutorial,beginner"}
    )
    task_id = response.json()["task_id"]

# Check status
status_response = requests.get(
    f"http://localhost:8001/documents/tasks/{task_id}"
)
print(status_response.json())

# Search
search_response = requests.post(
    "http://localhost:8001/documents/search",
    json={"query": "How to get started?", "top_k": 5}
)
results = search_response.json()
```

## Configuration

### Chunking Configuration

```python
orchestrator = IngestionOrchestrator(
    chunk_size=1000,        # Max characters per chunk
    chunk_overlap=200,      # Characters to overlap between chunks
    embedding_batch_size=100  # Embeddings per API call
)
```

**Recommendations:**
- **Small docs (< 10 pages)**: chunk_size=500, overlap=100
- **Medium docs (10-100 pages)**: chunk_size=1000, overlap=200
- **Large docs (> 100 pages)**: chunk_size=1500, overlap=300

### Embedding Configuration

In `.env`:
```bash
EMBEDDING_MODEL=text-embedding-3-small  # Fast, good quality
# Or for better quality:
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSION=1536  # Match model dimension
```

## Performance

### Benchmarks (on M1 Mac, local PostgreSQL)

| Operation | Time | Notes |
|-----------|------|-------|
| Load 1 PDF (10 pages) | ~1s | PyPDF2 extraction |
| Chunk 5000 words | ~0.1s | Recursive splitting |
| Embed 100 chunks | ~2s | OpenAI API batch |
| Insert 100 chunks | ~0.5s | PostgreSQL batch |
| Search (cosine) | ~50ms | IVFFlat index |

### Optimization Tips

1. **Batch embeddings**: Use batch_size=100 for best API efficiency
2. **Concurrent ingestion**: Set max 5 concurrent files to avoid rate limits
3. **Index tuning**: Adjust `lists` parameter in IVFFlat for your dataset size
4. **Connection pooling**: Already configured in VectorStoreClient

## Monitoring

### Check Ingestion Status

```python
# Get task status
task = orchestrator.get_task_status(task_id)
print(f"Status: {task.status}")
print(f"Progress: {task.progress_percentage:.1f}%")
print(f"Chunks: {task.processed_chunks}/{task.total_chunks}")
```

### View Statistics

```bash
python -m src.cli stats
```

Output:
```
📊 RAG Pipeline Statistics

Total Documents: 145
Total Tasks: 50
  - Completed: 48
  - Failed: 2
  - Pending: 0
```

## Troubleshooting

### Issue: "PyPDF2 not found"
```bash
uv pip install PyPDF2
```

### Issue: "OpenAI rate limit"
- Reduce `embedding_batch_size` to 50
- Add retry delay in code
- Check your OpenAI quota

### Issue: "PostgreSQL connection failed"
- Check Docker: `docker ps | grep postgres`
- Verify DATABASE_URL in `.env`
- Test connection: `psql $DATABASE_URL`

### Issue: "Slow search performance"
- Rebuild index: `CREATE INDEX CONCURRENTLY ...`
- Increase `lists` parameter for larger datasets
- Consider adding metadata filters to narrow results

## API Reference

### FastAPI Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/upload` | Upload single file |
| POST | `/documents/ingest` | Ingest directory |
| GET | `/documents/tasks/{id}` | Get task status |
| GET | `/documents/` | List documents |
| GET | `/documents/{id}` | Get document info |
| DELETE | `/documents/{id}` | Delete document |
| POST | `/documents/search` | Search documents |
| GET | `/documents/stats/summary` | Get statistics |

Full API docs: `http://localhost:8001/docs`

## Future Enhancements

- [ ] Support for more file formats (Excel, CSV, JSON)
- [ ] Incremental updates (detect changed files)
- [ ] Batch delete operations
- [ ] Advanced filtering (date ranges, size, etc.)
- [ ] Webhook notifications for task completion
- [ ] S3/Azure Blob Storage integration
- [ ] Multi-language support
- [ ] Custom embedding models (Sentence Transformers)
- [ ] Hybrid search (keyword + semantic)

## Contributing

To add support for a new file format:

1. Add loader method to `DocumentLoader` class
2. Update `_loaders` dict with file extension mapping
3. Add file type to `DocumentType` enum
4. Update tests
