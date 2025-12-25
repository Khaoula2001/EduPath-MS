from fastapi import FastAPI, BackgroundTasks
import subprocess
import os
import logging
import uvicorn

app = FastAPI(title="PrepData API", description="API for controlling PrepData ETL tasks")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dossier des DAGs Airflow ou script direct
DAGS_PATH = os.getenv("AIRFLOW_DAGS_PATH", "/opt/airflow/dags")

@app.get("/health")
def health():
    return {"status": "UP", "service": "PrepData API"}

@app.get("/features")
def get_features(student_id: int):
    """
    Mock endpoint to return features for a student.
    In a real scenario, this would query the analytics database.
    """
    # Mock data
    return {
        "student_id": student_id,
        "total_clicks": 150,
        "active_days": 25,
        "last_active": "2023-10-27"
    }

@app.post("/run-etl")
async def run_etl(background_tasks: BackgroundTasks):
    """
    Déclenche le pipeline ETL en arrière-plan.
    En production, cela devrait appeler l'API Airflow.
    Ici, on simule ou on lance un script de déclenchement.
    """
    background_tasks.add_task(trigger_airflow_dag)
    return {"message": "ETL pipeline triggered", "status": "running"}

def trigger_airflow_dag():
    """
    Utilise la CLI Airflow pour déclencher le DAG.
    """
    try:
        # Commande pour déclencher le DAG via Docker exec ou CLI
        # Supposant que l'API tourne dans le même environnement qu'Airflow
        logger.info("Triggering DAG prepadata_complete_etl...")
        result = subprocess.run(
            ["airflow", "dags", "trigger", "prepadata_complete_etl"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info(f"DAG triggered successfully: {result.stdout}")
        else:
            logger.error(f"Failed to trigger DAG: {result.stderr}")
    except Exception as e:
        logger.error(f"Error triggering DAG: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
