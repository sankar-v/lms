# Development Guide

## Prerequisites

- **Docker & Docker Compose**: For running all services locally
- **Node.js 20+**: For frontend development
- **Python 3.11+**: For backend and AI services
- **OpenAI API Key**: For AI services

## Initial Setup

### 1. Clone and Navigate
```bash
cd lms
```

### 2. Set Up Environment Variables

#### Backend
```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
```

#### AI Services
```bash
cd ai-services
cp .env.example .env
# Add your OpenAI API key
```

#### Docker Compose
```bash
cd infrastructure/docker
cp .env.example .env
# Add your OpenAI API key
```

### 3. Start All Services with Docker Compose

```bash
cd infrastructure/docker
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Qdrant (port 6333)
- Backend API (port 8000)
- AI Services (port 8001)
- Frontend (port 3000)

### 4. Verify Services

- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs
- AI Services Docs: http://localhost:8001/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

## Development Workflow

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### AI Services Development

```bash
cd ai-services
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## Database Operations

### Run Migrations
```bash
cd backend
alembic upgrade head
```

### Create Migration
```bash
alembic revision --autogenerate -m "description"
```

### Seed Data
```bash
psql -U lms_user -d lms_db -f database/seeds/sample_data.sql
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Code Style

### Python
- Use Black for formatting: `black .`
- Use Ruff for linting: `ruff check .`

### TypeScript
- Use ESLint: `npm run lint`
- Format on save enabled in VS Code

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port
lsof -ti:3000 | xargs kill -9
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# View logs
docker logs lms_postgres
```

### Clear All Docker Data
```bash
docker-compose down -v
```
