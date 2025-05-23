# 🏙️ Marne & Gondoire - Plateforme IA

Cette plateforme intègre le **Model Context Protocol (MCP)** pour permettre à des agents IA d'interagir avec les outils métiers de Marne & Gondoire via une interface standardisée.

## 📋 Présentation

La plateforme Marne & Gondoire IA est conçue pour:

- Collecter des données depuis des sources web via des scrapers
- Exécuter des requêtes SQL sur la base de données analytique
- Lancer des workflows Airflow
- Générer des prévisions pour les indicateurs clés
- Exposer ces fonctionnalités aux agents IA via le protocole MCP

## 🛠️ Installation

### Prérequis

- Docker et Docker Compose
- Python 3.9+ (pour le développement local)
- Git

### Installation avec Docker

1. Cloner le dépôt:
```bash
git clone https://github.com/votre-organisation/marne-gondoire-ia.git
cd marne-gondoire-ia/mg-platform
```

2. Configurer les variables d'environnement:
```bash
cp .env.example .env
# Modifier le fichier .env avec vos informations
```

3. Lancer l'environnement avec Docker Compose:
```bash
docker-compose up -d
```

4. Vérifier que tout fonctionne correctement:
```bash
docker-compose ps
```

### Installation locale (développement)

1. Créer un environnement virtuel:
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
```

2. Installer les dépendances:
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement:
```bash
cp .env.example .env
# Modifier le fichier .env avec vos informations
```

4. Lancer le serveur MCP:
```bash
cd mg-platform
uvicorn mcp_server.main:app --reload --port 8080
```

## 🚀 Utilisation

### Serveur MCP

Le serveur MCP expose les fonctionnalités via l'URL `/mcp`. Vous pouvez accéder à l'interface Swagger à l'adresse: `http://localhost:8080/docs`.

### Outils disponibles

Le serveur MCP expose les outils suivants:

- **run_sql**: Exécuter des requêtes SQL sur la base de données
- **launch_scraper**: Lancer des scrapers pour collecter des données
- **get_indicator**: Obtenir des valeurs d'indicateurs
- **forecast_kpi**: Générer des prévisions pour des indicateurs

### Utilisation avec OpenAI

```python
from clients.openai_agent import MGOpenAIClient

client = MGOpenAIClient()
response = client.chat("Quelle est la tendance des permis de construire pour les 3 prochains mois?")
print(response["content"])
```

### Utilisation avec Claude

```python
from clients.claude_agent import MGClaudeClient

client = MGClaudeClient()
response = client.chat("Combien de logements ont été autorisés le mois dernier?")
print(response["content"])
```

## 📊 Exemple de workflow

1. **Collecte des données**:
   - Les scrapers récupèrent des données depuis des sites comme Sitadel
   - Les données sont stockées dans la base PostgreSQL

2. **Analyse prédictive**:
   - Les modèles Prophet ou TFT génèrent des prévisions
   - Les résultats sont exposés via l'API

3. **Intégration avec les agents IA**:
   - Les agents comme GPT-4 ou Claude peuvent accéder aux données et aux prévisions
   - Les utilisateurs interagissent avec les données via des chatbots

## 📝 Documentation

- [Documentation du SDK MCP](https://github.com/modelcontextprotocol/python-sdk)
- [Documentation FastMCP](https://pypi.org/project/fastmcp/)
- [Guide de développement](./docs/development.md)

## 🧪 Tests

Pour exécuter les tests unitaires:

```bash
cd mg-platform
pytest
```

## 🤝 Contribution

Les contributions sont les bienvenues! Veuillez suivre ces étapes:

1. Forker le dépôt
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committer vos changements (`git commit -m 'Add some amazing feature'`)
4. Pousser la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence [MIT](./LICENSE).

## 📧 Contact

Pour toute question concernant ce projet, veuillez contacter: data@mg-data.local
