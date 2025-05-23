"""
DAG pour le scraping des données Sitadel (permis de construire)
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import sys
import json
import requests

# Ajouter le chemin du projet pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configuration par défaut pour le DAG
default_args = {
    'owner': 'marne-et-gondoire',
    'depends_on_past': False,
    'email': ['data@mg-data.local'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# URL du serveur MCP
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://mcp_server:8080/mcp")

def run_sitadel_scraper(**kwargs):
    """
    Lance le scraping des données Sitadel via le serveur MCP
    """
    url = "https://www.statistiques.developpement-durable.gouv.fr/la-base-des-permis-de-construire"
    tool_name = "launch_scraper"
    
    # Préparer la requête au serveur MCP
    headers = {"Content-Type": "application/json"}
    payload = {
        "name": tool_name,
        "arguments": {
            "spider": "sitadel",
            "url": url
        }
    }
    
    try:
        # Appeler le serveur MCP
        response = requests.post(f"{MCP_SERVER_URL}/tools", headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"Scraper lancé avec succès: {json.dumps(result, indent=2)}")
        
        # Stocker l'ID du processus pour suivi
        kwargs['ti'].xcom_push(key='scraper_pid', value=result.get('pid'))
        return result
        
    except Exception as e:
        print(f"Erreur lors du lancement du scraper: {str(e)}")
        raise

def check_scraper_status(**kwargs):
    """
    Vérifie le statut du processus de scraping
    """
    # Récupérer l'ID du processus depuis XCom
    ti = kwargs['ti']
    pid = ti.xcom_pull(key='scraper_pid', task_ids='run_sitadel_scraper')
    
    if not pid:
        print("Aucun ID de processus trouvé")
        return False
    
    # Dans un cas réel, on vérifierait l'état du processus et les fichiers de sortie
    # Pour cet exemple, nous simulons simplement une vérification
    print(f"Vérification du statut pour le processus {pid}")
    
    # Simulation: vérifier si un fichier de statut existe
    status_file = os.path.join("scrapers", "jobs", f"{pid}.json")
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            status = json.load(f)
            print(f"Statut: {json.dumps(status, indent=2)}")
            return status.get('status') == 'completed'
    
    return False

def process_scraped_data(**kwargs):
    """
    Traite les données récupérées par le scraper
    """
    print("Traitement des données récupérées...")
    # Dans un cas réel, on traiterait les fichiers de sortie, on les chargerait en BDD, etc.
    return True

# Créer le DAG
with DAG(
    'scrape_sitadel_data',
    default_args=default_args,
    description='Récupère les dernières données Sitadel des permis de construire',
    schedule_interval=timedelta(days=7),  # Exécution hebdomadaire
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['scraping', 'sitadel', 'permis'],
) as dag:

    # Tâche 1: Lancement du scraper
    task_run_scraper = PythonOperator(
        task_id='run_sitadel_scraper',
        python_callable=run_sitadel_scraper,
        provide_context=True,
    )
    
    # Tâche 2: Vérification du statut
    task_check_status = PythonOperator(
        task_id='check_scraper_status',
        python_callable=check_scraper_status,
        provide_context=True,
    )
    
    # Tâche 3: Traitement des données
    task_process_data = PythonOperator(
        task_id='process_scraped_data',
        python_callable=process_scraped_data,
        provide_context=True,
    )
    
    # Définir l'ordre des tâches
    task_run_scraper >> task_check_status >> task_process_data
