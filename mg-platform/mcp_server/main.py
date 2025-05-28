from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'application
app = FastAPI(
    title="MG Data MCP Server",
    description="Serveur MCP pour la plateforme Marne & Gondoire",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes principales
@app.get("/")
async def root():
    """Point d'entrée principal du serveur"""
    return {
        "message": "Serveur MCP Marne & Gondoire",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "project": "Marne & Gondoire"
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
            "database": "⏳ Non configuré",
            "tools": "✅ Basiques disponibles"
        }
    }

@app.get("/info")
async def project_info():
    """Informations détaillées sur le projet"""
    return {
        "project": "Marne & Gondoire", 
        "description": "Plateforme d'analyse de données avec agents IA",
        "version": "0.1.0",
        "capabilities": [
            "API REST FastAPI",
            "Health monitoring", 
            "Documentation automatique",
            "Outils de base"
        ],
        "status": "en développement",
        "endpoints": {
            "root": "/",
            "health": "/health", 
            "info": "/info",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/tools")
async def list_tools():
    """Liste les outils disponibles"""
    try:
        from mcp_server.tools.basic import list_available_tools
        tools = list_available_tools()
        return {
            "tools": tools,
            "count": len(tools),
            "status": "loaded"
        }
    except ImportError:
        return {
            "tools": [],
            "count": 0,
            "status": "error",
            "message": "Impossible de charger les outils"
        }

@app.get("/status")
async def project_status():
    """Statut détaillé du projet"""
    try:
        from mcp_server.tools.basic import get_project_status
        status = get_project_status()
        return status
    except ImportError:
        return {
            "project_name": "Marne & Gondoire",
            "version": "0.1.0", 
            "status": "erreur de configuration",
            "error": "Impossible de charger les outils de statut"
        }

# Point d'entrée pour lancer le serveur directement
if __name__ == "__main__":
    # Configuration depuis les variables d'environnement
    port = int(os.getenv("SERVER_PORT", 8080))
    host = os.getenv("SERVER_HOST", "localhost")
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🚀 Démarrage du serveur MCP Marne & Gondoire")
    print(f"📍 Adresse: http://{host}:{port}")
    print(f"📚 Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health check: http://{host}:{port}/health")
    
    uvicorn.run(
        "mcp_server.main:app",  # Référence correcte au module
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )