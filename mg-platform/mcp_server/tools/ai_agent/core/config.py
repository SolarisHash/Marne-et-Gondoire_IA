# ============================================================================
# CONFIGURATION CENTRALISÉE
# mg-platform/mcp_server/tools/ai_agent/core/config.py
# ============================================================================

"""
Configuration centralisée pour l'Agent IA d'enrichissement
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class SearchConfig:
    """Configuration pour les stratégies de recherche"""
    web_timeout: int = 10
    linkedin_timeout: int = 8
    max_retries: int = 2
    rate_limit_delay: float = 3.0
    user_agents: List[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ])

@dataclass
class ValidationConfig:
    """Configuration pour la validation qualité"""
    quality_threshold_real: int = 85  # Noms réels
    quality_threshold_fallback: int = 60  # "NON-DIFFUSIBLE"
    minimum_name_similarity: float = 50.0
    minimum_geo_match: float = 70.0
    
@dataclass
class OutputConfig:
    """Configuration pour la sauvegarde"""
    colorize_ai_data: bool = True
    preserve_siret_format: bool = True
    add_metadata_columns: bool = True
    excel_engine: str = 'openpyxl'

# Configuration par défaut - COMPATIBLE avec legacy
DEFAULT_CONFIG: Dict[str, Any] = {
    # Qualité et validation
    "quality_threshold": 60,  # Plus permissif que 85
    "rate_limit_delay": 3,
    "search_mode": "real",  # "real" ou "simulation"
    "max_retries": 2,
    "duckduckgo_timeout": 10,
    "validation_timeout": 8,
    "fallback_enabled": True,
    
    # Paths et fichiers
    "raw_data_dir": "data/raw",
    "processed_data_dir": "data/processed", 
    "logs_dir": "logs",
    
    # Session et logging
    "log_level": "INFO",
    "detailed_logging": True,
    "session_id_format": "%Y%m%d_%H%M%S",
    
    # Sources et priorités
    "source_priority": ["linkedin", "web_search", "fallback"],
    "enable_real_search": True,
    "enable_fallback": True,
    
    # Formats de sortie
    "excel_colorization": True,
    "generate_analytics": True,
    "create_backups": False
}

# Mapping des colonnes standards
COLUMN_MAPPING = {
    "company_name": ["Nom courant/Dénomination", "Dénomination", "Nom"],
    "siret": ["SIRET", "Siret", "siret"],
    "commune": ["Commune", "Ville", "commune"],
    "website": ["Site Web établissement", "Site web", "Website"],
    "naf_code": ["Code NAF", "APE", "Activité"],
    "naf_label": ["Libellé NAF", "Libellé activité", "Secteur"]
}

# Configuration des types d'enrichissement par colonne
ENRICHMENT_STRATEGIES = {
    "website": {
        "priority": "CRITIQUE",
        "sources": ["linkedin", "duckduckgo", "google"],
        "fallback_enabled": True,
        "validation_strict": False
    },
    "email": {
        "priority": "HAUTE", 
        "sources": ["linkedin", "website_parsing"],
        "fallback_enabled": False,
        "validation_strict": True
    },
    "phone": {
        "priority": "MOYENNE",
        "sources": ["linkedin", "website_parsing"],
        "fallback_enabled": False,
        "validation_strict": True
    }
}

def get_config(custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Retourne la configuration finale en fusionnant les valeurs par défaut
    avec la configuration personnalisée
    """
    config = DEFAULT_CONFIG.copy()
    
    if custom_config:
        config.update(custom_config)
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """Valide que la configuration est cohérente"""
    
    required_keys = [
        "quality_threshold", "rate_limit_delay", "search_mode",
        "raw_data_dir", "processed_data_dir", "logs_dir"
    ]
    
    # Vérifier les clés requises
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Clé de configuration manquante: {key}")
    
    # Valider les valeurs
    if not 0 <= config["quality_threshold"] <= 100:
        raise ValueError("quality_threshold doit être entre 0 et 100")
    
    if config["rate_limit_delay"] < 0:
        raise ValueError("rate_limit_delay doit être positif")
    
    if config["search_mode"] not in ["real", "simulation"]:
        raise ValueError("search_mode doit être 'real' ou 'simulation'")
    
    return True