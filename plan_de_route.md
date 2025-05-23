[![MARNE ET GONDOIRE - LAGNY SUR MARNE | AtelierJL](https://tse3.mm.bing.net/th?id=OIP.4dUDEJlNFj_DOX926ov-kAHaC9\&pid=Api)](https://www.atelierjl.fr/copie-de-lyon-entree-est-zac-mermoz)

Voici une feuille de route détaillée au format Markdown pour le projet **Marne & Gondoire**, intégrant le **Model Context Protocol (MCP)** afin de permettre à vos agents IA d'interagir de manière standardisée avec les outils métiers.

---

# 📘 Feuille de Route : Projet Marne & Gondoire avec MCP

## 🎯 Objectif

Mettre en place une plateforme d'agents IA capable de :

* Scraper des données depuis des sites web.
* Exécuter des requêtes SQL sur des bases de données internes.
* Lancer des workflows Airflow.
* Générer des prévisions à l'aide de modèles Prophet ou TFT.
* Le tout via le **Model Context Protocol (MCP)**, assurant une interopérabilité avec des LLMs comme GPT-4o, Claude ou Gemini.([Epsilon3D][1])

---

## 🧱 Structure du Projet

```
mg-platform/
├── mcp_server/
│   ├── main.py         # Serveur FastAPI + SDK MCP
│   ├── tools/
│   │   ├── sql.py      # Fonction run_sql
│   │   ├── scraper.py  # Fonction launch_scraper
│   │   └── kpi.py      # Fonctions get_indicator, forecast_kpi
│   └── tests/
├── dags/               # Workflows Airflow
├── scrapers/           # Spiders Scrapy & Playwright
├── models/             # Modèles Prophet, TFT
├── clients/
│   ├── openai_agent.py # Client MCP pour GPT-4o
│   ├── claude_agent.py # Client MCP pour Claude 4
│   └── langgraph.py    # Agent ReAct LangChain
└── docker-compose.yml
```

---

## ⚙️ Installation des Dépendances

### 1. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows : .venv\Scripts\activate
```

### 2. Installer les paquets nécessaires

```bash
pip install "mcp[cli]" fastapi uvicorn[standard] sqlalchemy psycopg2-binary
```

> **Remarque** : Le SDK officiel MCP est disponible sous le nom `mcp` avec l'extra `[cli]` pour inclure les outils en ligne de commande.&#x20;

---

## 🚀 Développement du Serveur MCP

### 1. Exemple de serveur (`main.py`)

```python
from fastapi import FastAPI
from mcp.server import MCPServer, Tool, Arg, String, Integer
from tools.sql import run_sql
from tools.scraper import launch_scraper
from tools.kpi import get_indicator, forecast_kpi

app = FastAPI(title="MG Data MCP")

server = MCPServer(
    name="mg-data-mcp",
    description="Outils pour le pipeline Marne & Gondoire",
    version="0.1.0"
)

server.add_tool(
    Tool(
        name="run_sql",
        description="Exécute une requête SQL en lecture seule sur la base de données analytique",
        args=[Arg("query", String())],
        func=run_sql,
        permissions=["viewer", "editor"]
    )
)
server.add_tool(
    Tool(
        name="launch_scraper",
        description="Lance un spider Scrapy ou Playwright par nom",
        args=[Arg("spider", String()), Arg("url", String())],
        func=launch_scraper,
        permissions=["editor"]
    )
)
server.add_tool(
    Tool(
        name="get_indicator",
        description="Retourne la valeur d'un KPI pour une date donnée",
        args=[Arg("name", String()), Arg("date", String())],
        func=get_indicator,
        permissions=["viewer"]
    )
)
server.add_tool(
    Tool(
        name="forecast_kpi",
        description="Retourne une prévision pour un KPI donné",
        args=[Arg("name", String()), Arg("horizon", Integer())],
        func=forecast_kpi,
        permissions=["viewer"]
    )
)

app.mount("/mcp", server.as_fastapi())
```

### 2. Lancer le serveur localement

```bash
uvicorn mcp_server.main:app --reload --port 8080
```

---

## 🛠️ Implémentation des Outils

### 1. Exécution de requêtes SQL (`tools/sql.py`)

```python
from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://mg:pwd@db:5432/analytics")

def run_sql(query: str) -> dict:
    with engine.begin() as conn:
        rows = conn.execute(text(query)).mappings().all()
    return {"rows": [dict(r) for r in rows]}
```

### 2. Lancer un scraper (`tools/scraper.py`)

```python
import subprocess

def launch_scraper(spider: str, url: str) -> dict:
    cmd = ["scrapy", "crawl", spider, "-a", f"start_url={url}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    return {"pid": proc.pid}
```

### 3. Gestion des KPIs (`tools/kpi.py`)

```python
import pandas as pd
from models.prophet import load_prophet

def get_indicator(name: str, date: str):
    # Implémentation pour récupérer la valeur du KPI
    pass

def forecast_kpi(name: str, horizon: int = 12):
    model = load_prophet(name)
    # Implémentation pour générer la prévision
    pass
```

---

## 🤖 Intégration des Agents

### 1. OpenAI Agents SDK (`clients/openai_agent.py`)

```python
from openai import OpenAI
from openai.agents import Agent, MCPClient

mcp = MCPClient(url="http://localhost:8080/mcp")
agent = Agent(model="gpt-4o-mini", tools=[mcp])

response = agent.chat("Lance le scraper 'sitadel' sur https://... et dis-moi le PID.")
print(response.message)
```

### 2. Anthropic Claude (`clients/claude_agent.py`)

```python
from anthropic import Anthropic, MCPClient

anthropic = Anthropic()
mcp = MCPClient(url="http://localhost:8080/mcp")
chat = anthropic.claude.tools(client=mcp)

print(chat("run_sql: SELECT COUNT(*) FROM fact_permis"))
```

---

## 🔐 Sécurité et Authentification

* **En développement local** : Utiliser un token Bearer simple dans l'en-tête `Authorization`.
* **En production** : Mettre en place OAuth2 ou mTLS pour sécuriser les communications.

---

## 🧪 Tests et CI/CD

* **Tests unitaires** : Utiliser `pytest` pour tester les fonctions exposées.
* **CI/CD** : Mettre en place des workflows avec GitHub Actions pour automatiser les tests et les déploiements.

---

## ☁️ Déploiement en Production

* **Serveur** : Déployer le serveur MCP sur un environnement de production sécurisé.
* **Nom de domaine** : Configurer un sous-domaine (ex. `mcp.mg-data.local`) avec un certificat TLS valide.
* **Scalabilité** : Envisager l'utilisation de solutions comme Cloudflare Workers pour une meilleure scalabilité.

---

## 📚 Ressources Complémentaires

* [Documentation officielle du SDK MCP](https://github.com/modelcontextprotocol/python-sdk)
* [Guide d'installation de FastMCP](https://pypi.org/project/fastmcp/)
* [Tutoriel pour construire un serveur MCP simple en Python](https://github.com/ruslanmv/Simple-MCP-Server-with-Python)

---

Cette feuille de route vous guidera dans la mise en place d'une infrastructure robuste et évolutive, permettant à vos agents IA d'interagir efficacement avec vos outils métiers via le protocole MCP.

[1]: https://www.epsilon3d.fr/residence-bleu-horizon/?utm_source=chatgpt.com "Résidence Bleu Horizon - Epsilon3D"
