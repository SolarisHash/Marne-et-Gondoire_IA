# ============================================================================
# RECHERCHE WEB RÉELLE
# mg-platform/mcp_server/tools/ai_agent/search/web_search.py
# ============================================================================

"""
Module de recherche web réelle avec DuckDuckGo et Google
Responsabilités:
- Recherche DuckDuckGo avec gestion HTTP 202
- Validation sites trouvés (scoring 50%+)
- Rate limiting (2 sec entre requêtes)
- Headers rotatifs anti-détection
"""

import requests
import time
import random
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

from ..core.exceptions import SearchError, WebSearchTimeoutError, RateLimitError
from ..utils.validators import is_valid_business_website


class WebSearchEngine:
    """Moteur de recherche web avec multiple sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get("duckduckgo_timeout", 10)
        self.rate_limit = config.get("rate_limit_delay", 2)
        self.user_agents = config.get("user_agents", [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        ])
    
    def search_company_website(self, company_name: str, commune: str) -> Dict[str, Any]:
        """
        Recherche le site web d'une entreprise
        
        Args:
            company_name: Nom de l'entreprise
            commune: Commune de l'entreprise
            
        Returns:
            Dict avec résultats de recherche
        """
        
        result = {
            "found": False,
            "website": "",
            "source": "",
            "confidence": 0,
            "attempted_queries": [],
            "error_reason": ""
        }
        
        try:
            # Générer requêtes de recherche intelligentes
            search_queries = self._generate_search_queries(company_name, commune)
            result["attempted_queries"] = search_queries
            
            # Essayer chaque requête
            for i, query in enumerate(search_queries, 1):
                
                # DuckDuckGo en priorité
                websites = self._search_duckduckgo(query)
                
                if websites:
                    # Valider les résultats
                    for website in websites:
                        validation = self._validate_website(website, company_name, commune)
                        
                        if validation["is_valid"] and validation["confidence"] >= 50:
                            result.update({
                                "found": True,
                                "website": website,
                                "source": "DuckDuckGo",
                                "confidence": validation["confidence"]
                            })
                            return result
                
                # Google en fallback si DuckDuckGo échoue
                if i == len(search_queries):  # Dernière tentative
                    google_results = self._search_google(query)
                    
                    for website in google_results:
                        validation = self._validate_website(website, company_name, commune)
                        
                        if validation["is_valid"] and validation["confidence"] >= 50:
                            result.update({
                                "found": True,
                                "website": website,
                                "source": "Google",
                                "confidence": validation["confidence"]
                            })
                            return result
                
                # Rate limiting entre requêtes
                time.sleep(self.rate_limit)
            
            result["error_reason"] = "Aucun site web valide trouvé"
            return result
            
        except Exception as e:
            result["error_reason"] = f"Erreur recherche web: {str(e)}"
            return result
    
    def _generate_search_queries(self, company_name: str, commune: str) -> List[str]:
        """Génère des requêtes de recherche optimisées"""
        
        queries = []
        
        if company_name and commune:
            # Requêtes principales
            queries.extend([
                f'"{company_name}" {commune} site officiel',
                f'"{company_name}" {commune}',
                f'{company_name} {commune} www',
                f'{company_name} {commune} contact'
            ])
        
        # Limiter à 3 requêtes pour éviter le spam
        return queries[:3]
    
    def _search_duckduckgo(self, query: str, max_results: int = 5) -> List[str]:
        """Recherche DuckDuckGo avec gestion HTTP 202"""
        
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'DNT': '1',
                'Connection': 'close'
            }
            
            # URL DuckDuckGo
            encoded_query = urllib.parse.quote(query)
            ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            response = requests.get(ddg_url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 202:
                # HTTP 202 = DuckDuckGo nous demande d'attendre
                time.sleep(2)
                # Retry une fois
                response = requests.get(ddg_url, headers=headers, timeout=self.timeout)
            
            if response.status_code != 200:
                return []
            
            # Parser les résultats
            return self._parse_duckduckgo_results(response.content, max_results)
            
        except requests.exceptions.Timeout:
            raise WebSearchTimeoutError(f"Timeout DuckDuckGo pour: {query}")
        except requests.exceptions.RequestException as e:
            raise SearchError(f"Erreur DuckDuckGo: {str(e)}")
    
    def _parse_duckduckgo_results(self, content: bytes, max_results: int) -> List[str]:
        """Parse les résultats DuckDuckGo"""
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            websites = []
            
            # Extraire les liens de résultats
            for result in soup.find_all('div', class_=['result', 'web-result']):
                link_tag = result.find('a', href=True)
                if not link_tag:
                    continue
                
                url = link_tag.get('href', '')
                
                # Nettoyer l'URL DuckDuckGo
                if '/l/?uddg=' in url:
                    try:
                        clean_url = urllib.parse.unquote(url.split('/l/?uddg=')[1].split('&')[0])
                        url = clean_url
                    except:
                        continue
                
                # Valider l'URL
                if is_valid_business_website(url):
                    websites.append(url)
                    
                    if len(websites) >= max_results:
                        break
            
            return websites
            
        except Exception:
            return []
    
    def _search_google(self, query: str, max_results: int = 3) -> List[str]:
        """Recherche Google (utilisation limitée)"""
        
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept-Language': 'fr-FR,fr;q=0.9'
            }
            
            # URL Google Search
            encoded_query = urllib.parse.quote(query)
            google_url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"
            
            response = requests.get(google_url, headers=headers, timeout=self.timeout)
            
            if response.status_code != 200:
                return []
            
            return self._parse_google_results(response.content, max_results)
            
        except Exception:
            return []
    
    def _parse_google_results(self, content: bytes, max_results: int) -> List[str]:
        """Parse les résultats Google"""
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            websites = []
            
            # Extraire les liens de résultats Google
            for result in soup.find_all('div', class_='g'):
                link_tag = result.find('a', href=True)
                if link_tag:
                    url = link_tag.get('href', '')
                    
                    if url.startswith('/url?q='):
                        # Nettoyer URL Google
                        url = url.split('/url?q=')[1].split('&')[0]
                        url = urllib.parse.unquote(url)
                    
                    if is_valid_business_website(url):
                        websites.append(url)
                        
                        if len(websites) >= max_results:
                            break
            
            return websites
            
        except Exception:
            return []
    
    def _validate_website(self, website: str, company_name: str, commune: str) -> Dict[str, Any]:
        """Valide qu'un site web correspond à l'entreprise"""
        
        validation = {
            "is_valid": False,
            "confidence": 0,
            "details": {}
        }
        
        try:
            # Télécharger le contenu du site
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(website, headers=headers, timeout=8, allow_redirects=True)
            
            if response.status_code != 200:
                return validation
            
            # Parser le contenu
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Calcul de confiance
            confidence = self._calculate_website_confidence(
                page_text, company_name, commune
            )
            
            validation.update({
                "is_valid": confidence >= 50,
                "confidence": confidence,
                "details": {
                    "content_length": len(page_text),
                    "has_company_name": company_name.lower() in page_text,
                    "has_commune": commune.lower() in page_text
                }
            })
            
            return validation
            
        except Exception:
            return validation
    
    def _calculate_website_confidence(self, page_text: str, company_name: str, commune: str) -> int:
        """Calcule le score de confiance pour un site web"""
        
        score = 30  # Score de base
        
        # Bonus nom d'entreprise
        if company_name and company_name.lower() in page_text:
            score += 40
        
        # Bonus commune
        if commune and commune.lower() in page_text:
            score += 25
        
        # Bonus département/région
        if any(indicator in page_text for indicator in ['77', 'seine-et-marne', 'île-de-france']):
            score += 10
        
        # Malus pour contenu suspect
        if any(pattern in page_text for pattern in ['domain for sale', 'site en construction']):
            score -= 30
        
        return max(0, min(100, score))