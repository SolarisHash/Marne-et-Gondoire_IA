"""
Spider Scrapy pour récupérer les données des permis de construire depuis le site Sitadel
"""
import scrapy
import re
import json
import os
from datetime import datetime
from scrapy.http import Request
from scrapy.utils.project import get_project_settings

class SitadelSpider(scrapy.Spider):
    name = "sitadel"
    allowed_domains = ["statistiques.developpement-durable.gouv.fr"]
    
    def __init__(self, start_url=None, *args, **kwargs):
        super(SitadelSpider, self).__init__(*args, **kwargs)
        # URL de départ par défaut
        self.start_url = start_url or "https://www.statistiques.developpement-durable.gouv.fr/la-base-des-permis-de-construire"
        self.download_folder = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sitadel")
        
        # Créer le dossier de téléchargement s'il n'existe pas
        os.makedirs(self.download_folder, exist_ok=True)
        
        # Journal des données récupérées
        self.data_log = []
        
    def start_requests(self):
        yield Request(url=self.start_url, callback=self.parse)
        
    def parse(self, response):
        """
        Page principale: recherche les liens vers les données des permis de construire
        """
        self.logger.info(f"Traitement de la page principale: {response.url}")
        
        # Chercher les liens vers les fichiers de données
        # Nous recherchons spécifiquement les liens vers des fichiers zip ou csv
        data_links = response.css('a[href$=".zip"], a[href$=".csv"], a[href*="permis-de-construire"]')
        
        for link in data_links:
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            
            if href and (href.endswith('.zip') or href.endswith('.csv') or 'permis' in href.lower()):
                url = response.urljoin(href)
                self.logger.info(f"Fichier de données trouvé: {url}")
                
                yield Request(
                    url=url,
                    callback=self.parse_data_file,
                    meta={'file_name': os.path.basename(url), 'description': text}
                )
            elif href:
                # Suivre d'autres liens pertinents
                url = response.urljoin(href)
                if 'permis' in href.lower() or 'sitadel' in href.lower() or 'donnees' in href.lower():
                    self.logger.info(f"Suivre le lien: {url}")
                    yield Request(url=url, callback=self.parse)
        
    def parse_data_file(self, response):
        """
        Traite un fichier de données téléchargé
        """
        file_name = response.meta.get('file_name')
        description = response.meta.get('description')
        
        self.logger.info(f"Téléchargement du fichier: {file_name}")
        
        # Chemin complet pour sauvegarder le fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.download_folder, f"{timestamp}_{file_name}")
        
        # Sauvegarder le fichier
        with open(file_path, 'wb') as f:
            f.write(response.body)
        
        # Enregistrer dans le journal
        self.data_log.append({
            'url': response.url,
            'file_name': file_name,
            'description': description,
            'saved_path': file_path,
            'timestamp': datetime.now().isoformat()
        })
        
        self.logger.info(f"Fichier sauvegardé: {file_path}")
        
    def closed(self, reason):
        """
        À la fermeture du spider, enregistre le journal des données récupérées
        """
        self.logger.info(f"Spider fermé: {reason}")
        
        # Sauvegarder le journal
        log_path = os.path.join(self.download_folder, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(log_path, 'w') as f:
            json.dump(self.data_log, f, indent=2)
        
        self.logger.info(f"Journal des données récupérées sauvegardé: {log_path}")
        
        # Mettre à jour le fichier de statut
        job_id = os.environ.get('SCRAPY_JOB', 'unknown')
        status_file = os.path.join(os.path.dirname(__file__), "..", "jobs", f"{job_id}.json")
        
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    status_data = json.load(f)
                    
                status_data['status'] = 'completed'
                status_data['files_downloaded'] = len(self.data_log)
                status_data['completion_time'] = datetime.now().isoformat()
                
                with open(status_file, 'w') as f:
                    json.dump(status_data, f, indent=2)
                    
                self.logger.info(f"Statut mis à jour: {status_file}")
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la mise à jour du statut: {str(e)}")
