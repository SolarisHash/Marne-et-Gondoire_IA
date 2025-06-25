# ============================================================================
# ENRICHMENT MODULE INIT
# mg-platform/mcp_server/tools/ai_agent/enrichment/__init__.py
# ============================================================================

"""
Module enrichment de l'Agent IA - Stratégies d'enrichissement et validation
"""

from .strategies import EnrichmentStrategy
from .validation import QualityValidator

# Import futur
# from .scoring import AdvancedScoring

__all__ = [
    # Actuellement disponible
    "EnrichmentStrategy",
    "QualityValidator",
    
    # À venir
    # "AdvancedScoring"
]