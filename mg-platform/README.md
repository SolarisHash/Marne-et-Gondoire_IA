# Marne & Gondoire - Plateforme MCP

## 🎯 Objectif
Plateforme d'agents IA utilisant le Model Context Protocol (MCP) pour l'analyse de données et l'automatisation.

## 🚀 Démarrage Rapide

### Installation
```bash
# Cloner et se positionner
cd mg-platform

# Activer l'environnement virtuel
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Lancement
```bash
# Démarrer le serveur
python mcp_server/main.py
# ou
uvicorn mcp_server.main:app --reload --port 8080
```

### Test
- Interface web: http://localhost:8080
- Documentation API: http://localhost:8080/docs
- Health check: http://localhost:8080/health

## 📁 Structure
```
mg-platform/
├── mcp_server/         # Serveur MCP FastAPI
├── tools/              # Outils métiers
├── scrapers/           # Scrapers web
├── models/             # Modèles ML
├── clients/            # Clients IA
├── data/               # Données
└── tests/              # Tests
```

## 🔧 Développement
```bash
# Tests
pytest

# Linter (optionnel)
pip install black flake8
black .
flake8 .
```