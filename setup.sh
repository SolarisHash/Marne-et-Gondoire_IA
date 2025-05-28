#!/bin/bash

# Script de configuration automatique pour Marne & Gondoire MCP Platform
# Usage: bash setup.sh

set -e  # Arrêter en cas d'erreur

echo "🚀 Configuration de la plateforme Marne & Gondoire MCP"
echo "=================================================="

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✅ Python détecté: $(python3 --version)"

# 1. Créer la structure du projet
echo "📁 Création de la structure de base..."

# Créer tous les dossiers
mkdir -p mg-platform/{mcp_server/{tools,tests},dags,scrapers/spiders,models/{prophet,tft},clients,data/{raw,processed,enriched},logs,config,docs}

cd mg-platform

# 2. Créer l'environnement virtuel
echo "🐍 Création de l'environnement virtuel..."
python3 -m venv .venv

# 3. Activer l'environnement virtuel (détection automatique de l'OS)
echo "⚡ Activation de l'environnement virtuel..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
    ACTIVATE_CMD=".venv\\Scripts\\activate"
else
    # Linux/Mac
    source .venv/bin/activate
    ACTIVATE_CMD="source .venv/bin/activate"
fi

# 4. Créer requirements.txt
echo "📦 Création du fichier requirements.txt..."
cat > requirements.txt << 'EOF'
# FastAPI et serveur
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Base de données
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# Data processing
pandas==2.1.3
numpy==1.25.2
openpyxl==3.1.2

# Utils
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.25.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
EOF

# 5. Installer les dépendances de base
echo "⬇️  Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Créer les fichiers de configuration
echo "⚙️  Création des fichiers de configuration..."

# .env.example
cat > .env.example << 'EOF'
# Base de données
DATABASE_URL=postgresql://mg_user:mg_password@localhost:5432/mg_analytics

# API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Configuration serveur
SERVER_HOST=localhost
SERVER_PORT=8080
DEBUG=true

# Scraping
USER_AGENT=MGPlatform/1.0 (+https://your-domain.com)
EOF

# Copier vers .env pour le développement
cp .env.example .env

# .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# Environment variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data files
data/raw/*
data/processed/*
data/enriched/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/enriched/.gitkeep

# Logs
logs/*.log
*.log

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db
EOF

# 7. Créer les fichiers .gitkeep
touch data/raw/.gitkeep data/processed/.gitkeep data/enriched/.gitkeep logs/.gitkeep

# 8. Créer les fichiers Python de base
echo "🐍 Création des fichiers Python de base..."

# mcp_server/__init__.py
mkdir -p mcp_server/tools
cat > mcp_server/__init__.py << 'EOF'
"""
Serveur MCP pour la plateforme Marne & Gondoire
"""

__version__ = "0.1.0"
__author__ = "Équipe Marne & Gondoire"
EOF

# mcp_server/main.py
cat > mcp_server/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI(
    title="MG Data MCP Server",
    description="Serveur MCP pour la plateforme Marne & Gondoire",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Serveur MCP Marne & Gondoire",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mg-data-mcp",
        "tools": ["basic"]
    }

if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 8080))
    host = os.getenv("SERVER_HOST", "localhost")
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)
EOF

# mcp_server/tools/__init__.py
cat > mcp_server/tools/__init__.py << 'EOF'
"""
Outils disponibles pour le serveur MCP
"""
EOF

# mcp_server/tools/basic.py
cat > mcp_server/tools/basic.py << 'EOF'
from datetime import datetime
from typing import Dict, List

def get_project_status() -> Dict:
    return {
        "project_name": "Marne & Gondoire",
        "version": "0.1.0",
        "status": "en développement",
        "last_updated": datetime.now().isoformat()
    }

def list_available_tools() -> List[Dict]:
    return [
        {
            "name": "get_project_status",
            "description": "Retourne le statut du projet",
            "status": "active"
        }
    ]
EOF

# tests/test_basic.py
mkdir -p tests
cat > tests/__init__.py << 'EOF'
EOF

cat > tests/test_basic.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from mcp_server.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["status"] == "running"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
EOF

# 9. Créer le README
cat > README.md << 'EOF'
# Marne & Gondoire - Plateforme MCP

## 🎯 Objectif
Plateforme d'agents IA utilisant le Model Context Protocol (MCP).

## 🚀 Démarrage Rapide

### Installation
```bash
# Activer l'environnement virtuel
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Lancer le serveur
python mcp_server/main.py
```

### Test
- Interface: http://localhost:8080
- Health: http://localhost:8080/health
- Tests: `pytest`

## 📁 Structure
```
mg-platform/
├── mcp_server/     # Serveur MCP
├── tools/          # Outils métiers  
├── data/           # Données
└── tests/          # Tests
```
EOF

# 10. Initialiser git si pas déjà fait
# if [ ! -d .git ]; then
#     echo "📝 Initialisation de Git..."
#     git init
#     git add .
#     git commit -m "Initial setup: Marne & Gondoire MCP Platform"
# fi

# 11. Test rapide
echo "🧪 Test de fonctionnement..."
python -c "
from mcp_server.tools.basic import get_project_status
print('✅ Import des outils: OK')
status = get_project_status()
print(f'✅ Test outil: {status[\"project_name\"]}')
"

echo ""
echo "🎉 Configuration terminée avec succès !"
echo "=================================================="
echo ""
echo "📋 Prochaines étapes:"
echo "1. Activer l'environnement: $ACTIVATE_CMD"
echo "2. Lancer le serveur: python mcp_server/main.py"
echo "3. Tester: http://localhost:8080"
echo "4. Exécuter les tests: pytest"
echo ""
echo "📁 Répertoire de travail: $(pwd)"
echo "🌟 Le projet est prêt pour le développement !"