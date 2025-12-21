# StudentProfiler Microservice

Ce microservice est responsable de l'analyse des comportements des étudiants et de leur classification (clustering) basés sur des données d'apprentissage.

## Architecture

Le projet suit une architecture modulaire basée sur FastAPI :

```
student-profiler/
├── app/
│   ├── api/                 # Gestion des routes API (Endpoints)
│   ├── core/                # Configuration et connexion Base de Données
│   ├── models/              # Modèles SQLAlchemy (Table PostgreSQL)
│   ├── schemas/             # Schémas Pydantic (Validation des données)
│   ├── services/            # Logique Métier (Chargement modèle ML, Prédiction)
│   └── main.py              # Point d'entrée de l'application
├── Dockerfile               # Configuration Docker
├── requirements.txt         # Dépendances Python
└── student_profiler_model.joblib # Modèle ML pré-entraîné
```

## Fonctionnalités

1.  **Prédiction de Cluster** : Reçoit des metrics étudiants, applique un pipeline ML (Imputation, Scaling, PCA, KMeans) et retourne le cluster et le type de profil.
2.  **Stockage** : Sauvegarde ou met à jour le profil étudiant dans une base PostgreSQL (`student_profiles`).

## Installation et Exécution avec Docker Compose (Recommandé)

Le service est configuré pour fonctionner dans l'écosystème **EduPath-MS**.

```bash
docker-compose up -d postgres student-profiler
```

Le service sera accessible sur `http://localhost:8000`.

## Utilisation avec Postman

### Endpoint : `/predict_clusters`
- **Méthode** : `POST`
- **URL** : `http://localhost:8000/predict_clusters`
- **Headers** : `Content-Type: application/json`
- **Body (Raw JSON)** :

```json
{
  "student_id": 12345,
  "total_clicks": 1500,
  "assessment_submissions_count": 5,
  "mean_score": 85.5,
  "active_days": 120,
  "study_duration": 4500.0,
  "progress_rate": 0.92
}
```

### Réponse Attendue (Exemple)
```json
{
    "student_id": 12345,
    "cluster_id": 1,
    "profil_type": "Assidu (Regular)",
    "timestamp": "2025-12-21T17:50:00.000000"
}
```

### Health Check
- **Méthode** : `GET`
- **URL** : `http://localhost:8000/health`

## Docker

Pour construire et lancer avec Docker manuellement :

```bash
docker build -t student-profiler .
docker run -p 8000:8000 --env PG_HOST=host.docker.internal --env PG_USER=prepadata --env PG_PASSWORD=prepadata_pwd --env PG_DB=analytics student-profiler
```
