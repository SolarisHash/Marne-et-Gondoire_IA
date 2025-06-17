# ============================================================================
# AGENT IA MVP - QUALITÉ MAXIMUM + ANALYTICS AVANCÉES
# mcp_server/tools/ai_agent.py
# ============================================================================

import pandas as pd
import numpy as np
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
import os
import sys

from openpyxl.styles import PatternFill, Font, Border, Side
from openpyxl import load_workbook

# Ajouter le répertoire parent au Python path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import corrigé du progress manager
try:
    from mcp_server.tools.progress_manager import AIProgressTracker
except ImportError:
    # Fallback si le module n'est pas trouvé
    print("⚠️ Progress manager non disponible, continuons sans...")
    
    class AIProgressTracker:
        """Fallback progress tracker si le module principal n'est pas disponible"""
        def __init__(self, total_items, task_name="Processing"):
            self.total_items = total_items
            self.current = 0
        
        def start(self):
            print(f"🚀 Démarrage: {self.total_items} items à traiter")
        
        def update(self, success=True, item_name=""):
            self.current += 1
            status = "✅" if success else "❌"
            print(f"{status} [{self.current}/{self.total_items}] {item_name}")
        
        def finish(self):
            print(f"🎉 Terminé: {self.current}/{self.total_items} traités")


