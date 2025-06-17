from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional
from fastapi.responses import PlainTextResponse

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

@app.get("/analyze-advanced")
async def analyze_advanced():
    """Analyse avancée avec détection précise des opportunités LinkedIn"""
    try:
        # Import direct du fichier
        import os
        import importlib.util
        
        # Chemin vers le fichier data_analyzer.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        analyzer_path = os.path.join(current_dir, "tools", "data_analyzer.py")
        
        if not os.path.exists(analyzer_path):
            return {
                "error": f"Fichier non trouvé: {analyzer_path}",
                "current_dir": current_dir,
                "tools_exists": os.path.exists(os.path.join(current_dir, "tools"))
            }
        
        # Charger le module dynamiquement
        spec = importlib.util.spec_from_file_location("data_analyzer", analyzer_path)
        data_analyzer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_analyzer)
        
        # Appeler la fonction
        result = data_analyzer.analyze_data_gaps_advanced()
        return result
        
    except Exception as e:
        return {
            "error": f"Erreur: {str(e)}",
            "type": type(e).__name__,
            "current_dir": os.path.dirname(os.path.abspath(__file__))
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

@app.get("/analyze-color", response_class=PlainTextResponse)
async def analyze_with_colors():
    """Version avec codes couleur ANSI pour terminal"""
    try:
        import os
        import importlib.util
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        analyzer_path = os.path.join(current_dir, "tools", "data_analyzer.py")
        
        spec = importlib.util.spec_from_file_location("data_analyzer", analyzer_path)
        data_analyzer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_analyzer)
        
        result = data_analyzer.analyze_data_gaps_advanced()
        
        if "error" in result:
            return f"\033[91m❌ ERREUR: {result['error']}\033[0m"
        
        # Codes couleur ANSI
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        BOLD = '\033[1m'
        END = '\033[0m'
        
        report = f"""
{BOLD}{CYAN}🚀 ANALYSE MARNE & GONDOIRE{END}
{CYAN}{'='*50}{END}

{BOLD}📁 FICHIER:{END}
  {result['file_info']['name']}
  {GREEN}{result['file_info']['total_companies']:,} entreprises{END} | {result['file_info']['total_columns']} colonnes

{BOLD}📊 VUE D'ENSEMBLE:{END}
  Complétion moyenne: {GREEN if result['global_stats']['average_completion_rate'] > 70 else YELLOW}{result['global_stats']['average_completion_rate']}%{END}
  Champs manquants: {RED}{result['global_stats']['total_missing_fields']:,}{END}

{BOLD}{RED}🔥 TOP OPPORTUNITÉS LINKEDIN:{END}
"""
        
        for i, priority in enumerate(result['top_priorities'][:3], 1):
            priority_color = RED if "CRITIQUE" in priority['priority'] else YELLOW if "HAUTE" in priority['priority'] else GREEN
            report += f"""
                {BOLD}{i}. {priority['column']}{END}
                {RED}Manquants: {priority['missing_count']:,}{END} | {GREEN}Gain: {priority['estimated_gain']:,}{END}
                {priority_color}{priority['priority']}{END}
            """

        # Sites web spécifiquement
        site_priority = result['top_priorities'][0]
        if 'site' in site_priority['column'].lower():
            report += f"""
                {BOLD}{GREEN}💰 JACKPOT SITES WEB:{END}
                {RED}{site_priority['missing_count']:,}{END} sites manquants sur {result['file_info']['total_companies']:,}
                {GREEN}{site_priority['estimated_gain']:,}{END} sites récupérables via LinkedIn
                {YELLOW}Temps estimé: {result['batch_strategy']['estimated_processing_time']}{END}
            """

        report += f"""
                {BOLD}{BLUE}🚀 COMMANDES RAPIDES:{END}
                Test:       {CYAN}curl http://localhost:8080/enrich?test_mode=true{END}
                Sites web:  {CYAN}curl -X POST http://localhost:8080/enrich-websites{END}
                Rapport:    {CYAN}curl http://localhost:8080/analyze-report{END}

                {BOLD}{GREEN}✨ Prêt pour l'enrichissement !{END}
            """
        
        return report
        
    except Exception as e:
        return f"\033[91m❌ ERREUR: {str(e)}\033[0m"

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
