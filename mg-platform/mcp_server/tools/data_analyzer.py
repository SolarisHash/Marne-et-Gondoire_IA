# ============================================================================
# ANALYSEUR SIMPLE ET FONCTIONNEL - mcp_server/tools/data_analyzer.py
# ============================================================================

import pandas as pd
import numpy as np
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

def analyze_complete_file(file_path: str = None) -> Dict[str, Any]:
    """
    Analyseur simple qui fonctionne à coup sûr
    Analyse TOUTES les colonnes avec détection automatique basique
    """
    
    try:
        # 1. Trouver et lire le fichier
        if file_path is None:
            file_path = find_excel_file()
        
        if not file_path:
            return {"error": "Aucun fichier Excel trouvé dans data/raw/"}
        
        # 2. Lire le fichier
        df = read_excel_safe(file_path)
        
        # 3. Nettoyer les données
        df_clean = clean_dataframe(df)
        
        print(f"📊 Analyse: {len(df_clean)} lignes × {len(df_clean.columns)} colonnes")
        
        # 4. Analyser chaque colonne
        all_columns = {}
        enrichment_opportunities = {}
        
        for col_name in df_clean.columns:
            print(f"🔍 Analyse colonne: {col_name}")
            
            # Analyse de base de la colonne
            col_analysis = analyze_column(df_clean[col_name], col_name)
            all_columns[col_name] = col_analysis
            
            # Si enrichissable, ajouter aux opportunités
            if col_analysis["enrichment_potential"]["is_enrichable"]:
                enrichment_opportunities[col_name] = {
                    "missing_count": col_analysis["missing_count"],
                    "completion_rate": col_analysis["completion_rate"],
                    "estimated_gain": col_analysis["enrichment_potential"]["estimated_gain"],
                    "priority": col_analysis["enrichment_potential"]["priority"],
                    "sources": col_analysis["enrichment_potential"]["sources"]
                }
        
        # 5. Statistiques globales
        global_stats = calculate_global_stats(df_clean, all_columns)
        
        # 6. Résultat final
        result = {
            "status": "✅ ANALYSE COMPLÈTE TERMINÉE",
            "file_info": {
                "filename": Path(file_path).name,
                "total_rows": len(df_clean),
                "total_columns": len(df_clean.columns),
                "file_size_mb": round(Path(file_path).stat().st_size / (1024*1024), 2)
            },
            "global_stats": global_stats,
            "all_columns_analysis": all_columns,
            "enrichment_opportunities": enrichment_opportunities,
            "sample_data": get_sample_data(df_clean)
        }
        
        return result
        
    except Exception as e:
        return {
            "error": f"Erreur: {str(e)}",
            "error_type": type(e).__name__,
            "file_path": str(file_path) if file_path else "None"
        }

def find_excel_file() -> Optional[str]:
    """Trouve un fichier Excel dans data/raw/"""
    try:
        project_root = Path(__file__).parent.parent.parent
        raw_dir = project_root / "data" / "raw"
        
        # Chercher fichiers Excel
        excel_files = list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls"))
        
        if excel_files:
            return str(excel_files[0])  # Prendre le premier trouvé
        
        return None
    except Exception:
        return None

def read_excel_safe(file_path: str) -> pd.DataFrame:
    """Lecture sécurisée du fichier Excel"""
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        return df
    except Exception as e:
        # Essayer avec xlrd si openpyxl échoue
        try:
            df = pd.read_excel(file_path)
            return df
        except Exception:
            raise Exception(f"Impossible de lire le fichier Excel: {str(e)}")

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoyage basique du DataFrame"""
    df_clean = df.copy()
    
    # Remplacer NaN par chaînes vides
    df_clean = df_clean.fillna('')
    
    # Nettoyer les espaces
    for col in df_clean.select_dtypes(include=['object']).columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()
    
    return df_clean

def analyze_column(series: pd.Series, col_name: str) -> Dict[str, Any]:
    """Analyse complète d'une colonne"""
    
    # Détecter les valeurs manquantes
    missing_patterns = detect_missing_patterns(series)
    missing_count = count_missing_values(series, missing_patterns)
    
    total_count = len(series)
    present_count = total_count - missing_count
    completion_rate = (present_count / total_count * 100) if total_count > 0 else 0
    
    # Analyser le contenu
    content_analysis = analyze_content(series, missing_patterns)
    
    # Détecter le type de colonne
    column_type = detect_column_type(col_name, series, content_analysis)
    
    # Évaluer le potentiel d'enrichissement
    enrichment_potential = assess_enrichment_potential(col_name, column_type, missing_count)
    
    return {
        "completion_rate": round(completion_rate, 1),
        "missing_count": missing_count,
        "present_count": present_count,
        "missing_patterns_detected": missing_patterns,
        "content_analysis": content_analysis,
        "detected_type": column_type,
        "enrichment_potential": enrichment_potential
    }

