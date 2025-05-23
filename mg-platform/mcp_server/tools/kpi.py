import pandas as pd
import numpy as np
import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Union, List
import logging

# Import conditionnel pour Prophet pour gérer les cas où il n'est pas installé
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

# Import conditionnel pour PyTorch Forecasting et notre classe TFTForecaster
try:
    import torch
    from pytorch_forecasting.models import TemporalFusionTransformer
    
    # Add models directory to path for TFTForecaster
    models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))
    if models_path not in sys.path:
        sys.path.append(models_path)
        
    from tft_forecaster import TFTForecaster
    TFT_AVAILABLE = True
except ImportError:
    TFT_AVAILABLE = False

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("kpi.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Chemin vers les modèles
MODELS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

def load_prophet(kpi_name: str):
    """
    Charge un modèle Prophet pour un KPI spécifique.
    
    Args:
        kpi_name: Le nom du KPI pour lequel charger le modèle
        
    Returns:
        Le modèle Prophet chargé, ou None si non disponible
    """
    if not PROPHET_AVAILABLE:
        logger.error("Prophet n'est pas disponible. Installez-le avec 'pip install prophet'.")
        return None
        
    model_path = os.path.join(MODELS_PATH, "prophet", f"{kpi_name}.json")
    
    if not os.path.exists(model_path):
        logger.error(f"Modèle Prophet pour {kpi_name} introuvable à {model_path}")
        return None
        
    try:
        # Charger le modèle serialisé
        with open(model_path, 'r') as fin:
            model_json = json.load(fin)
            
        model = Prophet().from_json(model_json)
        logger.info(f"Modèle Prophet pour {kpi_name} chargé avec succès")
        return model
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle Prophet pour {kpi_name}: {str(e)}")
        return None

def load_tft(kpi_name: str):
    """
    Charge un modèle Temporal Fusion Transformer pour un KPI spécifique.
    
    Args:
        kpi_name: Le nom du KPI pour lequel charger le modèle
        
    Returns:
        Le modèle TFT chargé, ou None si non disponible
    """
    if not TFT_AVAILABLE:
        logger.error("PyTorch Forecasting n'est pas disponible.")
        return None
        
    model_path = os.path.join(MODELS_PATH, "tft", f"{kpi_name}.pt")
    
    if not os.path.exists(model_path):
        logger.error(f"Modèle TFT pour {kpi_name} introuvable à {model_path}")
        return None
        
    try:
        # Charger le modèle PyTorch
        model = TemporalFusionTransformer.load_from_checkpoint(model_path)
        logger.info(f"Modèle TFT pour {kpi_name} chargé avec succès")
        return model
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle TFT pour {kpi_name}: {str(e)}")
        return None

def get_historical_data(kpi_name: str) -> Union[pd.DataFrame, None]:
    """
    Récupère les données historiques pour un KPI donné.
    
    Args:
        kpi_name: Le nom du KPI pour lequel récupérer les données
        
    Returns:
        Un DataFrame pandas contenant les données historiques, ou None en cas d'erreur
    """
    try:
        data_file = os.path.join(DATA_PATH, f"{kpi_name}.csv")
        
        if not os.path.exists(data_file):
            logger.error(f"Fichier de données pour {kpi_name} introuvable à {data_file}")
            return None
            
        df = pd.read_csv(data_file)
        
        # Convertir la colonne de date en datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
        return df
        
    except Exception as e:
        logger.error(f"Erreur lors de la lecture des données pour {kpi_name}: {str(e)}")
        return None

def get_indicator(name: str, date: str) -> Dict[str, Any]:
    """
    Retourne la valeur d'un KPI pour une date donnée.
    
    Args:
        name: Le nom du KPI à récupérer
        date: La date pour laquelle récupérer la valeur (format YYYY-MM-DD)
        
    Returns:
        Un dictionnaire contenant la valeur du KPI et des métadonnées
    """
    try:
        # Valider le format de date
        parsed_date = pd.to_datetime(date)
        
        # Charger les données historiques
        df = get_historical_data(name)
        if df is None:
            return {"error": f"Données introuvables pour le KPI '{name}'"}
        
        # Filtrer les données pour la date demandée
        result = df[df['date'] == parsed_date]
        
        if result.empty:
            return {"error": f"Pas de données disponibles pour {name} à la date {date}"}
            
        # Retourner la valeur et les métadonnées
        value = float(result['value'].iloc[0]) if 'value' in result.columns else None
        
        return {
            "name": name,
            "date": date,
            "value": value,
            "metadata": {
                "unit": df.get("unit", ""),
                "source": "historical_data"
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du KPI {name} pour la date {date}: {str(e)}")
        return {"error": str(e)}

def forecast_kpi(name: str, horizon: int = 12) -> Dict[str, Any]:
    """
    Retourne une prévision pour un KPI donné.
    
    Args:
        name: Le nom du KPI à prévoir
        horizon: L'horizon de prévision en périodes (jours, mois selon le KPI)
        
    Returns:
        Un dictionnaire contenant les valeurs prévues et des métadonnées
    """
    try:
        # Charger les données historiques
        df = get_historical_data(name)
        if df is None:
            return {"error": f"Données introuvables pour le KPI '{name}'"}
        
        # Déterminer le type de modèle à utiliser
        model_type = "prophet"  # Par défaut, utiliser Prophet
        
        # Si un modèle TFT existe, l'utiliser en priorité
        tft_model_path = os.path.join(MODELS_PATH, "tft", f"{name}.pt")
        if os.path.exists(tft_model_path) and TFT_AVAILABLE:
            model_type = "tft"
            
        # Générer la prévision
        forecast_values = []
        
        if model_type == "prophet":
            # Utiliser Prophet
            model = load_prophet(name)
            if model is None:
                return {"error": f"Le modèle de prévision pour '{name}' est indisponible"}
                
            # Préparer les futures dates pour la prévision
            last_date = df['date'].max()
            future = pd.DataFrame({
                'ds': [last_date + timedelta(days=i) for i in range(1, horizon + 1)]
            })
            
            # Générer la prévision
            forecast = model.predict(future)
            
            # Extraire les résultats
            forecast_values = [
                {"date": row['ds'].strftime('%Y-%m-%d'), "value": float(row['yhat']), 
                 "lower": float(row['yhat_lower']), "upper": float(row['yhat_upper'])}
                for _, row in forecast.iterrows()
            ]
              elif model_type == "tft":
            # Utiliser Temporal Fusion Transformer
            try:
                # Utiliser notre classe TFTForecaster
                forecaster = TFTForecaster()
                # Charger le modèle TFT
                forecaster.load_model(name)
                
                # Préparer les données pour la prévision
                # On a besoin de créer un DataFrame contenant les dernières données disponibles
                # et les features nécessaires pour la prévision
                
                # Déterminer si les données sont multivariées (plusieurs séries)
                if "series_id" in df.columns:
                    # Grouper par série_id pour obtenir les derniers points de chaque série
                    latest_data = df.groupby("series_id").tail(forecaster.max_encoder_length)
                    
                    # Assurer que time_idx est correct et continue pour la prédiction
                    last_time_idx = df["time_idx"].max()
                    
                    # Créer un dataframe pour chaque série avec les index temporels futurs
                    future_dfs = []
                    for series_id in df["series_id"].unique():
                        series_data = latest_data[latest_data["series_id"] == series_id].copy()
                        
                        # Créer les index temporels pour la prévision
                        future_time_idx = np.arange(
                            last_time_idx + 1,
                            last_time_idx + horizon + 1
                        )
                        
                        # Dernière date connue
                        last_date = series_data["date"].max()
                        
                        # Générer les futures dates selon la fréquence des données
                        # On estime la fréquence à partir des deux dernières dates
                        date_diff = (series_data["date"].iloc[-1] - series_data["date"].iloc[-2]).days
                        freq = "D" if date_diff < 28 else "MS"  # Jour ou Mois
                        
                        future_dates = pd.date_range(
                            start=last_date + pd.Timedelta(days=1 if freq == "D" else 31),
                            periods=horizon,
                            freq=freq
                        )
                        
                        # Créer le DataFrame de prédiction pour cette série
                        future_df = pd.DataFrame({
                            "time_idx": future_time_idx,
                            "series_id": series_id,
                            "date": future_dates
                        })
                        
                        # Ajouter les features temporelles
                        future_df["year"] = future_df["date"].dt.year
                        future_df["month"] = future_df["date"].dt.month
                        
                        if freq == "D":
                            future_df["day"] = future_df["date"].dt.day
                            future_df["dayofweek"] = future_df["date"].dt.dayofweek
                        
                        future_dfs.append(future_df)
                    
                    # Combiner toutes les séries futures
                    future_df = pd.concat(future_dfs, axis=0)
                    
                    # Combiner avec les données historiques pour avoir un dataset complet
                    combined_df = pd.concat([df, future_df], axis=0)
                    
                else:
                    # Données à série unique
                    latest_data = df.tail(forecaster.max_encoder_length).copy()
                    last_time_idx = df["time_idx"].max()
                    last_date = df["date"].max()
                    
                    # Estimer la fréquence
                    date_diff = (df["date"].iloc[-1] - df["date"].iloc[-2]).days
                    freq = "D" if date_diff < 28 else "MS"  # Jour ou Mois
                    
                    future_dates = pd.date_range(
                        start=last_date + pd.Timedelta(days=1 if freq == "D" else 31),
                        periods=horizon,
                        freq=freq
                    )
                    
                    # Créer le DataFrame de prédiction
                    future_df = pd.DataFrame({
                        "time_idx": np.arange(last_time_idx + 1, last_time_idx + horizon + 1),
                        "date": future_dates
                    })
                    
                    # Ajouter les features temporelles
                    future_df["year"] = future_df["date"].dt.year
                    future_df["month"] = future_df["date"].dt.month
                    
                    if freq == "D":
                        future_df["day"] = future_df["date"].dt.day
                        future_df["dayofweek"] = future_df["date"].dt.dayofweek
                    
                    # Combiner avec les données historiques
                    combined_df = pd.concat([df, future_df], axis=0)
                
                # Effectuer la prédiction
                predictions = forecaster.predict(combined_df)
                
                # Traiter les prédictions
                # Le format retourné dépend du modèle TFT, mais on suppose qu'il contient:
                # - la valeur prédite (median)
                # - les intervalles de confiance (quantiles)
                
                forecast_values = []
                
                # Extraire les prédictions pour chaque point de temps futur
                for i, pred_time in enumerate(future_dates):
                    # Récupérer les quantiles pour les intervalles de confiance
                    median = predictions.iloc[i]["median"] if "median" in predictions else predictions.iloc[i]["prediction"]
                    lower = predictions.iloc[i]["0.1"] if "0.1" in predictions else median * 0.9
                    upper = predictions.iloc[i]["0.9"] if "0.9" in predictions else median * 1.1
                    
                    forecast_values.append({
                        "date": pred_time.strftime('%Y-%m-%d'),
                        "value": float(median),
                        "lower": float(lower),
                        "upper": float(upper)
                    })
                
            except Exception as e:
                logger.error(f"Erreur lors de la prévision TFT pour {name}: {str(e)}")
                return {"error": f"Erreur de prévision TFT: {str(e)}"}
            
        # Retourner les résultats
        return {
            "name": name,
            "horizon": horizon,
            "model": model_type,
            "forecast": forecast_values,
            "metadata": {
                "last_historical_date": df['date'].max().strftime('%Y-%m-%d'),
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la prévision pour {name}: {str(e)}")
        return {"error": str(e)}
