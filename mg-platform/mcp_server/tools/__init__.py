"""
Outils disponibles pour le serveur MCP
"""

from .basic import get_project_status, list_available_tools
from .data_analyzer import analyze_data_gaps_advanced  # Nom corrigé

# Import conditionnel pour éviter les erreurs si le module n'existe pas
try:
    from .linkedin_scraper import enrich_file_with_linkedin, test_linkedin_enrichment
    LINKEDIN_AVAILABLE = True
except ImportError:
    LINKEDIN_AVAILABLE = False
    def enrich_file_with_linkedin(*args, **kwargs):
        return {"error": "Module LinkedIn non disponible"}
    def test_linkedin_enrichment(*args, **kwargs):
        return {"error": "Module LinkedIn non disponible"}

__all__ = [
    "get_project_status", 
    "list_available_tools", 
    "analyze_data_gaps_advanced",  # Nom corrigé
    "enrich_file_with_linkedin",
    "test_linkedin_enrichment"
]