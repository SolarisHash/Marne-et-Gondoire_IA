# ============================================================================
# VALIDATION QUALITÉ
# mg-platform/mcp_server/tools/ai_agent/enrichment/validation.py
# ============================================================================

"""
Module de validation qualité des enrichissements
Responsabilités:
- Score adaptatif selon stratégie (noms réels: 85%, NON-DIFFUSIBLE: 60%)
- Calcul bonus (géo, secteur, source)
- Validation unique (pas de double validation)
- Interface unifiée pour les stratégies
"""

import re
from typing import Dict, Any


class QualityValidator:
    """Validateur de qualité avec scoring adaptatif"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def validate_enrichment_result(self, strategy_result: Dict, company_data: Dict, threshold: int) -> Dict[str, Any]:
        """
        Validation principale d'un résultat d'enrichissement
        
        Args:
            strategy_result: Résultat de la stratégie d'enrichissement
            company_data: Données originales de l'entreprise
            threshold: Seuil de qualité à appliquer
            
        Returns:
            Dict avec validation et score
        """
        
        # Récupérer le score de confiance de la stratégie
        ai_confidence = strategy_result["data"].get("ai_validation_score", 0)
        
        # Calcul du score final avec bonus
        final_score = self._calculate_enhanced_score(
            ai_confidence, strategy_result, company_data
        )
        
        # Validation selon le seuil
        is_valid = final_score >= threshold
        
        return {
            "is_valid": is_valid,
            "quality_score": final_score,
            "threshold_used": threshold,
            "validation_method": "adaptive_scoring",
            "error_reason": "" if is_valid else f"Qualité insuffisante ({final_score}% < {threshold}%)",
            "score_breakdown": self._get_score_breakdown(ai_confidence, strategy_result, company_data)
        }
    
    def _calculate_enhanced_score(self, base_score: float, strategy_result: Dict, company_data: Dict) -> int:
        """Calcule le score final avec bonus contextuels"""
        
        enhanced_score = base_score
        
        # Bonus géographique
        geo_bonus = self._calculate_geo_bonus(strategy_result["data"], company_data)
        enhanced_score += geo_bonus
        
        # Bonus secteur
        sector_bonus = self._calculate_sector_bonus(strategy_result["data"], company_data)
        enhanced_score += sector_bonus
        
        # Bonus source
        source_bonus = self._calculate_source_bonus(strategy_result)
        enhanced_score += source_bonus
        
        # Bonus cohérence données
        coherence_bonus = self._calculate_coherence_bonus(strategy_result["data"], company_data)
        enhanced_score += coherence_bonus
        
        return min(100, max(0, int(enhanced_score)))
    
    def _calculate_geo_bonus(self, enriched_data: Dict, company_data: Dict) -> float:
        """Bonus pour cohérence géographique"""
        
        bonus = 0
        
        # Bonus si commune cohérente
        enriched_location = enriched_data.get("location", "").lower()
        expected_commune = company_data.get("commune", "").lower()
        
        if enriched_location and expected_commune:
            if expected_commune in enriched_location:
                bonus += 10
            elif any(word in enriched_location for word in expected_commune.split()):
                bonus += 5
        
        return bonus
    
    def _calculate_sector_bonus(self, enriched_data: Dict, company_data: Dict) -> float:
        """Bonus pour cohérence sectorielle"""
        
        bonus = 0
        
        # Bonus si secteur cohérent avec NAF
        enriched_sector = enriched_data.get("business_sector", "").lower()
        naf_label = company_data.get("naf_label", "").lower()
        
        if enriched_sector and naf_label:
            # Vérifier correspondance mots-clés
            sector_keywords = self._extract_sector_keywords(enriched_sector)
            naf_keywords = self._extract_sector_keywords(naf_label)
            
            common_keywords = set(sector_keywords) & set(naf_keywords)
            if common_keywords:
                bonus += 5
        
        return bonus
    
    def _calculate_source_bonus(self, strategy_result: Dict) -> float:
        """Bonus selon la source des données"""
        
        source = strategy_result.get("source", "")
        
        source_scores = {
            "WEB_SEARCH_REAL": 15,      # Recherche web réelle
            "WEB_SEARCH_ALTERNATIVE": 10, # Recherche alternative
            "INTELLIGENT_ENHANCEMENT": 8,  # Amélioration intelligente
            "INTELLIGENT_GENERATION": 5    # Génération intelligente
        }
        
        return source_scores.get(source, 0)
    
    def _calculate_coherence_bonus(self, enriched_data: Dict, company_data: Dict) -> float:
        """Bonus pour cohérence globale des données"""
        
        bonus = 0
        
        # Bonus si nom d'entreprise cohérent
        enriched_name = enriched_data.get("company_name", "").lower()
        original_name = company_data.get("name", "").lower()
        
        if enriched_name and original_name and original_name != "information non-diffusible":
            # Vérifier similarité
            similarity = self._calculate_name_similarity(enriched_name, original_name)
            if similarity > 70:
                bonus += 10
            elif similarity > 50:
                bonus += 5
        
        # Bonus si site web semble professionnel
        website = enriched_data.get("website", "")
        if website:
            if self._is_professional_website(website):
                bonus += 5
        
        return bonus
    
    def _extract_sector_keywords(self, text: str) -> list:
        """Extrait les mots-clés significatifs d'un texte de secteur"""
        
        if not text:
            return []
        
        # Mots-clés sectoriels importants
        sector_keywords = [
            "informatique", "logiciel", "développement", "digital", "tech",
            "conseil", "consulting", "expertise", "management",
            "construction", "bâtiment", "travaux", "rénovation",
            "commerce", "vente", "magasin", "distribution",
            "transport", "logistique", "déplacement",
            "santé", "médical", "soins", "cabinet"
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in sector_keywords if kw in text_lower]
        
        return found_keywords
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calcule la similarité entre deux noms"""
        
        if not name1 or not name2:
            return 0
        
        # Normaliser
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        
        # Correspondance exacte
        if n1 == n2:
            return 100
        
        # L'un contient l'autre
        if n1 in n2 or n2 in n1:
            return 85
        
        # Similarité par mots
        words1 = set(n1.split())
        words2 = set(n2.split())
        
        if words1 and words2:
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            similarity = (intersection / union) * 100
            return similarity
        
        return 20  # Similarité minimale
    
    def _is_professional_website(self, website: str) -> bool:
        """Détermine si un site web semble professionnel"""
        
        if not website:
            return False
        
        website_lower = website.lower()
        
        # Indicateurs de professionnalisme
        professional_indicators = [
            website.startswith("https://"),  # HTTPS
            ".fr" in website_lower,          # Domaine français
            len(website) > 20,               # URL complète
            not any(spam in website_lower for spam in ["free", "perso", "test"])
        ]
        
        return sum(professional_indicators) >= 2
    
    def _get_score_breakdown(self, base_score: float, strategy_result: Dict, company_data: Dict) -> Dict[str, float]:
        """Retourne le détail du calcul de score pour debugging"""
        
        return {
            "base_score": base_score,
            "geo_bonus": self._calculate_geo_bonus(strategy_result["data"], company_data),
            "sector_bonus": self._calculate_sector_bonus(strategy_result["data"], company_data),
            "source_bonus": self._calculate_source_bonus(strategy_result),
            "coherence_bonus": self._calculate_coherence_bonus(strategy_result["data"], company_data)
        }
    
    def validate_data_consistency(self, enriched_data: Dict, original_data: Dict) -> Dict[str, Any]:
        """Validation de cohérence avancée (optionnelle)"""
        
        issues = []
        warnings = []
        
        # Vérifier cohérence nom
        enriched_name = enriched_data.get("company_name", "")
        original_name = original_data.get("name", "")
        
        if original_name and original_name != "INFORMATION NON-DIFFUSIBLE":
            similarity = self._calculate_name_similarity(enriched_name, original_name)
            if similarity < 30:
                issues.append(f"Incohérence nom: '{enriched_name}' vs '{original_name}'")
        
        # Vérifier cohérence géographique
        enriched_location = enriched_data.get("location", "")
        expected_commune = original_data.get("commune", "")
        
        if enriched_location and expected_commune:
            if expected_commune.lower() not in enriched_location.lower():
                warnings.append(f"Localisation incohérente: '{enriched_location}' vs '{expected_commune}'")
        
        return {
            "is_consistent": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }