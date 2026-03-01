"""
Configuration management for the AI Legal Research Assistant.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    api_title: str = "AI Legal Research Assistant"
    api_version: str = "2.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Google Gemini Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model: str = "models/gemini-2.5-flash"
    embedding_model: str = "models/gemini-embedding-001"
    max_tokens: int = 2000
    temperature: float = 0.3
    
    # Endee Vector Database Configuration
    endee_api_key: Optional[str] = Field(default=None, env="ENDEE_API_KEY")
    endee_url: str = Field(default="https://api.endee.io/v1", env="ENDEE_URL")
    
    # Database Configuration
    vector_db_path: str = "./data/vector_db"
    query_history_db: str = "./data/query_history.db"
    
    # Document Processing
    documents_path: str = "./data/documents"
    max_upload_size_mb: int = 50
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Search Configuration
    vector_weight: float = 0.7  # 70% vector, 30% keyword
    keyword_weight: float = 0.3
    top_k_results: int = 5
    similarity_threshold: float = 0.7
    
    # Performance Settings
    enable_performance_logging: bool = True
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # Cache Settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure required directories exist
Path(settings.vector_db_path).parent.mkdir(parents=True, exist_ok=True)
Path(settings.query_history_db).parent.mkdir(parents=True, exist_ok=True)
Path(settings.documents_path).mkdir(parents=True, exist_ok=True)
Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
