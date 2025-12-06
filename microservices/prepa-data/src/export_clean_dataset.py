import pandas as pd
from sqlalchemy import create_engine

# -----------------------------
# 1. Config PostgreSQL Docker
# -----------------------------
PG_USER = "prepadata"
PG_PASSWORD = "prepadata_pwd"
PG_HOST = "postgres"     # nom du service Docker, PAS localhost
PG_PORT = 5432
PG_DB = "analytics"

# Table que tu veux exporter
# - soit dataset final analytics :
TABLE_NAME = "analytics.student_features"
# - soit dataset normalisé :
# TABLE_NAME = "staging.student_features_normalized"

# -----------------------------
# 2. Connexion à PostgreSQL
# -----------------------------
conn_str = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
engine = create_engine(conn_str)

print(f"Lecture de la table {TABLE_NAME}...")
df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", engine)
print(f"✅ Chargé {len(df)} lignes et {len(df.columns)} colonnes")

# -----------------------------
# 3. Export vers un CSV
# -----------------------------
output_path = "/opt/prepadata/data/student_features_clean.csv"
df.to_csv(output_path, index=False)
print(f"✅ Fichier CSV exporté vers : {output_path}")
