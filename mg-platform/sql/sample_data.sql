-- Generate sample data for testing purposes
-- This script inserts example records into the database tables

-- Set the search path
SET search_path TO mg_data, public;

-- Sample communes in Marne et Gondoire
INSERT INTO dim_commune (code, nom, departement, region, population, superficie, densite, latitude, longitude)
VALUES
    ('77243', 'Lagny-sur-Marne', '77', 'Île-de-France', 21236, 5.68, 3738.73, 48.877, 2.698),
    ('77307', 'Montévrain', '77', 'Île-de-France', 11282, 5.34, 2112.73, 48.877, 2.747),
    ('77468', 'Thorigny-sur-Marne', '77', 'Île-de-France', 9931, 4.76, 2086.34, 48.883, 2.713),
    ('77121', 'Chanteloup-en-Brie', '77', 'Île-de-France', 3952, 3.15, 1254.60, 48.856, 2.743),
    ('77085', 'Bussy-Saint-Martin', '77', 'Île-de-France', 738, 2.46, 300.00, 48.850, 2.688),
    ('77438', 'Saint-Thibault-des-Vignes', '77', 'Île-de-France', 6431, 4.92, 1307.11, 48.869, 2.677)
ON CONFLICT (code) DO NOTHING;

-- Sample building permits
INSERT INTO fact_permis (numero_permis, date_depot, date_decision, nature_projet, categorie, surface_plancher, nb_logements, commune_code, commune_nom, adresse, latitude, longitude, statut)
VALUES
    ('PC07724322A0001', '2022-01-15', '2022-03-22', 'Construction neuve', 'Logement collectif', 2150.75, 28, '77243', 'Lagny-sur-Marne', '15 Rue de la Fontaine, 77400 Lagny-sur-Marne', 48.878, 2.699, 'Accepté'),
    ('PC07724322A0002', '2022-02-03', '2022-04-15', 'Extension', 'Maison individuelle', 45.20, 0, '77243', 'Lagny-sur-Marne', '8 Rue du Chemin de Fer, 77400 Lagny-sur-Marne', 48.879, 2.695, 'Accepté'),
    ('PC07730722A0010', '2022-03-12', '2022-05-20', 'Construction neuve', 'Logement collectif', 1850.00, 24, '77307', 'Montévrain', '3 Avenue de l\'Europe, 77144 Montévrain', 48.878, 2.749, 'Accepté'),
    ('PC07746822A0005', '2022-04-01', '2022-06-10', 'Construction neuve', 'Maison individuelle', 130.50, 1, '77468', 'Thorigny-sur-Marne', '12 Rue des Coteaux, 77400 Thorigny-sur-Marne', 48.884, 2.714, 'Accepté'),
    ('PC07712122A0002', '2022-05-15', '2022-07-22', 'Construction neuve', 'Logement collectif', 950.25, 12, '77121', 'Chanteloup-en-Brie', '5 Rue de la Ferme, 77600 Chanteloup-en-Brie', 48.855, 2.745, 'Accepté'),
    ('PC07724322A0015', '2022-06-08', '2022-08-15', 'Extension', 'Local commercial', 85.70, 0, '77243', 'Lagny-sur-Marne', '45 Rue du Chemin de Gouvernes, 77400 Lagny-sur-Marne', 48.875, 2.702, 'Accepté'),
    ('PC07724322A0025', '2022-07-04', '2022-09-10', 'Construction neuve', 'Logement collectif', 1750.00, 22, '77243', 'Lagny-sur-Marne', '18 Avenue de la République, 77400 Lagny-sur-Marne', 48.876, 2.697, 'Accepté'),
    ('PC07743822A0008', '2022-08-15', NULL, 'Construction neuve', 'Local commercial', 450.80, 0, '77438', 'Saint-Thibault-des-Vignes', '10 Rue de la Mare, 77400 Saint-Thibault-des-Vignes', 48.870, 2.675, 'En cours'),
    ('PC07730722A0018', '2022-09-02', '2022-11-15', 'Construction neuve', 'Logement collectif', 2200.00, 30, '77307', 'Montévrain', '12 Avenue François Mitterrand, 77144 Montévrain', 48.876, 2.748, 'Accepté'),
    ('PC07708522A0001', '2022-10-05', '2022-12-20', 'Construction neuve', 'Maison individuelle', 145.30, 1, '77085', 'Bussy-Saint-Martin', '3 Rue de la Fontaine, 77600 Bussy-Saint-Martin', 48.851, 2.690, 'Accepté')