def detect_missing_patterns(series: pd.Series) -> List[str]:
    """Détecte les patterns de valeurs manquantes"""
    
    # Patterns standards
    standard_patterns = ['', 'nan', 'NaN', 'NULL', 'null', 'N/A', 'n/a', '-', '--']
    
    # Compter les valeurs les plus fréquentes
    value_counts = series.astype(str).str.strip().value_counts()
    
    detected_patterns = []
    
    # Ajouter les patterns standards trouvés
    for pattern in standard_patterns:
        if pattern in value_counts.index:
            detected_patterns.append(pattern)
    
    # Chercher des patterns spécifiques (comme "INFORMATION NON-DIFFUSIBLE")
    for value, count in value_counts.head(10).items():
        if count > len(series) * 0.05:  # Si > 5% des valeurs
            value_upper = str(value).strip().upper()
            if any(word in value_upper for word in ['INFORMATION', 'NON', 'DIFFUSIBLE', 'RENSEIGNE']):
                detected_patterns.append(str(value).strip())
    
    return list(set(detected_patterns))

def count_missing_values(series: pd.Series, missing_patterns: List[str]) -> int:
    """Compte les valeurs manquantes selon les patterns détectés"""
    missing_count = 0
    
    for pattern in missing_patterns:
        missing_count += (series.astype(str).str.strip() == pattern).sum()
    
    return missing_count

def analyze_content(series: pd.Series, missing_patterns: List[str]) -> Dict[str, Any]:
    """Analyse le contenu d'une colonne"""
    
    # Filtrer les valeurs non manquantes
    mask = ~series.astype(str).str.strip().isin(missing_patterns)
    non_empty = series[mask]
    
    if len(non_empty) == 0:
        return {
            "unique_values": 0,
            "avg_length": 0,
            "sample_values": [],
            "contains_numbers": False,
            "contains_emails": False,
            "contains_urls": False
        }
    
    # Analyses basiques
    sample_values = non_empty.head(3).astype(str).tolist()
    
    # Détecter des patterns dans le contenu
    text_series = non_empty.astype(str)
    
    return {
        "unique_values": len(non_empty.unique()),
        "avg_length": round(text_series.str.len().mean(), 1),
        "sample_values": sample_values,
        "contains_numbers": text_series.str.contains(r'\d', na=False).any(),
        "contains_emails": text_series.str.contains('@', na=False).any(),
        "contains_urls": text_series.str.contains(r'http|www\.', na=False).any(),
        "most_common": str(non_empty.mode().iloc[0]) if len(non_empty.mode()) > 0 else ""
    }

def detect_column_type(col_name: str, series: pd.Series, content_analysis: Dict) -> Dict[str, Any]:
    """Détecte le type d'une colonne"""
    
    col_lower = col_name.lower()
    
    # Détection par nom de colonne
    if any(word in col_lower for word in ['siret', 'siren']):
        category = "identifier"
    elif any(word in col_lower for word in ['site', 'web', 'url']):
        category = "web"
    elif any(word in col_lower for word in ['email', 'mail']):
        category = "contact_email"
    elif any(word in col_lower for word in ['telephone', 'phone']):
        category = "contact_phone"
    elif any(word in col_lower for word in ['nom', 'denomination', 'raison']):
        category = "company_name"
    elif any(word in col_lower for word in ['prenom', 'prénom']):
        category = "person_name"
    elif any(word in col_lower for word in ['dirigeant', 'gerant', 'president']):
        category = "executive"
    elif any(word in col_lower for word in ['effectif', 'salarie']):
        category = "workforce"
    elif any(word in col_lower for word in ['adresse', 'rue', 'voie']):
        category = "address"
    elif any(word in col_lower for word in ['commune', 'ville']):
        category = "location"
    elif any(word in col_lower for word in ['activite', 'secteur', 'naf']):
        category = "activity"
    else:
        category = "other"
    
    # Détecter par contenu si pas trouvé par nom
    if category == "other":
        if content_analysis["contains_emails"]:
            category = "contact_email"
        elif content_analysis["contains_urls"]:
            category = "web"
    
    return {
        "category": category,
        "detection_method": "name_based" if category != "other" else "content_based"
    }

