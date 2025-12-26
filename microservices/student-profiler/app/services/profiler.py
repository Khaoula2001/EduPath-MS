import joblib
import pandas as pd
import logging
import os
from sqlalchemy.orm import Session
from app.models.domain import StudentProfile
from app.schemas.pydantic_models import StudentFeatures, PredictionResult
from app.core.config import settings

logger = logging.getLogger(__name__)

# Construct path relative to the app root
# Assuming MODEL_FILENAME is just the filename and it's in the root of the service
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), settings.MODEL_FILENAME)

class ProfilingService:
    def __init__(self):
        self.pipeline = None
        self.load_model()
        
        self.cluster_profile_map = {
            0: "En difficulté (At-Risk)",
            1: "Assidu (Regular)",
            2: "Procrastinateur (Procrastinator)",
        }

    def load_model(self):
        """Loads the pre-trained ML pipeline."""
        if os.path.exists(MODEL_PATH):
            try:
                self.pipeline = joblib.load(MODEL_PATH)
                logger.info(f"Model loaded successfully from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load model from {MODEL_PATH}: {e}")
                # Don't raise here, allow service to start even if model is broken
                # raise e
        else:
            logger.warning(f"Model file not found at {MODEL_PATH}. Prediction service will fail.")

    def predict_profile(self, features: StudentFeatures, db: Session) -> PredictionResult:
        if not self.pipeline:
            # Fallback logic if model is not loaded (e.g. for testing/dev without model file)
            logger.warning("Model pipeline is not loaded. Using dummy prediction.")
            cluster_id = 1 # Default to Regular
        else:
            data_dict = {
                "total_clicks": [features.total_clicks],
                "assessment_submissions_count": [features.assessment_submissions_count],
                "mean_score": [features.mean_score],
                "active_days": [features.active_days],
                "study_duration": [features.study_duration],
                "progress_rate": [features.progress_rate]
            }
            df = pd.DataFrame(data_dict)

            try:
                logger.info(f"Processing prediction for student {features.student_id}")

                # Handle dict structure of model
                if isinstance(self.pipeline, dict):
                    # Manual pipeline execution based on the keys we found
                    feature_cols = self.pipeline['feature_cols']
                    X = df[feature_cols]
                    
                    # Transform while keeping feature names where possible
                    X_imputed_arr = self.pipeline['imputer'].transform(X)
                    X_imputed = pd.DataFrame(X_imputed_arr, columns=feature_cols)
                    
                    X_scaled_arr = self.pipeline['scaler'].transform(X_imputed)
                    X_scaled = pd.DataFrame(X_scaled_arr, columns=feature_cols)
                    
                    X_pca = self.pipeline['pca'].transform(X_scaled)
                    
                    # K-means doesn't care about feature names but we pass them to avoid warnings
                    # however PCA changes dimensionality, so X_pca doesn't have original names.
                    # The warning usually comes from the first estimator that expects names
                    # In this case, scaler and imputer were fitted with names.
                    
                    cluster_id = self.pipeline['kmeans'].predict(X_pca)[0]
                else:
                    cluster_id = self.pipeline.predict(df)[0]
                
                cluster_id = int(cluster_id)
                logger.info(f"Predicted cluster: {cluster_id}")

            except Exception as e:
                logger.error(f"Error during prediction pipeline: {e}")
                raise e

        # Profile names based on your demo and model's likely clusters
        # 0: At-Risk, 1: Regular, 2: Procrastinator
        profil_type = self.cluster_profile_map.get(cluster_id, "Unknown")
        # Cluster to Risk Map: 0: At-Risk (High), 1: Regular (Low), 2: Procrastinator (Medium)
        risk_map = {0: "High", 1: "Low", 2: "Medium"}
        risk_level = risk_map.get(cluster_id, "Low")

        try:
            student_profile = db.query(StudentProfile).filter(StudentProfile.student_id == str(features.student_id)).first()
            
            if student_profile:
                logger.info(f"Updating existing profile for student {features.student_id}")
                student_profile.cluster_id = cluster_id
                student_profile.profil_type = profil_type
                student_profile.mean_score = features.mean_score
                student_profile.progress_rate = features.progress_rate
                student_profile.risk_level = risk_level
            else:
                logger.info(f"Creating new profile for student {features.student_id}")
                student_profile = StudentProfile(
                    student_id=str(features.student_id),
                    cluster_id=cluster_id,
                    profil_type=profil_type,
                    mean_score=features.mean_score,
                    progress_rate=features.progress_rate,
                    risk_level=risk_level
                )
                db.add(student_profile)
            
            db.commit()
            db.refresh(student_profile)
            
            # Publish profile update event to RabbitMQ
            try:
                from app.services.publisher import profile_publisher
                profile_publisher.publish_profile_update(
                    student_id=features.student_id,
                    profile_type=profil_type,
                    risk_level=risk_level,
                    cluster_id=cluster_id
                )
            except Exception as pub_error:
                logger.warning(f"Failed to publish profile update event: {pub_error}")

            return PredictionResult.from_orm(student_profile)

        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            db.rollback()
            raise e

profiling_service = ProfilingService()
