# ============================================================================
# STRATÉGIES D'ENRICHISSEMENT
# mg-platform/mcp_server/tools/ai_agent/enrichment/strategies.py
# ============================================================================

"""
Module des stratégies d'enrichissement intelligentes
Responsabilités:
- Coordination des 2 stratégies (noms réels vs NON-DIFFUSIBLE)
- Orchestration recherche web + fallback
- Gestion des seuils adaptatifs
- Interface unifiée pour l'agent principal
"""

import pandas as pd
from typing import Dict, Any, Optional

from ..search.web_search import WebSearchEngine
from ..search.fallback import IntelligentFallbackGenerator
from ..enrichment.validation import QualityValidator
from ..core.exceptions import EnrichmentError


class EnrichmentStrategy:
    """Orchestrateur des stratégies d'enrichissement"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.web_search = WebSearchEngine(config)
        self.fallback_generator = IntelligentFallbackGenerator(config)
        self.quality_validator = QualityValidator(config)
    
    def enrich_single_company(self, company: pd.Series, company_idx: int, logger) -> Dict[str, Any]:
        """
        Enrichissement d'une entreprise avec stratégie adaptative
        
        Args:
            company: Série pandas avec données entreprise
            company_idx: Index de l'entreprise
            logger: Logger pour traçabilité
            
        Returns:
            Dict avec résultat d'enrichissement
        """
        
        try:
            # Extraction et préparation des données
            company_data = self._extract_company_data(company)
            
            # Validation données d'entrée
            if not self._validate_input_data(company_data):
                return {
                    "success": False,
                    "error_reason": "Données d'entrée insuffisantes (SIRET ou commune manquant)",
                    "ai_decision_log": {"decision": "SKIP", "reason": "Données minimales insuffisantes"}
                }
            
            # Déterminer la stratégie selon le nom disponible
            strategy_result = self._determine_enrichment_strategy(company_data, logger)
            
            if not strategy_result["found"]:
                return {
                    "success": False,
                    "error_reason": strategy_result["error_reason"],
                    "attempted_searches": strategy_result.get("attempted_queries", []),
                    "ai_decision_log": {
                        "decision": "NO_RESULTS",
                        "search_strategy": company_data["search_strategy"],
                        "reason": strategy_result["error_reason"]
                    }
                }
            
            # Validation qualité avec seuil adaptatif
            validation_result = self._validate_enrichment_quality(
                strategy_result, company_data, logger
            )
            
            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "error_reason": validation_result["error_reason"],
                    "attempted_searches": strategy_result.get("attempted_queries", []),
                    "ai_decision_log": {
                        "decision": "QUALITY_REJECTED",
                        "quality_score": validation_result["quality_score"],
                        "threshold": validation_result["threshold_used"],
                        "search_strategy": company_data["search_strategy"]
                    }
                }
            
            # Succès !
            return {
                "success": True,
                "data": strategy_result["data"],
                "quality_score": validation_result["quality_score"],
                "quality_report": validation_result,
                "ai_decision_log": {
                    "decision": "ACCEPTED",
                    "quality_score": validation_result["quality_score"],
                    "search_method": strategy_result.get("source", "unknown"),
                    "search_strategy": company_data["search_strategy"],
                    "threshold_used": validation_result["threshold_used"]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_reason": f"Erreur technique enrichissement: {str(e)}",
                "ai_decision_log": {"decision": "ERROR", "error": str(e)}
            }
    
    def _extract_company_data(self, company: pd.Series) -> Dict[str, Any]:
        """Extrait et structure les données d'entreprise"""
        
        company_data = {
            "name": str(company.get('Nom courant/Dénomination', '')).strip(),
            "commune": str(company.get('Commune', '')).strip(),
            "siret": str(company.get('SIRET', '')).strip(),
            "naf_code": str(company.get('Code NAF', '')).strip(),
            "naf_label": str(company.get('Libellé NAF', '')).strip()
        }
        
        # Déterminer la stratégie de recherche
        if (not company_data["name"] or 
            company_data["name"] in ["INFORMATION NON-DIFFUSIBLE", "", "nan", "NaN"]):
            company_data["search_strategy"] = "alternative"
            company_data["search_name"] = self._build_alternative_search_name(company_data)
        else:
            company_data["search_strategy"] = "standard"
            company_data["search_name"] = company_data["name"]
        
        return company_data
    
    def _validate_input_data(self, company_data: Dict[str, Any]) -> bool:
        """Validation minimale des données d'entrée"""
        return bool(company_data["siret"] and company_data["commune"])
    
    def _build_alternative_search_name(self, company_data: Dict) -> str:
        """Construit un nom de recherche pour les entreprises NON-DIFFUSIBLE"""
        
        search_parts = [company_data["commune"]]
        
        # Ajouter mots-clés du secteur NAF
        naf_label = company_data.get("naf_label", "")
        if naf_label:
            # Extraire les premiers mots significatifs
            naf_words = naf_label.lower().split()
            significant_words = [word for word in naf_words 
                               if len(word) > 4 and word not in ['autres', 'activite', 'services']]
            if significant_words:
                search_parts.extend(significant_words[:2])
        
        return " ".join(search_parts) if search_parts else company_data["commune"]
    
    def _determine_enrichment_strategy(self, company_data: Dict, logger) -> Dict[str, Any]:
        """Détermine et exécute la stratégie d'enrichissement appropriée"""
        
        if company_data["search_strategy"] == "standard":
            return self._execute_standard_strategy(company_data, logger)
        else:
            return self._execute_alternative_strategy(company_data, logger)
    
    def _execute_standard_strategy(self, company_data: Dict, logger) -> Dict[str, Any]:
        """Stratégie standard pour entreprises avec nom connu"""
        
        logger.info(f"🔍 Recherche standard: {company_data['name']}")
        
        # 1. Recherche web réelle
        web_result = self.web_search.search_company_website(
            company_data["name"], 
            company_data["commune"]
        )
        
        if web_result["found"]:
            logger.info(f"✅ Site web trouvé: {web_result['website']}")
            
            return {
                "found": True,
                "data": {
                    "company_name": company_data["name"],
                    "website": web_result["website"],
                    "location": company_data["commune"],
                    "search_source": web_result["source"],
                    "ai_validation_score": web_result["confidence"]
                },
                "source": "WEB_SEARCH_REAL",
                "attempted_queries": web_result.get("attempted_queries", [])
            }
        
        # 2. Fallback intelligent si échec
        if self.config.get("fallback_enabled", True):
            logger.info("🔄 Fallback vers génération intelligente")
            
            fallback_result = self.fallback_generator.generate_company_data(company_data)
            
            if fallback_result["found"]:
                # Marquer clairement comme fallback
                fallback_result["data"]["ai_validation_score"] = fallback_result["confidence"]
                fallback_result["attempted_queries"] = web_result.get("attempted_queries", [])
                
                return fallback_result
        
        return {
            "found": False,
            "error_reason": "Aucune donnée fiable trouvée (web + fallback)",
            "attempted_queries": web_result.get("attempted_queries", [])
        }
    
    def _execute_alternative_strategy(self, company_data: Dict, logger) -> Dict[str, Any]:
        """Stratégie alternative pour entreprises NON-DIFFUSIBLE"""
        
        logger.info(f"Nom non disponible, recherche alternative pour SIRET {company_data['siret'][:8]}...")
        
        # 1. Recherche web avec nom alternatif
        web_result = self.web_search.search_company_website(
            company_data["search_name"],
            company_data["commune"]
        )
        
        if web_result["found"]:
            logger.info(f"✅ Site web trouvé via recherche alternative: {web_result['website']}")
            
            return {
                "found": True,
                "data": {
                    "company_name": f"Entreprise {company_data['commune']}",  # Nom générique
                    "website": web_result["website"],
                    "location": company_data["commune"],
                    "search_source": web_result["source"],
                    "search_method": "alternative_search",
                    "ai_validation_score": web_result["confidence"]
                },
                "source": "WEB_SEARCH_ALTERNATIVE",
                "attempted_queries": web_result.get("attempted_queries", [])
            }
        
        # 2. Génération intelligente (prioritaire pour NON-DIFFUSIBLE)
        logger.info("🤖 Génération intelligente pour entreprise anonyme")
        
        fallback_result = self.fallback_generator.generate_company_data(company_data)
        
        if fallback_result["found"]:
            fallback_result["data"]["ai_validation_score"] = fallback_result["confidence"]
            fallback_result["attempted_queries"] = web_result.get("attempted_queries", [])
            
            return fallback_result
        
        return {
            "found": False,
            "error_reason": "Échec recherche alternative + génération",
            "attempted_queries": web_result.get("attempted_queries", [])
        }
    
    def _validate_enrichment_quality(self, strategy_result: Dict, company_data: Dict, logger) -> Dict[str, Any]:
        """Validation qualité avec seuils adaptatifs"""
        
        # Déterminer le seuil selon la stratégie
        if company_data["search_strategy"] == "alternative":
            quality_threshold = self.config.get("quality_threshold_fallback", 60)
            logger.info(f"Seuil adapté pour recherche alternative: {quality_threshold}%")
        else:
            quality_threshold = self.config.get("quality_threshold", 85)
        
        # Déléguer la validation au module spécialisé
        return self.quality_validator.validate_enrichment_result(
            strategy_result, company_data, quality_threshold
        )