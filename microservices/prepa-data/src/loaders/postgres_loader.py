# src/loaders/postgres_loader.py
import pandas as pd
from sqlalchemy import create_engine, text
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_engine(pg_cfg: Dict[str,Any]):
    user = pg_cfg.get('user')
    pwd = pg_cfg.get('password')
    host = pg_cfg.get('host')
    port = pg_cfg.get('port')
    db = pg_cfg.get('dbname')
    conn = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    engine = create_engine(conn, pool_pre_ping=True)
    return engine

def save_features(df: pd.DataFrame, table: str, pg_cfg: Dict[str,Any], if_exists='replace'):
    engine = get_engine(pg_cfg)
    schema, table_name = table.split('.')
    logger.info("Saving features to %s.%s rows=%s", schema, table_name, len(df))
    df.to_sql(table_name, engine, schema=schema, if_exists=if_exists, index=False, method='multi', chunksize=1000)
    engine.dispose()

def upsert_features(df: pd.DataFrame, table: str, pg_cfg: Dict[str,Any], primary_keys=['id_student','code_module','code_presentation']):
    engine = get_engine(pg_cfg)
    schema, table_name = table.split('.')
    tmp_table = f"{table_name}_tmp"
    logger.info("Upserting features into %s.%s (tmp %s), rows=%s", schema, table_name, tmp_table, len(df))
    df.to_sql(tmp_table, engine, schema=schema, if_exists='replace', index=False, method='multi', chunksize=1000)
    pk_cols = ", ".join(primary_keys)
    cols = [c for c in df.columns if c not in primary_keys]
    if not cols:
        logger.warning("No non-PK columns to update.")
    set_clause = ", ".join([f"{c}=EXCLUDED.{c}" for c in cols])
    insert_cols = ", ".join(df.columns)
    sql = f"""
    INSERT INTO {schema}.{table_name} ({insert_cols})
    SELECT {insert_cols} FROM {schema}.{tmp_table}
    ON CONFLICT ({pk_cols}) DO UPDATE SET
    {set_clause};
    DROP TABLE IF EXISTS {schema}.{tmp_table};
    """
    with engine.begin() as conn:
        conn.execute(text(sql))
    engine.dispose()
    logger.info("Upsert finished.")