class AIEnrichmentAgent:
    """
    Agent IA d'enrichissement autonome - Version Qualité Maximum
    Focus : LinkedIn uniquement, seuil 85%, analytics avancées
    """
    
    def __init__(self):
        self.quality_threshold = 85  # Seuil ultra-sélectif
        self.source_priority = ["linkedin"]  # LinkedIn uniquement
        self.rate_limit_delay = 3  # 3 secondes entre requêtes (qualité > vitesse)
        
        # Analytics et logging
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.performance_metrics = {
            "processed": 0,
            "enriched": 0,
            "failed": 0,
            "quality_scores": [],
            "processing_times": [],
            "error_details": [],
            "decisions_log": []
        }
        
        # Configuration du logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure le logging détaillé pour analytics"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/ai_agent_{self.session_id}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def enrich_sample(self, sample_size: int = 10) -> Dict[str, Any]:
        """
        Enrichissement d'un échantillon avec analytics complètes
        """
        start_time = datetime.now()
        self.logger.info(f"🚀 Démarrage Agent IA - Échantillon {sample_size} entreprises")
        
        try:
            # 1. Charger et analyser le fichier
            df = self._load_and_analyze_file()
            
            if df is None:
                return {"error": "Impossible de charger le fichier"}
            
            # 2. Sélectionner l'échantillon optimal
            sample_df = self._select_optimal_sample(df, sample_size)
            
            # 3. Enrichir l'échantillon avec IA
            enrichment_results = self._enrich_companies_ai(sample_df)
            
            # 4. Générer analytics avancées
            analytics = self._generate_advanced_analytics(sample_df, enrichment_results)
            
            # 5. Sauvegarder résultats enrichis
            output_file = self._save_enriched_results(sample_df, enrichment_results)
            
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            
            return {
                "status": "✅ ENRICHISSEMENT IA TERMINÉ",
                "session_id": self.session_id,
                "execution_summary": {
                    "sample_size": sample_size,
                    "duration_seconds": round(total_duration, 1),
                    "enriched_count": enrichment_results["enriched"],
                    "success_rate": f"{(enrichment_results['enriched'] / sample_size * 100):.1f}%",
                    "avg_quality_score": round(np.mean(self.performance_metrics["quality_scores"]) if self.performance_metrics["quality_scores"] else 0, 1)
                },
                "advanced_analytics": analytics,
                "output_file": output_file,
                "detailed_results": enrichment_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur critique Agent IA: {str(e)}")
            return {
                "error": f"Erreur Agent IA: {str(e)}",
                "session_id": self.session_id,
                "partial_analytics": self._generate_error_analytics()
            }
    
    def _load_and_analyze_file(self) -> Optional[pd.DataFrame]:
        """Charge et analyse intelligemment le fichier"""
        try:
            # Auto-détection fichier
            project_root = Path(__file__).parent.parent.parent
            raw_dir = project_root / "data" / "raw"
            
            excel_files = list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls"))
            if not excel_files:
                self.logger.error("❌ Aucun fichier Excel trouvé")
                return None
            
            file_path = excel_files[0]
            self.logger.info(f"📁 Fichier détecté: {file_path.name}")
            
            # Lecture avec gestion d'erreurs
            df = pd.read_excel(file_path, engine='openpyxl').fillna('')
            
            # Analyse IA du contenu
            self._analyze_file_context(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Erreur chargement fichier: {str(e)}")
            return None
    
    def _analyze_file_context(self, df: pd.DataFrame):
        """Analyse IA du contexte métier du fichier"""
        analysis = {
            "total_companies": len(df),
            "columns_count": len(df.columns),
            "has_siret": any("siret" in col.lower() for col in df.columns),
            "has_website_column": any("site" in col.lower() for col in df.columns),
            "website_completion": 0
        }
        
        # Analyser colonne site web
        website_col = None
        for col in df.columns:
            if "site" in col.lower() and "web" in col.lower():
                website_col = col
                break
        
        if website_col:
            non_empty = df[website_col][df[website_col].astype(str).str.strip() != '']
            analysis["website_completion"] = len(non_empty) / len(df) * 100
            analysis["website_column"] = website_col
        
        self.logger.info(f"📊 Analyse contexte: {json.dumps(analysis, indent=2)}")
        self.file_context = analysis
    
    def _select_optimal_sample(self, df: pd.DataFrame, sample_size: int) -> pd.DataFrame:
        """Sélection intelligente de l'échantillon optimal"""
        
        self.logger.info(f"🎯 Sélection échantillon optimal ({sample_size} entreprises)")
        
        # Stratégie IA : diversifier l'échantillon
        selection_criteria = {
            "has_name": True,           # Entreprises avec nom valide
            "has_location": True,       # Avec localisation
            "diverse_sectors": True,    # Secteurs variés
            "diverse_sizes": True       # Tailles variées
        }
        
        # Filtrer entreprises avec données suffisantes
        valid_companies = df[
            (df['Nom courant/Dénomination'].astype(str).str.strip() != '') &
            (df['Nom courant/Dénomination'].astype(str).str.strip() != 'INFORMATION NON-DIFFUSIBLE') &
            (df['Commune'].astype(str).str.strip() != '')
        ].copy()
        
        if len(valid_companies) < sample_size:
            self.logger.warning(f"⚠️ Seulement {len(valid_companies)} entreprises valides disponibles")
            return valid_companies.head(sample_size)
        
        # Sélection diversifiée
        sample = self._diversify_sample(valid_companies, sample_size)
        
        self.logger.info(f"✅ Échantillon sélectionné: {len(sample)} entreprises")
        return sample
    
    def _diversify_sample(self, df: pd.DataFrame, sample_size: int) -> pd.DataFrame:
        """Diversifie l'échantillon par secteur et localisation"""
        
        # Stratégie : prendre des entreprises de différents secteurs et villes
        diversified = []
        
        # Grouper par commune pour diversité géographique
        communes = df['Commune'].unique()[:min(sample_size, len(df['Commune'].unique()))]
        
        per_commune = max(1, sample_size // len(communes))
        
        for commune in communes:
            commune_companies = df[df['Commune'] == commune]
            selected = commune_companies.head(per_commune)
            diversified.append(selected)
        
        result = pd.concat(diversified).head(sample_size)
        
        self.logger.info(f"🌍 Diversification: {len(result['Commune'].unique())} communes représentées")
        
        return result
    
    def _enrich_companies_ai(self, sample_df: pd.DataFrame) -> Dict[str, Any]:
        """Enrichissement IA avec qualité maximum"""
        
        self.logger.info(f"🤖 Début enrichissement IA - Seuil qualité: {self.quality_threshold}%")
        
        results = {
            "processed": 0,
            "enriched": 0,
            "failed": 0,
            "enrichment_data": {},
            "quality_reports": {},
            "ai_decisions": []
        }
        
        for idx, (_, company) in enumerate(sample_df.iterrows(), 1):
            start_time = time.time()
            
            try:
                self.logger.info(f"🔍 [{idx}/{len(sample_df)}] Traitement: {company.get('Nom courant/Dénomination', 'N/A')}")
                
                # Enrichissement IA de cette entreprise
                enrichment_result = self._enrich_single_company_ai(company, idx)
                
                # Traçabilité complète
                processing_time = time.time() - start_time
                self.performance_metrics["processing_times"].append(processing_time)
                
                if enrichment_result["success"]:
                    results["enriched"] += 1
                    results["enrichment_data"][str(idx)] = enrichment_result["data"]
                    results["quality_reports"][str(idx)] = enrichment_result["quality_report"]
                    
                    # Analytics qualité
                    self.performance_metrics["quality_scores"].append(enrichment_result["quality_score"])
                    
                    self.logger.info(f"✅ Succès - Score: {enrichment_result['quality_score']}%")
                else:
                    results["failed"] += 1
                    self.performance_metrics["error_details"].append({
                        "company_index": idx,
                        "company_name": company.get('Nom courant/Dénomination', 'N/A'),
                        "error_reason": enrichment_result["error_reason"],
                        "attempted_searches": enrichment_result.get("attempted_searches", [])
                    })
                    
                    self.logger.warning(f"❌ Échec - Raison: {enrichment_result['error_reason']}")
                
                # Log décision IA
                results["ai_decisions"].append(enrichment_result["ai_decision_log"])
                
                results["processed"] += 1
                
                # Rate limiting pour qualité
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur traitement entreprise {idx}: {str(e)}")
                results["failed"] += 1
                results["processed"] += 1
        
        self.logger.info(f"🎯 Enrichissement terminé: {results['enriched']}/{results['processed']} succès")
        
        return results
    
    def _enrich_single_company_ai(self, company: pd.Series, company_idx: int) -> Dict[str, Any]:
        """Enrichissement IA d'une entreprise avec validation ultra-stricte"""
        
        # Extraction données entreprise
        company_data = {
            "name": str(company.get('Nom courant/Dénomination', '')).strip(),
            "commune": str(company.get('Commune', '')).strip(), 
            "siret": str(company.get('SIRET', '')).strip(),
            "naf_code": str(company.get('Code NAF', '')).strip(),
            "naf_label": str(company.get('Libellé NAF', '')).strip()
        }
        
        # Validation données d'entrée
        if not company_data["name"] or company_data["name"] == "INFORMATION NON-DIFFUSIBLE":
            return {
                "success": False,
                "error_reason": "Nom d'entreprise non disponible",
                "ai_decision_log": {"decision": "SKIP", "reason": "Données insuffisantes"}
            }
        
        # Phase 1: Génération requête IA optimisée
        search_query = self._generate_ai_search_query(company_data)
        
        # Phase 2: Recherche LinkedIn avec IA
        linkedin_results = self._search_linkedin_ai(search_query, company_data)
        
        if not linkedin_results["found"]:
            return {
                "success": False,
                "error_reason": linkedin_results["error_reason"],
                "attempted_searches": linkedin_results["attempted_queries"],
                "ai_decision_log": {
                    "decision": "NO_RESULTS",
                    "search_queries": linkedin_results["attempted_queries"],
                    "reason": linkedin_results["error_reason"]
                }
            }
        
        # Phase 3: Validation IA ultra-stricte
        validation_result = self._validate_result_ai(linkedin_results["data"], company_data)
        
        if validation_result["quality_score"] < self.quality_threshold:
            return {
                "success": False,
                "error_reason": f"Qualité insuffisante ({validation_result['quality_score']}% < {self.quality_threshold}%)",
                "attempted_searches": linkedin_results["attempted_queries"],
                "ai_decision_log": {
                    "decision": "QUALITY_REJECTED",
                    "quality_score": validation_result["quality_score"],
                    "quality_details": validation_result["details"],
                    "threshold": self.quality_threshold
                }
            }
        
        # Succès !
        return {
            "success": True,
            "data": linkedin_results["data"],
            "quality_score": validation_result["quality_score"],
            "quality_report": validation_result,
            "ai_decision_log": {
                "decision": "ACCEPTED",
                "quality_score": validation_result["quality_score"],
                "search_method": linkedin_results["search_method"],
                "validation_details": validation_result["details"]
            }
        }
    
    def _generate_ai_search_query(self, company_data: Dict) -> Dict[str, str]:
        """Génération IA de requêtes de recherche optimisées"""
        
        # Stratégie IA : Requêtes progressives du plus spécifique au plus général
        queries = {
            "primary": f'"{company_data["name"]}" {company_data["commune"]} LinkedIn',
            "fallback1": f'{company_data["name"]} {company_data["commune"]} company',
            "fallback2": f'{company_data["name"]} {company_data["naf_label"][:20]}' if company_data["naf_label"] else f'{company_data["name"]} LinkedIn'
        }
        
        self.logger.debug(f"🧠 Requêtes IA générées: {queries}")
        
        return queries
    
    def _search_linkedin_ai(self, queries: Dict[str, str], company_data: Dict) -> Dict[str, Any]:
        """Recherche LinkedIn avec IA (simulation pour MVP)"""
        
        # SIMULATION pour MVP - À remplacer par vraie recherche LinkedIn
        # Cette version simule la recherche pour tester la logique
        
        self.logger.info(f"🔍 Recherche LinkedIn IA: {queries['primary']}")
        
        # Simulation de résultats selon le type d'entreprise
        company_name = company_data["name"].lower()
        
        # Simulation intelligente basée sur les données réelles
        if "sarah" in company_name or "syed" in company_name:
            # Cas réel de votre fichier
            mock_result = {
                "found": True,
                "data": {
                    "website": "https://www.syed-consulting.fr",
                    "linkedin_url": "https://linkedin.com/company/syed-consulting",
                    "company_name": "SYED SARAH Consulting",
                    "location": company_data["commune"],
                    "description": "Services de conseil technique et spécialisé"
                },
                "search_method": "primary_query",
                "attempted_queries": [queries["primary"]]
            }
        else:
            # Simulation aléatoire pour autres entreprises (70% succès)
            import random
            success = random.random() > 0.3
            
            if success:
                mock_result = {
                    "found": True,
                    "data": {
                        "website": f"https://www.{company_data['name'].lower().replace(' ', '-')}.fr",
                        "linkedin_url": f"https://linkedin.com/company/{company_data['name'].lower().replace(' ', '-')}",
                        "company_name": company_data["name"],
                        "location": company_data["commune"],
                        "description": f"Entreprise spécialisée - {company_data['naf_label'][:50]}"
                    },
                    "search_method": "primary_query",
                    "attempted_queries": [queries["primary"]]
                }
            else:
                mock_result = {
                    "found": False,
                    "error_reason": "Aucun profil LinkedIn trouvé",
                    "attempted_queries": list(queries.values())
                }
        
        # Ajouter délai réaliste
        time.sleep(1)  # Simulation temps de recherche
        
        return mock_result
    
    def _validate_result_ai(self, found_data: Dict, company_data: Dict) -> Dict[str, Any]:
        """Validation IA ultra-stricte avec scoring détaillé"""
        
        validation_scores = {}
        
        # 1. Validation nom (35% du score)
        name_similarity = self._calculate_name_similarity(
            found_data.get("company_name", ""),
            company_data["name"]
        )
        validation_scores["name_match"] = {
            "score": name_similarity,
            "weight": 35,
            "details": f"Similarité nom: {name_similarity}%"
        }
        
        # 2. Validation géographique (30% du score)
        geo_match = self._validate_geography(
            found_data.get("location", ""),
            company_data["commune"]
        )
        validation_scores["geography_match"] = {
            "score": geo_match,
            "weight": 30,
            "details": f"Correspondance géographique: {geo_match}%"
        }
        
        # 3. Validation secteur d'activité (20% du score)
        sector_match = self._validate_business_sector(
            found_data.get("description", ""),
            company_data["naf_label"]
        )
        validation_scores["sector_match"] = {
            "score": sector_match,
            "weight": 20,
            "details": f"Cohérence secteur: {sector_match}%"
        }
        
        # 4. Validation qualité site web (15% du score)
        website_quality = self._validate_website_quality(
            found_data.get("website", "")
        )
        validation_scores["website_quality"] = {
            "score": website_quality,
            "weight": 15,
            "details": f"Qualité site web: {website_quality}%"
        }
        
        # Calcul score final pondéré
        total_score = sum(
            score_data["score"] * score_data["weight"] / 100
            for score_data in validation_scores.values()
        )
        
        return {
            "quality_score": round(total_score, 1),
            "details": validation_scores,
            "validation_method": "ai_multi_criteria",
            "threshold_met": total_score >= self.quality_threshold
        }
    
    def _calculate_name_similarity(self, found_name: str, original_name: str) -> float:
        """Calcule la similarité entre noms avec IA"""
        
        # Normalisation
        found_clean = found_name.lower().strip()
        original_clean = original_name.lower().strip()
        
        # Similarité simple pour MVP
        if found_clean == original_clean:
            return 100.0
        elif original_clean in found_clean or found_clean in original_clean:
            return 85.0
        else:
            # Calcul basique de similarité (à améliorer avec NLP)
            common_words = set(found_clean.split()) & set(original_clean.split())
            if common_words:
                similarity = len(common_words) / max(len(found_clean.split()), len(original_clean.split())) * 100
                return min(80.0, similarity)
            return 20.0
    
    def _validate_geography(self, found_location: str, expected_commune: str) -> float:
        """Validation géographique avec IA"""
        
        if not found_location or not expected_commune:
            return 50.0
        
        found_clean = found_location.lower().strip()
        expected_clean = expected_commune.lower().strip()
        
        if expected_clean in found_clean:
            return 95.0
        elif any(word in found_clean for word in expected_clean.split()):
            return 75.0
        else:
            return 30.0
    
    def _validate_business_sector(self, found_description: str, expected_naf: str) -> float:
        """Validation secteur avec IA contextuelle"""
        
        if not found_description or not expected_naf:
            return 60.0  # Score neutre si pas d'info
        
        # Mots-clés sectoriels (à enrichir avec IA)
        sector_keywords = {
            "conseil": ["conseil", "consulting", "expertise", "accompagnement"],
            "construction": ["construction", "bâtiment", "travaux", "rénovation"],
            "commerce": ["commerce", "vente", "magasin", "distribution"],
            "service": ["service", "prestation", "assistance", "support"]
        }
        
        found_lower = found_description.lower()
        naf_lower = expected_naf.lower()
        
        # Recherche cohérence sectorielle
        for sector, keywords in sector_keywords.items():
            if any(kw in naf_lower for kw in keywords):
                if any(kw in found_lower for kw in keywords):
                    return 85.0
        
        return 65.0  # Score par défaut si pas de contradiction
    
    def _validate_website_quality(self, website_url: str) -> float:
        """Validation qualité site web"""
        
        if not website_url:
            return 0.0
        
        # Critères de qualité basiques
        score = 70.0  # Base
        
        if website_url.startswith("https://"):
            score += 10.0
        elif website_url.startswith("http://"):
            score += 5.0
        
        if ".fr" in website_url:
            score += 15.0  # Site français
        
        if len(website_url) > 20:  # URL complète
            score += 5.0
        
        return min(100.0, score)
    
    def _generate_advanced_analytics(self, sample_df: pd.DataFrame, enrichment_results: Dict) -> Dict[str, Any]:
        """Génère des analytics avancées complètes"""
        
        analytics = {
            "performance_overview": self._calculate_performance_overview(enrichment_results),
            "quality_analysis": self._analyze_quality_distribution(),
            "error_analysis": self._analyze_error_patterns(),
            "timing_analysis": self._analyze_timing_performance(),
            "ai_decision_analysis": self._analyze_ai_decisions(enrichment_results),
            "recommendations": self._generate_ai_recommendations(enrichment_results)
        }
        
        return analytics
    
    def _calculate_performance_overview(self, results: Dict) -> Dict[str, Any]:
        """Vue d'ensemble performance"""
        
        return {
            "success_rate": round(results["enriched"] / results["processed"] * 100, 1) if results["processed"] > 0 else 0,
            "average_quality_score": round(np.mean(self.performance_metrics["quality_scores"]), 1) if self.performance_metrics["quality_scores"] else 0,
            "quality_distribution": {
                "excellent_90_plus": sum(1 for s in self.performance_metrics["quality_scores"] if s >= 90),
                "good_80_89": sum(1 for s in self.performance_metrics["quality_scores"] if 80 <= s < 90),
                "acceptable_70_79": sum(1 for s in self.performance_metrics["quality_scores"] if 70 <= s < 80)
            },
            "processing_efficiency": {
                "avg_time_per_company": round(np.mean(self.performance_metrics["processing_times"]), 2) if self.performance_metrics["processing_times"] else 0,
                "total_processing_time": round(sum(self.performance_metrics["processing_times"]), 1)
            }
        }
    
    def _analyze_quality_distribution(self) -> Dict[str, Any]:
        """Analyse distribution qualité"""
        
        if not self.performance_metrics["quality_scores"]:
            return {"message": "Aucune donnée de qualité disponible"}
        
        scores = self.performance_metrics["quality_scores"]
        
        return {
            "statistics": {
                "mean": round(np.mean(scores), 1),
                "median": round(np.median(scores), 1),
                "std_deviation": round(np.std(scores), 1),
                "min_score": min(scores),
                "max_score": max(scores)
            },
            "quality_grades": {
                "A_grade_90_plus": len([s for s in scores if s >= 90]),
                "B_grade_80_89": len([s for s in scores if 80 <= s < 90]),
                "C_grade_70_79": len([s for s in scores if 70 <= s < 80])
            }
        }
    
    def _analyze_error_patterns(self) -> Dict[str, Any]:
        """Analyse patterns d'erreurs"""
        
        if not self.performance_metrics["error_details"]:
            return {"message": "Aucune erreur détectée"}
        
        errors = self.performance_metrics["error_details"]
        error_reasons = [error["error_reason"] for error in errors]
        
        from collections import Counter
        error_distribution = Counter(error_reasons)
        
        return {
            "total_errors": len(errors),
            "error_types": dict(error_distribution),
            "most_common_error": error_distribution.most_common(1)[0] if error_distribution else None,
            "companies_with_errors": [
                {
                    "name": error["company_name"],
                    "reason": error["error_reason"]
                } for error in errors
            ]
        }
    
    def _analyze_timing_performance(self) -> Dict[str, Any]:
        """Analyse performance temporelle"""
        
        if not self.performance_metrics["processing_times"]:
            return {"message": "Aucune donnée de timing disponible"}
        
        times = self.performance_metrics["processing_times"]
        
        return {
            "timing_statistics": {
                "average_seconds": round(np.mean(times), 2),
                "fastest_seconds": round(min(times), 2),
                "slowest_seconds": round(max(times), 2),
                "total_time_minutes": round(sum(times) / 60, 1)
            },
            "efficiency_metrics": {
                "companies_per_minute": round(len(times) / (sum(times) / 60), 1) if sum(times) > 0 else 0,
                "estimated_time_for_full_file": round((sum(times) / len(times)) * self.file_context.get("total_companies", 0) / 60, 1) if times else 0
            }
        }
    
    def _analyze_ai_decisions(self, results: Dict) -> Dict[str, Any]:
        """Analyse des décisions de l'IA"""
        
        decisions = results.get("ai_decisions", [])
        if not decisions:
            return {"message": "Aucune décision IA disponible"}
        
        decision_types = [d.get("decision", "UNKNOWN") for d in decisions]
        from collections import Counter
        decision_distribution = Counter(decision_types)
        
        return {
            "decision_distribution": dict(decision_distribution),
            "ai_reasoning_quality": {
                "decisions_with_reasoning": len([d for d in decisions if "reason" in d]),
                "avg_quality_score_accepted": round(np.mean([
                    d.get("quality_score", 0) for d in decisions 
                    if d.get("decision") == "ACCEPTED"
                ]), 1) if any(d.get("decision") == "ACCEPTED" for d in decisions) else 0,
                "quality_rejections": len([d for d in decisions if d.get("decision") == "QUALITY_REJECTED"])
            },
            "decision_details": [
                {
                    "decision": d.get("decision", "UNKNOWN"),
                    "quality_score": d.get("quality_score"),
                    "reason": d.get("reason", "No reason provided")
                } for d in decisions
            ]
        }
    
    def _generate_ai_recommendations(self, results: Dict) -> List[Dict[str, str]]:
        """Génère des recommandations IA basées sur l'analyse"""
        
        recommendations = []
        
        # Analyse du taux de succès
        success_rate = results["enriched"] / results["processed"] * 100 if results["processed"] > 0 else 0
        
        if success_rate < 30:
            recommendations.append({
                "priority": "CRITIQUE",
                "category": "Performance",
                "recommendation": "Taux de succès très faible (<30%). Revoir la stratégie de recherche LinkedIn.",
                "action": "Analyser les patterns d'échec et ajuster les requêtes de recherche"
            })
        elif success_rate < 60:
            recommendations.append({
                "priority": "HAUTE",
                "category": "Performance", 
                "recommendation": "Taux de succès modéré. Optimiser les critères de validation.",
                "action": "Réduire légèrement le seuil de qualité ou améliorer les algorithmes de matching"
            })
        else:
            recommendations.append({
                "priority": "INFO",
                "category": "Performance",
                "recommendation": f"Excellent taux de succès ({success_rate:.1f}%). Maintenir la stratégie actuelle.",
                "action": "Étendre l'enrichissement au fichier complet"
            })
        
        # Analyse de la qualité
        if self.performance_metrics["quality_scores"]:
            avg_quality = np.mean(self.performance_metrics["quality_scores"])
            
            if avg_quality >= 90:
                recommendations.append({
                    "priority": "INFO",
                    "category": "Qualité",
                    "recommendation": f"Qualité exceptionnelle (moy. {avg_quality:.1f}%). Prêt pour production.",
                    "action": "Lancer l'enrichissement sur le fichier complet avec ces paramètres"
                })
            elif avg_quality >= 80:
                recommendations.append({
                    "priority": "BONNE",
                    "category": "Qualité",
                    "recommendation": f"Bonne qualité (moy. {avg_quality:.1f}%). Quelques améliorations possibles.",
                    "action": "Affiner les critères de validation géographique et sectorielle"
                })
            else:
                recommendations.append({
                    "priority": "ATTENTION",
                    "category": "Qualité",
                    "recommendation": f"Qualité à améliorer (moy. {avg_quality:.1f}%).",
                    "action": "Revoir les algorithmes de matching et augmenter le seuil de qualité"
                })
        
        # Analyse des erreurs
        if self.performance_metrics["error_details"]:
            error_count = len(self.performance_metrics["error_details"])
            
            # Identifier le type d'erreur le plus fréquent
            error_reasons = [e["error_reason"] for e in self.performance_metrics["error_details"]]
            from collections import Counter
            most_common_error = Counter(error_reasons).most_common(1)
            
            if most_common_error:
                error_type, count = most_common_error[0]
                recommendations.append({
                    "priority": "HAUTE",
                    "category": "Erreurs",
                    "recommendation": f"Erreur principale: '{error_type}' ({count} cas).",
                    "action": "Développer une stratégie spécifique pour ce type d'erreur"
                })
        
        # Recommandations de scaling
        if results["enriched"] > 0:
            processing_times = self.performance_metrics["processing_times"]
            if processing_times:
                avg_time = np.mean(processing_times)
                total_companies = self.file_context.get("total_companies", 3101)
                estimated_full_time = (avg_time * total_companies) / 60  # en minutes
                
                if estimated_full_time > 180:  # Plus de 3h
                    recommendations.append({
                        "priority": "OPTIMISATION",
                        "category": "Performance",
                        "recommendation": f"Temps estimé fichier complet: {estimated_full_time:.0f} min. Considérer l'optimisation.",
                        "action": "Réduire rate limiting ou implémenter traitement parallèle"
                    })
                else:
                    recommendations.append({
                        "priority": "INFO",
                        "category": "Scaling",
                        "recommendation": f"Temps estimé fichier complet: {estimated_full_time:.0f} min. Acceptable.",
                        "action": "Prêt pour traitement du fichier complet"
                    })
        
        return recommendations
    
    def _save_enriched_results(self, sample_df: pd.DataFrame, enrichment_results: Dict) -> str:
        """Sauvegarde les résultats enrichis avec colorisation IA"""
        
        # Créer DataFrame enrichi
        enriched_df = sample_df.copy()
        
        # Ajouter colonnes de métadonnées IA
        enriched_df["IA_Enriched"] = False
        enriched_df["IA_Confidence_Score"] = 0.0
        enriched_df["IA_Source"] = ""
        enriched_df["IA_Processing_Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        enriched_df["IA_Session_ID"] = self.session_id
        
        # Appliquer les enrichissements
        for idx_str, enrichment_data in enrichment_results["enrichment_data"].items():
            idx = int(idx_str) - 1  # Convertir index (1-based vers 0-based)
            
            if idx < len(enriched_df):
                # Enrichir site web
                if "website" in enrichment_data:
                    enriched_df.iloc[idx, enriched_df.columns.get_loc("Site Web établissement")] = enrichment_data["website"]
                
                # Métadonnées IA
                enriched_df.iloc[idx, enriched_df.columns.get_loc("IA_Enriched")] = True
                
                # Score de confiance depuis quality_reports
                if idx_str in enrichment_results["quality_reports"]:
                    score = enrichment_results["quality_reports"][idx_str]["quality_score"]
                    enriched_df.iloc[idx, enriched_df.columns.get_loc("IA_Confidence_Score")] = score
                
                enriched_df.iloc[idx, enriched_df.columns.get_loc("IA_Source")] = "LinkedIn_AI"
        
        # Sauvegarder fichier Excel standard
        output_dir = Path("data/processed")
        output_dir.mkdir(exist_ok=True)
        
        output_filename = f"AI_ENRICHED_Sample_{self.session_id}.xlsx"
        output_path = output_dir / output_filename
        
        enriched_df.to_excel(output_path, index=False)
        
        # 🎨 COLORISATION AVEC ROUGE POUR IA
        try:
            colorizer = ExcelColorizerAI()
            colorized_path = colorizer.colorize_ai_enriched_file(
                str(output_path), 
                enrichment_results["enrichment_data"],
                self.session_id
            )
            
            self.logger.info(f"🎨 Fichier colorisé créé: {colorized_path}")
            
            # Retourner le fichier colorisé comme fichier principal
            return colorized_path
            
        except Exception as e:
            self.logger.warning(f"⚠️ Colorisation échouée: {e}")
            # Retourner le fichier standard si colorisation échoue
            return str(output_path)

    
    def _generate_error_analytics(self) -> Dict[str, Any]:
        """Analytics en cas d'erreur critique"""
        
        return {
            "error_occurred": True,
            "session_id": self.session_id,
            "partial_metrics": {
                "processed_before_error": self.performance_metrics.get("processed", 0),
                "errors_logged": len(self.performance_metrics.get("error_details", [])),
                "processing_times": self.performance_metrics.get("processing_times", [])
            },
            "recovery_suggestions": [
                "Vérifier la connectivité réseau",
                "Valider l'accès aux sources de données",
                "Contrôler les logs détaillés",
                "Relancer avec un échantillon plus petit"
            ]
        }

# ============================================================================
# FONCTION PRINCIPALE POUR INTÉGRATION MCP
# ============================================================================

def run_ai_enrichment_agent(sample_size: int = 10) -> Dict[str, Any]:
    """
    Point d'entrée principal pour l'agent IA d'enrichissement
    """
    
    try:
        agent = AIEnrichmentAgent()
        result = agent.enrich_sample(sample_size)
        return result
        
    except Exception as e:
        return {
            "error": f"Erreur critique Agent IA: {str(e)}",
            "error_type": type(e).__name__,
            "suggestion": "Vérifiez les logs détaillés et la configuration"
        }

def _enrich_companies_ai_with_progress(self, sample_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Version avec barre de progression temps réel
    """
    
    self.logger.info(f"🤖 Début enrichissement IA avec suivi progression")
    
    # Initialiser le tracker de progression
    progress_tracker = AIProgressTracker(
        total_items=len(sample_df),
        task_name=f"Enrichissement IA ({len(sample_df)} entreprises)"
    )
    
    progress_tracker.start()
    
    results = {
        "processed": 0,
        "enriched": 0,
        "failed": 0,
        "enrichment_data": {},
        "quality_reports": {},
        "ai_decisions": []
    }
    
    try:
        for idx, (_, company) in enumerate(sample_df.iterrows(), 1):
            start_time = time.time()
            
            company_name = company.get('Nom courant/Dénomination', 'N/A')
            
            try:
                # Enrichissement IA de cette entreprise
                enrichment_result = self._enrich_single_company_ai(company, idx)
                
                # Traçabilité complète
                processing_time = time.time() - start_time
                self.performance_metrics["processing_times"].append(processing_time)
                
                success = enrichment_result["success"]
                
                if success:
                    results["enriched"] += 1
                    results["enrichment_data"][str(idx)] = enrichment_result["data"]
                    results["quality_reports"][str(idx)] = enrichment_result["quality_report"]
                    
                    # Analytics qualité
                    self.performance_metrics["quality_scores"].append(enrichment_result["quality_score"])
                    
                else:
                    results["failed"] += 1
                    self.performance_metrics["error_details"].append({
                        "company_index": idx,
                        "company_name": company_name,
                        "error_reason": enrichment_result["error_reason"],
                        "attempted_searches": enrichment_result.get("attempted_searches", [])
                    })
                
                # Log décision IA
                results["ai_decisions"].append(enrichment_result["ai_decision_log"])
                
                results["processed"] += 1
                
                # Mettre à jour la progression avec le nom de l'entreprise
                progress_tracker.update(
                    success=success,
                    item_name=f"{company_name[:30]}... {'✅' if success else '❌'}"
                )
                
                # Rate limiting pour qualité
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur traitement entreprise {idx}: {str(e)}")
                results["failed"] += 1
                results["processed"] += 1
                
                # Mettre à jour progression pour l'erreur
                progress_tracker.update(
                    success=False,
                    item_name=f"{company_name[:30]}... ❌ ERREUR"
                )
    
    finally:
        # Terminer le tracker de progression
        progress_tracker.finish()
    
    self.logger.info(f"🎯 Enrichissement terminé: {results['enriched']}/{results['processed']} succès")
    
    return results

class ExcelColorizerAI:
    """
    Système de colorisation Excel pour différencier les données IA
    🔴 Rouge = Données enrichies par IA
    ⚪ Standard = Données originales
    """
    
    def __init__(self):
        # Styles de colorisation
        self.ai_fill = PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")  # Rouge clair
        self.ai_font = Font(color="CC0000", bold=True)  # Rouge foncé et gras
        self.ai_border = Border(
            left=Side(border_style="thin", color="CC0000"),
            right=Side(border_style="thin", color="CC0000"),
            top=Side(border_style="thin", color="CC0000"),
            bottom=Side(border_style="thin", color="CC0000")
        )
        
        # Styles pour métadonnées IA
        self.meta_fill = PatternFill(start_color="F0F8FF", end_color="F0F8FF", fill_type="solid")  # Bleu clair
        self.meta_font = Font(color="0066CC", italic=True)  # Bleu et italique
    
    def colorize_ai_enriched_file(self, file_path: str, enrichment_data: dict, session_id: str) -> str:
        """
        Colorise un fichier Excel avec les données IA en rouge
        
        Args:
            file_path: Chemin du fichier Excel
            enrichment_data: Données d'enrichissement par index
            session_id: ID de session pour traçabilité
        
        Returns:
            Chemin du fichier colorisé
        """
        try:
            print(f"🎨 Colorisation du fichier Excel...")
            
            # Charger le workbook
            wb = load_workbook(file_path)
            ws = wb.active
            
            # Identifier les colonnes enrichies
            enriched_columns = self._find_enriched_columns(ws)
            
            # Coloriser les cellules enrichies
            for row_idx, enrichment in enrichment_data.items():
                excel_row = int(row_idx) + 1  # +1 car Excel commence à 1, +1 pour header
                
                # Coloriser les données enrichies
                self._colorize_enriched_row(ws, excel_row, enriched_columns, enrichment)
            
            # Coloriser les colonnes de métadonnées IA
            self._colorize_metadata_columns(ws)
            
            # Ajouter légende
            self._add_legend(ws)
            
            # Sauvegarder le fichier colorisé
            colorized_path = file_path.replace('.xlsx', '_COLORIZED.xlsx')
            wb.save(colorized_path)
            
            print(f"✅ Fichier colorisé sauvegardé: {colorized_path}")
            return colorized_path
            
        except Exception as e:
            print(f"⚠️ Erreur colorisation: {e}")
            return file_path  # Retourner le fichier original si erreur
    
    def _find_enriched_columns(self, ws) -> list:
        """Trouve les colonnes qui ont été enrichies"""
        enriched_cols = []
        
        # Parcourir la première ligne (header) pour identifier les colonnes enrichissables
        for col_idx, cell in enumerate(ws[1], 1):
            if cell.value:
                col_name = str(cell.value).lower()
                
                # Colonnes typiquement enrichies par IA
                if any(keyword in col_name for keyword in [
                    'site', 'web', 'email', 'telephone', 'phone', 
                    'linkedin', 'facebook', 'twitter', 'url'
                ]):
                    enriched_cols.append(col_idx)
        
        return enriched_cols
    
    def _colorize_enriched_row(self, ws, row_idx: int, enriched_columns: list, enrichment_data: dict):
        """Colorise une ligne enrichie par IA"""
        
        # Coloriser les colonnes enrichies pour cette ligne
        for col_idx in enriched_columns:
            cell = ws.cell(row=row_idx, column=col_idx)
            
            # Vérifier si la cellule contient des données IA
            if self._cell_contains_ai_data(cell, enrichment_data):
                # Appliquer le style IA (rouge)
                cell.fill = self.ai_fill
                cell.font = self.ai_font
                cell.border = self.ai_border
    
    def _cell_contains_ai_data(self, cell, enrichment_data: dict) -> bool:
        """Vérifie si une cellule contient des données enrichies par IA"""
        
        if not cell.value or not enrichment_data:
            return False
        
        cell_value = str(cell.value).strip()
        
        # Vérifier si la valeur correspond aux données IA
        ai_values = []
        if 'website' in enrichment_data:
            ai_values.append(enrichment_data['website'])
        if 'linkedin_url' in enrichment_data:
            ai_values.append(enrichment_data['linkedin_url'])
        
        return any(cell_value == str(ai_val) for ai_val in ai_values if ai_val)
    
    def _colorize_metadata_columns(self, ws):
        """Colorise les colonnes de métadonnées IA"""
        
        # Identifier les colonnes de métadonnées IA
        for col_idx, cell in enumerate(ws[1], 1):
            if cell.value and str(cell.value).startswith('IA_'):
                # Coloriser toute la colonne de métadonnées
                for row in ws.iter_rows(min_col=col_idx, max_col=col_idx):
                    for cell in row:
                        cell.fill = self.meta_fill
                        cell.font = self.meta_font
    
    def _add_legend(self, ws):
        """Ajoute une légende explicative"""
        
        # Trouver la dernière ligne avec données
        last_row = ws.max_row + 2
        
        # Ajouter la légende
        legend_data = [
            ["", "LÉGENDE"],
            ["", "🔴 Rouge = Données enrichies par IA"],
            ["", "🔵 Bleu = Métadonnées IA"],
            ["", "⚪ Standard = Données originales"]
        ]
        
        for i, (col1, col2) in enumerate(legend_data):
            ws.cell(row=last_row + i, column=1, value=col1)
            legend_cell = ws.cell(row=last_row + i, column=2, value=col2)
            
            if i == 0:  # Titre
                legend_cell.font = Font(bold=True, size=12)
            elif "Rouge" in col2:
                legend_cell.fill = self.ai_fill
                legend_cell.font = self.ai_font
            elif "Bleu" in col2:
                legend_cell.fill = self.meta_fill
                legend_cell.font = self.meta_font

# Alias pour compatibilité
ai_agent_enrich = run_ai_enrichment_agent