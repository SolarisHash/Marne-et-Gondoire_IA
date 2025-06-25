# ============================================================================
# EXCEPTIONS PERSONNALISÉES
# mg-platform/mcp_server/tools/ai_agent/core/exceptions.py
# ============================================================================

"""
Exceptions personnalisées pour l'Agent IA d'enrichissement
"""

class AIAgentError(Exception):
    """Exception de base pour l'Agent IA"""
    pass

class DataLoadError(AIAgentError):
    """Erreur lors du chargement des données"""
    pass

class DataValidationError(AIAgentError):
    """Erreur lors de la validation des données"""
    pass

class EnrichmentError(AIAgentError):
    """Erreur lors de l'enrichissement"""
    pass

class SearchError(AIAgentError):
    """Erreur lors des recherches web/LinkedIn"""
    pass

class ValidationError(AIAgentError):
    """Erreur lors de la validation qualité"""
    pass

class OutputError(AIAgentError):
    """Erreur lors de la sauvegarde"""
    pass

class ConfigurationError(AIAgentError):
    """Erreur de configuration"""
    pass

class RateLimitError(SearchError):
    """Erreur de limite de débit"""
    pass

class WebSearchTimeoutError(SearchError):
    """Timeout lors des recherches web"""
    pass