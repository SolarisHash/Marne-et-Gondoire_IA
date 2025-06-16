import time
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import quote
import json
from pathlib import Path
import pandas as pd

class LinkedInEnricher:
    """
    Enrichisseur de données via LinkedIn
    Support API et scraping selon disponibilité
    """
    
    def __init__(self, method: str = "search_engine"):
        """
        Initialize LinkedIn enricher
        
        Args:
            method: "search_engine" (Google site:linkedin) ou "direct" (scraping direct)
        """
        self.method = method
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.rate_limit_delay = 2  # secondes entre requêtes
        
    def enrich_company_batch(self, companies_data: List[Dict], target_columns: List[str]) -> Dict[str, Any]:
        """
        Enrichit un batch d'entreprises via LinkedIn
        
        Args:
            companies_data: Liste des entreprises avec [nom, siret, ville...]
            target_columns: Colonnes à enrichir ['Site Web établissement', 'Effectif réel établissement'...]
            
        Returns:
            Dict avec résultats enrichissement
        """
        results = {
            "processed": 0,
            "enriched": 0,
            "failed": 0,
            "enrichment_data": {},
            "errors": []
        }
        
        for i, company in enumerate(companies_data):
            try:
                print(f"🔍 Traitement {i+1}/{len(companies_data)}: {company.get('nom', 'N/A')}")
                
                # Rechercher l'entreprise sur LinkedIn
                linkedin_data = self.search_company_linkedin(company)
                
                if linkedin_data:
                    # Extraire les données selon les colonnes demandées
                    enriched_data = self.extract_target_data(linkedin_data, target_columns)
                    
                    # Identifier l'entreprise (SIRET ou nom)
                    company_id = company.get('siret') or company.get('nom') or str(i)
                    results["enrichment_data"][company_id] = enriched_data
                    results["enriched"] += 1
                else:
                    results["failed"] += 1
                    
                results["processed"] += 1
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "company": company.get('nom', 'Unknown'),
                    "error": str(e)
                })
                
        return results
    
    def search_company_linkedin(self, company: Dict) -> Optional[Dict]:
        """
        Recherche une entreprise sur LinkedIn
        """
        nom = company.get('nom') or company.get('Nom courant/Dénomination', '')
        ville = self.extract_city(company)
        
        if not nom:
            return None
            
        if self.method == "search_engine":
            return self.search_via_google(nom, ville)
        elif self.method == "direct":
            return self.search_direct_linkedin(nom, ville)
        
        return None
    
    def search_via_google(self, company_name: str, city: str = "") -> Optional[Dict]:
        """
        Recherche via Google avec site:linkedin.com
        """
        try:
            # Construction requête de recherche
            search_terms = [company_name]
            if city:
                search_terms.append(city)
            
            query = f"site:linkedin.com/company {' '.join(search_terms)}"
            
            # Simulation d'une recherche (à remplacer par vraie API)
            # En développement, on retourne des données mockées
            return self.mock_linkedin_company_data(company_name)
            
        except Exception as e:
            print(f"❌ Erreur recherche Google: {e}")
            return None
    
    def search_direct_linkedin(self, company_name: str, city: str = "") -> Optional[Dict]:
        """
        Recherche directe sur LinkedIn (nécessite gestion anti-bot)
        """
        # Cette méthode nécessiterait un scraping plus sophistiqué
        # Pour l'instant, retourner des données mockées
        return self.mock_linkedin_company_data(company_name)
    
    def extract_target_data(self, linkedin_data: Dict, target_columns: List[str]) -> Dict:
        """
        Extrait les données demandées depuis les données LinkedIn
        """
        extracted = {}
        
        for column in target_columns:
            column_lower = column.lower()
            
            # Sites web
            if any(term in column_lower for term in ['site', 'web', 'url']):
                extracted[column] = linkedin_data.get('website', '')
            
            # Effectifs
            elif 'effectif' in column_lower:
                extracted[column] = linkedin_data.get('employee_count', '')
            
            # Description/Activité
            elif any(term in column_lower for term in ['description', 'activité', 'activite']):
                extracted[column] = linkedin_data.get('description', '')
            
            # Secteur
            elif 'secteur' in column_lower or 'industrie' in column_lower:
                extracted[column] = linkedin_data.get('industry', '')
                
        return extracted
    
    def extract_city(self, company: Dict) -> str:
        """
        Extrait la ville depuis les données d'adresse
        """
        # Essayer différents champs possibles
        for field in ['Commune', 'commune', 'ville', 'Ville', 'Adresse - CP et commune']:
            if field in company and company[field]:
                city = str(company[field]).strip()
                # Nettoyer le CP si présent (ex: "77400 LAGNY-SUR-MARNE" → "LAGNY-SUR-MARNE")
                if ' ' in city and city.split()[0].isdigit():
                    return city.split(' ', 1)[1]
                return city
        return ""
    
    def mock_linkedin_company_data(self, company_name: str) -> Dict:
        """
        Données mockées pour développement/test
        À remplacer par vraies données LinkedIn
        """
        return {
            "name": company_name,
            "website": f"https://www.{company_name.lower().replace(' ', '').replace('&', 'et')}.fr",
            "employee_count": "10-50 employés",
            "industry": "Services aux entreprises",
            "description": f"Entreprise spécialisée dans son secteur d'activité",
            "linkedin_url": f"https://linkedin.com/company/{company_name.lower().replace(' ', '-')}",
            "confidence_score": 0.8
        }

