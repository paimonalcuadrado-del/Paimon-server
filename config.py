"""
Configuration management using pydantic-settings for environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Configuration
    auth_token: str = "default-secret-token"
    host: str = "0.0.0.0"
    port: int = 8080
    
    # MEGA Configuration
    mega_email: Optional[str] = None
    mega_password: Optional[str] = None
    
    # Temporary Upload Directory
    temp_upload_dir: str = "temp_uploads"
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
