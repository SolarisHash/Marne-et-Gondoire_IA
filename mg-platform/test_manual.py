#!/usr/bin/env python3
"""
Test manuel simple pour vérifier le fonctionnement de base
"""
import sys
import os

# Ajouter le projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test des imports de base"""
    try:
        from mcp_server.main import app
        print("✅ Import de mcp_server.main: OK")
        
        from mcp_server.tools.basic import get_project_status
        print("✅ Import de mcp_server.tools.basic: OK")
        
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_basic_functionality():
    """Test de fonctionnalité de base"""
    try:
        from mcp_server.tools.basic import get_project_status
        status = get_project_status()
        assert status["project_name"] == "Marne & Gondoire"
        print("✅ Test get_project_status: OK")
        
        from fastapi.testclient import TestClient
        from mcp_server.main import app
        client = TestClient(app)
        
        response = client.get("/")
        assert response.status_code == 200
        print("✅ Test endpoint racine: OK")
        
        response = client.get("/health")
        assert response.status_code == 200
        print("✅ Test health check: OK")
        
        return True
    except Exception as e:
        print(f"❌ Erreur de test: {e}")
        return False

if __name__ == "__main__":
    print(" Tests manuels du serveur MCP Marne & Gondoire")
    print("=" * 50)
    
    if test_imports() and test_basic_functionality():
        print("\n��� Tous les tests sont passés !")
        print("Vous pouvez maintenant lancer le serveur avec:")
        print("python mcp_server/main.py")
    else:
        print("\n❌ Certains tests ont échoué.")
        sys.exit(1)
