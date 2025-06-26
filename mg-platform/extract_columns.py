#!/usr/bin/env python3
"""
Script d'extraction des colonnes - mg-platform
Analyse le fichier Excel source et extrait toutes les colonnes en JSON structuré

Usage: python extract_columns.py
Fichier temporaire - à supprimer après vérification
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime

def find_excel_file():
    """Trouve automatiquement le fichier Excel dans data/raw/"""
    try:
        # Chercher depuis le répertoire actuel
        raw_dirs = [
            Path("data/raw"),
            Path("mg-platform/data/raw"),
            Path("../data/raw")
        ]
        
        for raw_dir in raw_dirs:
            if raw_dir.exists():
                # Chercher fichiers Excel
                excel_files = list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls"))
                if excel_files:
                    return str(excel_files[0])
        
        return None
    except Exception as e:
        print(f"Erreur recherche fichier: {e}")
        return None

def analyze_column_content(series, column_name):
    """Analyse le contenu d'une colonne en détail"""
    
    # Convertir en string pour analyse uniforme
    str_series = series.astype(str).str.strip()
    
    # Patterns de valeurs manquantes
    missing_patterns = ['', 'nan', 'NaN', 'NULL', 'null', 'N/A', 'n/a', '-', '--', 'INFORMATION NON-DIFFUSIBLE']
    
    # Statistiques de base
    total_values = len(series)
    missing_mask = str_series.isin(missing_patterns)
    missing_count = missing_mask.sum()
    present_count = total_values - missing_count
    completion_rate = round((present_count / total_values * 100), 2) if total_values > 0 else 0
    
    # Valeurs non manquantes pour analyse
    non_missing = str_series[~missing_mask]
    
    # Échantillons de valeurs
    sample_values = non_missing.head(5).tolist() if len(non_missing) > 0 else []
    
    # Valeurs uniques
    unique_values = len(non_missing.unique()) if len(non_missing) > 0 else 0
    
    # Détection de patterns (regex corrigée)
    contains_numbers = non_missing.str.contains(r'\d', na=False).any() if len(non_missing) > 0 else False
    contains_emails = non_missing.str.contains(r'@', na=False).any() if len(non_missing) > 0 else False
    contains_urls = non_missing.str.contains(r'http|www\.', na=False, case=False).any() if len(non_missing) > 0 else False
    contains_phone = non_missing.str.contains(r'(?:\+33|0[1-9])(?:[\s\-\.]?[0-9]{2}){4}', na=False).any() if len(non_missing) > 0 else False
    
    # Longueur moyenne
    avg_length = round(non_missing.str.len().mean(), 1) if len(non_missing) > 0 else 0
    
    # Type de données détecté
    data_type = detect_column_type(column_name, non_missing)
    
    # Valeur la plus fréquente
    most_common = non_missing.mode().iloc[0] if len(non_missing.mode()) > 0 else None
    most_common_count = (non_missing == most_common).sum() if most_common else 0
    
    return {
        "statistics": {
            "total_values": total_values,
            "present_count": present_count,
            "missing_count": missing_count,
            "completion_rate": completion_rate,
            "unique_values": unique_values,
            "avg_length": avg_length
        },
        "content_analysis": {
            "sample_values": sample_values,
            "most_common_value": most_common,
            "most_common_count": most_common_count,
            "contains_numbers": contains_numbers,
            "contains_emails": contains_emails,
            "contains_urls": contains_urls,
            "contains_phone": contains_phone
        },
        "data_type": data_type,
        "missing_patterns_found": [pattern for pattern in missing_patterns if (str_series == pattern).any()]
    }

