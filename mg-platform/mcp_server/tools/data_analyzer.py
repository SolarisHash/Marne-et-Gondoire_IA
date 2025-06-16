import pandas as pd
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

def analyze_data_gaps_advanced(file_path: str = None) -> Dict[str, Any]:
    """
    Analyse avancée d'un fichier Excel pour identifier les données manquantes
    Optimisé pour de gros volumes (3000+ entreprises)
    """
    
    try:
        # Auto-détection du fichier dans data/raw/
        if file_path is None:
            project_root = Path(__file__).parent.parent.parent
            raw_dir = project_root / "data" / "raw"
            
            excel_files = list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls"))
            if not excel_files:
                return {"error": "Aucun fichier Excel trouvé dans data/raw/"}
            
            file_path = excel_files[0]
            print(f"📊 Analyse avancée du fichier: {file_path.name}")
        
        # Lecture du fichier Excel
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"📈 Fichier chargé: {len(df)} entreprises, {len(df.columns)} colonnes")
        
        # Patterns de valeurs manquantes spécifiques SIRENE
        missing_patterns = [
            '', 
            'INFORMATION NON-DIFFUSIBLE', 
            'NON-DIFFUSIBLE',
            'Non renseigné',
            'N/A',
            'nan', 
            'NaN'
        ]
        
        # Analyse détaillée par colonne
        analysis = {}
        total_rows = len(df)
        
        for col in df.columns:
            # Calculer les valeurs manquantes
            missing_mask = df[col].isnull()
            
            # Ajouter les patterns spécifiques
            for pattern in missing_patterns[:-2]:  # Exclure nan/NaN déjà gérés
                if pattern:
                    missing_mask |= (df[col].astype(str).str.strip() == pattern)
            
            missing_count = missing_mask.sum()
            present_count = total_rows - missing_count
            completion_rate = (present_count / total_rows) * 100
            
            # Déterminer si enrichissable via LinkedIn
            enrichable = is_linkedin_enrichable(col)
            priority = get_enrichment_priority(col, completion_rate, missing_count)
            
            analysis[col] = {
                "completion_rate": round(completion_rate, 1),
                "missing_count": int(missing_count),
                "present_count": int(present_count),
                "linkedin_enrichable": enrichable,
                "priority": priority,
                "estimated_gain": calculate_potential_gain(col, missing_count) if enrichable else 0
            }
        
        # Identifier les meilleures opportunités
        linkedin_opportunities = {
            col: data for col, data in analysis.items()
            if data["linkedin_enrichable"] and data["missing_count"] > 100  # Au moins 100 manquants
        }
        
        # Statistiques globales
        avg_completion = sum(data["completion_rate"] for data in analysis.values()) / len(analysis)
        total_missing_fields = sum(data["missing_count"] for data in analysis.values())
        
        # Recommandations spécifiques pour gros volume
        recommendations = generate_batch_recommendations(linkedin_opportunities, total_rows)
        
        return {
            "status": "✅ ANALYSE AVANCÉE TERMINÉE",
            "file_info": {
                "name": Path(file_path).name,
                "path": str(file_path),
                "total_companies": total_rows,
                "total_columns": len(df.columns),
                "file_size_mb": round(Path(file_path).stat().st_size / (1024*1024), 2)
            },
            "global_stats": {
                "average_completion_rate": round(avg_completion, 1),
                "total_missing_fields": int(total_missing_fields),
                "fields_per_company": round(total_missing_fields / total_rows, 1)
            },
            "column_analysis": analysis,
            "linkedin_opportunities": linkedin_opportunities,
            "recommendations": recommendations,
            "batch_strategy": {
                "recommended_batch_size": min(50, max(10, total_rows // 100)),
                "estimated_processing_time": f"{(total_rows * 2) // 60} minutes",
                "rate_limiting": "2 secondes entre requêtes"
            },
            "top_priorities": get_top_priorities(linkedin_opportunities),
            "sample_companies": get_sample_companies(df, limit=5)
        }
        
    except Exception as e:
        return {
            "error": f"Erreur lors de l'analyse avancée: {str(e)}",
            "file_path": str(file_path) if file_path else "Non spécifié"
        }

def is_linkedin_enrichable(column_name: str) -> bool:
    """Détermine si une colonne peut être enrichie via LinkedIn"""
    linkedin_fields = {
        # Sites web - priorité max
        'site web': True, 'website': True, 'url': True,
        
        # Effectifs - très faisable
        'effectif': True, 'taille': True, 'salaries': True,
        
        # Dirigeants - possible
        'dirigeant': True, 'gérant': True, 'président': True, 'ceo': True,
        'directeur': True, 'nom': True, 'prénom': True,
        
        # Secteur/activité - disponible
        'activité': True, 'secteur': True, 'industrie': True, 'description': True,
        
        # Contacts - parfois disponible
        'email': True, 'mail': True, 'telephone': True, 'phone': True
    }
    
    column_lower = column_name.lower()
    return any(term in column_lower for term, enrichable in linkedin_fields.items() if enrichable)

def get_enrichment_priority(column_name: str, completion_rate: float, missing_count: int) -> str:
    """Calcule la priorité d'enrichissement"""
    column_lower = column_name.lower()
    
    # Sites web = toujours priorité max si beaucoup manquent
    if any(term in column_lower for term in ['site', 'web', 'url']) and missing_count > 50:
        return "🔥 CRITIQUE"
    
    # Effectifs avec beaucoup de manquants
    elif 'effectif' in column_lower and missing_count > 500:
        return "🟠 HAUTE"
    
    # Dirigeants avec beaucoup de manquants  
    elif any(term in column_lower for term in ['dirigeant', 'nom', 'prénom']) and missing_count > 1000:
        return "🟡 MOYENNE"
    
    # Autres selon taux et volume
    elif completion_rate < 30 and missing_count > 500:
        return "🟠 HAUTE"
    elif completion_rate < 70 and missing_count > 100:
        return "🟡 MOYENNE"
    else:
        return "🟢 FAIBLE"

def calculate_potential_gain(column_name: str, missing_count: int) -> int:
    """Estime le nombre d'enrichissements possibles"""
    column_lower = column_name.lower()
    
    # Taux de succès estimés selon le type de données
    if any(term in column_lower for term in ['site', 'web']):
        success_rate = 0.75  # 75% des entreprises ont un site trouvable
    elif 'effectif' in column_lower:
        success_rate = 0.60  # 60% des effectifs trouvables
    elif any(term in column_lower for term in ['dirigeant', 'nom']):
        success_rate = 0.50  # 50% des dirigeants trouvables
    else:
        success_rate = 0.40  # 40% pour autres données
    
    return int(missing_count * success_rate)

def generate_batch_recommendations(opportunities: Dict, total_companies: int) -> List[Dict]:
    """Génère des recommandations pour traitement par batch"""
    recommendations = []
    
    # Sites web
    web_cols = [col for col in opportunities.keys() if any(term in col.lower() for term in ['site', 'web'])]
    if web_cols:
        missing = sum(opportunities[col]["missing_count"] for col in web_cols)
        gain = sum(opportunities[col]["estimated_gain"] for col in web_cols)
        
        recommendations.append({
            "action": "🌐 Enrichissement sites web",
            "columns": web_cols,
            "companies_affected": missing,
            "estimated_success": gain,
            "priority": "🔥 CRITIQUE",
            "batch_approach": f"Traiter par batch de 50 entreprises",
            "estimated_time": f"{(missing * 2) // 60} minutes"
        })
    
    # Effectifs
    effectif_cols = [col for col in opportunities.keys() if 'effectif' in col.lower()]
    if effectif_cols:
        missing = sum(opportunities[col]["missing_count"] for col in effectif_cols)
        gain = sum(opportunities[col]["estimated_gain"] for col in effectif_cols)
        
        recommendations.append({
            "action": "👥 Mise à jour effectifs",
            "columns": effectif_cols,
            "companies_affected": missing,
            "estimated_success": gain,
            "priority": "🟠 HAUTE",
            "batch_approach": "Traiter en même temps que les sites web"
        })
    
    if not recommendations:
        recommendations.append({
            "action": "✅ Données bien remplies",
            "message": f"Peu d'opportunités d'enrichissement sur {total_companies} entreprises"
        })
    
    return recommendations

def get_top_priorities(opportunities: Dict) -> List[Dict]:
    """Retourne les 5 colonnes les plus prioritaires"""
    priority_order = {"🔥 CRITIQUE": 4, "🟠 HAUTE": 3, "🟡 MOYENNE": 2, "🟢 FAIBLE": 1}
    
    sorted_opportunities = sorted(
        opportunities.items(),
        key=lambda x: (
            priority_order.get(x[1]["priority"], 0),
            x[1]["missing_count"]
        ),
        reverse=True
    )
    
    return [
        {
            "column": col,
            "missing_count": data["missing_count"],
            "priority": data["priority"],
            "estimated_gain": data["estimated_gain"]
        }
        for col, data in sorted_opportunities[:5]
    ]

def get_sample_companies(df: pd.DataFrame, limit: int = 5) -> List[Dict]:
    """Retourne un échantillon d'entreprises"""
    # Colonnes clés à afficher
    key_columns = []
    for col in df.columns:
        if any(term in col.lower() for term in ['siret', 'nom', 'denomination', 'commune']):
            key_columns.append(col)
    
    if not key_columns:
        key_columns = df.columns[:5].tolist()
    
    sample = df[key_columns].head(limit)
    return sample.to_dict('records')
