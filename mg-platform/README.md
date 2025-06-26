# Marne & Gondoire - Plateforme MCP

## 🎯 Objectif
Plateforme d'agents IA utilisant le Model Context Protocol (MCP) pour l'analyse de données et l'automatisation.

## 🚀 Démarrage Rapide

### Installation
```bash
# Cloner et se positionner
cd mg-platform

# Activer l'environnement virtuel
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Lancement
```bash
# Démarrer le serveur
python mcp_server/main.py
# ou
uvicorn mcp_server.main:app --reload --port 8080
```

### Test
- Interface web: http://localhost:8080
- Documentation API: http://localhost:8080/docs
- Health check: http://localhost:8080/health

## 📁 Structure
```
mg-platform/
├── mcp_server/         # Serveur MCP FastAPI
├── tools/              # Outils métiers
├── scrapers/           # Scrapers web
├── models/             # Modèles ML
├── clients/            # Clients IA
├── data/               # Données
└── tests/              # Tests
```

## 🔧 Développement
```bash
# Tests
pytest

# Linter (optionnel)
pip install black flake8
black .
flake8 .
```

# 📊 Analyse détaillée du fichier de données

# 📊 Interprétation de l'analyse - 3101 entreprises

## 🎯 **Synthèse Exécutive**

### **Fichier analysé :**
- **3,101 entreprises** de Seine-et-Marne (77)
- **27 colonnes** de données SIRENE
- **Taux de complétion moyen : 71.7%**
- **7.7 champs manquants** par entreprise en moyenne

---

## 🔥 **OPPORTUNITÉ MAJEURE : Sites Web**

### **Site Web établissement** - PRIORITÉ CRITIQUE
- **99.8% des entreprises** n'ont PAS de site web renseigné
- **3,096 sites web manquants** sur 3,101 entreprises
- **Gain estimé : 2,322 sites** trouvables via LinkedIn (75% de succès)
- **Impact :** Données de contact, activité, services

**💡 C'est votre JACKPOT d'enrichissement !**

---

## 👥 **Dirigeants à compléter**

### **Prénoms manquants**
- **96.8% des prénoms** sont "INFORMATION NON-DIFFUSIBLE"
- **3,001 prénoms** à rechercher
- **Gain estimé : 1,500 prénoms** via LinkedIn

### **Dénominations sociales**
- **96.7% des noms d'entreprise** sont non-diffusibles
- **2,998 raisons sociales** à enrichir
- **Gain estimé : 1,499 noms** d'entreprises

---

## ✅ **Données Déjà Complètes (100%)**

Ces colonnes sont parfaitement remplies :
- **SIRET** ✅ (identifiant unique)
- **Adresse - CP et commune** ✅ (localisation)
- **Code NAF** ✅ (secteur d'activité)
- **Forme juridique** ✅ (statut légal)
- **Effectifs** ✅ (taille d'entreprise)
- **Dates** ✅ (création, événements)

---

## 🚀 **Plan d'Action Recommandé**

### **Phase 1 : Sites Web (CRITIQUE)**
```
🎯 Objectif : 3,096 sites web
⏱️ Temps estimé : 103 minutes
📦 Batch size : 31 entreprises/batch
🔄 Rate limit : 2 secondes/requête
```

**Méthode :**
1. Recherche LinkedIn avec `Nom + Commune`
2. Extraction URL site web depuis pages LinkedIn
3. Validation accessibilité des sites

### **Phase 2 : Enrichissement Dirigeants**
```
🎯 Objectif : 3,001 prénoms + 2,998 noms
⏱️ Temps estimé : ~200 minutes
```

**Méthode :**
1. Recherche dirigeants via LinkedIn
2. Extraction nom/prénom depuis profils
3. Cross-check avec SIRET

---

## 📈 **Impact Business Attendu**

### **Avant enrichissement :**
- 5 entreprises avec site web (0.2%)
- 100 prénoms dirigeants (3.2%)
- 103 noms d'entreprise (3.3%)

### **Après enrichissement LinkedIn :**
- **2,327 entreprises avec site web** (75%)
- **1,600 prénoms dirigeants** (52%)
- **1,602 noms d'entreprise** (52%)

### **ROI de l'enrichissement :**
- **+46,440% de sites web** 🚀
- **+1,500% de prénoms dirigeants** 📈
- **+1,456% de noms d'entreprise** 💼

---

## 🎯 **Particularités du Fichier**

### **Échantillon d'entreprises :**
1. **SYED SARAH** (Chalifert) - Données complètes ✅
2. **Entreprises anonymisées** - Majoritairement "INFORMATION NON-DIFFUSIBLE"
3. **Dirigeants génériques** - Beaucoup de "le directeur"

### **Géographie :**
- Toutes en **Seine-et-Marne (77)**
- Communes : Chalifert, Pontcarré, Lagny-sur-Marne, etc.
- **Excellent pour ciblage géographique local**

---

## 💡 **Recommandations Stratégiques**

### **1. Commencer par un test**
```bash
# Test sur 50 entreprises d'abord
curl -X POST "http://localhost:8080/enrich?test_mode=true&max_companies=50"
```

### **2. Focus sites web d'abord**
- **Impact maximum** avec effort minimum
- **Données immédiatement exploitables**
- **Base pour enrichissements futurs**

### **3. Traitement par batch géographique**
- Grouper par commune pour optimiser recherches
- Traiter les entreprises actives en priorité

### **4. Validation des résultats**
- Vérifier 10% des sites trouvés manuellement
- Ajuster algorithmes selon qualité

---

## 🎉 **Conclusion**

Votre fichier est une **mine d'or d'opportunités d'enrichissement** !

**Avec 99.8% des sites web manquants, vous pouvez potentiellement multiplier par 464 vos données de sites web en une seule opération d'enrichissement LinkedIn.**

**Prêt pour l'étape suivante : développer l'enrichisseur LinkedIn automatisé ?**
