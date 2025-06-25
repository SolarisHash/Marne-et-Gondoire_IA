#!/usr/bin/env python3
"""
Script de test pour vérifier que tous les imports fonctionnent
À exécuter depuis mg-platform/ : python test_imports_ai_agent.py
"""

import sys
import os
from pathlib import Path

# Ajouter le projet au Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test tous les imports de l'architecture modulaire"""
    
    print("🧪 Test des imports - Architecture modulaire Agent IA")
    print("=" * 60)
    
    tests = []
    
    # Test 1 : Point d'entrée principal
    try:
        from mcp_server.tools.ai_agent import run_ai_enrichment_agent
        tests.append(("✅", "Point d'entrée principal", "run_ai_enrichment_agent"))
    except ImportError as e:
        tests.append(("❌", "Point d'entrée principal", f"Erreur: {e}"))
    
    # Test 2 : Module core
    try:
        from mcp_server.tools.ai_agent.core import AIEnrichmentAgent, DEFAULT_CONFIG
        tests.append(("✅", "Core module", "AIEnrichmentAgent + config"))
    except ImportError as e:
        tests.append(("❌", "Core module", f"Erreur: {e}"))
    
    # Test 3 : Module data
    try:
        from mcp_server.tools.ai_agent.data import DataLoader
        tests.append(("✅", "Data module", "DataLoader"))
    except ImportError as e:
        tests.append(("❌", "Data module", f"Erreur: {e}"))
    
    # Test 4 : Module enrichment
    try:
        from mcp_server.tools.ai_agent.enrichment import EnrichmentStrategy, QualityValidator
        tests.append(("✅", "Enrichment module", "EnrichmentStrategy + QualityValidator"))
    except ImportError as e:
        tests.append(("❌", "Enrichment module", f"Erreur: {e}"))
    
    # Test 5 : Module search
    try:
        from mcp_server.tools.ai_agent.search import WebSearchEngine, IntelligentFallbackGenerator
        tests.append(("✅", "Search module", "WebSearchEngine + IntelligentFallbackGenerator"))
    except ImportError as e:
        tests.append(("❌", "Search module", f"Erreur: {e}"))
    
    # Test 6 : Module output
    try:
        from mcp_server.tools.ai_agent.output import ExcelWriter
        tests.append(("✅", "Output module", "ExcelWriter"))
    except ImportError as e:
        tests.append(("❌", "Output module", f"Erreur: {e}"))
    
    # Test 7 : Module utils
    try:
        from mcp_server.tools.ai_agent.utils import is_valid_business_website, setup_session_logging
        tests.append(("✅", "Utils module", "Validators + Logging"))
    except ImportError as e:
        tests.append(("❌", "Utils module", f"Erreur: {e}"))
    
    # Test 8 : Compatibilité legacy
    try:
        from mcp_server.tools.ai_agent import ai_agent_enrich
        tests.append(("✅", "Compatibilité legacy", "ai_agent_enrich alias"))
    except ImportError as e:
        tests.append(("❌", "Compatibilité legacy", f"Erreur: {e}"))
    
    # Afficher résultats
    print("\n📊 RÉSULTATS DES TESTS:")
    for status, module, detail in tests:
        print(f"{status} {module:<25} | {detail}")
    
    # Statistiques
    success_count = sum(1 for status, _, _ in tests if status == "✅")
    total_count = len(tests)
    
    print(f"\n🎯 BILAN: {success_count}/{total_count} tests réussis ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 TOUS LES IMPORTS FONCTIONNENT ! Architecture prête.")
        return True
    else:
        print("⚠️  Certains imports échouent. Vérifiez la structure des fichiers.")
        return False

def test_basic_functionality():
    """Test fonctionnel basique"""
    
    print("\n🔧 Test fonctionnel basique...")
    
    try:
        from mcp_server.tools.ai_agent.core import get_config, validate_config
        
        # Test configuration
        config = get_config()
        is_valid = validate_config(config)
        
        print(f"✅ Configuration: {len(config)} paramètres, validation: {is_valid}")
        
        # Test instanciation agent
        from mcp_server.tools.ai_agent.core import AIEnrichmentAgent
        agent = AIEnrichmentAgent()
        
        print(f"✅ Agent instancié: Session {agent.session_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur fonctionnelle: {e}")
        return False

def check_file_structure():
    """Vérifier la structure des fichiers"""
    
    print("\n📁 Vérification structure fichiers...")
    
    expected_files = [
        "mcp_server/tools/ai_agent/__init__.py",
        "mcp_server/tools/ai_agent/core/__init__.py",
        "mcp_server/tools/ai_agent/core/agent.py",
        "mcp_server/tools/ai_agent/core/config.py",
        "mcp_server/tools/ai_agent/core/exceptions.py",
        "mcp_server/tools/ai_agent/data/__init__.py",
        "mcp_server/tools/ai_agent/data/loader.py",
        "mcp_server/tools/ai_agent/enrichment/__init__.py",
        "mcp_server/tools/ai_agent/enrichment/strategies.py",
        "mcp_server/tools/ai_agent/enrichment/validation.py",
        "mcp_server/tools/ai_agent/search/__init__.py",
        "mcp_server/tools/ai_agent/search/web_search.py",
        "mcp_server/tools/ai_agent/search/fallback.py",
        "mcp_server/tools/ai_agent/output/__init__.py",
        "mcp_server/tools/ai_agent/output/excel_writer.py",
        "mcp_server/tools/ai_agent/utils/__init__.py",
        "mcp_server/tools/ai_agent/utils/validators.py",
        "mcp_server/tools/ai_agent/utils/logging.py"
    ]
    
    missing_files = []
    present_files = []
    
    for file_path in expected_files:
        full_path = project_root / file_path
        if full_path.exists():
            present_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    print(f"✅ Fichiers présents: {len(present_files)}/{len(expected_files)}")
    
    if missing_files:
        print("❌ Fichiers manquants:")
        for file in missing_files[:5]:  # Limiter l'affichage
            print(f"   • {file}")
        if len(missing_files) > 5:
            print(f"   • ... et {len(missing_files) - 5} autres")
    
    return len(missing_files) == 0

if __name__ == "__main__":
    print(f"📂 Répertoire de travail: {project_root}")
    
    # Tests
    structure_ok = check_file_structure()
    imports_ok = test_imports()
    
    if imports_ok:
        functionality_ok = test_basic_functionality()
        
        if structure_ok and imports_ok and functionality_ok:
            print("\n🎉 ARCHITECTURE COMPLÈTEMENT FONCTIONNELLE !")
            print("👉 Vous pouvez maintenant tester avec: python progress_client.py --sample_size 3")
        else:
            print("\n⚠️  Architecture partiellement fonctionnelle")
    else:
        print("\n❌ Architecture non fonctionnelle - corriger les imports d'abord")
    
    print("\n" + "=" * 60)