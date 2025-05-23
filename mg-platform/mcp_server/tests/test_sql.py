import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json

# Ajouter le répertoire parent au sys.path pour pouvoir importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importer le module à tester
from tools.sql import run_sql

class TestSQLModule(unittest.TestCase):
    """Tests unitaires pour le module SQL."""

    @patch('tools.sql.engine')
    def test_run_sql_select_query(self, mock_engine):
        """Test avec une requête SELECT valide."""
        # Configuration du mock pour simuler le comportement de la base de données
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        
        # Simuler le résultat de la requête
        mock_result = [
            {"id": 1, "name": "Lagny"}, 
            {"id": 2, "name": "Thorigny"}
        ]
        mock_mappings = MagicMock()
        mock_mappings.all.return_value = mock_result
        mock_conn.execute.return_value.mappings.return_value = mock_mappings
        
        # Exécuter la fonction à tester
        query = "SELECT * FROM communes"
        result = run_sql(query)
        
        # Vérifier que la fonction a été appelée correctement
        mock_conn.execute.assert_called_once()
        
        # Vérifier le résultat
        self.assertIn("rows", result)
        self.assertEqual(len(result["rows"]), 2)
        self.assertEqual(result["rows"][0]["name"], "Lagny")
        self.assertEqual(result["rows"][1]["name"], "Thorigny")
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["row_count"], 2)
        self.assertEqual(result["metadata"]["query"], query)

    def test_run_sql_update_query(self):
        """Test avec une requête UPDATE (non autorisée)."""
        query = "UPDATE communes SET nom = 'X' WHERE id = 1"
        result = run_sql(query)
        
        # Vérifier que la requête a été rejetée
        self.assertIn("error", result)
        self.assertIn("non autorisée", result["error"])

    @patch('tools.sql.engine')
    def test_run_sql_error_handling(self, mock_engine):
        """Test de la gestion des erreurs."""
        # Configuration du mock pour simuler une erreur
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.side_effect = Exception("Erreur de base de données")
        
        # Exécuter la fonction à tester
        result = run_sql("SELECT * FROM table_inexistante")
        
        # Vérifier que l'erreur est gérée correctement
        self.assertIn("error", result)
        self.assertIn("Erreur de base de données", result["error"])

if __name__ == '__main__':
    unittest.main()
