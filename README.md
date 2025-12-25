# EduPath-MS — Learning Analytics & Recommendations

**EduPath-MS** is an intelligent platform based on a microservices architecture designed to support student success in higher education. The system analyzes learning traces from LMS (Learning Management Systems) to predict dropout risks and provide personalized pedagogical recommendations.

---

## System Architecture

The project adopts a secure, event-driven microservices architecture, fully containerized via **Docker** and orchestrated by **Docker Compose**.

### Main Data Flow
1.  **Extraction**: The `LMS Connector` retrieves grades and logs from Moodle.
2.  **Transformation (ETL)**: `PrepaData` (via **Airflow**) cleans and transforms this data into performance indicators (KPIs).
3.  **Artificial Intelligence**:
    -   `StudentProfiler` segments students by behavior (K-Means).
    -   `PathPredictor` predicts dropout risks (XGBoost).
    -   `RecoBuilder` suggests adapted resources (BERT & Faiss).
4.  **Communication & Alerting**: Critical alerts are broadasted via **RabbitMQ**.
5.  **Restitution**: Interfaces consume data via a centralized **API Gateway**.

---

## Project Structure

```
EduPath-MS/
├── microservices/
│   ├── api-gateway/          # Unique entry point (Node.js)
│   ├── lms-connector/        # Moodle Connector (Node.js)
│   ├── prepa-data/           # ETL Pipeline & API (Python/Airflow)
│   ├── student-profiler/     # Student Clustering (FastAPI)
│   ├── path-predictor/       # Success Prediction (FastAPI)
│   ├── recco-builder/        # Recommendation Engine (FastAPI)
│   ├── teacher-console-api/  # Teacher Dashboard Backend (FastAPI)
│   ├── student-coach-api/    # Student App Backend (FastAPI)
│   ├── TeacherConsole/       # Teacher Frontend (Angular)
│   └── student_coach/        # Student Mobile App (Flutter)
├── sql/                      # SQL Initialization Scripts
├── docker-compose.yml        # Multi-service Orchestration
├── Jenkinsfile               # Dockerized CI/CD Pipeline
└── README.md                 # Documentation
```

---

## Components & Microservices

All services are accessible via the **API Gateway** (Port `4000`).

| Service | Technology | Port | Main Role |
| :--- | :--- | :--- | :--- |
| **API Gateway** | Node.js / Express | `4000` | Gateway, JWT Security and Routing Proxy. |
| **LMS Connector** | Node.js / Express | `3001` | Interface with Moodle APIs. |
| **PrepaData** | FastAPI / Airflow | `8001` | ETL, Feature Engineering and Airflow orchestration. |
| **StudentProfiler** | FastAPI | `8000` | Behavioral student segmentation. |
| **PathPredictor** | FastAPI | `8002` | Success prediction and RabbitMQ alerting. |
| **RecoBuilder** | FastAPI / BERT | `8003` | Semantic similarity-based recommendations. |
| **TeacherConsole API**| FastAPI | `8004` | Backend for the Angular dashboard. |
| **StudentCoach API** | FastAPI | `8005` | Backend for the Flutter application. |

---

## CI/CD & Pipeline

The project includes a high-performance **Jenkinsfile** that automates:
-   Source code checkout.
-   Parallel build of all microservice Docker images.
-   Automatic versioning via `BUILD_NUMBER`.
-   Image tagging (`latest` and versioned) for the Docker registry.

---

## Infrastructure & Storage

-   **PostgreSQL**: Dedicated databases per service (`lms_db`, `prepadata_db`, etc.).
-   **RabbitMQ**: Message broker for asynchronous communication (Alerting).
-   **MinIO** (`9999`): S3-compatible storage for pedagogical documents.
-   **MLflow** (`5000`): Machine Learning model lifecycle management.
-   **Apache Airflow** (`8081`): Visual orchestration of ETL pipelines.
-   **Elasticsearch** (`9200`): Log analysis and search.

---

## Installation

### Prerequisites
-   **Docker Desktop** (with Docker Compose)
-   **Jenkins** (Optional, for CI/CD)

### Startup

1.  **Cloning**:
    ```bash
    git clone https://github.com/NisrineLachguer/EduPath-MS.git
    cd EduPath-MS
    ```

2.  **Launch (Build & Start)**:
    ```bash
    docker-compose up -d --build
    ```
    *Note: The initial download of AI models (BERT) may take some time during the first build.*

---

## Security

Access to microservices is protected by **JWT** via the Gateway:
1.  Authentication via `POST /login`.
2.  Token inclusion in the `Authorization: Bearer <your_token>` header.

---

## Interfaces

-   **Teacher Dashboard**: Powerful Web interface developed in Angular.
-   **Student App**: Native mobile experience via Flutter.