def detect_column_type(column_name, series):
    """Détecte le type d'une colonne basé sur son nom et contenu"""
    
    col_lower = column_name.lower()
    
    # Détection par nom de colonne
    type_mapping = {
        "identifier": ["siret", "siren", "id", "identifiant"],
        "company_name": ["nom", "denomination", "raison", "sociale", "entreprise"],
        "person_name": ["prenom", "prénom", "firstname"],
        "executive": ["dirigeant", "gerant", "president", "directeur"],
        "location": ["commune", "ville", "city", "adresse", "address"],
        "contact_email": ["email", "mail", "courriel"],
        "contact_phone": ["telephone", "phone", "tel"],
        "website": ["site", "web", "url", "www"],
        "activity": ["activite", "secteur", "naf", "ape", "metier"],
        "workforce": ["effectif", "salarie", "employe"],
        "legal": ["juridique", "statut", "forme"],
        "date": ["date", "creation", "debut", "fin"],
        "financial": ["capital", "chiffre", "affaires", "ca"]
    }
    
    for data_type, keywords in type_mapping.items():
        if any(keyword in col_lower for keyword in keywords):
            return {
                "category": data_type,
                "detection_method": "name_based",
                "keywords_matched": [kw for kw in keywords if kw in col_lower]
            }
    
    # Détection par contenu si pas trouvé par nom
    if len(series) > 0:
        sample_text = " ".join(series.head(10).astype(str)).lower()
        
        if "@" in sample_text:
            return {"category": "contact_email", "detection_method": "content_based", "keywords_matched": ["@"]}
        elif any(url in sample_text for url in ["http", "www", ".com", ".fr"]):
            return {"category": "website", "detection_method": "content_based", "keywords_matched": ["url_pattern"]}
        elif series.str.contains(r'^\d+$', na=False).any():
            return {"category": "numeric", "detection_method": "content_based", "keywords_matched": ["numeric_pattern"]}
    
    return {"category": "other", "detection_method": "unknown", "keywords_matched": []}

def assess_enrichment_potential(column_name, column_analysis):
    """Évalue le potentiel d'enrichissement d'une colonne"""
    
    data_type = column_analysis["data_type"]["category"]
    missing_count = column_analysis["statistics"]["missing_count"]
    completion_rate = column_analysis["statistics"]["completion_rate"]
    
    # Configuration de l'enrichissement par type
    enrichment_config = {
        "website": {"enrichable": True, "priority": "CRITIQUE", "success_rate": 75, "sources": ["LinkedIn", "Google", "DuckDuckGo"]},
        "contact_email": {"enrichable": True, "priority": "HAUTE", "success_rate": 60, "sources": ["LinkedIn", "Sites web"]},
        "contact_phone": {"enrichable": True, "priority": "MOYENNE", "success_rate": 50, "sources": ["LinkedIn", "Annuaires"]},
        "company_name": {"enrichable": True, "priority": "HAUTE", "success_rate": 70, "sources": ["LinkedIn", "Registres"]},
        "person_name": {"enrichable": True, "priority": "MOYENNE", "success_rate": 55, "sources": ["LinkedIn"]},
        "executive": {"enrichable": True, "priority": "MOYENNE", "success_rate": 60, "sources": ["LinkedIn"]},
        "activity": {"enrichable": True, "priority": "FAIBLE", "success_rate": 50, "sources": ["LinkedIn", "Sites web"]},
        "identifier": {"enrichable": False, "priority": "FAIBLE", "success_rate": 5, "sources": []},
        "location": {"enrichable": False, "priority": "FAIBLE", "success_rate": 15, "sources": ["APIs"]},
        "other": {"enrichable": False, "priority": "FAIBLE", "success_rate": 10, "sources": []}
    }
    
    config = enrichment_config.get(data_type, enrichment_config["other"])
    
    # Ajuster la priorité selon le volume et le taux de complétion
    if missing_count > 1000 and config["enrichable"]:
        priority = "CRITIQUE"
    elif missing_count > 500 and config["enrichable"]:
        priority = "HAUTE"
    elif missing_count > 100 and config["enrichable"] and completion_rate < 50:
        priority = config["priority"]
    else:
        priority = "FAIBLE" if missing_count < 50 else config["priority"]
    
    estimated_gain = int(missing_count * (config["success_rate"] / 100)) if config["enrichable"] else 0
    
    return {
        "is_enrichable": config["enrichable"],
        "priority": priority,
        "success_rate": config["success_rate"],
        "estimated_gain": estimated_gain,
        "potential_sources": config["sources"],
        "recommendation": get_enrichment_recommendation(missing_count, completion_rate, config["enrichable"])
    }

