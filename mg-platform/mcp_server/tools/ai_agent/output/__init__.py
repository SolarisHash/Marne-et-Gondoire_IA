# ============================================================================
# OUTPUT MODULE INIT
# mg-platform/mcp_server/tools/ai_agent/output/__init__.py
# ============================================================================

"""
Module output de l'Agent IA - Sauvegarde et génération de rapports
"""

from .excel_writer import ExcelWriter

# Imports futurs
# from .colorizer import ExcelColorizer
# from .reporter import AnalyticsReporter

__all__ = [
    # Actuellement disponible
    "ExcelWriter",
    
    # À venir
    # "ExcelColorizer",
    # "AnalyticsReporter"
]