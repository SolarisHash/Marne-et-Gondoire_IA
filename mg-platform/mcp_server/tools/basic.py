from datetime import datetime
from typing import Dict, List, Optional
import os
import sys

def get_project_status() -> Dict:
    """
    Retourne le statut actuel du projet avec informations détaillées
    """
    return {
        "project_name": "Marne & Gondoire",
        "version": "0.1.0",
        "status": "en développement",
        "last_updated": datetime.now().isoformat(),
        "environment": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "working_directory": os.getcwd()
        },
        "components": {
            "mcp_server": "✅ Fonctionnel",
            "fastapi": "✅ Actif",
            "database": "⏳ En attente de configuration",
            "scrapers": "⏳ En attente d'implémentation", 
            "ml_models": "⏳ En attente d'implémentation",
            "tests": "✅ Configurés"
        },
        "next_steps": [
            "Configuration base de données",
            "Implémentation outils SQL",
            "Développement scrapers",
            "Intégration agents IA"
        ]
    }

def list_available_tools() -> List[Dict]:
    """Liste tous les outils disponibles - VERSION MISE À JOUR"""
    return [
        # Outils de base
        {
            "name": "get_project_status",
            "description": "Retourne le statut détaillé du projet",
            "category": "info",
            "status": "active",
            "version": "1.0",
            "parameters": [],
            "returns": "Dict avec informations du projet"
        },
        {
            "name": "list_available_tools", 
            "description": "Liste tous les outils disponibles",
            "category": "info",
            "status": "active",
            "version": "1.0",
            "parameters": [],
            "returns": "List[Dict] avec détails des outils"
        },
        
        # Nouveaux outils d'analyse
        {
            "name": "analyze_data_gaps",
            "description": "Analyse un fichier Excel/CSV pour identifier les données manquantes",
            "category": "analysis",
            "status": "active",
            "version": "1.0",
            "parameters": ["file_path: str (optionnel)"],
            "returns": "Dict avec analyse complète et opportunités d'enrichissement"
        },
        
        # Outils d'enrichissement LinkedIn
        {
            "name": "enrich_file_with_linkedin",
            "description": "Enrichit un fichier Excel via recherche LinkedIn",
            "category": "enrichment",
            "status": "active", 
            "version": "1.0",
            "parameters": [
                "file_path: str (optionnel)",
                "target_columns: List[str] (optionnel)", 
                "max_companies: int (optionnel)"
            ],
            "returns": "Dict avec résultats enrichissement et fichier généré"
        },
        {
            "name": "test_linkedin_enrichment",
            "description": "Test rapide enrichissement LinkedIn sur échantillon",
            "category": "enrichment",
            "status": "active",
            "version": "1.0", 
            "parameters": ["sample_size: int"],
            "returns": "Dict avec résultats de test"
        }
    ]

def get_system_info() -> Dict:
    """
    Informations système pour le diagnostic
    """
    return {
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "path": sys.path[:3]  # Premières entrées seulement
        },
        "environment": {
            "cwd": os.getcwd(),
            "user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
            "platform": sys.platform
        },
        "project": {
            "root": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "structure_ok": os.path.exists("mcp_server") and os.path.exists("tests")
        }
    }