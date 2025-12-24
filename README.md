# EduPath-MS — Learning Analytics & Recommendations

**EduPath-MS** est une plateforme intelligente basée sur une architecture microservices conçue pour accompagner la réussite des étudiants dans l'enseignement supérieur. Le système analyse les traces d'apprentissage issues des LMS (Learning Management Systems) pour prédire les risques de décrochage et proposer des recommandations pédagogiques personnalisées.

---

## Architecture du Système

Le projet adopte une architecture microservices sécurisée et orientée événements, orchestrée par **Docker Compose**.

### Flux de Données Principal
1.  **Extraction** : Le `LMS Connector` récupère les notes et logs depuis Moodle et les stocke dans une base brute.
2.  **Transformation (ETL)** : `PrepaData` (via **Airflow**) nettoie et transforme ces données en indicateurs de performance (KPIs).
3.  **Intelligence Artificielle** :
    -   `StudentProfiler` segmente les étudiants par comportement (K-Means).
    -   `PathPredictor` prédit les risques d'échec (XGBoost).
    -   `RecoBuilder` suggère des ressources adaptées (BERT & Faiss).
4.  **Communication & Alerting** : Les alertes critiques sont diffusées via **RabbitMQ**.
5.  **Restitution** : Les interfaces (Web & Mobile) consomment les données via une **API Gateway** centralisée.

---

## Composants & Microservices

Tous les services sont centralisés derrière l'**API Gateway** (Port `4000`).

| Service | Technologie | Port Interne | Rôle Principal |
| :--- | :--- | :--- | :--- |
| **API Gateway** | Node.js / Express | `4000` | Point d'entrée unique, Sécurité JWT et Proxy. |
| **LMS Connector** | Node.js / Express | `3001` | Synchronisation avec les APIs Moodle. |
| **PrepaData** | FastAPI / Airflow | `8001` | Pipeline ETL automatisé et Feature Engineering. |
| **StudentProfiler** | FastAPI | `8000` | Clustering et détection de profils types. |
| **PathPredictor** | FastAPI | `8002` | Prédiction de réussite et envoi d'alertes RabbitMQ. |
| **RecoBuilder** | FastAPI / BERT | `8003` | Moteur de recommandation sémantique. |
| **TeacherConsole API**| FastAPI | `8004` | Backend pour le tableau de bord enseignant. |
| **StudentCoach API** | FastAPI | `8005` | Backend pour l'application mobile étudiante. |

---

## Sécurité & Accès

Le système utilise une simulation de flux **OAuth2 avec JWT** :
- **Authentification** : Obtenez un token via `POST http://localhost:4000/login`.
- **Autorisation** : Toutes les requêtes vers les microservices via la Gateway doivent inclure le header `Authorization: Bearer <votre_token>`.

---

## Infrastructure & Stockage

-   **PostgreSQL** : Isolation totale. Chaque microservice possède sa propre base de données dédiée (`lms_db`, `prepadata_db`, `profiler_db`, etc.).
-   **RabbitMQ** : Gestion des messages asynchrones pour les alertes de décrochage.
-   **MinIO** (`9999`) : Stockage objet pour les ressources pédagogiques multimédias.
-   **MLflow** (`5000`) : Suivi des expériences et versionnage des modèles ML.
-   **Apache Airflow** (`8081`) : Orchestration des pipelines de données.
-   **Elasticsearch** (`9200`) : Moteur de recherche et d'analyse.

---

## Installation et Configuration

### Prérequis
-   **Docker** & **Docker Compose**
-   **Git**

### Démarrage Rapide

1.  **Cloner le projet** :
    ```bash
    git clone https://github.com/NisrineLachguer/EduPath-MS.git
    cd EduPath-MS
    ```

2.  **Lancer l'ensemble des services** :
    ```bash
    docker-compose up -d --build
    ```
    *Note : L'initialisation complète (PostgreSQL + Airflow) peut prendre 1 à 2 minutes.*

3.  **Initialiser les données de recommandation** (Optionnel) :
    L'indexation initiale se fait automatiquement au démarrage du service `RecoBuilder`.

---

## Interfaces Utilisateurs

-   **Teacher Console (Angular)** : Dashboard permettant aux enseignants de visualiser les statistiques de la classe et les alertes de risque.
-   **Student Coach (Flutter)** : Application mobile pour les étudiants (progression, coaching et ressources).

---

## Fonctionnalités Clés
-   **Isolation des Données** : Architecture propre avec une base par service.
-   **Gateway Centralisée** : Gestion unifiée du routage et de la sécurité.
-   **Alertes en Temps Réel** : Notification instantanée des comportements à risque via RabbitMQ.
-   **IA Avancée** : Utilisation de modèles Transformers et de Gradient Boosting pour l'analyse prédictive.
