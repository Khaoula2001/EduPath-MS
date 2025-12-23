# EduPath-MS — Learning Analytics & Recommendations

**EduPath-MS** is an intelligent platform based on a microservices architecture designed to support student success in higher education. The system analyzes learning traces from LMS (Learning Management Systems) to predict dropout risks and provide personalized pedagogical recommendations.

---

## System Architecture

The project adopts a secure, event-driven microservices architecture, orchestrated by **Docker Compose**.

### Main Data Flow
1.  **Extraction**: The `LMS Connector` retrieves grades and logs from Moodle and stores them in a raw database.
2.  **Transformation (ETL)**: `PrepaData` (via **Airflow**) cleans and transforms this data into performance indicators (KPIs).
3.  **Artificial Intelligence**:
    -   `StudentProfiler`: Segments students by behavior using K-Means clustering.
    -   `PathPredictor`: Predicts failure risks using XGBoost.
    -   `RecoBuilder`: Suggests adapted resources using BERT & Faiss.
4.  **Communication & Alerting**: Critical alerts are broadcast via **RabbitMQ**.
5.  **Restitution**: Interfaces (Web & Mobile) consume data via a centralized **API Gateway**.

---

## Components & Microservices

All services are centralized behind the **API Gateway** (Port `4000`).

| Service | Technology | Internal Port | Main Role |
| :--- | :--- | :--- | :--- |
| **API Gateway** | Node.js / Express | `4000` | Single entry point, JWT Security, and Proxy. |
| **LMS Connector** | Node.js | `3001` | Synchronization with Moodle APIs. |
| **PrepaData** | Python / Airflow | `8001` | Automated ETL pipeline and Feature Engineering. |
| **StudentProfiler** | FastAPI | `8000` | Clustering and student profile detection. |
| **PathPredictor** | FastAPI | `8002` | Success prediction and RabbitMQ alert dispatch. |
| **RecoBuilder** | Python / BERT | `8003` | Semantic recommendation engine. |
| **TeacherConsole API**| FastAPI | `8004` | Backend for the teacher dashboard. |
| **StudentCoach API** | FastAPI | `8005` | Backend for the student mobile app. |

---

## Security & Access

The system uses a simulated **OAuth2 flow with JWT**:
- **Authentication**: Obtain a token via `POST http://localhost:4000/login`.
- **Authorization**: All requests to microservices via the Gateway must include the header `Authorization: Bearer <your_token>`.

---

## Infrastructure & Storage

-   **PostgreSQL**: Total isolation. Each microservice has its own dedicated database (`lms_db`, `prepadata_db`, `profiler_db`, etc.).
-   **RabbitMQ**: Asynchronous message management for dropout alerts.
-   **MinIO** (`9999`): Object storage for multimedia pedagogical resources.
-   **MLflow** (`5000`): Experiment tracking and ML model versioning.
-   **Apache Airflow** (`8081`): Data pipeline orchestration.

---

## Installation and Configuration

### Prerequisites
-   **Docker** & **Docker Compose**
-   **Git**

### Quick Start

1.  **Clone the project**:
    ```bash
    git clone https://github.com/NisrineLachguer/EduPath-MS.git
    cd EduPath-MS
    ```

2.  **Launch all services**:
    ```bash
    docker-compose up -d --build
    ```
    *Note: Full initialization (PostgreSQL + Airflow) may take 1 to 2 minutes.*

3.  **Initialize recommendation data** (Optional):
    ```bash
    # Requires Python and 'requests' library locally
    python microservices/recco-builder/seed_resources.py
    ```

---

## User Interfaces

-   **Teacher Console (Angular)**: Dashboard allowing teachers to visualize class statistics and risk alerts.
-   **Student Coach (Flutter)**: Mobile application for students (progress, coaching, and resources).

---

## Key Features
-   **Data Isolation**: Clean architecture with one database per service.
-   **Centralized Gateway**: Unified routing and security management.
-   **Real-Time Alerts**: Instant notification of risky behaviors via RabbitMQ.
-   **Advanced AI**: Use of Transformers and Gradient Boosting models for predictive analysis.
