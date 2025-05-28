#!/usr/bin/env python3
"""
Script de test alternatif pour contourner les problèmes de path sur Windows
"""
import sys
import os
import subprocess

# Ajouter le répertoire du projet au Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_tests():
    """Lance les tests avec la configuration appropriée"""
    # Définir la variable d'environnement PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = project_root
    
    # Lancer pytest avec le bon path
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    
    try:
        result = subprocess.run(cmd, env=env, cwd=project_root)
        return result.returncode
    except Exception as e:
        print(f"Erreur lors de l'exécution des tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
