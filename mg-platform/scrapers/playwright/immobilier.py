"""
Spider Playwright pour scraper des données immobilières nécessitant l'exécution de JavaScript
"""
import os
import sys
import json
import asyncio
from datetime import datetime
import re
from playwright.async_api import async_playwright
import pandas as pd
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("immobilier_spider.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("immobilier_spider")

class ImmobilierSpider:
    """
    Spider pour récupérer des données immobilières à partir de sites web dynamiques.
    """
    
    def __init__(self, start_url=None):
        """
        Initialise le spider avec l'URL de départ et les dossiers de stockage
        """
        self.start_url = start_url or "https://www.seloger.com/recherche-avancee/achat/77/lagny-sur-marne/"
        self.data_folder = os.path.join(os.path.dirname(__file__), "..", "..", "data", "immobilier")
        self.screenshot_folder = os.path.join(self.data_folder, "screenshots")
        
        # Créer les dossiers nécessaires
        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.screenshot_folder, exist_ok=True)
        
        # Journal des données
        self.data_log = []
        
        # Données récupérées
        self.properties = []
        
    async def run(self):
        """
        Exécute le scraping avec Playwright
        """
        logger.info(f"Démarrage du scraping: {self.start_url}")
        
        async with async_playwright() as p:
            # Lancer le navigateur
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Configuration du navigateur
            await page.set_viewport_size({"width": 1280, "height": 800})
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            
            try:
                # Naviguer vers l'URL de départ
                await page.goto(self.start_url, wait_until="networkidle")
                
                # Accepter les cookies si nécessaire
                try:
                    accept_button = await page.wait_for_selector("button:has-text('Accepter')", timeout=5000)
                    if accept_button:
                        await accept_button.click()
                        logger.info("Cookies acceptés")
                except Exception as e:
                    logger.warning(f"Pas de popup de cookies ou erreur: {str(e)}")
                
                # Prendre une capture d'écran de la page d'accueil
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(self.screenshot_folder, f"{timestamp}_homepage.png")
                await page.screenshot(path=screenshot_path)
                logger.info(f"Capture d'écran sauvegardée: {screenshot_path}")
                
                # Scraper les annonces
                await self._scrape_listings(page)
                
                # Traiter les données collectées
                self._process_data()
                
            except Exception as e:
                logger.error(f"Erreur lors du scraping: {str(e)}")
                
            finally:
                # Fermer le navigateur
                await browser.close()
                
        # Enregistrer le statut final
        self._update_status("completed")
        logger.info("Scraping terminé")
                
    async def _scrape_listings(self, page):
        """
        Scrape les annonces immobilières sur la page
        """
        logger.info("Extraction des annonces immobilières")
        
        # Boucle à travers plusieurs pages (simuler pour cet exemple)
        for page_num in range(1, 3):  # Limiter à 2 pages pour l'exemple
            if page_num > 1:
                # Aller à la page suivante (adapter selon le site réel)
                next_page_button = await page.query_selector("a.pagination__next-button")
                if next_page_button:
                    await next_page_button.click()
                    await page.wait_for_load_state("networkidle")
                else:
                    logger.info("Pas de bouton 'page suivante' trouvé, arrêt du scraping")
                    break
            
            # Attendre que les éléments soient chargés
            await asyncio.sleep(2)  # Pause pour s'assurer que tout est chargé
            
            # Extraire les annonces (adapter les sélecteurs selon le site réel)
            property_cards = await page.query_selector_all("div.c-item-card")
            
            for i, card in enumerate(property_cards):
                try:
                    # Extraire les données de l'annonce
                    property_data = {}
                    
                    # Titre
                    title_el = await card.query_selector(".c-item-card__title")
                    property_data["title"] = await title_el.text_content() if title_el else "Inconnu"
                    
                    # Prix
                    price_el = await card.query_selector(".c-item-card__price")
                    price_text = await price_el.text_content() if price_el else ""
                    # Nettoyer et extraire le prix
                    property_data["price"] = self._extract_price(price_text)
                    
                    # Surface
                    surface_el = await card.query_selector(".c-item-card__surface")
                    surface_text = await surface_el.text_content() if surface_el else ""
                    # Extraire la surface
                    property_data["surface"] = self._extract_surface(surface_text)
                    
                    # Adresse
                    location_el = await card.query_selector(".c-item-card__address")
                    property_data["location"] = await location_el.text_content() if location_el else "Inconnu"
                    
                    # URL de l'annonce
                    link_el = await card.query_selector("a.c-item-card__link")
                    property_data["url"] = await page.evaluate("(el) => el.href", link_el) if link_el else ""
                    
                    # Date d'ajout aux résultats
                    property_data["scraped_at"] = datetime.now().isoformat()
                    
                    # Ajouter l'annonce à la liste
                    self.properties.append(property_data)
                    logger.debug(f"Annonce extraite: {property_data['title']}")
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'extraction d'une annonce: {str(e)}")
            
            logger.info(f"Page {page_num} traitée, {len(property_cards)} annonces trouvées")
            
            # Prendre une capture d'écran de chaque page
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(self.screenshot_folder, f"{timestamp}_page{page_num}.png")
            await page.screenshot(path=screenshot_path)
            
    def _extract_price(self, price_text):
        """
        Extrait le prix d'une chaîne de texte
        """
        if not price_text:
            return None
            
        # Motif pour trouver des nombres
        match = re.search(r'(\d[\d\s]*)', price_text)
        if match:
            # Nettoyer et convertir en nombre
            price_str = match.group(1).replace(' ', '')
            try:
                return int(price_str)
            except ValueError:
                return None
        return None
        
    def _extract_surface(self, surface_text):
        """
        Extrait la surface d'une chaîne de texte
        """
        if not surface_text:
            return None
            
        # Motif pour trouver la surface en m²
        match = re.search(r'(\d+(?:[,.]\d+)?)\s*m²', surface_text)
        if match:
            # Convertir en nombre
            surface_str = match.group(1).replace(',', '.')
            try:
                return float(surface_str)
            except ValueError:
                return None
        return None
        
    def _process_data(self):
        """
        Traite les données collectées (conversion en DataFrame, etc.)
        """
        if not self.properties:
            logger.warning("Aucune donnée à traiter")
            return
            
        logger.info(f"Traitement de {len(self.properties)} annonces immobilières")
        
        # Convertir en DataFrame
        df = pd.DataFrame(self.properties)
        
        # Enregistrer en CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(self.data_folder, f"immobilier_{timestamp}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"Données sauvegardées: {csv_path}")
        
        # Enregistrer en JSON
        json_path = os.path.join(self.data_folder, f"immobilier_{timestamp}.json")
        df.to_json(json_path, orient='records', indent=2)
        logger.info(f"Données sauvegardées: {json_path}")
        
        # Ajouter au journal
        self.data_log.append({
            'source_url': self.start_url,
            'properties_count': len(self.properties),
            'csv_path': csv_path,
            'json_path': json_path,
            'timestamp': datetime.now().isoformat()
        })
        
        # Sauvegarder le journal
        log_path = os.path.join(self.data_folder, f"log_{timestamp}.json")
        with open(log_path, 'w') as f:
            json.dump(self.data_log, f, indent=2)
            
    def _update_status(self, status):
        """
        Met à jour le fichier de statut du job
        """
        job_id = os.environ.get('SCRAPY_JOB', 'unknown')
        status_file = os.path.join(os.path.dirname(__file__), "..", "jobs", f"{job_id}.json")
        
        try:
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    status_data = json.load(f)
            else:
                status_data = {
                    'spider': 'immobilier',
                    'url': self.start_url,
                    'pid': os.getpid(),
                    'timestamp': datetime.now().isoformat()
                }
                
            status_data['status'] = status
            status_data['properties_count'] = len(self.properties)
            status_data['completion_time'] = datetime.now().isoformat()
            
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
            logger.info(f"Statut mis à jour: {status_file}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut: {str(e)}")

# Fonction principale pour exécuter le script directement
async def main():
    # Récupérer l'URL depuis les arguments si disponible
    start_url = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Initialiser et exécuter le spider
    spider = ImmobilierSpider(start_url)
    await spider.run()

# Exécuter le script
if __name__ == "__main__":
    asyncio.run(main())
