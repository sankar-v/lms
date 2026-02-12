# Hybrid Configuration System

The application now uses a flexible hybrid configuration approach that combines YAML files with environment variable overrides.

## Configuration Priority

Settings are loaded in the following priority order (highest to lowest):

1. **Environment Variables** - Highest priority
2. **YAML Config Files** - Environment-specific or default
3. **Default Values** - Hardcoded in `config.py`

## Configuration Files

### `config.yaml` (Default)
Base configuration used when no environment is specified.

### `config.dev.yaml` (Development)
Development-specific settings. Activated by setting `ENV=dev`

### `config.prod.yaml` (Production)
Production-specific settings. Activated by setting `ENV=prod`

## Usage Examples

### Local Development
```bash
# Use default config.yaml
python main.py

# Or explicitly use dev config
ENV=dev python main.py
```

### Production Deployment
```bash
# Use production config
ENV=prod python main.py

# Override sensitive values with environment variables
ENV=prod OPENAI_API_KEY=sk-real-key DATABASE_URL=postgresql://... python main.py
```

### Docker/Kubernetes
```yaml
# docker-compose.yml or k8s deployment
environment:
  - ENV=prod
  - OPENAI_API_KEY=${OPENAI_API_KEY}
  - DATABASE_URL=${DATABASE_URL}
volumes:
  - ./config.prod.yaml:/app/config.prod.yaml
```

## Environment Variables

All settings can be overridden with environment variables:

- `OPENAI_API_KEY` - OpenAI API key (recommended via env var)
- `DATABASE_URL` - Database connection string
- `LLM_MODEL` - Language model name
- `LLM_TEMPERATURE` - Model temperature
- `EMBEDDING_MODEL` - Embedding model name
- `EMBEDDING_DIMENSION` - Embedding vector dimension
- `CHUNK_SIZE` - Document chunk size
- `CHUNK_OVERLAP` - Chunk overlap size
- `TOP_K_RESULTS` - Number of retrieval results
- `SIMILARITY_THRESHOLD` - Similarity threshold
- `BACKEND_API_URL` - Backend service URL
- `ENV` - Environment selector (dev/prod)

## Benefits

✅ **No redeployment needed** - Update YAML files and restart
✅ **Environment-specific configs** - Easy dev/staging/prod management
✅ **Type safety** - Pydantic validation
✅ **Security** - Secrets via env vars, configs in files
✅ **Flexibility** - Multiple override layers
