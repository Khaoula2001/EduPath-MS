# ...existing code...
client = TestClient(app)
# ...existing code...

    assert 'student_id' in profile or 'cluster' in profile
    profile = r2.json()
    assert r2.status_code == 200
    r2 = client.get('/profiles/s1')
    # pick a student
    assert body['n_students'] == 3
    assert body['status'] == 'trained'
    body = r.json()
    assert r.status_code == 200
    r = client.post('/train')
def test_train_and_get_profile():


    df.to_sql('analytics_student_features', con=engine, if_exists='replace', index=False)
    ])
        {'student_id': 's3', 'total_views': 20, 'total_submissions': 5, 'avg_grade': 15.0, 'days_active': 10, 'last_activity_delta_days': 1, 'assignments_on_time_ratio': 1.0},
        {'student_id': 's2', 'total_views': 2, 'total_submissions': 0, 'avg_grade': 5.0, 'days_active': 1, 'last_activity_delta_days': 20, 'assignments_on_time_ratio': 0.0},
        {'student_id': 's1', 'total_views': 10, 'total_submissions': 2, 'avg_grade': 12.0, 'days_active': 5, 'last_activity_delta_days': 2, 'assignments_on_time_ratio': 1.0},
    df = pd.DataFrame([
    engine = get_engine()
    # create a sample analytics_student_features table
    os.environ['DATABASE_URL'] = f"sqlite:///{tmp.name}"
    tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    # Use a temporary sqlite file
def setup_module(module):


from db import get_engine
from api import app

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import sys
# Ensure the module path resolves to src

from fastapi.testclient import TestClient
import pytest
import pandas as pd
import tempfile
import os

