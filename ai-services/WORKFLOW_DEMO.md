# Complete RAG Workflow Demo - Setup Instructions

## What We've Built

I've created a complete end-to-end RAG (Retrieval-Augmented Generation) pipeline demonstration that shows:

1. **Document Upload** - Upload documents (MD, TXT, PDF, DOCX)
2. **Embedding Generation** - Create vector embeddings using OpenAI
3. **Vector Storage** - Store in PostgreSQL with pgvector
4. **Semantic Search** - Retrieve relevant documents using NLP
5. **AI-Powered Answers** - Generate contextual answers using GPT-4

## Files Created

### Test Data
- `test_data/engineering_best_practices.md` - Sample document about engineering best practices

### Workflow Scripts
- `examples/complete_workflow_cli.py` - CLI-based workflow demonstration
- `examples/complete_workflow_api.py` - REST API-based workflow demonstration
- `examples/README.md` - Detailed documentation

## Prerequisites

### 1. Database Setup
```bash
# Start PostgreSQL with pgvector
docker run -d \
  --name postgres-pgvector \
  -e POSTGRES_USER=lms_user \
  -e POSTGRES_PASSWORD=lms_password \
  -e POSTGRES_DB=lms_db \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Or use existing database
psql -d lms_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. OpenAI API Key
You need a valid OpenAI API key. Update `.env`:

```bash
# Edit .env file
OPENAI_API_KEY=sk-your-actual-key-here
DATABASE_URL=postgresql://lms_user:lms_password@localhost:5432/lms_db
```

**Important**: Make sure the API key is on a single line with no extra spaces or line breaks.

### 3. Install Dependencies
```bash
cd ai-services
pip install -r requirements.txt
```

## Running the Workflows

### Option 1: CLI Workflow (Direct Python)

This runs the complete pipeline directly using Python components:

```bash
cd ai-services
python examples/complete_workflow_cli.py
```

**What it does:**
1. ✅ Initializes embedding service, vector store, retriever, and generator
2. 📄 Loads and chunks the test document
3. 🔢 Generates embeddings for all chunks
4. 💾 Stores chunks and embeddings in PostgreSQL
5. 🔍 Tests semantic search with multiple queries
6. 🤖 Generates AI-powered answers using retrieved context

**Expected output:**
```
================================================================================
RAG PIPELINE COMPLETE WORKFLOW DEMONSTRATION
================================================================================

📦 Step 1: Initializing components...
✅ Components initialized

📄 Step 2: Uploading and processing document...
   Document: engineering_best_practices.md
✅ Document processed:
   - Task ID: abc-123
   - Total chunks: 15
   - Status: completed

💾 Step 3: Verifying storage...
✅ Vector store stats:
   - Total documents: 1
   - Total chunks: 15

🔍 Step 4: Testing document retrieval...
   Query 1: 'What are the microservices design principles?'
   ----------------------------------------------------------------------
   ✅ Found 3 relevant chunks:
      1. Score: 0.892
         Preview: ## Microservices Architecture\n\n### Service Design Principles\n1. **Single Responsibility**: Each...
         Source: engineering_best_practices.md
      ...

🤖 Step 5: Generating AI-powered answer...
   Question: 'What security practices should we follow for authentication and data protection?'
   ----------------------------------------------------------------------
   
   📝 Generated Answer:
   Based on the documentation, here are the key security practices to follow:
   
   **Authentication & Authorization:**
   - Use OAuth 2.0 / OpenID Connect for authentication
   - Implement role-based access control (RBAC)
   - Never store credentials in code or configuration files
   - Rotate secrets regularly
   
   **Data Protection:**
   - Encrypt data at rest and in transit
   - Implement data classification policies
   - Follow GDPR and data privacy regulations
   - Use Azure Private Link for secure connections
   
   📚 Sources: engineering_best_practices.md

================================================================================
✅ WORKFLOW COMPLETED SUCCESSFULLY
================================================================================
```

### Option 2: REST API Workflow

This demonstrates the same workflow using HTTP requests to the FastAPI service:

```bash
# Terminal 1: Start the API server
cd ai-services
python main.py

# Terminal 2: Run the API workflow
python examples/complete_workflow_api.py
```

**What it does:**
1. 🏥 Checks API health
2. 📄 Uploads document via `/documents/upload` endpoint
3. ⏳ Monitors processing status via `/documents/task/{id}` endpoint
4. 📚 Lists stored documents via `/documents/list` endpoint
5. 🔍 Searches for information via `/documents/search` endpoint
6. 🤖 Gets AI answers via `/chat` endpoint

**API Endpoints Used:**
- `GET /health` - Health check
- `POST /documents/upload` - Upload document
- `GET /documents/task/{task_id}` - Check processing status
- `GET /documents/list` - List all documents
- `POST /documents/search` - Semantic search
- `POST /chat` - Get AI-powered answers

## Architecture

```
┌─────────────────┐
│   User uploads  │
│    document     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Document Loader │ ← Loads .md, .txt, .pdf, .docx
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Document Chunker │ ← Splits into 1000-char chunks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Embedding Service│ ← OpenAI text-embedding-3-small
│  (OpenAI API)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │ ← PostgreSQL + pgvector
│  (PostgreSQL)   │
└────────┬────────┘
         │
         ▼
    [User Query]
         │
         ▼
┌─────────────────┐
│   Retriever     │ ← Semantic search (cosine similarity)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Generator     │ ← GPT-4 with context
│   (OpenAI API)  │
└────────┬────────┘
         │
         ▼
   [AI Answer with Sources]
```

## Troubleshooting

### "Connection error" or "Illegal header value"
- Check that `OPENAI_API_KEY` in `.env` is valid and on a single line
- Ensure no extra spaces or line breaks in the API key
- Verify the key works: `curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_KEY"`

### "Database connection failed"
- Ensure PostgreSQL is running: `docker ps` or `pg_isready`
- Check DATABASE_URL in `.env` matches your database
- Verify pgvector extension: `psql -d lms_db -c "SELECT * FROM pg_extension WHERE extname='vector';"`

### "Import errors"
- Run from correct directory: `cd ai-services`
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.9+)

## Sample Test Queries

The workflow demonstrates these queries:
1. "What are the microservices design principles?"
2. "How should we handle secrets and credentials?"
3. "What are the Kubernetes best practices?"
4. "What security practices should we follow for authentication and data protection?"

You can modify the scripts to test your own queries!

## What's Next

After the demo works, you can:
- Add your own documents to `test_data/`
- Modify queries in the workflow scripts
- Use the CLI tool: `python -m src.cli ingest <file>` and `python -m src.cli search "<query>"`
- Build your own applications using the REST API
- Integrate with your frontend application

## Configuration

All settings are managed through the hybrid configuration system:
- Default values: `config.yaml`
- Development: `config.dev.yaml` (set `ENV=dev`)
- Production: `config.prod.yaml` (set `ENV=prod`)
- Secrets: Environment variables (`.env` file)

See `CONFIG_GUIDE.md` for more details.
