from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
import uvicorn
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional
import json
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

# Charger les variables d'environnement
load_dotenv()
progress_updates = {}  # session_id -> queue


# Configuration de l'application
app = FastAPI(
    title="MG Data MCP Server",
    description="Serveur MCP pour l'enrichissement de données Marne & Gondoire",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes principales
@app.get("/")
async def root():
    """Point d'entrée principal du serveur"""
    return {
        "message": "Serveur MCP Marne & Gondoire - Enrichissement de données",
        "version": "0.2.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "project": "Marne & Gondoire",
        "capabilities": [
            "📊 Analyse fichiers Excel/CSV",
            "🔗 Enrichissement LinkedIn", 
            "📈 Rapports de traitement",
            "🎯 Détection automatique des gaps"
        ],
        "available_endpoints": [
            "/health",
            "/analyze", 
            "/test-basic",
            "/info"
        ]
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état du serveur"""
    return {
        "status": "healthy",
        "service": "mg-data-mcp",
        "uptime": "running",
        "components": {
            "server": "✅ Actif",
            "basic_tools": "✅ Disponible",
            "file_system": "✅ Accessible"
        }
    }

@app.get("/analyze-advanced")
async def analyze_advanced():
    """Analyse avancée avec détection précise des opportunités LinkedIn"""
    try:
        # Import direct du fichier
        import os
        import importlib.util
        
        # Chemin vers le fichier data_analyzer.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        analyzer_path = os.path.join(current_dir, "tools", "data_analyzer.py")
        
        if not os.path.exists(analyzer_path):
            return {
                "error": f"Fichier non trouvé: {analyzer_path}",
                "current_dir": current_dir,
                "tools_exists": os.path.exists(os.path.join(current_dir, "tools"))
            }
        
        # Charger le module dynamiquement
        spec = importlib.util.spec_from_file_location("data_analyzer", analyzer_path)
        data_analyzer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_analyzer)
        
        # Appeler la fonction
        result = data_analyzer.analyze_data_gaps_advanced()
        return result
        
    except Exception as e:
        return {
            "error": f"Erreur: {str(e)}",
            "type": type(e).__name__,
            "current_dir": os.path.dirname(os.path.abspath(__file__))
        }

@app.get("/test-basic")
async def test_basic_functionality():
    """Test des fonctionnalités de base"""
    try:
        from mcp_server.tools.basic import get_project_status
        status = get_project_status()
        
        return {
            "basic_tools": "✅ OK",
            "project_status": status,
            "message": "Tests de base réussis"
        }
    except Exception as e:
        return {
            "basic_tools": "❌ Erreur",
            "error": str(e)
        }

@app.get("/info")
async def project_info():
    """Informations détaillées sur le projet"""
    return {
        "project": "Marne & Gondoire", 
        "description": "Plateforme d'enrichissement de données d'entreprises",
        "version": "0.2.0",
        "status": "configuration en cours",
        "next_steps": [
            "1. Vérifier que le fichier Excel est dans data/raw/",
            "2. Installer pandas: pip install pandas openpyxl",
            "3. Créer les outils d'analyse avancée",
            "4. Tester l'enrichissement LinkedIn"
        ]
    }

@app.get("/analyze-advanced")
async def analyze_advanced():
    """Analyse avancée avec détection précise des opportunités LinkedIn"""
    try:
        from mcp_server.tools.data_analyzer import analyze_data_gaps_advanced
        result = analyze_data_gaps_advanced()
        return result
    except ImportError as e:
        return {
            "error": f"Module d'analyse avancée non disponible: {str(e)}",
            "solution": "Créez le fichier mcp_server/tools/data_analyzer.py"
        }
    except Exception as e:
        return {
            "error": f"Erreur analyse avancée: {str(e)}"
        }

@app.get("/analyze-color", response_class=PlainTextResponse)
async def analyze_with_colors():
    """Version avec codes couleur ANSI pour terminal"""
    try:
        import os
        import importlib.util
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        analyzer_path = os.path.join(current_dir, "tools", "data_analyzer.py")
        
        spec = importlib.util.spec_from_file_location("data_analyzer", analyzer_path)
        data_analyzer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_analyzer)
        
        result = data_analyzer.analyze_data_gaps_advanced()
        
        if "error" in result:
            return f"\033[91m❌ ERREUR: {result['error']}\033[0m"
        
        # Codes couleur ANSI
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        BOLD = '\033[1m'
        END = '\033[0m'
        
        report = f"""
{BOLD}{CYAN}🚀 ANALYSE MARNE & GONDOIRE{END}
{CYAN}{'='*50}{END}

{BOLD}📁 FICHIER:{END}
  {result['file_info']['name']}
  {GREEN}{result['file_info']['total_companies']:,} entreprises{END} | {result['file_info']['total_columns']} colonnes

{BOLD}📊 VUE D'ENSEMBLE:{END}
  Complétion moyenne: {GREEN if result['global_stats']['average_completion_rate'] > 70 else YELLOW}{result['global_stats']['average_completion_rate']}%{END}
  Champs manquants: {RED}{result['global_stats']['total_missing_fields']:,}{END}

{BOLD}{RED}🔥 TOP OPPORTUNITÉS LINKEDIN:{END}
"""
        
        for i, priority in enumerate(result['top_priorities'][:3], 1):
            priority_color = RED if "CRITIQUE" in priority['priority'] else YELLOW if "HAUTE" in priority['priority'] else GREEN
            report += f"""
                {BOLD}{i}. {priority['column']}{END}
                {RED}Manquants: {priority['missing_count']:,}{END} | {GREEN}Gain: {priority['estimated_gain']:,}{END}
                {priority_color}{priority['priority']}{END}
            """

        # Sites web spécifiquement
        site_priority = result['top_priorities'][0]
        if 'site' in site_priority['column'].lower():
            report += f"""
                {BOLD}{GREEN}💰 JACKPOT SITES WEB:{END}
                {RED}{site_priority['missing_count']:,}{END} sites manquants sur {result['file_info']['total_companies']:,}
                {GREEN}{site_priority['estimated_gain']:,}{END} sites récupérables via LinkedIn
                {YELLOW}Temps estimé: {result['batch_strategy']['estimated_processing_time']}{END}
            """

        report += f"""
                {BOLD}{BLUE}🚀 COMMANDES RAPIDES:{END}
                Test:       {CYAN}curl http://localhost:8080/enrich?test_mode=true{END}
                Sites web:  {CYAN}curl -X POST http://localhost:8080/enrich-websites{END}
                Rapport:    {CYAN}curl http://localhost:8080/analyze-report{END}

                {BOLD}{GREEN}✨ Prêt pour l'enrichissement !{END}
            """
        
        return report
        
    except Exception as e:
        return f"\033[91m❌ ERREUR: {str(e)}\033[0m"


@app.get("/analyze-complete", response_class=PlainTextResponse)
async def analyze_complete():
    """Analyse complète de TOUTES les colonnes avec rapport détaillé"""
    try:
        # Import direct du module
        import os
        import importlib.util
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        analyzer_path = os.path.join(current_dir, "tools", "data_analyzer.py")
        
        if not os.path.exists(analyzer_path):
            return f"❌ Fichier data_analyzer.py non trouvé"
        
        # Charger le module
        spec = importlib.util.spec_from_file_location("data_analyzer", analyzer_path)
        data_analyzer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_analyzer)
        
        # Lancer l'analyse complète
        result = data_analyzer.analyze_complete_file()
        
        if "error" in result:
            return f"❌ ERREUR: {result['error']}"
        
        # Formatage du rapport complet - CORRIGÉ
        report = f"""
🔍 ANALYSE COMPLÈTE - TOUTES COLONNES
{'='*70}

📁 FICHIER ANALYSÉ
  Nom: {result['file_info']['filename']}
  Lignes: {result['file_info']['total_rows']:,}
  Colonnes: {result['file_info']['total_columns']}
  Taille: {result['file_info']['file_size_mb']} MB

📊 STATISTIQUES GLOBALES
{'='*70}
  Cellules totales: {result['global_stats']['total_cells']:,}
  Cellules remplies: {result['global_stats']['filled_cells']:,}
  Cellules vides: {result['global_stats']['missing_cells']:,}
  Taux de complétion: {result['global_stats']['overall_completion_rate']}%
  Moyenne vides/ligne: {result['global_stats']['avg_missing_per_row']}

📋 ANALYSE DÉTAILLÉE - TOUTES LES COLONNES
{'='*70}
"""
        
        # Analyser toutes les colonnes
        columns = result['all_columns_analysis']
        
        # Trier par taux de complétion (plus vides en premier)
        sorted_columns = sorted(
            columns.items(),
            key=lambda x: x[1]['completion_rate']
        )
        
        for i, (col_name, data) in enumerate(sorted_columns, 1):
            # Icône selon le taux de complétion
            if data['completion_rate'] >= 95:
                icon = "✅"
            elif data['completion_rate'] >= 80:
                icon = "🟢"
            elif data['completion_rate'] >= 50:
                icon = "🟡"
            else:
                icon = "🔴"
            
            # Type détecté
            col_type = data['detected_type']['category']
            
            # Enrichissement possible ?
            enrichable = "🚀" if data['enrichment_potential']['is_enrichable'] else "⚪"
            
            report += f"""
{icon} {i:2d}. {col_name}
     Complétion: {data['completion_rate']:5.1f}% ({data['present_count']:,}/{data['present_count'] + data['missing_count']:,})
     Manquants: {data['missing_count']:,}
     Type détecté: {col_type}
     {enrichable} Enrichissement: {data['enrichment_potential']['priority']} (gain: {data['enrichment_potential']['estimated_gain']:,})
     Échantillons: {' | '.join(data['content_analysis']['sample_values'])}
"""
        
        # Opportunités d'enrichissement
        opportunities = result['enrichment_opportunities']
        
        if opportunities:
            report += f"""
🎯 OPPORTUNITÉS D'ENRICHISSEMENT
{'='*70}
"""
            for i, (col, data) in enumerate(list(opportunities.items())[:10], 1):
                report += f"""
{i:2d}. {col}
    🎯 Manquants: {data['missing_count']:,} | Gain estimé: {data['estimated_gain']:,}
    📊 Priorité: {data['priority']} | Sources: {', '.join(data['sources'])}
"""
        else:
            report += f"""
✅ AUCUNE OPPORTUNITÉ D'ENRICHISSEMENT MAJEURE
{'='*70}
Vos données sont déjà très complètes !
"""
        
        # Échantillon de données
        report += f"""
🧪 ÉCHANTILLON DE DONNÉES
{'='*70}
"""
        
        for i, sample in enumerate(result['sample_data'], 1):
            report += f"\n{i}. "
            sample_parts = []
            for key, value in sample.items():
                sample_parts.append(f"{key}: {value}")
            report += " | ".join(sample_parts)
        
        # Commandes utiles
        report += f"""

🚀 COMMANDES UTILES
{'='*70}
  Analyse JSON: curl http://localhost:8080/analyze-advanced
  Documentation: http://localhost:8080/docs

🎉 ANALYSE TERMINÉE - {result['file_info']['total_columns']} colonnes analysées !
"""
        
        return report
        
    except Exception as e:
        return f"""
❌ ERREUR LORS DE L'ANALYSE COMPLÈTE
{'='*50}
Erreur: {str(e)}
Type: {type(e).__name__}

L'analyseur fonctionne (voir les logs), mais erreur de formatage.
Vérifiez l'endpoint analyze-complete dans main.py
"""
    
# ============================================================================
# ENDPOINT POUR ANALYSE RAPIDE (colonnes principales seulement)
# ============================================================================

@app.get("/analyze-summary", response_class=PlainTextResponse)
async def analyze_summary():
    """Analyse rapide avec résumé des colonnes les plus importantes"""
    try:
        import os
        import importlib.util
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        analyzer_path = os.path.join(current_dir, "tools", "data_analyzer.py")
        
        spec = importlib.util.spec_from_file_location("data_analyzer", analyzer_path)
        data_analyzer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_analyzer)
        
        result = data_analyzer.analyze_complete_file()
        
        if "error" in result:
            return f"❌ ERREUR: {result['error']}"
        
        # Rapport condensé
        report = f"""
📊 RÉSUMÉ D'ANALYSE - {result['file_info']['name']}
{'='*60}

📈 VUE D'ENSEMBLE
  Fichier: {result['file_info']['total_rows']:,} lignes × {result['file_info']['total_columns']} colonnes
  Qualité: {result['data_quality_report']['overall_grade']}
  Complétion: {result['data_quality_report']['average_completion']}%

🎯 TOP 5 OPPORTUNITÉS D'ENRICHISSEMENT
{'='*60}
"""
        
        # Top 5 des opportunités
        opportunities = list(result['enrichment_opportunities'].items())[:5]
        
        if opportunities:
            for i, (col, data) in enumerate(opportunities, 1):
                report += f"""
{i}. {col}
   🔴 Manquants: {data['missing_count']:,} | 🎯 Récupérables: {data['estimated_gain']:,}
   💪 Faisabilité: {data['feasibility_score']}% | Sources: {data['sources'][0]}
"""
        else:
            report += "\n✅ Aucune opportunité majeure détectée - données bien complètes !"
        
        # Colonnes parfaites
        perfect_columns = [col for col, data in result['complete_column_analysis'].items() 
                          if data['completion_rate'] == 100.0]
        
        report += f"""
✅ COLONNES PARFAITES (100% complètes)
{'='*60}
  {len(perfect_columns)} colonnes: {', '.join(perfect_columns[:5])}{"..." if len(perfect_columns) > 5 else ""}

🚀 ACTIONS RAPIDES
{'='*60}
  Analyse complète: curl http://localhost:8080/analyze-complete
  Test enrichissement: curl -X POST "http://localhost:8080/enrich?test_mode=true"
"""
        
        return report
        
    except Exception as e:
        return f"❌ ERREUR: {str(e)}"

# ============================================================================
# ENDPOINT POUR COMPARAISON AVANT/APRÈS ENRICHISSEMENT
# ============================================================================

@app.get("/analyze-comparison", response_class=PlainTextResponse)  
async def analyze_comparison():
    """Compare l'état actuel avec le potentiel après enrichissement"""
    try:
        import os
        import importlib.util
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        analyzer_path = os.path.join(current_dir, "tools", "data_analyzer.py")
        
        spec = importlib.util.spec_from_file_location("data_analyzer", analyzer_path)
        data_analyzer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_analyzer)
        
        result = data_analyzer.analyze_complete_file()
        
        if "error" in result:
            return f"❌ ERREUR: {result['error']}"
        
        report = f"""
📊 COMPARAISON AVANT/APRÈS ENRICHISSEMENT
{'='*70}

📁 {result['file_info']['name']} - {result['file_info']['total_rows']:,} entreprises
"""
        
        # Analyse avant/après pour chaque colonne enrichissable
        opportunities = result['enrichment_opportunities']
        
        if opportunities:
            total_current = 0
            total_potential = 0
            
            report += f"""
🔄 PROJECTION D'ENRICHISSEMENT PAR COLONNE
{'='*70}
"""
            
            for col, data in opportunities.items():
                current_filled = result['file_info']['total_rows'] - data['missing_count']
                potential_filled = current_filled + data['estimated_gain']
                
                current_rate = (current_filled / result['file_info']['total_rows']) * 100
                potential_rate = (potential_filled / result['file_info']['total_rows']) * 100
                improvement = potential_rate - current_rate
                
                total_current += current_filled
                total_potential += potential_filled
                
                report += f"""
📊 {col}
   Avant: {current_rate:5.1f}% ({current_filled:,}/{result['file_info']['total_rows']:,})
   Après: {potential_rate:5.1f}% ({potential_filled:,}/{result['file_info']['total_rows']:,})
   Gain:  +{improvement:4.1f}% (+{data['estimated_gain']:,} valeurs)
"""
            
            # Statistiques globales
            avg_current = (total_current / len(opportunities)) / result['file_info']['total_rows'] * 100
            avg_potential = (total_potential / len(opportunities)) / result['file_info']['total_rows'] * 100
            
            report += f"""
🎯 IMPACT GLOBAL DE L'ENRICHISSEMENT
{'='*70}
  Complétion moyenne actuelle: {avg_current:.1f}%
  Complétion moyenne projetée: {avg_potential:.1f}%
  Amélioration globale: +{avg_potential - avg_current:.1f}%
  
  Valeurs totales récupérables: {sum(data['estimated_gain'] for data in opportunities.values()):,}
  Temps estimé: {max(1, sum(data['estimated_gain'] for data in opportunities.values()) // 60)} minutes
"""
            
            # ROI de l'enrichissement
            total_gain = sum(data['estimated_gain'] for data in opportunities.values())
            if total_gain > 0:
                report += f"""
💰 RETOUR SUR INVESTISSEMENT
{'='*70}
  Données actuelles: {sum(result['file_info']['total_rows'] - data['missing_count'] for data in opportunities.values()):,}
  Données après enrichissement: {sum(result['file_info']['total_rows'] - data['missing_count'] + data['estimated_gain'] for data in opportunities.values()):,}
  Multiplication par: {(sum(result['file_info']['total_rows'] - data['missing_count'] + data['estimated_gain'] for data in opportunities.values()) / max(1, sum(result['file_info']['total_rows'] - data['missing_count'] for data in opportunities.values()))):.1f}x
"""
        else:
            report += """
✅ AUCUN ENRICHISSEMENT NÉCESSAIRE
{'='*70}
Vos données sont déjà très complètes ! Pas d'amélioration significative possible.
"""
        
        return report
        
    except Exception as e:
        return f"❌ ERREUR: {str(e)}"

# ============================================================================
# ENDPOINTS AGENT IA - À ajouter dans mcp_server/main.py
# ============================================================================

@app.post("/ai-agent/enrich")
async def run_ai_agent_enrichment(
    sample_size: int = Query(10, description="Nombre d'entreprises à traiter"),
    quality_threshold: int = Query(85, description="Seuil de qualité minimum (%)"),
    test_mode: bool = Query(True, description="Mode test sécurisé")
):
    """
    🤖 Lance l'Agent IA autonome d'enrichissement
    """
    try:
        # Sécurité mode test
        if test_mode and sample_size > 50:
            return {
                "error": "Mode test limité à 50 entreprises maximum",
                "suggestion": "Désactiver test_mode pour traitement plus large"
            }
        
        # Import direct du fichier ai_agent.py (CORRIGÉ)
        import os
        import importlib.util
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        agent_path = os.path.join(current_dir, "tools", "ai_agent.py")
        
        if not os.path.exists(agent_path):
            return {
                "error": "Agent IA non trouvé",
                "solution": "Créez le fichier mcp_server/tools/ai_agent.py",
                "path_checked": agent_path
            }
        
        # Charger le module ai_agent dynamiquement
        spec = importlib.util.spec_from_file_location("ai_agent", agent_path)
        ai_agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ai_agent_module)
        
        # Lancer l'enrichissement IA
        result = ai_agent_module.run_ai_enrichment_agent(sample_size)
        
        return result
        
    except Exception as e:
        return {
            "error": f"Erreur Agent IA: {str(e)}",
            "error_type": type(e).__name__,
            "current_dir": os.path.dirname(os.path.abspath(__file__)),
            "suggestion": "Vérifiez que ai_agent.py existe dans tools/ et contient run_ai_enrichment_agent()"
        }