ON CONFLICT (numero_permis) DO NOTHING;

-- Sample real estate data
INSERT INTO fact_immobilier (reference, type_bien, prix, surface, nb_pieces, nb_chambres, etage, annee_construction, dpe, commune_code, commune_nom, quartier, adresse, latitude, longitude, url_annonce, date_publication)
VALUES
    ('IMMO-LGN-001', 'Appartement', 289000.00, 65.40, 3, 2, 2, 2010, 'C', '77243', 'Lagny-sur-Marne', 'Centre-ville', '25 Rue Saint-Denis, 77400 Lagny-sur-Marne', 48.877, 2.698, 'https://example.com/annonce1', '2023-01-05'),
    ('IMMO-LGN-002', 'Maison', 450000.00, 120.80, 5, 3, NULL, 1985, 'D', '77243', 'Lagny-sur-Marne', 'Les Heurteaux', '8 Rue des Écoles, 77400 Lagny-sur-Marne', 48.878, 2.695, 'https://example.com/annonce2', '2023-01-08'),
    ('IMMO-MTV-001', 'Appartement', 340000.00, 78.50, 4, 2, 3, 2018, 'B', '77307', 'Montévrain', 'Éco-quartier', '15 Avenue de l''Europe, 77144 Montévrain', 48.876, 2.748, 'https://example.com/annonce3', '2023-01-10'),
    ('IMMO-THG-001', 'Maison', 398000.00, 110.00, 5, 3, NULL, 1992, 'D', '77468', 'Thorigny-sur-Marne', 'Les Cerisiers', '7 Rue des Pointes, 77400 Thorigny-sur-Marne', 48.882, 2.712, 'https://example.com/annonce4', '2023-01-15'),
    ('IMMO-LGN-003', 'Appartement', 199000.00, 45.20, 2, 1, 1, 2005, 'C', '77243', 'Lagny-sur-Marne', 'Centre-ville', '3 Rue du Château Fort, 77400 Lagny-sur-Marne', 48.876, 2.700, 'https://example.com/annonce5', '2023-01-20'),
    ('IMMO-CHT-001', 'Maison', 510000.00, 150.30, 6, 4, NULL, 2008, 'C', '77121', 'Chanteloup-en-Brie', 'Les Chênes', '12 Allée des Charmes, 77600 Chanteloup-en-Brie', 48.855, 2.746, 'https://example.com/annonce6', '2023-01-25'),
    ('IMMO-STT-001', 'Appartement', 228000.00, 55.80, 3, 2, 4, 2000, 'D', '77438', 'Saint-Thibault-des-Vignes', 'Centre', '25 Avenue des Joncs, 77400 Saint-Thibault-des-Vignes', 48.868, 2.676, 'https://example.com/annonce7', '2023-01-30'),
    ('IMMO-MTV-002', 'Appartement', 295000.00, 68.40, 3, 2, 2, 2015, 'C', '77307', 'Montévrain', 'Val d''Europe', '8 Rue de la Société des Nations, 77144 Montévrain', 48.875, 2.750, 'https://example.com/annonce8', '2023-02-05'),
    ('IMMO-BSM-001', 'Maison', 620000.00, 180.00, 7, 5, NULL, 2002, 'C', '77085', 'Bussy-Saint-Martin', 'Centre', '2 Route de la Brosse, 77600 Bussy-Saint-Martin', 48.852, 2.688, 'https://example.com/annonce9', '2023-02-10'),
    ('IMMO-LGN-004', 'Appartement', 275000.00, 62.50, 3, 2, 3, 2012, 'C', '77243', 'Lagny-sur-Marne', 'Saint-Laurent', '15 Rue de la Marne, 77400 Lagny-sur-Marne', 48.875, 2.701, 'https://example.com/annonce10', '2023-02-15')
ON CONFLICT (reference) DO NOTHING;

