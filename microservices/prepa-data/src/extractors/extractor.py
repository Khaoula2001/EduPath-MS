# src/extractors/extractor.py
"""
Extractor Module
================
Handles extraction of data from various sources (CSV, PostgreSQL)
and loading into PostgreSQL raw_data schema.
"""

import os
import pandas as pd
from typing import Dict, Any, List
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -----------------------------
# Utility Functions
# -----------------------------

def get_postgres_engine(pg_cfg: Dict[str, Any]) -> create_engine:
    """
    Create PostgreSQL connection engine.
    
    Args:
        pg_cfg: PostgreSQL configuration dictionary
    
    Returns:
        SQLAlchemy engine instance
    """
    user = pg_cfg.get('user', 'prepadata')
    pwd = pg_cfg.get('password', 'prepadata_pwd')
    host = pg_cfg.get('host', 'postgres')
    port = pg_cfg.get('port', 5432)
    db = pg_cfg.get('dbname', 'analytics')
    conn_str = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    return create_engine(conn_str, pool_pre_ping=True)


def read_csv_safe(path: str) -> pd.DataFrame:
    """
    Safely read CSV file with error handling.
    
    Args:
        path: Path to CSV file
    
    Returns:
        DataFrame or empty DataFrame if file not found
    """
    if not os.path.exists(path):
        logger.warning(f"File not found: {path}. Returning empty DataFrame.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
        logger.debug(f"Successfully read {path}: {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Failed to read CSV {path}: {e}")
        return pd.DataFrame()


def read_oulad(oulad_dir: str) -> Dict[str, pd.DataFrame]:
    """
    Read OULAD CSV files from directory.
    
    Args:
        oulad_dir: Directory containing OULAD CSV files
    
    Returns:
        Dictionary of DataFrames keyed by table name
    """
    logger.info(f"Reading OULAD data from: {oulad_dir}")

    files = {
        'student_info': 'studentInfo.csv',
        'student_registration': 'studentRegistration.csv',
        'assessments': 'assessments.csv',
        'student_assessment': 'studentAssessment.csv',
        'vle': 'vle.csv',
        'student_vle': 'studentVle.csv',
        'courses': 'courses.csv'
    }

    data = {}
    for key, filename in files.items():
        file_path = os.path.join(oulad_dir, filename)
        df = read_csv_safe(file_path)

        if not df.empty:
            data[key] = df
            logger.info(f"Loaded OULAD {key}: {len(df)} rows from {filename}")
        else:
            data[key] = pd.DataFrame()
            logger.warning(f"No data loaded for {key} from {filename}")

    return data


def read_from_postgres(pg_cfg: Dict[str, Any], source_tag: str) -> Dict[str, pd.DataFrame]:
    """
    Read data from PostgreSQL analytics.raw_learning_data table.
    
    Args:
        pg_cfg: PostgreSQL configuration
        source_tag: Source identifier ('OULAD' or 'MOODLE')
    
    Returns:
        Dictionary of DataFrames keyed by data type
    """
    logger.info(f"Loading data from PostgreSQL, source={source_tag}")
    engine = get_postgres_engine(pg_cfg)

    data_types = ['student_info', 'student_registration', 'assessments',
                  'student_assessment', 'vle', 'student_vle', 'courses']

    result = {}
    for dtype in data_types:
        query = f"""
        SELECT * FROM analytics.raw_learning_data 
        WHERE source = '{source_tag}' 
        AND data_type = '{dtype}'
        AND processed = FALSE
        """
        try:
            df = pd.read_sql(query, engine)

            # Reconstruct DataFrame from raw_json if necessary
            if not df.empty and 'raw_json' in df.columns:
                json_data = df['raw_json'].apply(lambda x: x if isinstance(x, dict) else {})
                reconstructed = pd.DataFrame(json_data.tolist())
                result[dtype] = reconstructed
            else:
                result[dtype] = df

            logger.info(f"Loaded {dtype} from PostgreSQL: {len(result[dtype])} rows")
        except Exception as e:
            logger.warning(f"Failed to load {dtype}: {e}")
            result[dtype] = pd.DataFrame()

    engine.dispose()
    return result


def read_moodle(moodle_dir: str) -> Dict[str, pd.DataFrame]:
    """
    Read Moodle CSV files from directory.
    
    Args:
        moodle_dir: Directory containing Moodle CSV files
    
    Returns:
        Dictionary of DataFrames keyed by table name
    """
    logger.info(f"Reading Moodle data from: {moodle_dir}")

    files = {
        'student_info': 'users.csv',
        'student_registration': 'enrolments.csv',
        'assessments': 'assessments.csv',
        'student_assessment': 'quiz_attempts.csv',
        'vle': 'activities_catalog.csv',
        'student_vle': 'logs.csv',
        'courses': 'courses.csv'
    }

    data = {}
    for key, filename in files.items():
        file_path = os.path.join(moodle_dir, filename)
        df = read_csv_safe(file_path)

        if not df.empty:
            data[key] = df
            logger.info(f"Loaded Moodle {key}: {len(df)} rows from {filename}")
        else:
            data[key] = pd.DataFrame()
            logger.warning(f"No data loaded for {key} from {filename}")

    return data


def load_source(source: str, path: str = None, pg_cfg: Dict[str, Any] = None) -> Dict[str, pd.DataFrame]:
    """
    Load data from source (PostgreSQL or CSV).
    
    Args:
        source: 'oulad' or 'moodle'
        path: CSV directory path (for fallback)
        pg_cfg: PostgreSQL configuration
    
    Returns:
        Dictionary of DataFrames
    
    Raises:
        ValueError: If no data source available
    """
    logger.info(f"Loading source: {source}")

    # Priority 1: Read from PostgreSQL if config provided
    if pg_cfg:
        return read_from_postgres(pg_cfg, source.upper())

    # Priority 2: Fallback to CSV files
    if path and os.path.exists(path):
        if source.lower() == 'oulad':
            return read_oulad(path)
        elif source.lower() == 'moodle':
            return read_moodle(path)

    raise ValueError(f"No data source available for source={source}. "
                     f"Provide either pg_cfg or valid path.")


# -----------------------------
# Extractor Class
# -----------------------------

class Extractor:
    """
    Extractor class for loading data from CSV files into PostgreSQL.
    
    Attributes:
        data_dir: Directory containing CSV files
        pg_config: PostgreSQL configuration
        engine: SQLAlchemy engine instance
        TABLE_MAPPING: Mapping of data keys to PostgreSQL tables
    """

    TABLE_MAPPING = {
        'student_info': 'raw_data.student_info',
        'student_registration': 'raw_data.student_registration',
        'assessments': 'raw_data.assessments',
        'student_assessment': 'raw_data.student_assessment',
        'vle': 'raw_data.vle',
        'student_vle': 'raw_data.student_vle',
        'courses': 'raw_data.courses',
    }

    def __init__(self, data_dir: str, pg_config: Dict[str, Any]):
        """
        Initialize Extractor.
        
        Args:
            data_dir: Directory containing OULAD CSV files
            pg_config: PostgreSQL configuration dictionary
        """
        self.data_dir = data_dir
        self.pg_config = pg_config or {}
        self.engine = get_postgres_engine(self.pg_config)

        logger.info(f"Initialized Extractor with data_dir={data_dir}")

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names (strip, lowercase).
        
        Args:
            df: Input DataFrame
        
        Returns:
            Normalized DataFrame
        """
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.copy()
        df.columns = [str(col).strip().lower() for col in df.columns]
        return df

    def _load_df(self, df: pd.DataFrame, full_table: str) -> int:
        """
        Load DataFrame into PostgreSQL table.
        
        Args:
            df: DataFrame to load
            full_table: Full table name (schema.table)
        
        Returns:
            Number of rows loaded
        """
        if df is None or df.empty:
            logger.warning(f"No data to load into {full_table}")
            return 0

        df = self._normalize_columns(df)
        schema, table_name = full_table.split('.')

        try:
            # Load data into PostgreSQL
            df.to_sql(
                table_name,
                self.engine,
                schema=schema,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )
            row_count = len(df)
            logger.info(f"Loaded {row_count} rows into {full_table}")
            return row_count

        except Exception as e:
            logger.error(f"Failed to load data into {full_table}: {e}")
            raise

    def extract_and_load(self) -> Dict[str, Any]:
        """
        Extract OULAD data from CSV files and load into PostgreSQL.
        
        Returns:
            Dictionary with row counts and total rows
            Example: {'row_counts': {'student_info': 1000, ...}, 'total_rows': 5000}
        
        Raises:
            Exception: If extraction or loading fails
        """
        logger.info("=" * 60)
        logger.info("Starting data extraction and loading")
        logger.info("=" * 60)

        # Create raw_data schema if it doesn't exist
        try:
            with self.engine.begin() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw_data;"))
                logger.info("Schema 'raw_data' created/verified")
        except Exception as e:
            logger.error(f"Failed to create schema 'raw_data': {e}")
            raise

        # Read OULAD CSV files
        try:
            data = read_oulad(self.data_dir)
            logger.info(f"Read {len(data)} data tables from {self.data_dir}")
        except Exception as e:
            logger.error(f"Failed to read OULAD data from {self.data_dir}: {e}")
            raise

        # Load each table into PostgreSQL
        row_counts: Dict[str, int] = {}
        total_rows = 0

        for key, df in data.items():
            table = self.TABLE_MAPPING.get(key)

            if not table:
                logger.warning(f"No table mapping found for key: {key}")
                continue

            if df.empty:
                logger.warning(f"Empty DataFrame for {key}, skipping")
                row_counts[key] = 0
                continue

            try:
                count = self._load_df(df, table)
                row_counts[key] = count
                total_rows += count
                logger.info(f"Successfully loaded {key}: {count} rows")

            except Exception as e:
                logger.error(f"Failed to load {key} into {table}: {e}")
                row_counts[key] = 0

        # Create summary
        result = {
            'row_counts': row_counts,
            'total_rows': total_rows,
            'success': total_rows > 0,
            'tables_loaded': len([k for k, v in row_counts.items() if v > 0])
        }

        logger.info("=" * 60)
        logger.info("Extraction and loading summary:")
        logger.info(f"  Total rows loaded: {total_rows:,}")
        logger.info(f"  Tables loaded: {result['tables_loaded']}/{len(row_counts)}")
        logger.info(f"  Success: {result['success']}")
        logger.info("=" * 60)

        return result

    def close(self) -> None:
        """
        Close database connections.
        """
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("Database connections closed")
        except Exception as e:
            logger.warning(f"Error closing database connections: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connections."""
        self.close()


# -----------------------------
# Legacy functions for backward compatibility
# -----------------------------

def create_extractor(data_dir: str, pg_config: Dict[str, Any]) -> Extractor:
    """
    Legacy function to create Extractor instance.
    
    Args:
        data_dir: Directory containing CSV files
        pg_config: PostgreSQL configuration
    
    Returns:
        Extractor instance
    """
    return Extractor(data_dir, pg_config)


def extract_and_load_oulad(data_dir: str, pg_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy function for one-time extraction and loading.
    
    Args:
        data_dir: Directory containing OULAD CSV files
        pg_config: PostgreSQL configuration
    
    Returns:
        Extraction result dictionary
    """
    extractor = Extractor(data_dir, pg_config)
    try:
        result = extractor.extract_and_load()
        return result
    finally:
        extractor.close()