import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ajouter le répertoire parent au path Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.main import app
from mcp_server.tools.basic import get_project_status, list_available_tools

client = TestClient(app)

def test_root_endpoint():
    """Test de l'endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["status"] == "running"

def test_health_check():
    """Test du health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "mg-data-mcp"

def test_project_status():
    """Test de l'outil get_project_status"""
    status = get_project_status()
    assert status["project_name"] == "Marne & Gondoire"
    assert "version" in status
    assert status["status"] == "en développement"

def test_list_tools():
    """Test de l'outil list_available_tools"""
    tools = list_available_tools()
    assert len(tools) > 0
    assert all("name" in tool for tool in tools)
    assert all("description" in tool for tool in tools)

def test_server_import():
    """Test que le serveur peut être importé sans erreur"""
    from mcp_server.main import app
    assert app is not None
    assert app.title == "MG Data MCP Server"