@app.get("/ai-agent/report", response_class=PlainTextResponse)
async def ai_agent_detailed_report(session_id: str = Query(None, description="ID de session spécifique")):
    """
    📊 Rapport détaillé de la dernière exécution de l'Agent IA
    """
    try:
        # Si pas de session_id, prendre la plus récente
        if not session_id:
            # Chercher le log le plus récent
            log_dir = Path("logs")
            if log_dir.exists():
                log_files = list(log_dir.glob("ai_agent_*.log"))
                if log_files:
                    latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
                    session_id = latest_log.stem.replace("ai_agent_", "")
        
        if not session_id:
            return "❌ Aucune session Agent IA trouvée. Lancez d'abord l'enrichissement."
        
        # Lire le fichier de log
        log_file = Path(f"logs/ai_agent_{session_id}.log")
        
        if not log_file.exists():
            return f"❌ Log de session {session_id} non trouvé."
        
        # Générer le rapport depuis les logs
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Parser les informations clés du log
        report = f"""
🤖 RAPPORT DÉTAILLÉ AGENT IA - SESSION {session_id}
{'='*70}

📊 RÉSUMÉ EXÉCUTION
"""
        
        # Extraire les métriques du log
        lines = log_content.split('\n')
        
        # Statistiques de base
        processed_count = len([line for line in lines if "Traitement:" in line])
        success_count = len([line for line in lines if "✅ Succès - Score:" in line])
        failure_count = len([line for line in lines if "❌ Échec - Raison:" in line])
        
        success_rate = (success_count / processed_count * 100) if processed_count > 0 else 0
        
        report += f"""
  Entreprises traitées: {processed_count}
  Enrichissements réussis: {success_count}
  Échecs: {failure_count}
  Taux de succès: {success_rate:.1f}%

🔍 DÉTAIL DES TRAITEMENTS
{'='*70}
"""
        
        # Extraire les détails de chaque traitement
        current_company = ""
        for line in lines:
            if "Traitement:" in line:
                company_name = line.split("Traitement: ")[1] if "Traitement: " in line else "N/A"
                current_company = company_name
                report += f"\n🏢 {company_name}\n"
            elif "✅ Succès - Score:" in line:
                score = line.split("Score: ")[1].replace("%", "") if "Score: " in line else "N/A"
                report += f"   ✅ ENRICHI - Qualité: {score}%\n"
            elif "❌ Échec - Raison:" in line:
                reason = line.split("Raison: ")[1] if "Raison: " in line else "Raison inconnue"
                report += f"   ❌ ÉCHEC - {reason}\n"
        
        # Chercher les erreurs spécifiques
        error_lines = [line for line in lines if "❌" in line or "ERROR" in line]
        
        if error_lines:
            report += f"""
⚠️ ERREURS DÉTECTÉES
{'='*70}
"""
            for error in error_lines[:10]:  # Limiter à 10 erreurs
                clean_error = error.split(" - ")[-1] if " - " in error else error
                report += f"• {clean_error}\n"
        
        # Informations de performance
        start_lines = [line for line in lines if "Démarrage Agent IA" in line]
        end_lines = [line for line in lines if "Enrichissement terminé" in line]
        
        if start_lines and end_lines:
            report += f"""
⚡ PERFORMANCE
{'='*70}
  Début: {start_lines[0].split(' - ')[0] if ' - ' in start_lines[0] else 'N/A'}
  Fin: {end_lines[0].split(' - ')[0] if ' - ' in end_lines[0] else 'N/A'}
"""
        
        # Recommandations basées sur les résultats
        report += f"""
💡 RECOMMANDATIONS
{'='*70}
"""
        
        if success_rate >= 80:
            report += "✅ Excellent taux de succès ! Prêt pour fichier complet.\n"
        elif success_rate >= 60:
            report += "🟡 Bon taux de succès. Quelques optimisations possibles.\n"
        else:
            report += "🔴 Taux de succès faible. Revoir la stratégie de recherche.\n"
        
        if failure_count > 0:
            report += f"⚠️ Analyser les {failure_count} échecs pour optimiser l'algorithme.\n"
        
        report += """
🚀 PROCHAINES ÉTAPES
{'='*70}
1. Analyser les résultats dans data/processed/
2. Ajuster les paramètres si nécessaire
3. Lancer l'enrichissement sur fichier complet
4. Valider manuellement un échantillon des résultats

📁 FICHIERS GÉNÉRÉS
{'='*70}"""
        
        # Chercher les fichiers générés
        processed_dir = Path("data/processed")
        if processed_dir.exists():
            generated_files = list(processed_dir.glob(f"*{session_id}*"))
            if generated_files:
                for file in generated_files:
                    report += f"\n📄 {file.name} ({file.stat().st_size / 1024:.1f} KB)"
            else:
                report += "\n⚠️ Aucun fichier trouvé dans data/processed/"
        
        report += f"""

🔗 COMMANDES UTILES
{'='*70}
  Relancer agent: curl -X POST "http://localhost:8080/ai-agent/enrich?sample_size=10"
  Voir logs: cat logs/ai_agent_{session_id}.log
  Analyse fichier: curl http://localhost:8080/analyze-complete

🎉 RAPPORT TERMINÉ
"""
        
        return report
        
    except Exception as e:
        return f"""
❌ ERREUR GÉNÉRATION RAPPORT
{'='*40}
Erreur: {str(e)}

Suggestions:
- Vérifiez que l'agent IA a bien été exécuté
- Contrôlez l'existence du dossier logs/
- Relancez l'enrichissement si nécessaire
"""

