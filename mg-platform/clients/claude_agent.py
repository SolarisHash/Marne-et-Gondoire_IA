import os
from dotenv import load_dotenv
import json
import requests
from typing import Dict, Any, List

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API Anthropic depuis les variables d'environnement
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# URL du serveur MCP
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")

class MGClaudeClient:
    """
    Client pour interagir avec l'API Anthropic Claude et le serveur MCP.
    """
    
    def __init__(self, api_key: str = None, mcp_url: str = None, model: str = "claude-3-opus-20240229"):
        """
        Initialise le client Claude avec la clé API et l'URL du serveur MCP.
        
        Args:
            api_key: La clé API Anthropic (par défaut: utilise la variable d'environnement)
            mcp_url: L'URL du serveur MCP (par défaut: utilise la variable d'environnement)
            model: Le modèle Claude à utiliser (par défaut: claude-3-opus-20240229)
        """
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.mcp_url = mcp_url or MCP_SERVER_URL
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key, 
            "anthropic-version": "2023-06-01"
        }
        
    def chat(self, prompt: str, system_message: str = None) -> Dict[str, Any]:
        """
        Envoie une requête de chat au modèle Claude avec accès au serveur MCP.
        
        Args:
            prompt: Le message de l'utilisateur
            system_message: Message système optionnel pour guider le modèle
            
        Returns:
            La réponse du modèle
        """
        try:
            # Message système par défaut expliquant les outils disponibles
            default_system_message = (
                f"Vous êtes un assistant IA pour Marne & Gondoire. "
                f"Vous avez accès aux outils suivants via le serveur MCP à {self.mcp_url}:\n"
                f"1. run_sql: Exécuter des requêtes SQL sur la base de données analytique\n"
                f"2. launch_scraper: Lancer des spiders de scraping\n"
                f"3. get_indicator: Obtenir des valeurs de KPI\n"
                f"4. forecast_kpi: Générer des prévisions pour des indicateurs\n"
                f"Utilisez ces outils pour répondre aux questions sur les données de Marne & Gondoire."
            )
            
            # Utiliser le message système personnalisé s'il est fourni
            system_message = system_message or default_system_message
            
            # Définir les outils disponibles via MCP
            tools = [
                {
                    "name": "run_sql",
                    "description": "Exécute une requête SQL en lecture seule sur la base de données analytique",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "La requête SQL à exécuter"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "launch_scraper",
                    "description": "Lance un spider Scrapy ou Playwright par nom",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "spider": {
                                "type": "string",
                                "description": "Le nom du spider à lancer"
                            },
                            "url": {
                                "type": "string", 
                                "description": "L'URL de départ pour le scraping"
                            }
                        },
                        "required": ["spider", "url"]
                    }
                },
                {
                    "name": "get_indicator",
                    "description": "Retourne la valeur d'un KPI pour une date donnée",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Le nom du KPI à récupérer"
                            },
                            "date": {
                                "type": "string",
                                "description": "La date pour laquelle récupérer la valeur (format YYYY-MM-DD)"
                            }
                        },
                        "required": ["name", "date"]
                    }
                },
                {
                    "name": "forecast_kpi",
                    "description": "Retourne une prévision pour un KPI donné",
                    "input_schema": {
                        "type": "object", 
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Le nom du KPI à prévoir"
                            },
                            "horizon": {
                                "type": "integer",
                                "description": "L'horizon de prévision en périodes (jours, mois selon le KPI)",
                                "default": 12
                            }
                        },
                        "required": ["name"]
                    }
                }
            ]
            
            # Payload pour l'API Claude
            payload = {
                "model": self.model,
                "system": system_message,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "tools": tools,
                "max_tokens": 1024
            }
            
            # Faire la requête à l'API Claude
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            response_data = response.json()
            
            # Traiter la réponse
            if response.status_code != 200:
                return {"error": f"Error {response.status_code}: {response_data.get('error', {}).get('message', 'Unknown error')}"}
            
            message = response_data.get('content', [])
            content_text = ""
            tool_calls = []
            
            # Extraire le contenu et les appels d'outils
            for block in message:
                if block.get('type') == 'text':
                    content_text += block.get('text', '')
                elif block.get('type') == 'tool_use':
                    tool_calls.append(block.get('tool_use', {}))
            
            # Si le modèle veut appeler un outil
            if tool_calls:
                tool_responses = []
                
                # Pour chaque appel d'outil
                for tool_call in tool_calls:
                    function_name = tool_call.get('name')
                    function_args = tool_call.get('input', {})
                    
                    # Appeler le serveur MCP
                    tool_response = self._call_mcp_tool(function_name, function_args)
                    tool_responses.append(tool_response)
                
                # Continuer la conversation avec les réponses des outils
                tool_outputs = []
                for i, tool_call in enumerate(tool_calls):
                    tool_outputs.append({
                        "tool_call_id": tool_call.get('id'),
                        "output": json.dumps(tool_responses[i])
                    })
                
                # Faire une nouvelle requête avec les résultats des outils
                new_messages = [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": message},
                    {"role": "tool", "content": tool_outputs}
                ]
                
                final_payload = {
                    "model": self.model,
                    "system": system_message,
                    "messages": new_messages,
                    "max_tokens": 1024
                }
                
                # Appeler à nouveau l'API Claude
                final_response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=final_payload
                )
                
                final_data = final_response.json()
                final_content = ""
                for block in final_data.get('content', []):
                    if block.get('type') == 'text':
                        final_content += block.get('text', '')
                
                return {
                    "content": final_content,
                    "tool_calls": [
                        {
                            "name": tc.get('name'),
                            "arguments": tc.get('input', {}),
                            "response": resp
                        }
                        for tc, resp in zip(tool_calls, tool_responses)
                    ]
                }
            
            # Si le modèle n'utilise pas d'outils
            return {"content": content_text}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _call_mcp_tool(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appelle un outil sur le serveur MCP.
        
        Args:
            function_name: Le nom de la fonction à appeler
            arguments: Les arguments de la fonction
            
        Returns:
            La réponse du serveur MCP
        """
        # Dans une implémentation réelle, faire une requête HTTP au serveur MCP
        # Pour l'instant, simulons les réponses pour tester
        
        if function_name == "run_sql":
            query = arguments.get("query", "")
            # Simulation d'une réponse
            if "SELECT" in query.upper():
                return {
                    "rows": [{"id": 1, "name": "Exemple"}],
                    "metadata": {"row_count": 1, "query": query}
                }
            else:
                return {"error": "Requête non valide"}
                
        elif function_name == "launch_scraper":
            spider = arguments.get("spider", "")
            url = arguments.get("url", "")
            # Simulation d'une réponse
            return {
                "pid": 12345,
                "spider": spider,
                "url": url,
                "timestamp": "2023-05-23T10:00:00",
                "status": "started"
            }
            
        elif function_name == "get_indicator":
            name = arguments.get("name", "")
            date = arguments.get("date", "")
            # Simulation d'une réponse
            return {
                "name": name,
                "date": date,
                "value": 42.5,
                "metadata": {"unit": "unités", "source": "historical_data"}
            }
            
        elif function_name == "forecast_kpi":
            name = arguments.get("name", "")
            horizon = arguments.get("horizon", 12)
            # Simulation d'une réponse
            return {
                "name": name,
                "horizon": horizon,
                "model": "prophet",
                "forecast": [
                    {"date": "2023-05-24", "value": 43.2, "lower": 40.1, "upper": 46.3},
                    {"date": "2023-05-25", "value": 44.1, "lower": 41.0, "upper": 47.2}
                ]
            }
            
        else:
            return {"error": f"Fonction inconnue: {function_name}"}


# Exemple d'utilisation
if __name__ == "__main__":
    client = MGClaudeClient()
    response = client.chat("Quels sont les permis de construire délivrés le mois dernier dans la commune de Lagny-sur-Marne?")
    print(json.dumps(response, indent=2))
