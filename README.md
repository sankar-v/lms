# Agentic AI-Powered Engineering Platform Learning and Onboarding Assistant

A full-stack learning management system with AI-powered personalized recommendations and RAG-based Q&A assistant.

## 🎯 Objectives

Design and build a personalized learning and onboarding capability as part of the existing company portal. The system will:
- Recommend tailored learning paths and modules based on a user's role, skills, and progress
- Answer questions about the engineering platform tech stack, architecture, and policies
- Track user progress and completion across modules and activities

Under the hood, the solution combines:
- A RAG (Retrieval-Augmented Generation) chatbot over internal documentation and knowledge bases
- A recommendation engine that guides users on what to learn next

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- OpenAI API Key

### Setup & Run

```bash
# 1. Run setup script
npm run setup

# 2. Add your OpenAI API key to:
#    - ai-services/.env
#    - infrastructure/docker/.env

# 3. Start all services
npm run dev

# 4. (Optional) Seed database with sample data
npm run seed
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **AI Services**: http://localhost:8001/docs

## 📁 Project Structure

```
lms/
├── frontend/              # React + TypeScript + Vite
├── backend/               # FastAPI + Python
├── ai-services/           # LangGraph + RAG Pipeline
├── database/              # PostgreSQL schemas and seeds
├── infrastructure/        # Docker configs
├── shared/                # Shared types and constants
├── docs/                  # Documentation
└── scripts/               # Setup and utility scripts
```

## 🛠️ Technology Stack

- **Frontend**: React, TypeScript, Vite, React Router
- **Backend**: FastAPI, Python, SQLAlchemy, PostgreSQL
- **AI/ML**: LangGraph, LangChain, OpenAI, pgvector
- **Infrastructure**: Docker, Docker Compose

## 📚 Key Features

### Personalized Learning Paths
- Curate and recommend courses/modules based on role, skills, and progress
- LLM-driven logic to adapt learning paths over time
- Exposure to multiple phases of the SDLC

### RAG-based Q&A Assistant
Answer questions about:
- Platform policies and guidelines
- Engineering tech stack and reference architectures
- Internal best practices, patterns, and playbooks

RAG connects LLMs to internal documentation using embeddings and vector databases, enabling accurate, domain-specific Q&A grounded in company knowledge.

### Progress Tracking
- Real-time progress monitoring
- Quiz assessments
- Completion tracking
- Learning analytics

## 📖 Documentation

- [Functional Requirements](FUNCTIONAL_REQUIREMENTS.md)
- [**RAG Pipeline Guide**](ai-services/README_RAG.md) - **Start here for document ingestion!**
- [Architecture Overview](docs/architecture/system-overview.md)
- [API Documentation](docs/api/endpoints.md)
- [Development Guide](docs/guides/development.md)

## 🚀 RAG Pipeline Quick Start

The RAG pipeline is production-ready and can be used **right now** to ingest and search documents:

```bash
# Install dependencies
cd ai-services
uv pip install -r requirements.txt

# Start PostgreSQL
cd ../infrastructure/docker
docker-compose up postgres -d

# Ingest your documents (CLI)
cd ../../ai-services
python -m src.cli ingest ../docs --pattern "*.md" --category documentation

# Search documents
python -m src.cli search "How do I deploy?" --top-k 5

# View all documents
python -m src.cli list

# Get statistics
python -m src.cli stats
```

**Three usage modes:**
1. **CLI Tool**: Command-line interface for quick operations
2. **Python SDK**: Programmatic access for custom workflows
3. **REST API**: HTTP endpoints for remote integration

See [RAG_PIPELINE.md](docs/RAG_PIPELINE.md) for complete documentation.

## 🧪 Development

### Run Individual Services

```bash
# Frontend
npm run frontend:dev

# Backend
npm run backend:dev

# AI Services
npm run ai:dev
```

### View Logs
```bash
cd infrastructure/docker
docker-compose logs -f [service-name]
```

### Stop Services
```bash
cd infrastructure/docker
docker-compose down
```

## 🔐 Environment Variables

See `.env.example` files in each service directory for required configuration.

## 🌟 Project Details

### Recommending Personalized Learning Paths
Curate and recommend courses/modules based on role (e.g., platform engineer, backend engineer), prior skills, and historical progress. Use LLM-driven logic to adapt learning paths over time, giving you exposure to multiple phases of the software development lifecycle (requirements, design, implementation, testing, deployment, and iteration).

### Providing a RAG-based Q&A Assistant
The assistant will answer questions related to:
- Platform policies and guidelines
- Engineering tech stack and reference architectures
- Internal best practices, patterns, and playbooks

RAG connects LLMs to internal documentation using embeddings and vector databases, enabling accurate, domain-specific Q&A grounded in company knowledge rather than generic internet data.

## 📝 License

MIT
