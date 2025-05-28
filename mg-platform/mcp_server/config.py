import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Serveur
    server_host: str = "localhost"
    server_port: int = 8080
    debug: bool = True
    
    # Base de données
    database_url: Optional[str] = None
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Scraping
    user_agent: str = "MGPlatform/1.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instance globale des paramètres
settings = Settings()