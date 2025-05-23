import subprocess
import os
from typing import Dict, Any
import json
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Chemin vers les scrapers
SCRAPERS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scrapers"))

def launch_scraper(spider: str, url: str) -> Dict[str, Any]:
    """
    Lance un spider Scrapy ou Playwright par nom.
    
    Args:
        spider: Le nom du spider à lancer
        url: L'URL de départ pour le scraping
        
    Returns:
        Un dictionnaire contenant les informations sur le processus lancé
    """
    # Valider le nom du spider (sécurité)
    if not spider.isalnum() and not all(c in spider for c in ['-', '_']):
        return {"error": "Nom de spider invalide"}
    
    # Enregistrer la demande de scraping
    timestamp = datetime.now().isoformat()
    logger.info(f"Demande de scraping : {spider} sur {url} à {timestamp}")
    
    try:
        # Déterminer si c'est un spider Scrapy ou Playwright
        if os.path.exists(os.path.join(SCRAPERS_PATH, "scrapy", f"{spider}.py")):
            # C'est un spider Scrapy
            cmd = ["scrapy", "crawl", spider, "-a", f"start_url={url}"]
            cwd = os.path.join(SCRAPERS_PATH, "scrapy")
        elif os.path.exists(os.path.join(SCRAPERS_PATH, "playwright", f"{spider}.py")):
            # C'est un spider Playwright
            cmd = ["python", f"{spider}.py", url]
            cwd = os.path.join(SCRAPERS_PATH, "playwright")
        else:
            return {"error": f"Spider '{spider}' introuvable"}
        
        # Lancer le processus
        proc = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        
        # Retourner l'ID du processus et les informations
        result = {
            "pid": proc.pid,
            "spider": spider,
            "url": url,
            "timestamp": timestamp,
            "status": "started"
        }
        
        # Enregistrer l'information dans un fichier JSON pour suivi
        with open(os.path.join(SCRAPERS_PATH, "jobs", f"{proc.pid}.json"), "w") as f:
            json.dump(result, f)
            
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors du lancement du spider {spider}: {str(e)}")
        return {"error": str(e)}