def get_enrichment_recommendation(missing_count, completion_rate, is_enrichable):
    """Génère une recommandation d'enrichissement"""
    
    if not is_enrichable:
        return "Non enrichissable automatiquement"
    
    if missing_count > 2000:
        return "PRIORITÉ MAXIMALE - Impact très fort"
    elif missing_count > 1000:
        return "PRIORITÉ HAUTE - Impact significatif"
    elif missing_count > 500:
        return "PRIORITÉ MOYENNE - Impact modéré"
    elif missing_count > 100:
        return "PRIORITÉ FAIBLE - Impact limité"
    else:
        return "Non prioritaire - Peu de valeurs manquantes"

def extract_columns_analysis():
    """Fonction principale d'extraction et analyse"""
    
    print("🔍 Recherche du fichier Excel...")
    
    # Trouver le fichier Excel
    file_path = find_excel_file()
    if not file_path:
        return {
            "error": "Aucun fichier Excel trouvé dans data/raw/",
            "searched_paths": ["data/raw/", "mg-platform/data/raw/", "../data/raw/"]
        }
    
    print(f"📁 Fichier trouvé: {file_path}")
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file_path, engine='openpyxl')
        df = df.fillna('')  # Remplacer NaN par chaînes vides
        
        print(f"📊 Analyse de {len(df)} lignes × {len(df.columns)} colonnes...")
        
        # Analyse globale
        file_info = {
            "file_path": file_path,
            "file_name": Path(file_path).name,
            "file_size_mb": round(Path(file_path).stat().st_size / (1024*1024), 2),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "analysis_date": datetime.now().isoformat()
        }
        
        # Analyse détaillée de chaque colonne
        columns_analysis = {}
        enrichment_opportunities = {}
        
        for i, column_name in enumerate(df.columns, 1):
            print(f"  🔍 Analyse colonne {i}/{len(df.columns)}: {column_name}")
            
            # Analyse complète de la colonne
            column_analysis = analyze_column_content(df[column_name], column_name)
            
            # Évaluation du potentiel d'enrichissement
            enrichment_potential = assess_enrichment_potential(column_name, column_analysis)
            column_analysis["enrichment_potential"] = enrichment_potential
            
            # Stocker l'analyse
            columns_analysis[column_name] = column_analysis
            
            # Si enrichissable, ajouter aux opportunités
            if enrichment_potential["is_enrichable"] and enrichment_potential["estimated_gain"] > 0:
                enrichment_opportunities[column_name] = {
                    "missing_count": column_analysis["statistics"]["missing_count"],
                    "completion_rate": column_analysis["statistics"]["completion_rate"],
                    "priority": enrichment_potential["priority"],
                    "estimated_gain": enrichment_potential["estimated_gain"],
                    "success_rate": enrichment_potential["success_rate"],
                    "sources": enrichment_potential["potential_sources"],
                    "recommendation": enrichment_potential["recommendation"]
                }
        
        # Statistiques globales
        total_cells = file_info["total_rows"] * file_info["total_columns"]
        total_missing = sum(col["statistics"]["missing_count"] for col in columns_analysis.values())
        global_completion = round(((total_cells - total_missing) / total_cells * 100), 2) if total_cells > 0 else 0
        
        global_stats = {
            "total_cells": total_cells,
            "filled_cells": total_cells - total_missing,
            "missing_cells": total_missing,
            "global_completion_rate": global_completion,
            "enrichable_columns": len(enrichment_opportunities),
            "total_enrichment_potential": sum(opp["estimated_gain"] for opp in enrichment_opportunities.values())
        }
        
        # Résultat final structuré
        result = {
            "extraction_info": {
                "script_version": "1.0",
                "extraction_successful": True,
                "extraction_date": datetime.now().isoformat()
            },
            "file_info": file_info,
            "global_statistics": global_stats,
            "columns_analysis": columns_analysis,
            "enrichment_opportunities": enrichment_opportunities,
            "summary": {
                "total_columns": len(df.columns),
                "columns_with_missing_data": len([col for col in columns_analysis.values() if col["statistics"]["missing_count"] > 0]),
                "most_complete_column": max(columns_analysis.keys(), key=lambda k: columns_analysis[k]["statistics"]["completion_rate"]),
                "least_complete_column": min(columns_analysis.keys(), key=lambda k: columns_analysis[k]["statistics"]["completion_rate"]),
                "top_enrichment_priorities": sorted(
                    enrichment_opportunities.keys(),
                    key=lambda k: enrichment_opportunities[k]["estimated_gain"],
                    reverse=True
                )[:5]
            }
        }
        
        return result
        
    except Exception as e:
        return {
            "error": f"Erreur lors de l'analyse: {str(e)}",
            "file_path": file_path,
            "error_type": type(e).__name__
        }

