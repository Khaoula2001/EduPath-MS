# Student Profiler Microservice

## Description
Le microservice Student Profiler agrège les indicateurs d'engagement et de performance des étudiants (issus de `analytics.student_features`) pour réaliser un clustering de profils avec PCA + KMeans. Les affectations de clusters sont persistées dans PostgreSQL (`analytics_student_profiles`).

Cette implémentation minimale fournie ici expose une API FastAPI et un service d'entraînement.

## Prérequis
- Python 3.10+
- PostgreSQL (optionnel) ou SQLite (utilisé par défaut en local via `DATABASE_URL`)

## Installation
```powershell
cd microservices/student-profiler
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration
- Fichier de configuration par défaut : `config/model_config.yaml`
- Vous pouvez définir `DATABASE_URL` pour pointer vers votre base de données (ex: `postgresql+psycopg2://user:pass@host:5432/dbname`) ; sinon les variables `PG_HOST`/`PG_DB`/... seront utilisées.

## Endpoints
- `POST /train` : entraîne PCA + KMeans, sauvegarde l'artifact Joblib et (ré)écrit `analytics_student_profiles`.
- `GET /profiles/{id_student}` : retourne le cluster le plus récent pour un étudiant.

## Lancement API
```powershell
uvicorn src.api:app --reload
```

## Mode de test (rapide)
Le test utilise une base SQLite temporaire pour vérifier le cycle d'entraînement et la récupération d'un profil.

```powershell
pip install -r requirements.txt
pytest -q
```

## Structure
- `src/` : code source (API, service, DB)
- `config/model_config.yaml` : paramètres du modèle et colonnes utilisées
- `artifacts/` : modèles sauvegardés
- `tests/` : tests unitaires

## Remarques
- Le service lit la table `analytics_student_features` (ou `analytics_student_features` en SQLite) qui doit contenir au moins une colonne `student_id` et les colonnes listées dans `config/model_config.yaml`.
- En production, adaptez la persistance (upsert plutôt qu'append) et gérez la rotation des artefacts.

