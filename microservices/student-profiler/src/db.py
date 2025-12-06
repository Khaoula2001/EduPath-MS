# ...existing code...
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import os
from urllib.parse import quote_plus
import pandas as pd

def get_database_url() -> str:
    # Prefer explicit DATABASE_URL for flexibility (sqlite:/// or postgres)
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    # Fallback to PG_* env vars and build a postgres url
    host = os.getenv("PG_HOST", "localhost")
    port = os.getenv("PG_PORT", "5432")
    db = os.getenv("PG_DB", "edupath")
    user = os.getenv("PG_USER", "edupath")
    password = os.getenv("PG_PASSWORD", "edupath")
    # If host is 'sqlite' or db ends with .db, help user by switching to sqlite
    if host == "sqlite" or db.endswith('.db'):
        return f"sqlite:///{db}"
    password_escaped = quote_plus(password)
    return f"postgresql+psycopg2://{user}:{password_escaped}@{host}:{port}/{db}"

_engine: Engine | None = None

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = get_database_url()
        _engine = create_engine(url, echo=False, future=True)
    return _engine


def read_student_features(query: str = None) -> pd.DataFrame:
    """Lit la table analytics.student_features ou exécute une requête SQL et renvoie un DataFrame."""
    engine = get_engine()
    if query is None:
        # convention: schema analytics, table student_features
        query = "SELECT * FROM analytics_student_features"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df


def write_student_profiles(df: pd.DataFrame) -> None:
    """Écrit/ajoute les profils dans analytics_student_profiles. Utilise to_sql pour compatibilité SQLite/Postgres."""
    engine = get_engine()
    # normalize table name for SQLite (no schema) and Postgres (analytics_student_profiles)
    table_name = "analytics_student_profiles"
    # Ensure timestamp column exists
    if 'profile_ts' not in df.columns:
        df['profile_ts'] = pd.Timestamp.now()
    # Use if_exists='append' to keep history; caller may remove duplicates beforehand
    df.to_sql(table_name, con=engine, if_exists='append', index=False)


def execute_sql(sql: str) -> None:
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()

# ...existing code...
