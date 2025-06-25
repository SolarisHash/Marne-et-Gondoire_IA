# ============================================================================
# UTILS MODULE INIT
# mg-platform/mcp_server/tools/ai_agent/utils/__init__.py
# ============================================================================

"""
Module utils de l'Agent IA - Utilitaires et fonctions communes
"""

from .validators import (
    is_valid_business_website,
    is_valid_siret,
    is_valid_email,
    clean_company_name,
    normalize_commune_name
)

from .logging import (
    setup_session_logging,
    setup_rotating_logs,
    log_enrichment_start,
    log_enrichment_end,
    log_company_processing,
    log_enrichment_success,
    log_enrichment_failure,
    log_performance_metrics,
    cleanup_old_logs
)

# Imports futurs
# from .text_utils import TextNormalizer, NameMatcher

__all__ = [
    # Validateurs
    "is_valid_business_website",
    "is_valid_siret", 
    "is_valid_email",
    "clean_company_name",
    "normalize_commune_name",
    
    # Logging
    "setup_session_logging",
    "setup_rotating_logs", 
    "log_enrichment_start",
    "log_enrichment_end",
    "log_company_processing",
    "log_enrichment_success",
    "log_enrichment_failure",
    "log_performance_metrics",
    "cleanup_old_logs",
    
    # À venir
    # "TextNormalizer",
    # "NameMatcher"
]