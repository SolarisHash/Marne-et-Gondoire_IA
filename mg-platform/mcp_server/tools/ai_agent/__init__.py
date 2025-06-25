# ============================================================================
# POINT D'ENTRÉE PRINCIPAL - Agent IA Refactorisé
# mg-platform/mcp_server/tools/ai_agent/__init__.py
# ============================================================================

"""
Agent IA d'enrichissement de données d'entreprises - Version Modulaire
Point d'entrée principal avec compatibilité totale
"""

from typing import Dict, Any
from .core.agent import AIEnrichmentAgent
from .core.config import DEFAULT_CONFIG

def run_ai_enrichment_agent(sample_size: int = 10) -> Dict[str, Any]:
    """
    Point d'entrée principal - COMPATIBLE avec main.py existant
    
    Args:
        sample_size: Nombre d'entreprises à traiter
        
    Returns:
        Dict avec résultats d'enrichissement complets
    """
    
    try:
        # Configuration par défaut (hérite des réglages legacy)
        config = {
            "quality_threshold": 60,  # Plus permissif que 85
            "rate_limit_delay": 3,
            "search_mode": "real",  # "real" ou "simulation"
            "max_retries": 2,
            "duckduckgo_timeout": 10,
            "validation_timeout": 8,
            "fallback_enabled": True
        }
        
        # Créer et lancer l'agent
        agent = AIEnrichmentAgent(config)
        result = agent.enrich_sample(sample_size)
        
        return result
        
    except Exception as e:
        return {
            "error": f"Erreur Agent IA: {str(e)}",
            "error_type": type(e).__name__,
            "suggestion": "Vérifiez les logs détaillés et la configuration"
        }

# Alias pour compatibilité avec legacy
ai_agent_enrich = run_ai_enrichment_agent

__all__ = ["run_ai_enrichment_agent", "ai_agent_enrich", "AIEnrichmentAgent"]