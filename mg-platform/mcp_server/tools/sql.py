from sqlalchemy import create_engine, text
import os
from typing import Dict, List, Any
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer les informations de connexion à la base de données depuis les variables d'environnement
DB_USER = os.getenv("DB_USER", "mg")
DB_PASSWORD = os.getenv("DB_PASSWORD", "pwd")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics")

# Construire l'URL de connexion
db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Créer le moteur SQLAlchemy
engine = create_engine(db_url)

def run_sql(query: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Exécuter une requête SQL en lecture seule sur la base de données analytique.
    
    Args:
        query: La requête SQL à exécuter
        
    Returns:
        Un dictionnaire contenant une liste de lignes de résultats
    """
    # Sécurité : vérifier que la requête est en lecture seule
    query_lower = query.lower().strip()
    if any(keyword in query_lower for keyword in ["update ", "delete ", "insert ", "drop ", "alter ", "truncate "]):
        return {"error": "Requêtes de modification non autorisées"}
    
    try:
        with engine.begin() as conn:
            rows = conn.execute(text(query)).mappings().all()
        
        # Conversion des lignes en dictionnaires pour la sérialisation JSON
        result = {"rows": [dict(row) for row in rows]}
        
        # Ajouter des métadonnées sur la requête
        result["metadata"] = {
            "row_count": len(result["rows"]),
            "query": query
        }
        
        return result
        
    except Exception as e:
        return {"error": str(e)}