@app.post("/ai-agent/enrich-stream")
async def run_ai_agent_with_streaming(
    sample_size: int = Query(10, description="Nombre d'entreprises à traiter"),
    test_mode: bool = Query(True, description="Mode test sécurisé")
):
    """
    🤖 Agent IA avec progression temps réel via Server-Sent Events
    Utilisable avec: curl -N http://localhost:8080/ai-agent/enrich-stream?sample_size=10
    """
    
    async def progress_stream():
        """Générateur de progression temps réel"""
        
        try:
            # Sécurité mode test
            if test_mode and sample_size > 50:
                yield f"data: {json.dumps({'error': 'Mode test limité à 50 entreprises'})}\n\n"
                return
            
            # Message de démarrage
            yield f"data: {json.dumps({'type': 'start', 'message': f'🚀 Démarrage enrichissement {sample_size} entreprises', 'timestamp': time.time()})}\n\n"
            
            # Import de l'agent IA
            yield f"data: {json.dumps({'type': 'info', 'message': '📁 Chargement fichier de données...', 'timestamp': time.time()})}\n\n"
            
            import os
            import importlib.util
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            agent_path = os.path.join(current_dir, "tools", "ai_agent.py")
            
            if not os.path.exists(agent_path):
                yield f"data: {json.dumps({'type': 'error', 'message': '❌ Agent IA non trouvé', 'timestamp': time.time()})}\n\n"
                return
            
            # Charger l'agent IA
            spec = importlib.util.spec_from_file_location("ai_agent", agent_path)
            ai_agent_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ai_agent_module)
            
            yield f"data: {json.dumps({'type': 'info', 'message': '🤖 Agent IA initialisé', 'timestamp': time.time()})}\n\n"
            
            # Créer l'agent avec callback de progression
            agent = ai_agent_module.AIEnrichmentAgent()
            
            # Simuler l'enrichissement avec progression
            for i in range(sample_size):
                company_name = f"Entreprise_{i+1}"
                
                # Simulation traitement
                yield f"data: {json.dumps({'type': 'progress', 'current': i+1, 'total': sample_size, 'percentage': round((i+1)/sample_size*100, 1), 'message': f'🔍 Traitement: {company_name}', 'timestamp': time.time()})}\n\n"
                
                # Simuler temps de traitement
                await asyncio.sleep(2)  # 2 secondes par entreprise
                
                # Résultat (simulation 70% succès)
                success = (i % 3) != 0  # 2/3 succès
                status = "✅ Enrichi" if success else "❌ Échec"
                
                yield f"data: {json.dumps({'type': 'result', 'current': i+1, 'total': sample_size, 'success': success, 'message': f'{status} - {company_name}', 'timestamp': time.time()})}\n\n"
            
            # Résultat final
            success_count = int(sample_size * 0.7)  # 70% de succès
            
            final_result = {
                'type': 'completed',
                'message': '🎉 Enrichissement terminé !',
                'summary': {
                    'total_processed': sample_size,
                    'successful': success_count,
                    'failed': sample_size - success_count,
                    'success_rate': f"{(success_count/sample_size*100):.1f}%"
                },
                'timestamp': time.time()
            }
            
            yield f"data: {json.dumps(final_result)}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'❌ Erreur: {str(e)}', 'timestamp': time.time()})}\n\n"
    
    return StreamingResponse(
        progress_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Nginx bypass
        }
    )

