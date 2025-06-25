# ============================================================================
# DATA MODULE INIT
# mg-platform/mcp_server/tools/ai_agent/data/__init__.py
# ============================================================================

"""
Module data de l'Agent IA - Chargement et traitement des données
"""

from .loader import DataLoader

# Imports futurs quand les modules seront créés
# from .analyzer import DataAnalyzer
# from .processor import DataProcessor

__all__ = [
    # Actuellement disponible
    "DataLoader",
    
    # À venir
    # "DataAnalyzer",
    # "DataProcessor"
]