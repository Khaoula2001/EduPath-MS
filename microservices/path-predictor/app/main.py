from fastapi import FastAPI
from app.model import predict_probability
from app.alert_logic import generate_alert

app = FastAPI(title="PathPredictor AI Service")

@app.post("/predict")
def predict(student_data: dict):
    prob_success = predict_probability(student_data)
    prob_failure = 1 - prob_success
    alert = generate_alert(prob_success)

    return {
        "student_id": student_data.get("student_id"),
        "probability_success": round(prob_success, 2),
        "probability_failure": round(prob_failure, 2),
        "alert": alert
    }
