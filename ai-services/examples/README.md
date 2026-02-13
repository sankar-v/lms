# RAG Workflow Testing Guide

This directory contains complete end-to-end workflow demonstrations for the RAG pipeline.

## Workflows Available

### 1. CLI Workflow (`complete_workflow_cli.py`)
Direct Python workflow using internal components.

**Steps:**
1. Upload document
2. Generate embeddings
3. Store in vector database
4. Retrieve relevant documents
5. Generate AI-powered answers

**Run:**
```bash
cd ai-services
python examples/complete_workflow_cli.py
```

**Prerequisites:**
- PostgreSQL with pgvector running
- OpenAI API key configured
- Python dependencies installed

---

### 2. REST API Workflow (`complete_workflow_api.py`)
HTTP-based workflow using FastAPI endpoints.

**Steps:**
1. Check API health
2. Upload document via API
3. Monitor processing status
4. List stored documents
5. Search for information
6. Get AI-powered answers

**Run:**
```bash
# Terminal 1: Start API server
cd ai-services
python main.py

# Terminal 2: Run workflow
python examples/complete_workflow_api.py
```

**Prerequisites:**
- API server running on http://localhost:8001
- PostgreSQL with pgvector running
- OpenAI API key configured

---

## Test Data

### `engineering_best_practices.md`
Sample document containing:
- Microservices architecture principles
- Cloud infrastructure guidelines
- Security best practices
- Development standards
- Monitoring and observability

This document is used to demonstrate:
- Document loading and chunking
- Embedding generation
- Vector storage
- Semantic search
- Context-aware answer generation

---

## Sample Queries

The workflows test these queries:
1. "What are the microservices design principles?"
2. "How should we handle secrets and credentials?"
3. "What are the Kubernetes best practices?"
4. "What security practices should we follow for authentication and data protection?"

---

## Expected Output

Both workflows will demonstrate:
- ✅ Document upload and processing
- ✅ Chunk creation and embedding generation
- ✅ Vector storage and retrieval
- ✅ Semantic search with relevance scores
- ✅ AI-generated answers with source attribution

---

## Troubleshooting

### CLI Workflow Issues
- **Import errors**: Ensure you're in the `ai-services` directory
- **Database errors**: Check PostgreSQL is running and pgvector extension is installed
- **OpenAI errors**: Verify `OPENAI_API_KEY` in `.env` file

### API Workflow Issues
- **Connection refused**: Start the API server first (`python main.py`)
- **Timeout errors**: Increase timeout in the script or check server logs
- **404 errors**: Verify API endpoints in `main.py` match the script

### Database Setup
```sql
-- Ensure pgvector extension is installed
CREATE EXTENSION IF NOT EXISTS vector;

-- Check if tables exist
\dt
```

---

## Architecture

```
┌─────────────┐
│   Document  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Document Loader │  (Load file)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Document Chunker│  (Split into chunks)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Embedding Service│  (Generate vectors)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Vector Store    │  (Store in PostgreSQL)
└────────┬─────────┘
         │
         ▼
    [Query] → Retriever → Generator → Answer
```
