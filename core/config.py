"""
Application configuration and settings.

This module handles all configuration aspects of the application:
1. Environment variables and settings
2. Directory structures
3. Application constants
4. Configuration validation
"""
from pathlib import Path
from enum import Enum
from typing import Dict, Any, Optional, Set
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# Directory Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    """Application settings with environment validation"""
    
    # Project Configuration
    PROJECT_NAME: str = Field(default="vPay", description="Project name")
    VERSION: str = Field(default="1.0.0", description="Project version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Database
    SUPABASE_URL: str = Field(..., description="Supabase URL")
    SUPABASE_KEY: str = Field(..., description="Supabase key")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    
    # LangChain Configuration
    LANGCHAIN_TRACING_V2: bool = Field(default=False, description="LangChain tracing")
    LANGCHAIN_API_KEY: Optional[str] = Field(default=None, description="LangChain API key")
    LANGCHAIN_PROJECT: Optional[str] = Field(default=None, description="LangChain project")
    LANGSMITH_API_KEY: Optional[str] = Field(default=None, description="LangSmith API key")
    
    # Inter Bank API
    INTER_CLIENT_ID: str = Field(..., description="Inter client ID")
    INTER_CLIENT_SECRET: str = Field(..., description="Inter client secret")
    INTER_CERT_FILE: Path = Field(..., description="Inter certificate file")
    INTER_KEY_FILE: Path = Field(..., description="Inter key file")
    INTER_ACCOUNT_NUMBER: Optional[str] = Field(default=None, description="Inter account number")
    
    # Processing
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="Max upload size in bytes")
    ALLOWED_EXTENSIONS: Set[str] = Field(default={".pdf"}, description="Allowed file extensions")
    
    # Validation
    AMOUNT_TOLERANCE: float = Field(default=0.01, description="Amount tolerance for validation")
    CNPJ_LENGTH: int = Field(default=14, description="CNPJ length")
    
    # LLM Configuration
    MODEL_NAME: str = Field(
        default="gpt-4o-mini",
        description="LLM model name",
        env="MODEL_NAME"  # Optional override via env
    )
    MODEL_TEMPERATURE: float = Field(
        default=0.0,
        description="LLM temperature",
        env="MODEL_TEMPERATURE"  # Optional override via env
    )
    MODEL_CHUNK_SIZE: int = Field(
        default=2000,
        description="Text chunk size",
        env="MODEL_CHUNK_SIZE"  # Optional override via env
    )
    MODEL_CHUNK_OVERLAP: int = Field(
        default=200,
        description="Text chunk overlap",
        env="MODEL_CHUNK_OVERLAP"  # Optional override via env
    )

    # Use SettingsConfigDict instead of model_config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Allow extra fields in environment
        use_enum_values=True
    )

# Application Constants
class FileExtension(str, Enum):
    """Supported file extensions"""
    PDF = ".pdf"
    CSV = ".csv"
    JSON = ".json"

class ProcessingStatus(str, Enum):
    """Processing status codes"""
    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    FAILED = "failed"
    VALIDATED = "validated"
    INVALID = "invalid"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Create settings instance
settings = get_settings()