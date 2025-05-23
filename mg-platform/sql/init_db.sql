-- Initialize the PostgreSQL analytics database for the Marne & Gondoire project
-- This script creates the necessary schema and tables for storing data

-- Create schema
CREATE SCHEMA IF NOT EXISTS mg_data;

-- Set the search path
SET search_path TO mg_data, public;

-- Create tables for building permits (Sitadel data)
CREATE TABLE IF NOT EXISTS fact_permis (
    id SERIAL PRIMARY KEY,
    numero_permis VARCHAR(50) UNIQUE NOT NULL,
    date_depot DATE NOT NULL,
    date_decision DATE,
    nature_projet VARCHAR(100),
    categorie VARCHAR(50),
    surface_plancher NUMERIC(10, 2),
    nb_logements INTEGER,
    commune_code VARCHAR(10),
    commune_nom VARCHAR(100),
    adresse TEXT,
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),
    statut VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on frequently queried fields
CREATE INDEX IF NOT EXISTS idx_permis_date_depot ON fact_permis(date_depot);
CREATE INDEX IF NOT EXISTS idx_permis_commune ON fact_permis(commune_code);

-- Create table for real estate data
CREATE TABLE IF NOT EXISTS fact_immobilier (
    id SERIAL PRIMARY KEY,
    reference VARCHAR(50) UNIQUE NOT NULL,
    type_bien VARCHAR(50),
    prix NUMERIC(12, 2),
    surface NUMERIC(8, 2),
    nb_pieces INTEGER,
    nb_chambres INTEGER,
    etage INTEGER,
    annee_construction INTEGER,
    dpe VARCHAR(2),
    commune_code VARCHAR(10),
    commune_nom VARCHAR(100),
    quartier VARCHAR(100),
    adresse TEXT,
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),
    url_annonce TEXT,
    date_publication DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on frequently queried fields
CREATE INDEX IF NOT EXISTS idx_immobilier_commune ON fact_immobilier(commune_code);
CREATE INDEX IF NOT EXISTS idx_immobilier_prix ON fact_immobilier(prix);
CREATE INDEX IF NOT EXISTS idx_immobilier_type ON fact_immobilier(type_bien);

-- Create dimension table for communes
CREATE TABLE IF NOT EXISTS dim_commune (
    code VARCHAR(10) PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    departement VARCHAR(3),
    region VARCHAR(50),
    population INTEGER,
    superficie NUMERIC(10, 2),
    densite NUMERIC(10, 2),
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6)
);

-- Create table for KPI indicators
CREATE TABLE IF NOT EXISTS fact_kpi (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    value NUMERIC(15, 4) NOT NULL,
    unit VARCHAR(20),
    source VARCHAR(100),
    UNIQUE(name, date)
);

-- Create index on KPI name and date
CREATE INDEX IF NOT EXISTS idx_kpi_name_date ON fact_kpi(name, date);

-- Create table for forecasts
CREATE TABLE IF NOT EXISTS fact_forecast (
    id SERIAL PRIMARY KEY,
    kpi_name VARCHAR(50) NOT NULL,
    forecast_date DATE NOT NULL,
    target_date DATE NOT NULL,
    value NUMERIC(15, 4) NOT NULL,
    lower_bound NUMERIC(15, 4),
    upper_bound NUMERIC(15, 4),
    model_type VARCHAR(50),
    model_version VARCHAR(50),
    UNIQUE(kpi_name, forecast_date, target_date)
);

-- Create index on forecast table
CREATE INDEX IF NOT EXISTS idx_forecast_kpi ON fact_forecast(kpi_name, target_date);

-- Create users and permissions
-- Admin user already created in docker-compose
-- Create read-only user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'mg_reader') THEN
        CREATE USER mg_reader WITH PASSWORD 'reader_pwd';
    END IF;
END
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA mg_data TO mg_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA mg_data TO mg_reader;

-- Save initial grant for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA mg_data GRANT SELECT ON TABLES TO mg_reader;

-- Create function to update timestamps automatically
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for timestamp updates
CREATE TRIGGER update_fact_permis_timestamp BEFORE UPDATE ON fact_permis
    FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

CREATE TRIGGER update_fact_immobilier_timestamp BEFORE UPDATE ON fact_immobilier
    FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
