# ...existing code...
import os
import joblib
import yaml
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from datetime import datetime
from . import db

# Load config
_cfg = None

def load_config():
    global _cfg
    if _cfg is None:
        cfg_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'model_config.yaml')
        # allow override path from env
        cfg_path = os.getenv('MODEL_CONFIG_PATH', cfg_path)
        with open(cfg_path, 'r', encoding='utf-8') as f:
            _cfg = yaml.safe_load(f)
    return _cfg


def _prepare_features(df: pd.DataFrame, used_columns: list) -> pd.DataFrame:
    # Ensure student_id is present
    if 'student_id' not in df.columns:
        raise ValueError('student_id column missing from features')
    # Select only numeric columns used for modeling (exclude student_id)
    cols = [c for c in used_columns if c in df.columns and c != 'student_id']
    if len(cols) == 0:
        raise ValueError('No feature columns found in data')
    X = df[cols].fillna(0).astype(float)
    return df[['student_id']].copy(), X, cols


def train_and_persist(artifact_path: str = None) -> dict:
    """Charge les features depuis la DB, entraîne PCA + KMeans, sauvegarde l'artifact et écrit les profils."""
    cfg = load_config()
    used_columns = cfg['features']['used_columns']

    # Read data
    try:
        features_df = db.read_student_features()
    except Exception as e:
        raise RuntimeError(f"Failed to read student features: {e}")

    if features_df.empty:
        return {"status": "no_data", "n_students": 0}

    ids_df, X, feature_cols = _prepare_features(features_df, used_columns)

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA
    n_comp = min(cfg['model'].get('pca_components', 5), X_scaled.shape[1])
    pca = PCA(n_components=n_comp, random_state=cfg['model'].get('random_state', 42))
    X_pca = pca.fit_transform(X_scaled)

    # KMeans
    n_clusters = cfg['model'].get('n_clusters', 4)
    km = KMeans(n_clusters=n_clusters, random_state=cfg['model'].get('random_state', 42))
    clusters = km.fit_predict(X_pca)

    # Prepare profiles DataFrame
    profiles = pd.DataFrame({
        'student_id': ids_df['student_id'].values,
        'cluster': clusters,
        'profile_ts': pd.Timestamp.now()
    })

    # Save artifacts
    artifacts_dir = artifact_path or cfg['artifacts'].get('path', './artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    model_artifact = os.path.join(artifacts_dir, f'student_profiler_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.joblib')
    joblib.dump({'scaler': scaler, 'pca': pca, 'kmeans': km, 'feature_cols': feature_cols}, model_artifact)

    # Persist profiles (append)
    db.write_student_profiles(profiles)

    return {
        'status': 'trained',
        'n_students': len(profiles),
        'artifact': model_artifact,
        'n_clusters': int(n_clusters)
    }


def get_latest_profile(student_id) -> dict | None:
    """Récupère le profil le plus récent d'un étudiant depuis la table analytics_student_profiles."""
    # Query to get latest profile for student
    q = f"SELECT * FROM analytics_student_profiles WHERE student_id = :sid ORDER BY profile_ts DESC LIMIT 1"
    engine = db.get_engine()
    with engine.connect() as conn:
        res = conn.execute("SELECT * FROM analytics_student_profiles WHERE student_id = :sid ORDER BY profile_ts DESC LIMIT 1", {'sid': student_id})
        row = res.first()
    if row is None:
        return None
    return dict(row._mapping)

# ...existing code...