def clean_data_for_json(obj, seen=None):
    """Nettoie récursivement les données pour éviter les références circulaires"""
    import numpy as np
    
    if seen is None:
        seen = set()
    
    # Éviter les références circulaires
    obj_id = id(obj)
    if obj_id in seen:
        return "<circular_reference>"
    
    # Conversion des types numpy
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        return str(obj)  # Convertir pandas en string
    
    # Traitement des collections
    if isinstance(obj, dict):
        seen.add(obj_id)
        result = {}
        for k, v in obj.items():
            try:
                result[str(k)] = clean_data_for_json(v, seen.copy())
            except:
                result[str(k)] = str(v)  # Fallback en string
        return result
    elif isinstance(obj, (list, tuple)):
        seen.add(obj_id)
        return [clean_data_for_json(item, seen.copy()) for item in obj]
    
    # Fallback pour autres types
    try:
        # Test si l'objet est JSON serializable
        json.dumps(obj)
        return obj
    except:
        return str(obj)

def save_results_to_file(results, output_file="columns_analysis.json"):
    """Sauvegarde les résultats dans un fichier JSON avec nettoyage sécurisé"""
    try:
        # Nettoyer les données
        clean_results = clean_data_for_json(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés dans: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        
        # Fallback : sauvegarder juste le résumé
        try:
            summary_only = {
                "extraction_info": results.get("extraction_info", {}),
                "file_info": results.get("file_info", {}),
                "global_statistics": results.get("global_statistics", {}),
                "enrichment_opportunities": clean_data_for_json(results.get("enrichment_opportunities", {})),
                "summary": results.get("summary", {})
            }
            
            with open("columns_summary.json", 'w', encoding='utf-8') as f:
                json.dump(summary_only, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Résumé sauvegardé dans: columns_summary.json")
            return True
        except Exception as e2:
            print(f"❌ Erreur fallback: {e2}")
            return False

def display_summary(results):
    """Affiche un résumé des résultats"""
    if "error" in results:
        print(f"❌ ERREUR: {results['error']}")
        return
    
    file_info = results["file_info"]
    global_stats = results["global_statistics"]
    enrichment_opps = results["enrichment_opportunities"]
    summary = results["summary"]
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE L'EXTRACTION DES COLONNES")
    print("="*60)
    print(f"📁 Fichier: {file_info['file_name']}")
    print(f"📏 Taille: {file_info['file_size_mb']} MB")
    print(f"📊 Dimensions: {file_info['total_rows']:,} lignes × {file_info['total_columns']} colonnes")
    print(f"✅ Complétion globale: {global_stats['global_completion_rate']}%")
    print()
    print(f"🎯 OPPORTUNITÉS D'ENRICHISSEMENT:")
    print(f"   • Colonnes enrichissables: {global_stats['enrichable_columns']}")
    print(f"   • Gain potentiel total: {global_stats['total_enrichment_potential']:,} valeurs")
    print()
    print(f"🔥 TOP 3 PRIORITÉS:")
    for i, col in enumerate(summary["top_enrichment_priorities"][:3], 1):
        opp = enrichment_opps[col]
        print(f"   {i}. {col}")
        print(f"      → {opp['missing_count']:,} manquants | Gain: {opp['estimated_gain']:,}")
        print(f"      → {opp['priority']} | {opp['recommendation']}")
    print("="*60)

def main():
    """Fonction principale"""
    print("🚀 Script d'extraction des colonnes - mg-platform")
    print("📋 Analyse complète du fichier Excel source")
    print("-" * 60)
    
    # Extraction et analyse
    results = extract_columns_analysis()
    
    # Sauvegarde en JSON
    save_results_to_file(results)
    
    # Affichage du résumé
    display_summary(results)
    
    print(f"\n💡 Fichier JSON généré: columns_analysis.json")
    print(f"🗑️ Supprimez ce script après vérification: rm extract_columns.py")

if __name__ == "__main__":
    main()