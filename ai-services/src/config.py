from pydantic_settings import BaseSettings
from pathlib import Path
import yaml
import os
from typing import Optional

class Settings(BaseSettings):
    # LLM Configuration
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7
    
    # Database Configuration (PostgreSQL with pgvector)
    DATABASE_URL: str = "postgresql://lms_user:lms_password@localhost:5432/lms_db"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Backend Service
    BACKEND_API_URL: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @classmethod
    def from_yaml(cls, config_path: Optional[str] = None) -> "Settings":
        """
        Load settings from YAML file with environment variable overrides.
        
        Priority (highest to lowest):
        1. Environment variables
        2. YAML config file
        3. Default values
        
        Args:
            config_path: Path to YAML config file. If None, will try to auto-detect
                        based on ENV environment variable (dev/prod) or use config.yaml
        
        Returns:
            Settings instance
        """
        config_dict = {}
        
        # Determine which config file to use
        if config_path is None:
            env = os.getenv("ENV", "").lower()
            base_dir = Path(__file__).parent.parent
            
            if env in ["dev", "development"]:
                config_path = base_dir / "config.dev.yaml"
            elif env in ["prod", "production"]:
                config_path = base_dir / "config.prod.yaml"
            else:
                config_path = base_dir / "config.yaml"
        else:
            config_path = Path(config_path)
        
        # Load YAML config if it exists
        if config_path.exists():
            with open(config_path) as f:
                yaml_data = yaml.safe_load(f) or {}
            
            # Flatten nested YAML structure to match environment variable names
            config_dict = cls._flatten_yaml(yaml_data)
        
        # Create settings instance (Pydantic will automatically override with env vars)
        return cls(**config_dict)
    
    @staticmethod
    def _flatten_yaml(yaml_data: dict) -> dict:
        """
        Flatten nested YAML structure to match Settings field names.
        
        Example:
            {'llm': {'model': 'gpt-4'}} -> {'LLM_MODEL': 'gpt-4'}
        """
        flattened = {}
        
        # LLM Configuration
        if "llm" in yaml_data:
            llm = yaml_data["llm"]
            if "openai_api_key" in llm:
                flattened["OPENAI_API_KEY"] = llm["openai_api_key"]
            if "model" in llm:
                flattened["LLM_MODEL"] = llm["model"]
            if "temperature" in llm:
                flattened["LLM_TEMPERATURE"] = llm["temperature"]
        
        # Database Configuration
        if "database" in yaml_data:
            db = yaml_data["database"]
            if "url" in db:
                flattened["DATABASE_URL"] = db["url"]
        
        # Embedding Configuration
        if "embedding" in yaml_data:
            emb = yaml_data["embedding"]
            if "model" in emb:
                flattened["EMBEDDING_MODEL"] = emb["model"]
            if "dimension" in emb:
                flattened["EMBEDDING_DIMENSION"] = emb["dimension"]
        
        # RAG Configuration
        if "rag" in yaml_data:
            rag = yaml_data["rag"]
            if "chunk_size" in rag:
                flattened["CHUNK_SIZE"] = rag["chunk_size"]
            if "chunk_overlap" in rag:
                flattened["CHUNK_OVERLAP"] = rag["chunk_overlap"]
            if "top_k_results" in rag:
                flattened["TOP_K_RESULTS"] = rag["top_k_results"]
            if "similarity_threshold" in rag:
                flattened["SIMILARITY_THRESHOLD"] = rag["similarity_threshold"]
        
        # Backend Configuration
        if "backend" in yaml_data:
            backend = yaml_data["backend"]
            if "api_url" in backend:
                flattened["BACKEND_API_URL"] = backend["api_url"]
        
        return flattened

# Initialize settings from YAML with env var overrides
settings = Settings.from_yaml()