-- Sample KPI data
INSERT INTO fact_kpi (name, date, value, unit, source)
VALUES
    ('logements_neufs_autorises', '2022-01-01', 28, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-02-01', 0, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-03-01', 24, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-04-01', 1, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-05-01', 12, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-06-01', 0, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-07-01', 22, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-08-01', 0, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-09-01', 30, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-10-01', 1, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-11-01', 0, 'nombre', 'Sitadel'),
    ('logements_neufs_autorises', '2022-12-01', 45, 'nombre', 'Sitadel'),
    
    ('prix_m2_moyen_appartement', '2023-01-01', 4420, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-02-01', 4450, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-03-01', 4470, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-04-01', 4510, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-05-01', 4550, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-06-01', 4530, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-07-01', 4580, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-08-01', 4600, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-09-01', 4620, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-10-01', 4650, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-11-01', 4630, 'euros', 'Immobilier'),
    ('prix_m2_moyen_appartement', '2023-12-01', 4610, 'euros', 'Immobilier'),
    
    ('prix_m2_moyen_maison', '2023-01-01', 3720, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-02-01', 3750, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-03-01', 3790, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-04-01', 3830, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-05-01', 3850, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-06-01', 3840, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-07-01', 3880, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-08-01', 3900, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-09-01', 3920, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-10-01', 3950, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-11-01', 3930, 'euros', 'Immobilier'),
    ('prix_m2_moyen_maison', '2023-12-01', 3910, 'euros', 'Immobilier')
ON CONFLICT (name, date) DO NOTHING;

-- Sample forecast data
INSERT INTO fact_forecast (kpi_name, forecast_date, target_date, value, lower_bound, upper_bound, model_type, model_version)
VALUES
    ('logements_neufs_autorises', '2023-01-01', '2023-01-01', 18, 10, 26, 'prophet', '1.0'),
    ('logements_neufs_autorises', '2023-01-01', '2023-02-01', 15, 8, 22, 'prophet', '1.0'),
    ('logements_neufs_autorises', '2023-01-01', '2023-03-01', 25, 18, 32, 'prophet', '1.0'),
    ('logements_neufs_autorises', '2023-01-01', '2023-04-01', 22, 15, 29, 'prophet', '1.0'),
    ('logements_neufs_autorises', '2023-01-01', '2023-05-01', 20, 12, 28, 'prophet', '1.0'),
    ('logements_neufs_autorises', '2023-01-01', '2023-06-01', 18, 10, 26, 'prophet', '1.0'),
    
    ('prix_m2_moyen_appartement', '2024-01-01', '2024-01-01', 4670, 4600, 4740, 'prophet', '1.0'),
    ('prix_m2_moyen_appartement', '2024-01-01', '2024-02-01', 4700, 4620, 4780, 'prophet', '1.0'),
    ('prix_m2_moyen_appartement', '2024-01-01', '2024-03-01', 4730, 4640, 4820, 'prophet', '1.0'),
    ('prix_m2_moyen_appartement', '2024-01-01', '2024-04-01', 4760, 4660, 4860, 'prophet', '1.0'),
    ('prix_m2_moyen_appartement', '2024-01-01', '2024-05-01', 4790, 4680, 4900, 'prophet', '1.0'),
    ('prix_m2_moyen_appartement', '2024-01-01', '2024-06-01', 4820, 4700, 4940, 'prophet', '1.0'),
    
    ('prix_m2_moyen_maison', '2024-01-01', '2024-01-01', 3970, 3900, 4040, 'prophet', '1.0'),
    ('prix_m2_moyen_maison', '2024-01-01', '2024-02-01', 4000, 3920, 4080, 'prophet', '1.0'),
    ('prix_m2_moyen_maison', '2024-01-01', '2024-03-01', 4030, 3940, 4120, 'prophet', '1.0'),
    ('prix_m2_moyen_maison', '2024-01-01', '2024-04-01', 4060, 3960, 4160, 'prophet', '1.0'),
    ('prix_m2_moyen_maison', '2024-01-01', '2024-05-01', 4090, 3980, 4200, 'prophet', '1.0'),
    ('prix_m2_moyen_maison', '2024-01-01', '2024-06-01', 4120, 4000, 4240, 'prophet', '1.0')
ON CONFLICT (kpi_name, forecast_date, target_date) DO NOTHING;
