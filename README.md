# 🎓 EduPath-MS — Learning Analytics & Recommandations

**EduPath-MS** est une plateforme intelligente basée sur une architecture microservices conçue pour accompagner la réussite des étudiants dans l'enseignement supérieur. Le système analyse les traces d'apprentissage issues des LMS (Learning Management Systems) pour prédire les risques de décrochage et proposer des recommandations pédagogiques personnalisées.

---

## 🏗️ Architecture du Système

Le projet adopte une architecture **orientée événements (Event-Driven)** orchestrée par un bus de messages (Kafka/RabbitMQ) au sein d'un environnement **Docker**.

Architecture EduPath-MS

![WhatsApp Image 2025-12-22 at 01 58 45](https://github.com/user-attachments/assets/ab2c9e3f-e140-4064-862e-550611224901)


### 🔄 Flux de Données
1. **Extraction** : Les traces brutes sont récupérées de Moodle/Canvas.
2. **Transformation** : Nettoyage et calcul d'indicateurs (engagement, score).
3. **Analyse & Profiling** : Classification des étudiants par comportements.
4. **Prédiction** : Calcul des probabilités de réussite/échec.
5. **Recommandation** : Suggestion de ressources via IA sémantique.
6. **Restitution** : Tableaux de bord pour les profs et coaching mobile pour les élèves.

---

## 🛠️ Composants & Microservices

### 🔌 Microservices Backend (Data & IA)

| Service | Technologie | Port | Description | Dépendances Clés |
| :--- | :--- | :--- | :--- | :--- |
| **LMSConnector** | Node.js | `3001` | Synchronisation des logs (Moodle/Canvas). | `axios`, `oauth2`, `pg` |
| **PrepaData** | Python / Airflow | `8081` | ETL, agrégation temporelle et indicateurs. | `pandas`, `airflow`, `sqlalchemy` |
| **StudentProfiler** | FastAPI | `8000` | Clustering et détection de typologies. | `scikit-learn`, `KMeans`, `PCA` |
| **PathPredictor** | FastAPI | `8002` | Prédiction des trajectoires et risques. | `XGBoost`, `MLflow`, `pydantic` |
| **RecoBuilder** | Flask / Python | `8003` | Moteur de recommandation sémantique. | `BERT (Transformers)`, `Faiss`, `numpy` |
| **TeacherConsole-API**| FastAPI | `8004` | API de gestion pur les enseignants. | `fastapi`, `postgresql` |
| **StudentCoach-API** | FastAPI | `8005` | API de coaching et feedback étudiant. | `fastapi`, `pydantic` |

### 💻 Interfaces (Frontend & Mobile)

*   **TeacherConsole (Angular)** : Dashboard analytique complet avec visualisations (Chart.js) pour identifier les groupes d'étudiants à risque.
*   **StudentCoach (Flutter)** : Application mobile permettant aux étudiants de suivre leur progression et d'accéder aux ressources recommandées.

### 🗄️ Infrastructure & Stockage

*   **PostgreSQL** : Multiples instances pour les données analytiques, historiques et métadonnées.
*   **MinIO** `9000` : Stockage objet pour les contenus multimédias (vidéos, PDF).
*   **RabbitMQ** : Bus d'événements pour la communication asynchrone.
*   **MLflow** `5000` : Tracking des modèles de Machine Learning.
*   **API Gateway** `4000` : Port d'entrée unique pour les requêtes front-end.

---

## 🚀 Installation et Configuration

### Prérequis
*   **Docker** & **Docker Compose**
*   **Python 3.10+** (pour le développement local)
*   **Node.js** (pour LMSConnector)

### Installation rapide

1. **Cloner le projet** :
   ```bash
   git clone https://github.com/Khaoula2001/EduPath-MS.git
   cd EduPath-MS
   ```

2. **Lancer l'infrastructure (Docker)** :
   ```bash
   docker-compose up -d --build
   ```

3. **Initialiser les ressources (Seeding)** :
   ```bash
   python microservices/recco-builder/seed_resources.py
   ```

---

## ✨ Fonctionnalités Clés

*    **Détection Précoce** : Identification automatique des étudiants "At-Risk" via XGBoost.
*    **Profiling Comportemental** : Segmentation (Procrastinateurs, Assidus, Fragiles).
*    **Recommandations Dynamiques** : Adaptation des suggestions selon le profil et le niveau de risque.
*    **Alerting Enseignant** : Notifications en temps réel lors de dérives de performance.
*    **Support Multimédia** : Intégration de vidéos et quiz interactifs via MinIO.

---

## 🎯 Objectifs du Projet

*   **Réduire le taux d'abandon** scolaire par un suivi personnalisé.
*   **Automatiser** l'analyse des traces d'apprentissage massives.
*   **Optimiser** le temps des enseignants grâce à des outils de remédiation ciblés.
*   **Favoriser l'engagement** étudiant par des feedbacks motivants.

---

## 📝 Licence
Ce projet est développé dans le cadre de la recherche en **Learning Analytics** .
