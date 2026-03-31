# 🎓📘 EduPath-MS — Intelligent Learning Analytics & Recommendations

<div align="center">
  <picture>
    <source srcset="https://github.com/user-attachments/assets/88387013-8b25-4da8-a9e7-193cb7223aa2" media="(prefers-color-scheme: dark)">
    <img src="screens/logo_placeholder.png" width="260" alt="EduPath-MS Logo">
  </picture>
</div>

**EduPath-MS** is a modular microservices-based system designed to transform raw learner logs into actionable educational interventions. The platform covers the entire data lifecycle, from multi-source LMS data ingestion (Moodle) to advanced semantic analysis using Transformer-based models (BERT), enabling the generation of individualized learning paths and proactive pedagogical decision-making.

---

## Contents

- [Overview](#overview)
- [Features](#features)
- [Monorepo Layout](#monorepo-layout)
- [Architecture](#architecture)
- [Microservices Portfolio](#microservices-portfolio)
- [Metrics (Model Quality)](#metrics-model-quality)
- [Quick Start (Docker)](#quick-start-docker)
- [Environment Variables](#environment-variables)
- [Test Scenarios](#test-scenarios)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

- **Goal:** Enhance student success by predicting dropout risks and providing personalized learning recommendations.
- **How:** Ingest LMS logs → Clean & Feature Engineer (Airflow) → Behavioral Profiling (K-Means) → Risk Prediction (XGBoost) → Semantic Recommendation (BERT + Faiss).
- **Why Microservices:** Ensures scalability, modularity, and technology flexibility (Node.js, Python, Java, Flutter, Angular).

---

## Features

- 📊 **Learning Analytics:** Real-time monitoring of student engagement and performance.
- 🤖 **Predictive Modeling:** Early warning system for at-risk students using XGBoost.
- 🧩 **Behavioral Profiling:** Automated student segmentation (PCA + K-Means).
- 📚 **Smart Recommendations:** Semantic resource matching via BERT embeddings.
- 📱 **Multi-platform:** Dedicated interfaces for teachers (Web) and students (Mobile).
- ⚙️ **Event-Driven:** Asynchronous communication via RabbitMQ for high responsiveness.

---

## Monorepo Layout

```
EduPath-MS/
├─ microservices/
│  ├─ api-gateway/            # Express.js Entry Point & Auth
│  ├─ eureka-server/          # Service Discovery (Spring Boot)
│  ├─ lms-connector/          # Moodle Ingestion (Node.js)
│  ├─ prepa-data/             # ETL & Orchestration (Python + Airflow)
│  ├─ student-profiler/       # Clustering ML Service (FastAPI)
│  ├─ path-predictor/         # Risk Prediction ML Service (FastAPI)
│  ├─ reco-builder/           # Semantic Recommender (FastAPI + BERT)
│  ├─ teacher-console-api/    # BFF for Teacher Web Dashboard
│  ├─ student-coach-api/      # BFF for Student Mobile App
│  ├─ TeacherConsole/         # Angular Frontend
│  └─ student_coach/          # Flutter Mobile App
├─ docker-compose.yml
└─ README.md
```

---

## Architecture

![EduPath-MS Architecture](screens/archis.png)

1.  **Ingestion**: `LMS Connector` polls raw data from Moodle LMS.
2.  **Processing (ETL)**: `PrepaData` (Airflow) transforms logs into analytical features.
3.  **Intelligence**: `Student Profiler`, `Path Predictor`, and `Reco Builder` provide ML insights.
4.  **Delivery**: `API Gateway` routes data to `Teacher Console` and `Student Coach`.

---

## Microservices Portfolio

| Service | Tech Stack | Port | Description |
| :--- | :--- | :--- | :--- |
| **API Gateway** | Node.js / Express | `4000` | Unified entry point, JWT auth. |
| **Eureka Server** | Java / Spring Boot | `8761` | Service Registry & Discovery. |
| **LMS Connector** | Node.js / Express | `3001` | Moodle API synchronization. |
| **PrepaData** | Python / Airflow | `8081` | ETL pipelines & orchestration. |
| **Student Profiler**| Python / FastAPI | `8000` | Behavioral clustering (K-Means). |
| **Path Predictor** | Python / FastAPI | `8002` | Risk prediction (XGBoost). |
| **Reco Builder** | Python / FastAPI | `8003` | Recommendations (BERT + Faiss). |
| **Teacher Console**| Angular | `8088` | Web Dashboard for instructors. |
| **Student Coach** | Flutter | N/A | Mobile App for students. |

---

## Metrics (Model Quality)

Evaluated on the **xAPI-Edu-Data** dataset (480 students, 16 features).

### 📈 Risk Prediction (XGBoost)
| Dataset | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Training** | 0.958 | 0.956 | 0.961 | 0.958 | 0.973 |
| **Validation** | 0.949 | 0.943 | 0.952 | 0.947 | 0.968 |
| **Test** | **0.946** | **0.941** | **0.948** | **0.944** | **0.965** |

### 👥 Student Profiling (PCA + K-Means)
| Method | Silhouette Score | Execution Time | Interpretability |
| :--- | :---: | :---: | :---: |
| **PCA + KMeans** | **0.58** | **2.3s** | **High** |
| PCA + GMM | 0.49 | 8.1s | Medium |

---

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/Khaoula2001/EduPath-MS.git
cd EduPath-MS

# 2. Start the platform
docker-compose up -d --build
```
> *Note: First-time build may take 10-15 minutes due to ML model (BERT) downloads.*

---

## Environment Variables

| Variable | Service | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `POSTGRES_PASSWORD` | Postgres | `prepadata_pwd` | DB Root Password |
| `RABBITMQ_DEFAULT_PASS`| RabbitMQ | `edupath` | Broker Password |
| `MOODLE_TOKEN` | LMS Connector| `340fe84e...` | Moodle API Access Token |
| `EUREKA_SERVER` | ML Services | `http://eureka...`| Service Discovery URL |
| `MLFLOW_S3_ENDPOINT` | MLflow | `http://minio...` | Artifact Storage URL |

---

## Test Scenarios

### 1. Full Integration (Moodle -> Analytics)
1. Log in to **Moodle** (`localhost:80`) and simulate activity.
2. Trigger the **Airflow DAG** via `localhost:8081`.
3. Verify data flow in **PostgreSQL**.
4. Observe updated risks in **Teacher Console** (`localhost:8088`).

---

## Roadmap

- [ ] Multi-LMS interoperability (Canvas, Blackboard).
- [ ] Reinforcement Learning for adaptive learning pathways.
- [ ] XAI (Explainable AI) for model prediction transparency.
- [ ] Real-time mobile notifications via Firebase.

---

## Contributing

We welcome contributions! Please follow our code style and submit a PR.

### **Contributors**
- **OUEDRHIRI Oumayma** — [ResearchGate](https://www.researchgate.net/profile/Oumayma-Ouedrhiri)
- **TABBAA Hiba** — [ResearchGate](https://www.researchgate.net/profile/Hiba-Tabbaa)
- **LACHGAR Mohamed** — [ResearchGate](https://www.researchgate.net/profile/Mohamed-Lachgar)
- **AIT BEL MEHDI Khaoula** — [GitHub](https://github.com/Khaoula2001)
- **LACHGUER Nisrine** — [GitHub](https://github.com/NisrineLachguer)
- **EL AMRANI Omar** — [GitHub](https://github.com/omarox844)
- **NADI Hajar** — [GitHub](https://github.com/NadiHajar)

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---
*Made with ❤️ by EduPath Team.*
