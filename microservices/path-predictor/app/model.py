import requests
import numpy as np
import joblib
import os

# URLs internes Docker (DNS par nom de service)
STUDENT_PROFILER_URL = "http://student-profiler:8000/profile"
PREPADATA_URL = "http://prepadata:8001/features"

# Ordre EXACT utilisé à l'entraînement
FEATURES = [
    "mean_score",
    "total_clicks",
    "active_days",
    "progress_rate",
    "cluster_id"
]

# Load model at module level
# Try multiple locations for the model file
MODEL_PATHS = [
    os.path.join(os.path.dirname(__file__), "../model/xgboost_model.pkl"),
    os.path.join(os.path.dirname(__file__), "../path_predictor_xgboost.pkl"),
    "/app/path_predictor_xgboost.pkl"
]

model = None
for path in MODEL_PATHS:
    if os.path.exists(path):
        try:
            model = joblib.load(path)
            print(f"Model loaded from {path}")
            break
        except Exception as e:
            print(f"Warning: Could not load model from {path}: {e}")

if model is None:
    print("Warning: No model file found. Predictions will be mocked.")

def fetch_features_from_services(student_id: int) -> dict:
    """
    Récupère les features depuis les microservices amont
    """
    # Mock implementation for now if services are not reachable
    # In production, this should handle connection errors gracefully
    try:
        # 1️⃣ StudentProfiler
        profiler_response = requests.get(
            f"{STUDENT_PROFILER_URL}/{student_id}",
            timeout=5
        )
        if profiler_response.status_code == 200:
            profiler = profiler_response.json()
        else:
            # Fallback mock data
            profiler = {"mean_score": 75.0, "progress_rate": 0.5, "cluster_id": 1}

        # 2️⃣ PrepaData
        # prepadata_response = requests.get(
        #     PREPADATA_URL,
        #     params={"student_id": student_id},
        #     timeout=5
        # )
        # prepadata_response.raise_for_status()
        # prepadata = prepadata_response.json()

        # Mock prepadata for now as endpoint might differ
        prepadata = {"total_clicks": 100, "active_days": 10}

        # 3️⃣ Fusion des features
        return {
            "mean_score": profiler.get("mean_score", 0),
            "progress_rate": profiler.get("progress_rate", 0),
            "cluster_id": profiler.get("cluster_id", 0),
            "total_clicks": prepadata.get("total_clicks", 0),
            "active_days": prepadata.get("active_days", 0)
        }
    except Exception as e:
        print(f"Error fetching features: {e}")
        # Return default values to avoid crashing
        return {
            "mean_score": 50.0,
            "progress_rate": 0.0,
            "cluster_id": 0,
            "total_clicks": 0,
            "active_days": 0
        }


def build_model_input(student_data: dict) -> np.ndarray:
    """
    Construit l'input numpy attendu par XGBoost
    """
    # If student_data contains the features directly, use them
    # Otherwise fetch them using student_id

    if "mean_score" in student_data:
        features = student_data
    else:
        student_id = student_data.get("student_id")
        if student_id:
            features = fetch_features_from_services(student_id)
        else:
             features = {f: 0 for f in FEATURES}

    # Ensure all features exist
    row = []
    for f in FEATURES:
        row.append(features.get(f, 0))

    return np.array([row])


def predict_probability(student_data: dict) -> float:
    """
    Prédit la probabilité de réussite
    """
    if model is None:
        return 0.5 # Default if model not loaded

    X = build_model_input(student_data)
    try:
        return float(model.predict_proba(X)[0][1])
    except Exception as e:
        print(f"Prediction error: {e}")
        return 0.0
