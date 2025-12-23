import requests
import numpy as np

# URLs internes Docker (DNS par nom de service)
STUDENT_PROFILER_URL = "http://student-profiler:8001/profile"
PREPADATA_URL = "http://prepadata:8002/features"

# Ordre EXACT utilisé à l'entraînement
FEATURES = [
    "mean_score",
    "total_clicks",
    "active_days",
    "progress_rate",
    "cluster_id"
]

def fetch_features_from_services(student_id: int) -> dict:
    """
    Récupère les features depuis les microservices amont
    """

    # 1️⃣ StudentProfiler
    profiler_response = requests.get(
        STUDENT_PROFILER_URL,
        params={"student_id": student_id},
        timeout=5
    )
    profiler_response.raise_for_status()
    profiler = profiler_response.json()

    # 2️⃣ PrepaData
    prepadata_response = requests.get(
        PREPADATA_URL,
        params={"student_id": student_id},
        timeout=5
    )
    prepadata_response.raise_for_status()
    prepadata = prepadata_response.json()

    # 3️⃣ Fusion des features
    return {
        "mean_score": profiler["mean_score"],
        "progress_rate": profiler["progress_rate"],
        "cluster_id": profiler["cluster_id"],  # vient du StudentProfiler
        "total_clicks": prepadata["total_clicks"],
        "active_days": prepadata["active_days"]
    }


def build_model_input(student_id: int) -> np.ndarray:
    """
    Construit l'input numpy attendu par XGBoost
    """
    features = fetch_features_from_services(student_id)

    return np.array([[features[f] for f in FEATURES]])


def predict_probability(student_id: int, model) -> float:
    """
    Prédit la probabilité de réussite
    """
    X = build_model_input(student_id)
    return float(model.predict_proba(X)[0][1])