def assess_enrichment_potential(col_name: str, column_type: Dict, missing_count: int) -> Dict[str, Any]:
    """Évalue le potentiel d'enrichissement"""
    
    category = column_type["category"]
    
    # Définir le potentiel selon le type
    enrichment_config = {
        "web": {"enrichable": True, "success_rate": 75, "sources": ["LinkedIn", "Google"], "priority": "CRITIQUE"},
        "contact_email": {"enrichable": True, "success_rate": 60, "sources": ["LinkedIn", "Sites web"], "priority": "HAUTE"},
        "contact_phone": {"enrichable": True, "success_rate": 50, "sources": ["LinkedIn", "Annuaires"], "priority": "MOYENNE"},
        "company_name": {"enrichable": True, "success_rate": 70, "sources": ["LinkedIn", "Registres"], "priority": "HAUTE"},
        "person_name": {"enrichable": True, "success_rate": 55, "sources": ["LinkedIn"], "priority": "MOYENNE"},
        "executive": {"enrichable": True, "success_rate": 60, "sources": ["LinkedIn"], "priority": "MOYENNE"},
        "workforce": {"enrichable": True, "success_rate": 65, "sources": ["LinkedIn"], "priority": "MOYENNE"},
        "activity": {"enrichable": True, "success_rate": 50, "sources": ["LinkedIn", "Sites web"], "priority": "FAIBLE"},
        "identifier": {"enrichable": False, "success_rate": 5, "sources": [], "priority": "FAIBLE"},
        "address": {"enrichable": False, "success_rate": 20, "sources": ["APIs"], "priority": "FAIBLE"},
        "location": {"enrichable": False, "success_rate": 15, "sources": ["APIs"], "priority": "FAIBLE"},
        "other": {"enrichable": False, "success_rate": 10, "sources": [], "priority": "FAIBLE"}
    }
    
    config = enrichment_config.get(category, enrichment_config["other"])
    
    # Ajuster la priorité selon le volume
    if missing_count > 1000 and config["enrichable"]:
        priority = "CRITIQUE"
    elif missing_count > 500 and config["enrichable"]:
        priority = "HAUTE"
    elif missing_count > 100 and config["enrichable"]:
        priority = config["priority"]
    else:
        priority = "FAIBLE"
    
    estimated_gain = int(missing_count * (config["success_rate"] / 100)) if config["enrichable"] else 0
    
    return {
        "is_enrichable": config["enrichable"],
        "success_rate": config["success_rate"],
        "sources": config["sources"],
        "priority": priority,
        "estimated_gain": estimated_gain
    }

def calculate_global_stats(df: pd.DataFrame, columns_analysis: Dict) -> Dict[str, Any]:
    """Calcule les statistiques globales"""
    
    total_cells = len(df) * len(df.columns)
    total_missing = sum(col["missing_count"] for col in columns_analysis.values())
    total_filled = total_cells - total_missing
    
    overall_completion = (total_filled / total_cells * 100) if total_cells > 0 else 0
    
    return {
        "total_cells": total_cells,
        "filled_cells": total_filled,
        "missing_cells": total_missing,
        "overall_completion_rate": round(overall_completion, 1),
        "avg_missing_per_row": round(total_missing / len(df), 1) if len(df) > 0 else 0
    }

def get_sample_data(df: pd.DataFrame, limit: int = 5) -> List[Dict[str, str]]:
    """Récupère un échantillon des données"""
    
    # Identifier les colonnes importantes
    important_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if any(word in col_lower for word in ['siret', 'nom', 'denomination', 'commune']):
            important_cols.append(col)
    
    # Si pas de colonnes importantes, prendre les 5 premières
    if not important_cols:
        important_cols = df.columns[:5].tolist()
    
    # Échantillon
    sample = df[important_cols].head(limit)
    
    # Convertir en format simple
    result = []
    for _, row in sample.iterrows():
        row_dict = {}
        for col in important_cols:
            value = str(row[col])
            if len(value) > 40:
                value = value[:37] + "..."
            row_dict[col] = value
        result.append(row_dict)
    
    return result

# Alias pour compatibilité
analyze_data_gaps_advanced = analyze_complete_file