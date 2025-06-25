# ============================================================================
# CORE MODULE INIT
# mg-platform/mcp_server/tools/ai_agent/core/__init__.py
# ============================================================================

"""
Module core de l'Agent IA - Classes et fonctions principales
"""

from .agent import AIEnrichmentAgent
from .config import DEFAULT_CONFIG, get_config, validate_config
from .exceptions import (
    AIAgentError, 
    DataLoadError, 
    DataValidationError,
    EnrichmentError, 
    SearchError, 
    ValidationError,
    OutputError, 
    ConfigurationError,
    RateLimitError,
    WebSearchTimeoutError
)

__all__ = [
    # Agent principal
    "AIEnrichmentAgent",
    
    # Configuration
    "DEFAULT_CONFIG", 
    "get_config", 
    "validate_config",
    
    # Exceptions
    "AIAgentError", 
    "DataLoadError", 
    "DataValidationError",
    "EnrichmentError", 
    "SearchError", 
    "ValidationError",
    "OutputError", 
    "ConfigurationError", 
    "RateLimitError",
    "WebSearchTimeoutError"
]