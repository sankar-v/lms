# LMS Architecture Documentation

## System Overview

The LMS is built as a microservices architecture with three main components:

### Frontend (React + TypeScript + Vite)
- **Port**: 3000
- **Purpose**: User interface for learning, progress tracking, and Q&A
- **Key Features**:
  - Dashboard with personalized recommendations
  - Learning path visualization
  - Interactive chat interface with RAG assistant
  - Progress tracking and analytics

### Backend API (FastAPI + Python)
- **Port**: 8000
- **Purpose**: Business logic and data management
- **Key Components**:
  - User management and authentication
  - Module and content management
  - Progress tracking
  - API gateway to AI services
- **Database**: PostgreSQL for relational data

### AI Services (LangGraph + LLM)
- **Port**: 8001
- **Purpose**: AI-powered recommendations and Q&A
- **Key Components**:
  - RAG pipeline for documentation Q&A
  - LangGraph agents for intelligent routing
  - Recommendation engine
  - Vector database integration (Qdrant)

## Data Flow

```
User → Frontend → Backend API → PostgreSQL
                     ↓
                 AI Services → Vector DB (Qdrant)
                     ↓
                   LLM (OpenAI)
```

## Communication Patterns

1. **Frontend ↔ Backend**: REST API over HTTP
2. **Backend ↔ AI Services**: HTTP with async/await
3. **AI Services ↔ Vector DB**: Qdrant client SDK
4. **AI Services ↔ LLM**: OpenAI API

## Security

- JWT-based authentication
- Role-based access control (RBAC)
- Environment-based configuration
- Secure credential management

## Scalability Considerations

- Stateless services for horizontal scaling
- Database connection pooling
- Async I/O throughout the stack
- Caching strategies (future enhancement)