# ==============================================================================
# Outil MCP principal pour l'enrichissement
# ==============================================================================

def enrich_file_with_linkedin(
    file_path: str = None, 
    target_columns: List[str] = None,
    max_companies: int = None
) -> Dict[str, Any]:
    """
    Outil MCP pour enrichir un fichier Excel via LinkedIn
    
    Args:
        file_path: Chemin vers le fichier (auto-détection si None)
        target_columns: Colonnes à enrichir (auto-détection si None)
        max_companies: Limite de traitement (utile pour tests)
    """
    
    try:
        # 1. Charger le fichier
        if file_path is None:
            project_root = Path(__file__).parent.parent.parent
            raw_dir = project_root / "data" / "raw"
            excel_files = list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls"))
            
            if not excel_files:
                return {"error": "Aucun fichier Excel trouvé dans data/raw/"}
            
            file_path = excel_files[0]
        
        # Lire le fichier
        df = pd.read_excel(file_path)
        print(f"📊 Fichier chargé: {len(df)} entreprises")
        
        # 2. Limiter pour les tests si demandé
        if max_companies and max_companies < len(df):
            df = df.head(max_companies)
            print(f"🧪 Mode test: limitation à {max_companies} entreprises")
        
        # 3. Auto-détecter les colonnes à enrichir si pas spécifiées
        if target_columns is None:
            target_columns = []
            for col in df.columns:
                col_lower = col.lower()
                if any(term in col_lower for term in ['site', 'web', 'effectif']):
                    target_columns.append(col)
            
            if not target_columns:
                return {"error": "Aucune colonne enrichissable détectée automatiquement"}
        
        print(f"🎯 Colonnes cibles: {target_columns}")
        
        # 4. Préparer les données entreprises
        companies_data = df.to_dict('records')
        
        # 5. Enrichir via LinkedIn
        enricher = LinkedInEnricher(method="search_engine")
        enrichment_results = enricher.enrich_company_batch(companies_data, target_columns)
        
        # 6. Appliquer les enrichissements au DataFrame
        enriched_df = df.copy()
        
        for company_id, enriched_data in enrichment_results["enrichment_data"].items():
            # Trouver l'index de l'entreprise (par SIRET ou position)
            if company_id.isdigit() and len(company_id) == 14:  # SIRET
                mask = df['SIRET'].astype(str) == company_id
            else:  # Par nom ou index
                try:
                    idx = int(company_id)
                    mask = df.index == idx
                except:
                    mask = df['Nom courant/Dénomination'] == company_id
            
            # Appliquer les enrichissements
            for col, value in enriched_data.items():
                if value and col in enriched_df.columns:
                    enriched_df.loc[mask, col] = value
        
        # 7. Sauvegarder le fichier enrichi
        output_path = Path(file_path).parent.parent / "processed" / f"enriched_{Path(file_path).name}"
        output_path.parent.mkdir(exist_ok=True)
        enriched_df.to_excel(output_path, index=False)
        
        return {
            "status": "success",
            "input_file": str(file_path),
            "output_file": str(output_path),
            "processing_stats": enrichment_results,
            "enriched_columns": target_columns,
            "summary": {
                "total_companies": len(df),
                "processed": enrichment_results["processed"],
                "enriched": enrichment_results["enriched"],
                "success_rate": f"{(enrichment_results['enriched'] / enrichment_results['processed'] * 100):.1f}%" if enrichment_results["processed"] > 0 else "0%"
            }
        }
        
    except Exception as e:
        return {
            "error": f"Erreur lors de l'enrichissement: {str(e)}",
            "suggestion": "Vérifiez que le fichier existe et est accessible"
        }

# ==============================================================================
# Tests et utilitaires
# ==============================================================================

def test_linkedin_enrichment(sample_size: int = 3) -> Dict:
    """
    Test de l'enrichissement LinkedIn sur un échantillon
    """
    return enrich_file_with_linkedin(
        max_companies=sample_size,
        target_columns=["Site Web établissement", "Effectif réel établissement"]
    )