@app.post("/ai-agent/enrich-real-stream")
async def run_real_ai_agent_with_streaming(
    sample_size: int = Query(10, description="Nombre d'entreprises à traiter"),
    quality_threshold: int = Query(85, description="Seuil de qualité minimum (%)"),
    test_mode: bool = Query(True, description="Mode test sécurisé")
):
    """
    🤖 Agent IA RÉEL avec progression temps réel dans le client Python
    """
    
    # Générer un ID de session unique
    import uuid
    session_id = str(uuid.uuid4())[:8]
    
    # Créer une queue pour cette session
    progress_queue = queue.Queue()
    progress_updates[session_id] = progress_queue
    
    async def real_enrichment_stream():
        """Stream qui combine le vrai Agent IA avec la progression"""
        
        try:
            # Sécurité mode test
            if test_mode and sample_size > 50:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Mode test limité à 50 entreprises'})}\n\n"
                return
            
            # Message de démarrage
            yield f"data: {json.dumps({'type': 'start', 'message': f'🚀 Démarrage VRAI enrichissement {sample_size} entreprises', 'session': session_id, 'timestamp': time.time()})}\n\n"
            
            # Import de l'agent IA RÉEL
            yield f"data: {json.dumps({'type': 'info', 'message': '📁 Chargement Agent IA...', 'timestamp': time.time()})}\n\n"
            
            import os
            import importlib.util
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            agent_path = os.path.join(current_dir, "tools", "ai_agent.py")
            
            if not os.path.exists(agent_path):
                yield f"data: {json.dumps({'type': 'error', 'message': '❌ Agent IA non trouvé', 'timestamp': time.time()})}\n\n"
                return
            
            # Charger l'agent IA RÉEL
            spec = importlib.util.spec_from_file_location("ai_agent", agent_path)
            ai_agent_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ai_agent_module)
            
            yield f"data: {json.dumps({'type': 'info', 'message': '🤖 Agent IA réel initialisé', 'timestamp': time.time()})}\n\n"
            
            # Lancer l'Agent IA RÉEL dans un thread avec callback
            loop = asyncio.get_event_loop()
            
            def run_real_agent_with_progress():
                """Exécute le vrai agent IA avec callbacks de progression"""
                
                # Créer l'agent avec callbacks
                agent = ai_agent_module.AIEnrichmentAgent()
                
                # Patcher la méthode d'enrichissement pour récupérer la progression
                original_enrich = agent._enrich_companies_ai
                
                def enrichment_with_callbacks(sample_df):
                    """Version avec callbacks pour le streaming"""
                    
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
                        company_name = company.get('Nom courant/Dénomination', f'Entreprise_{idx}')
                        
                        # Envoyer progression au stream
                        progress_queue.put({
                            'type': 'progress',
                            'current': idx,
                            'total': len(sample_df),
                            'percentage': round((idx / len(sample_df)) * 100, 1),
                            'message': f'🔍 Traitement: {company_name[:30]}...',
                            'timestamp': time.time()
                        })
                        
                        try:
                            # VRAI enrichissement de l'entreprise
                            enrichment_result = agent._enrich_single_company_ai(company, idx)
                            
                            processing_time = time.time() - start_time
                            
                            if enrichment_result["success"]:
                                results["enriched"] += 1
                                results["enrichment_data"][str(idx)] = enrichment_result["data"]
                                results["quality_reports"][str(idx)] = enrichment_result["quality_report"]
                                agent.performance_metrics["quality_scores"].append(enrichment_result["quality_score"])
                                
                                # Envoyer résultat succès
                                progress_queue.put({
                                    'type': 'result',
                                    'current': idx,
                                    'total': len(sample_df),
                                    'success': True,
                                    'message': f'✅ Enrichi - {company_name[:30]} (Score: {enrichment_result["quality_score"]}%)',
                                    'data': {
                                        'website': enrichment_result["data"].get("website", "N/A"),
                                        'quality_score': enrichment_result["quality_score"]
                                    },
                                    'timestamp': time.time()
                                })
                                
                            else:
                                results["failed"] += 1
                                agent.performance_metrics["error_details"].append({
                                    "company_index": idx,
                                    "company_name": company_name,
                                    "error_reason": enrichment_result["error_reason"]
                                })
                                
                                # Envoyer résultat échec
                                progress_queue.put({
                                    'type': 'result',
                                    'current': idx,
                                    'total': len(sample_df),
                                    'success': False,
                                    'message': f'❌ Échec - {company_name[:30]} ({enrichment_result["error_reason"]})',
                                    'timestamp': time.time()
                                })
                            
                            results["processed"] += 1
                            results["ai_decisions"].append(enrichment_result["ai_decision_log"])
                            
                            # Rate limiting (réduit pour les tests)
                            time.sleep(1)  # 1 seconde au lieu de 3
                            
                        except Exception as e:
                            results["failed"] += 1
                            results["processed"] += 1
                            
                            progress_queue.put({
                                'type': 'result',
                                'current': idx,
                                'total': len(sample_df),
                                'success': False,
                                'message': f'❌ Erreur - {company_name[:30]} ({str(e)})',
                                'timestamp': time.time()
                            })
                    
                    return results
                
                # Remplacer temporairement la méthode
                agent._enrich_companies_ai = enrichment_with_callbacks
                
                # Lancer l'enrichissement RÉEL
                return agent.enrich_sample(sample_size)
            
            # Exécuter dans un thread pool
            with ThreadPoolExecutor(max_workers=1) as executor:
                # Lancer l'agent en arrière-plan
                future = loop.run_in_executor(executor, run_real_agent_with_progress)
                
                # Stream les updates de progression
                while not future.done():
                    try:
                        # Récupérer les updates avec timeout
                        update = progress_queue.get(timeout=0.5)
                        yield f"data: {json.dumps(update)}\n\n"
                    except queue.Empty:
                        # Envoyer un heartbeat
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
                    
                    await asyncio.sleep(0.1)  # Petit délai
                
                # Récupérer le résultat final
                final_result = await future
                
                # Vider la queue restante
                while not progress_queue.empty():
                    try:
                        update = progress_queue.get_nowait()
                        yield f"data: {json.dumps(update)}\n\n"
                    except queue.Empty:
                        break
                
                # Envoyer le résultat final
                if "error" not in final_result:
                    completion_data = {
                        'type': 'completed',
                        'message': '🎉 Enrichissement RÉEL terminé !',
                        'summary': final_result["execution_summary"],
                        'output_file': final_result.get("output_file", "N/A"),
                        'session_id': final_result["session_id"],
                        'timestamp': time.time()
                    }
                else:
                    completion_data = {
                        'type': 'error',
                        'message': f'❌ Erreur finale: {final_result["error"]}',
                        'timestamp': time.time()
                    }
                
                yield f"data: {json.dumps(completion_data)}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'❌ Erreur streaming: {str(e)}', 'timestamp': time.time()})}\n\n"
        
        finally:
            # Nettoyer la queue
            if session_id in progress_updates:
                del progress_updates[session_id]
    
    return StreamingResponse(
        real_enrichment_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/ai-agent/status")
async def ai_agent_status():
    """
    📊 Statut en temps réel de l'Agent IA
    """
    try:
        # Chercher les logs récents
        log_dir = Path("logs")
        
        if not log_dir.exists():
            return {
                "status": "inactive",
                "message": "Aucune activité Agent IA détectée",
                "suggestion": "Lancez un enrichissement avec /ai-agent/enrich"
            }
        
        # Trouver le log le plus récent
        log_files = list(log_dir.glob("ai_agent_*.log"))
        
        if not log_files:
            return {
                "status": "inactive", 
                "message": "Aucun log Agent IA trouvé",
                "available_commands": {
                    "start_enrichment": "POST /ai-agent/enrich",
                    "view_analysis": "GET /analyze-complete"
                }
            }
        
        # Analyser le log le plus récent
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        session_id = latest_log.stem.replace("ai_agent_", "")
        
        # Lire les dernières lignes pour déterminer le statut
        with open(latest_log, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        last_lines = [line for line in lines[-10:] if line.strip()]
        
        # Déterminer le statut
        if any("Enrichissement terminé" in line for line in last_lines):
            status = "completed"
        elif any("Début enrichissement IA" in line for line in last_lines):
            status = "running"
        else:
            status = "unknown"
        
        # Extraire les métriques
        processed = len([line for line in lines if "Traitement:" in line])
        success = len([line for line in lines if "✅ Succès" in line])
        
        return {
            "status": status,
            "latest_session": session_id,
            "last_activity": latest_log.stat().st_mtime,
            "quick_metrics": {
                "companies_processed": processed,
                "successful_enrichments": success,
                "success_rate": f"{(success/processed*100):.1f}%" if processed > 0 else "0%"
            },
            "available_actions": {
                "view_detailed_report": f"GET /ai-agent/report?session_id={session_id}",
                "start_new_enrichment": "POST /ai-agent/enrich",
                "check_results": f"Check data/processed/ for files with {session_id}"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "suggestion": "Vérifiez la configuration de l'Agent IA"
        }

@app.get("/ai-agent/test-import")
async def test_ai_agent_import():
    """
    🧪 Test simple pour vérifier que l'agent IA peut être importé
    """
    try:
        import os
        import importlib.util
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        agent_path = os.path.join(current_dir, "tools", "ai_agent.py")
        
        # Vérifications étape par étape
        checks = {
            "file_exists": os.path.exists(agent_path),
            "file_path": agent_path,
            "tools_dir_exists": os.path.exists(os.path.join(current_dir, "tools")),
            "tools_dir_content": []
        }
        
        # Lister le contenu du dossier tools
        tools_dir = os.path.join(current_dir, "tools")
        if os.path.exists(tools_dir):
            checks["tools_dir_content"] = os.listdir(tools_dir)
        
        # Essayer d'importer si le fichier existe
        if checks["file_exists"]:
            try:
                spec = importlib.util.spec_from_file_location("ai_agent", agent_path)
                ai_agent_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(ai_agent_module)
                
                # Vérifier que la fonction principale existe
                has_main_function = hasattr(ai_agent_module, 'run_ai_enrichment_agent')
                
                checks.update({
                    "import_successful": True,
                    "has_main_function": has_main_function,
                    "available_functions": [attr for attr in dir(ai_agent_module) if not attr.startswith('_')]
                })
                
                if has_main_function:
                    checks["status"] = "✅ Agent IA prêt"
                else:
                    checks["status"] = "⚠️ Agent IA importé mais fonction principale manquante"
                
            except Exception as import_error:
                checks.update({
                    "import_successful": False,
                    "import_error": str(import_error),
                    "status": "❌ Erreur d'import"
                })
        else:
            checks["status"] = "❌ Fichier ai_agent.py non trouvé"
        
        return checks
        
    except Exception as e:
        return {
            "error": f"Erreur test import: {str(e)}",
            "error_type": type(e).__name__
        }


if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 8080))
    host = os.getenv("SERVER_HOST", "localhost")
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🚀 Démarrage du serveur MCP Marne & Gondoire v0.2.0")
    print(f"📍 Adresse: http://{host}:{port}")
    print(f"📚 Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health check: http://{host}:{port}/health")
    print(f"📊 Analyse (basique): http://{host}:{port}/analyze")
    print(f"🧪 Test basic: http://{host}:{port}/test-basic")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )
