from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'application
app = FastAPI(
    title="MG Data MCP Server",
    description="Serveur MCP pour l'enrichissement de données Marne & Gondoire",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes principales
@app.get("/")
async def root():
    """Point d'entrée principal du serveur"""
    return {
        "message": "Serveur MCP Marne & Gondoire - Enrichissement de données",
        "version": "0.2.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "project": "Marne & Gondoire",
        "capabilities": [
            "📊 Analyse fichiers Excel/CSV",
            "🔗 Enrichissement LinkedIn", 
            "📈 Rapports de traitement",
            "🎯 Détection automatique des gaps"
        ],
        "available_endpoints": [
            "/health",
            "/analyze", 
            "/test-basic",
            "/info"
        ]
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état du serveur"""
    return {
        "status": "healthy",
        "service": "mg-data-mcp",
        "uptime": "running",
        "components": {
            "server": "✅ Actif",
            "basic_tools": "✅ Disponible",
            "file_system": "✅ Accessible"
        }
    }

@app.get("/analyze")
async def analyze_excel_data(file_path: Optional[str] = None):
    """
    Analyse un fichier Excel pour identifier les données manquantes
    """
    try:
        # Test basique d'abord
        from pathlib import Path
        
        # Vérifier que data/raw existe
        project_root = Path(__file__).parent.parent
        raw_dir = project_root / "data" / "raw"
        
        if not raw_dir.exists():
            return {
                "error": "Dossier data/raw/ non trouvé",
                "current_dir": str(project_root),
                "suggestion": f"Créez le dossier: mkdir -p {raw_dir}"
            }
        
        # Lister les fichiers disponibles
        files = list(raw_dir.glob("*"))
        excel_files = list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls"))
        
        if not excel_files:
            return {
                "error": "Aucun fichier Excel trouvé",
                "raw_dir": str(raw_dir),
                "files_found": [f.name for f in files],
                "expected_file": "Non diffusible_2025-04-14.xlsx"
            }
        
        # Si on arrive ici, on a au moins un fichier Excel
        target_file = excel_files[0]
        
        # Test simple de lecture
        try:
            import pandas as pd
            df = pd.read_excel(target_file)
            
            return {
                "status": "success",
                "message": "Analyse basique réussie",
                "file_info": {
                    "name": target_file.name,
                    "path": str(target_file),
                    "rows": len(df),
                    "columns": len(df.columns)
                },
                "first_columns": list(df.columns[:10]),
                "next_step": "Créez data_analyzer.py pour analyse avancée"
            }
            
        except Exception as e:
            return {
                "error": f"Impossible de lire le fichier Excel: {str(e)}",
                "file": str(target_file),
                "suggestion": "Vérifiez que pandas et openpyxl sont installés: pip install pandas openpyxl"
            }
        
    except ImportError as e:
        return {
            "error": f"Module manquant: {str(e)}",
            "suggestion": "Installez pandas: pip install pandas openpyxl"
        }
    except Exception as e:
        return {
            "error": f"Erreur inattendue: {str(e)}",
            "type": type(e).__name__
        }

@app.get("/test-basic")
async def test_basic_functionality():
    """Test des fonctionnalités de base"""
    try:
        from mcp_server.tools.basic import get_project_status
        status = get_project_status()
        
        return {
            "basic_tools": "✅ OK",
            "project_status": status,
            "message": "Tests de base réussis"
        }
    except Exception as e:
        return {
            "basic_tools": "❌ Erreur",
            "error": str(e)
        }

@app.get("/info")
async def project_info():
    """Informations détaillées sur le projet"""
    return {
        "project": "Marne & Gondoire", 
        "description": "Plateforme d'enrichissement de données d'entreprises",
        "version": "0.2.0",
        "status": "configuration en cours",
        "next_steps": [
            "1. Vérifier que le fichier Excel est dans data/raw/",
            "2. Installer pandas: pip install pandas openpyxl",
            "3. Créer les outils d'analyse avancée",
            "4. Tester l'enrichissement LinkedIn"
        ]
    }

@app.get("/analyze-advanced")
async def analyze_advanced():
    """Analyse avancée avec détection précise des opportunités LinkedIn"""
    try:
        from mcp_server.tools.data_analyzer import analyze_data_gaps_advanced
        result = analyze_data_gaps_advanced()
        return result
    except ImportError as e:
        return {
            "error": f"Module d'analyse avancée non disponible: {str(e)}",
            "solution": "Créez le fichier mcp_server/tools/data_analyzer.py"
        }
    except Exception as e:
        return {
            "error": f"Erreur analyse avancée: {str(e)}"
        }

if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 8080))
    host = os.getenv("SERVER_HOST", "localhost")
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🚀 Démarrage du serveur MCP Marne & Gondoire v0.2.0")
    print(f"📍 Adresse: http://{host}:{port}")
    print(f"📚 Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health check: http://{host}:{port}/health")
    print(f"📊 Analyse (basique): http://{host}:{port}/analyze")
    print(f"🧪 Test basic: http://{host}:{port}/test-basic")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )
