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
    """
    Liste tous les outils disponibles avec leurs détails
    """
    return [
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
        # Outils planifiés
        {
            "name": "run_sql",
            "description": "Exécute une requête SQL sur la base de données",
            "category": "database",
            "status": "planned",
            "version": "0.0",
            "parameters": ["query: str"],
            "returns": "Dict avec résultats de la requête"
        },
        {
            "name": "launch_scraper",
            "description": "Lance un scraper web pour collecter des données",
            "category": "scraping", 
            "status": "planned",
            "version": "0.0",
            "parameters": ["spider: str", "url: str"],
            "returns": "Dict avec ID du processus et statut"
        },
        {
            "name": "get_indicator",
            "description": "Récupère la valeur d'un KPI pour une date donnée",
            "category": "analytics",
            "status": "planned", 
            "version": "0.0",
            "parameters": ["name: str", "date: str"],
            "returns": "Dict avec valeur du KPI"
        },
        {
            "name": "forecast_kpi",
            "description": "Génère une prévision pour un KPI donné",
            "category": "ml",
            "status": "planned",
            "version": "0.0", 
            "parameters": ["name: str", "horizon: int"],
            "returns": "Dict avec prévisions"
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