# ============================================================================
# CHARGEUR DE DONNÉES
# mg-platform/mcp_server/tools/ai_agent/data/loader.py
# ============================================================================

"""
Module de chargement et analyse des fichiers Excel
Responsabilités:
- Auto-détection fichier Excel dans data/raw/
- Lecture sécurisée avec pandas
- Analyse contexte (colonnes, données manquantes)
- Sélection échantillon (ordre original respecté)
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Optional

from ..core.exceptions import DataLoadError, DataValidationError
from ..core.config import COLUMN_MAPPING


class DataLoader:
    """Gestionnaire de chargement et analyse des données"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.file_context = {}
    
    def load_excel_file(self, file_path: str = None) -> Optional[pd.DataFrame]:
        """
        Charge un fichier Excel depuis data/raw/ avec auto-détection
        
        Args:
            file_path: Chemin spécifique (optionnel)
            
        Returns:
            DataFrame ou None si échec
        """
        try:
            if file_path is None:
                file_path = self._find_excel_file()
            
            if not file_path:
                raise DataLoadError("Aucun fichier Excel trouvé dans data/raw/")
            
            # Lecture avec gestion d'erreurs
            df = self._read_excel_safe(file_path)
            
            # Nettoyage basique
            df = self._clean_dataframe(df)
            
            # Analyser le contexte
            self.file_context = self.analyze_file_context(df)
            
            return df
            
        except Exception as e:
            raise DataLoadError(f"Erreur chargement fichier: {str(e)}")
    
    def _find_excel_file(self) -> Optional[str]:
        """Auto-détection du fichier Excel"""
        try:
            # Construire le chemin depuis la racine du projet
            project_root = Path(__file__).parent.parent.parent.parent.parent
            raw_dir = project_root / self.config["raw_data_dir"]
            
            # Chercher fichiers Excel
            excel_files = list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls"))
            
            if excel_files:
                return str(excel_files[0])  # Prendre le premier trouvé
            
            return None
            
        except Exception:
            return None
    
    def _read_excel_safe(self, file_path: str) -> pd.DataFrame:
        """Lecture sécurisée avec fallbacks"""
        try:
            # Essayer avec openpyxl d'abord
            df = pd.read_excel(file_path, engine='openpyxl')
            return df
        except Exception:
            try:
                # Fallback vers xlrd
                df = pd.read_excel(file_path)
                return df
            except Exception as e:
                raise DataLoadError(f"Impossible de lire le fichier Excel: {str(e)}")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoyage basique du DataFrame"""
        df_clean = df.copy()
        
        # Remplacer NaN par chaînes vides pour éviter les problèmes
        df_clean = df_clean.fillna('')
        
        # Nettoyer les espaces dans les colonnes texte
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
        
        return df_clean
    
    def analyze_file_context(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse intelligente du contexte métier du fichier"""
        
        analysis = {
            "total_companies": len(df),
            "columns_count": len(df.columns),
            "has_siret": False,
            "has_website_column": False,
            "website_completion": 0,
            "website_column": None,
            "column_mapping": {}
        }
        
        # Mapper les colonnes connues
        for standard_name, possible_names in COLUMN_MAPPING.items():
            for col in df.columns:
                if any(name.lower() in col.lower() for name in possible_names):
                    analysis["column_mapping"][standard_name] = col
                    break
        
        # Analyser SIRET
        if "siret" in analysis["column_mapping"]:
            analysis["has_siret"] = True
        
        # Analyser colonne site web
        if "website" in analysis["column_mapping"]:
            website_col = analysis["column_mapping"]["website"]
            analysis["has_website_column"] = True
            analysis["website_column"] = website_col
            
            # Calculer taux de complétion
            non_empty = df[website_col][df[website_col].astype(str).str.strip() != '']
            analysis["website_completion"] = len(non_empty) / len(df)
        
        return analysis
    
    def select_sample(self, df: pd.DataFrame, sample_size: int) -> pd.DataFrame:
        """
        Sélection d'échantillon RESPECTANT L'ORDRE ORIGINAL
        
        Args:
            df: DataFrame complet
            sample_size: Taille de l'échantillon
            
        Returns:
            DataFrame échantillon
        """
        
        # Critères minimum pour sélection
        required_columns = ["SIRET", "Commune"]
        
        # Vérifier que les colonnes existent
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise DataValidationError(f"Colonnes manquantes: {missing_columns}")
        
        # Filtrer les entreprises valides (SIRET et commune non vides)
        valid_mask = (
            (df['SIRET'].astype(str).str.strip() != '') &
            (df['SIRET'].astype(str).str.strip() != 'nan') &
            (df['Commune'].astype(str).str.strip() != '') &
            (df['Commune'].astype(str).str.strip() != 'nan')
        )
        
        valid_companies = df[valid_mask].copy()
        
        if len(valid_companies) == 0:
            raise DataValidationError("Aucune entreprise valide trouvée (SIRET + Commune requis)")
        
        # STRATÉGIE: Ordre séquentiel (les N premières)
        if sample_size <= len(valid_companies):
            final_sample = valid_companies.head(sample_size)
        else:
            final_sample = valid_companies
        
        return final_sample
    
    def get_column_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Statistiques sur les colonnes pour analytics"""
        
        stats = {}
        
        for col in df.columns:
            col_data = df[col].astype(str).str.strip()
            
            # Compter les valeurs manquantes (patterns multiples)
            missing_patterns = ['', 'nan', 'NaN', 'INFORMATION NON-DIFFUSIBLE']
            missing_count = col_data.isin(missing_patterns).sum()
            
            present_count = len(df) - missing_count
            completion_rate = (present_count / len(df) * 100) if len(df) > 0 else 0
            
            stats[col] = {
                "total_values": len(df),
                "present_count": present_count,
                "missing_count": missing_count,
                "completion_rate": round(completion_rate, 1),
                "unique_values": col_data[~col_data.isin(missing_patterns)].nunique(),
                "sample_values": col_data[~col_data.isin(missing_patterns)].head(3).tolist()
            }
        
        return stats
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validation basique de la qualité des données"""
        
        issues = []
        warnings = []
        
        # Vérifications basiques
        if len(df) == 0:
            issues.append("DataFrame vide")
        
        if len(df.columns) == 0:
            issues.append("Aucune colonne trouvée")
        
        # Vérifier colonnes essentielles
        essential_columns = ["SIRET", "Commune"]
        for col in essential_columns:
            if col not in df.columns:
                issues.append(f"Colonne essentielle manquante: {col}")
        
        # Vérifier taux de complétion SIRET
        if "SIRET" in df.columns:
            siret_completion = self._calculate_completion_rate(df["SIRET"])
            if siret_completion < 80:
                warnings.append(f"Taux de complétion SIRET faible: {siret_completion}%")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_companies": len(df),
            "total_columns": len(df.columns)
        }
    
    def _calculate_completion_rate(self, series: pd.Series) -> float:
        """Calcule le taux de complétion d'une série"""
        missing_patterns = ['', 'nan', 'NaN', 'INFORMATION NON-DIFFUSIBLE']
        non_missing = ~series.astype(str).str.strip().isin(missing_patterns)
        return (non_missing.sum() / len(series) * 100) if len(series) > 0 else 0