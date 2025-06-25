# ============================================================================
# SEARCH MODULE INIT
# mg-platform/mcp_server/tools/ai_agent/search/__init__.py
# ============================================================================

"""
Module search de l'Agent IA - Moteurs de recherche et fallback
"""

from .web_search import WebSearchEngine
from .fallback import IntelligentFallbackGenerator

# Import futur
# from .linkedin_search import LinkedInSearchEngine

__all__ = [
    # Actuellement disponible
    "WebSearchEngine",
    "IntelligentFallbackGenerator",
    
    # À venir
    # "LinkedInSearchEngine"
]