import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
from prophet import Prophet
import matplotlib.pyplot as plt

# Configuration du dossier de données et modèles
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "prophet"))

# S'assurer que les dossiers existent
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

def generate_sample_kpi_data(kpi_name, num_points=365, trend=0.05, seasonality=0.2, noise=0.1, 
                            start_date="2023-01-01", freq="D"):
    """
    Génère des données synthétiques pour un KPI donné.
    
    Args:
        kpi_name: Nom du KPI
        num_points: Nombre de points de données
        trend: Amplitude de la tendance (croissance linéaire)
        seasonality: Amplitude de la saisonnalité
        noise: Amplitude du bruit
        start_date: Date de début
        freq: Fréquence des données ('D' pour jour, 'M' pour mois)
        
    Returns:
        DataFrame pandas avec les données générées
    """
    print(f"Génération des données pour le KPI: {kpi_name}")
    
    # Créer des dates
    if freq == "M":
        dates = pd.date_range(start=start_date, periods=num_points, freq="MS")
    else:
        dates = pd.date_range(start=start_date, periods=num_points, freq="D")
    
    # Composante de tendance (croissance linéaire)
    trend_component = np.linspace(0, trend * num_points, num_points)
    
    # Composante saisonnière (selon que ce soit mensuel ou quotidien)
    if freq == "M":
        seasonality_component = seasonality * np.sin(np.linspace(0, 2 * np.pi * (num_points / 12), num_points))
    else:
        seasonality_component = seasonality * np.sin(np.linspace(0, 2 * np.pi * (num_points / 365), num_points))
    
    # Composante de bruit
    noise_component = noise * np.random.randn(num_points)
    
    # Valeur de base selon le KPI
    if "permis" in kpi_name.lower():
        base_value = 50  # Nombre moyen de permis
    elif "logements" in kpi_name.lower():
        base_value = 300  # Nombre de logements
    elif "prix" in kpi_name.lower():
        base_value = 3500  # Prix au m²
    else:
        base_value = 100  # Valeur par défaut
    
    # Calculer les valeurs finales
    values = base_value + trend_component + seasonality_component + noise_component
    
    # Assurer que les valeurs sont positives si nécessaire
    if "nombre" in kpi_name.lower() or "permis" in kpi_name.lower() or "logements" in kpi_name.lower():
        values = np.maximum(values, 0)
        values = np.round(values)  # Arrondir pour les comptages
    else:
        values = np.maximum(values, 0)  # Juste assurer des valeurs positives
    
    # Créer le DataFrame
    df = pd.DataFrame({
        "date": dates,
        "value": values
    })
    
    # Sauvegarder les données
    csv_path = os.path.join(DATA_DIR, f"{kpi_name}.csv")
    df.to_csv(csv_path, index=False)
    print(f"Données sauvegardées dans: {csv_path}")
    
    return df

def train_prophet_model(df, kpi_name, yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False):
    """
    Entraîne un modèle Prophet sur les données d'un KPI.
    
    Args:
        df: DataFrame avec les colonnes 'date' et 'value'
        kpi_name: Nom du KPI
        yearly_seasonality: Inclure la saisonnalité annuelle
        weekly_seasonality: Inclure la saisonnalité hebdomadaire
        daily_seasonality: Inclure la saisonnalité quotidienne
        
    Returns:
        Modèle Prophet entraîné
    """
    print(f"Entraînement du modèle Prophet pour: {kpi_name}")
    
    # Renommer les colonnes pour Prophet
    prophet_df = df.rename(columns={"date": "ds", "value": "y"})
    
    # Initialiser et entraîner le modèle
    model = Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality
    )
    model.fit(prophet_df)
    
    # Sauvegarder le modèle
    with open(os.path.join(MODEL_DIR, f"{kpi_name}.json"), 'w') as f:
        json.dump(model.to_json(), f)
    print(f"Modèle sauvegardé dans: {os.path.join(MODEL_DIR, f'{kpi_name}.json')}")
    
    # Générer des prévisions pour visualisation
    future = model.make_future_dataframe(periods=90)  # 90 jours dans le futur
    forecast = model.predict(future)
    
    # Visualiser la prévision
    fig = model.plot(forecast)
    plt.title(f"Prévision pour {kpi_name}")
    
    # Sauvegarder la visualisation
    fig_path = os.path.join(MODEL_DIR, f"{kpi_name}_forecast.png")
    plt.savefig(fig_path)
    plt.close()
    print(f"Visualisation de la prévision sauvegardée dans: {fig_path}")
    
    return model

def main():
    """
    Fonction principale pour générer des données et modèles pour plusieurs KPIs
    """
    # Définir les KPIs
    kpis = [
        {"name": "nb_permis_construire", "freq": "M", "points": 48, "trend": 0.3, "seasonality": 0.4},
        {"name": "nb_logements_autorises", "freq": "M", "points": 48, "trend": 0.5, "seasonality": 0.3},
        {"name": "prix_m2_appartements", "freq": "M", "points": 60, "trend": 10, "seasonality": 0.1},
        {"name": "delai_traitement_permis", "freq": "D", "points": 365, "trend": -0.01, "seasonality": 0.15}
    ]
    
    # Générer des données et entraîner des modèles pour chaque KPI
    for kpi in kpis:
        df = generate_sample_kpi_data(
            kpi["name"],
            num_points=kpi["points"],
            trend=kpi["trend"],
            seasonality=kpi["seasonality"],
            freq=kpi["freq"]
        )
        
        # Déterminer les paramètres de saisonnalité selon la fréquence
        if kpi["freq"] == "M":
            train_prophet_model(df, kpi["name"], 
                              yearly_seasonality=True, 
                              weekly_seasonality=False, 
                              daily_seasonality=False)
        else:
            train_prophet_model(df, kpi["name"],
                              yearly_seasonality=True,
                              weekly_seasonality=True,
                              daily_seasonality=False)
    
    print("Génération des données et entraînement des modèles terminés!")

if __name__ == "__main__":
    main()
