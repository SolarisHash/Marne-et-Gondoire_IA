# ============================================================================
# AGENT PRINCIPAL - Orchestration du processus complet
# mg-platform/mcp_server/tools/ai_agent/core/agent.py
# ============================================================================

"""
Agent IA principal - Orchestration et coordination des modules spécialisés
Maximum 300 lignes comme spécifié
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from .config import get_config, validate_config
from .exceptions import AIAgentError, DataLoadError, EnrichmentError
from ..data.loader import DataLoader
from ..enrichment.strategies import EnrichmentStrategy
from ..output.excel_writer import ExcelWriter
from ..utils.logging import setup_session_logging


class AIEnrichmentAgent:
    """
    Agent IA d'enrichissement autonome - Version modulaire
    Focus: Orchestration et coordination des modules spécialisés
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise l'agent avec configuration
        
        Args:
            config: Configuration personnalisée (optionnelle)
        """
        # Configuration
        self.config = get_config(config)
        validate_config(self.config)
        
        # Session et timing
        self.session_id = datetime.now().strftime(self.config["session_id_format"])
        self.start_time = None
        
        # Métriques de performance
        self.performance_metrics = {
            "processed": 0,
            "enriched": 0,
            "failed": 0,
            "quality_scores": [],
            "processing_times": [],
            "error_details": [],
            "decisions_log": []
        }
        
        # Modules spécialisés
        self.data_loader = DataLoader(self.config)
        self.enrichment_strategy = EnrichmentStrategy(self.config)
        self.excel_writer = ExcelWriter(self.config, self.session_id)
        
        # Logging
        self.logger = setup_session_logging(self.session_id, self.config)
        self.logger.info(f"Agent IA initialisé - Session: {self.session_id}")
    
    def enrich_sample(self, sample_size: int = 10) -> Dict[str, Any]:
        """
        Enrichissement d'un échantillon avec analytics complètes
        
        Args:
            sample_size: Nombre d'entreprises à traiter
            
        Returns:
            Dict avec résultats complets
        """
        self.start_time = datetime.now()
        self.logger.info(f"🚀 Démarrage Agent IA - Échantillon {sample_size} entreprises")
        
        try:
            # 1. Charger et analyser le fichier
            df = self._load_and_analyze_data()
            if df is None:
                raise DataLoadError("Impossible de charger le fichier de données")
            
            # 2. Sélectionner l'échantillon optimal
            sample_df = self._select_optimal_sample(df, sample_size)
            
            # 3. Enrichir l'échantillon
            enrichment_results = self._enrich_companies(sample_df)
            
            # 4. Sauvegarder résultats enrichis
            output_file = self._save_results(sample_df, enrichment_results)
            
            # 5. Générer analytics
            analytics = self._generate_analytics(sample_df, enrichment_results)
            
            return self._build_final_result(
                sample_size, enrichment_results, output_file, analytics
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur critique Agent IA: {str(e)}")
            return self._build_error_result(e)
    
    def _load_and_analyze_data(self):
        """Délègue le chargement au module spécialisé"""
        try:
            df = self.data_loader.load_excel_file()
            
            if df is not None:
                context = self.data_loader.analyze_file_context(df)
                self.logger.info(f"📊 Contexte fichier: {context['total_companies']} entreprises")
                
            return df
            
        except Exception as e:
            self.logger.error(f"Erreur chargement données: {e}")
            return None
    
    def _select_optimal_sample(self, df, sample_size: int):
        """Sélection intelligente de l'échantillon"""
        self.logger.info(f"Sélection échantillon optimal ({sample_size} entreprises)")
        
        # Utiliser la méthode du loader pour garder l'ordre original
        sample_df = self.data_loader.select_sample(df, sample_size)
        
        # Log de l'échantillon sélectionné
        self._log_sample_selection(sample_df)
        
        return sample_df
    
    def _enrich_companies(self, sample_df):
        """Délègue l'enrichissement au module spécialisé"""
        self.logger.info(f"🤖 Début enrichissement IA - Seuil qualité: {self.config['quality_threshold']}%")
        
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
                company_name = company.get('Nom courant/Dénomination', 'N/A')
                self.logger.info(f"🔍 [{idx}/{len(sample_df)}] Traitement: {company_name}")
                
                # Déléguer l'enrichissement
                enrichment_result = self.enrichment_strategy.enrich_single_company(
                    company, idx, self.logger
                )
                
                # Traçabilité
                processing_time = time.time() - start_time
                self.performance_metrics["processing_times"].append(processing_time)
                
                if enrichment_result["success"]:
                    results["enriched"] += 1
                    results["enrichment_data"][str(idx)] = enrichment_result["data"]
                    results["quality_reports"][str(idx)] = enrichment_result["quality_report"]
                    
                    self.performance_metrics["quality_scores"].append(
                        enrichment_result["quality_score"]
                    )
                    
                    self.logger.info(f"✅ Succès - Score: {enrichment_result['quality_score']}%")
                else:
                    results["failed"] += 1
                    self.performance_metrics["error_details"].append({
                        "company_index": idx,
                        "company_name": company_name,
                        "error_reason": enrichment_result["error_reason"]
                    })
                    
                    self.logger.warning(f"❌ Échec - Raison: {enrichment_result['error_reason']}")
                
                # Log décision IA
                results["ai_decisions"].append(enrichment_result.get("ai_decision_log", {}))
                results["processed"] += 1
                
                # Rate limiting
                time.sleep(self.config["rate_limit_delay"])
                
            except Exception as e:
                self.logger.error(f"❌ Erreur traitement entreprise {idx}: {str(e)}")
                results["failed"] += 1
                results["processed"] += 1
        
        self.logger.info(f"🎯 Enrichissement terminé: {results['enriched']}/{results['processed']} succès")
        return results
    
    def _save_results(self, sample_df, enrichment_results):
        """Délègue la sauvegarde au module spécialisé"""
        try:
            output_file = self.excel_writer.save_enriched_results(
                sample_df, enrichment_results, self.performance_metrics
            )
            
            self.logger.info(f"💾 Fichier sauvegardé: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde: {e}")
            return ""
    
    def _generate_analytics(self, sample_df, enrichment_results):
        """Génère des analytics basiques (délégation possible future)"""
        success_rate = 0
        if enrichment_results["processed"] > 0:
            success_rate = (enrichment_results["enriched"] / enrichment_results["processed"]) * 100
        
        avg_quality = 0
        if self.performance_metrics["quality_scores"]:
            avg_quality = sum(self.performance_metrics["quality_scores"]) / len(self.performance_metrics["quality_scores"])
        
        return {
            "success_rate": round(success_rate, 1),
            "average_quality_score": round(avg_quality, 1),
            "total_processing_time": sum(self.performance_metrics["processing_times"]),
            "errors_summary": len(self.performance_metrics["error_details"])
        }
    
    def _build_final_result(self, sample_size, enrichment_results, output_file, analytics):
        """Construit le résultat final"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        return {
            "status": "✅ ENRICHISSEMENT IA TERMINÉ",
            "session_id": self.session_id,
            "execution_summary": {
                "sample_size": sample_size,
                "duration_seconds": round(total_duration, 1),
                "enriched_count": enrichment_results["enriched"],
                "success_rate": f"{analytics['success_rate']}%",
                "avg_quality_score": analytics["average_quality_score"]
            },
            "advanced_analytics": analytics,
            "output_file": output_file,
            "detailed_results": enrichment_results
        }
    
    def _build_error_result(self, error):
        """Construit un résultat d'erreur"""
        return {
            "error": f"Erreur Agent IA: {str(error)}",
            "session_id": self.session_id,
            "error_type": type(error).__name__,
            "partial_analytics": {
                "processed_before_error": self.performance_metrics.get("processed", 0),
                "errors_logged": len(self.performance_metrics.get("error_details", []))
            }
        }
    
    def _log_sample_selection(self, sample_df):
        """Log des entreprises sélectionnées"""
        missing_names = sample_df[
            sample_df['Nom courant/Dénomination'].astype(str).str.strip().isin([
                '', 'INFORMATION NON-DIFFUSIBLE', 'nan', 'NaN'
            ])
        ]
        
        missing_websites = sample_df[
            sample_df.get('Site Web établissement', pd.Series()).astype(str).str.strip().isin([
                '', 'nan', 'NaN'
            ])
        ]
        
        self.logger.info(f"Échantillon final: {len(sample_df)} entreprises")
        self.logger.info(f"📊 Avec nom manquant: {len(missing_names)} ({len(missing_names)/len(sample_df)*100:.1f}%)")
        self.logger.info(f"📊 Avec site manquant: {len(missing_websites)} ({len(missing_websites)/len(sample_df)*100:.1f}%)")
        
        # Log premières entreprises pour vérification
        self.logger.info("Premières entreprises sélectionnées:")
        for i, (original_idx, row) in enumerate(sample_df.head(5).iterrows(), 1):
            nom = row['Nom courant/Dénomination']
            commune = row['Commune']
            siret = str(row['SIRET'])[:8] + "..."
            self.logger.info(f"   {i}. [Ligne {original_idx+2}] {nom} ({commune}) - SIRET: {siret}")


# Import nécessaire pour les logs
import pandas as pd