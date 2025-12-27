"""
PrepData ETL DAG - Complete Pipeline
=======================================
Automated preprocessing pipeline:
0. Create Schemas (raw_data, staging, analytics)
1. Extract (CSV → PostgreSQL raw_data)
2. Validate (data quality checks)
3. Clean (duplicates, missing values, outliers)
4. Encode (categorical & target encoding)
5. Aggregate (feature engineering)
6. Normalize (MinMax scaling)
7. Load (staging → analytics)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

import sys
import os

# Import PrepData modules
BASE_PATH = "/opt/prepadata/src"
sys.path.append(BASE_PATH)

from extractors.extractor import Extractor
from transformers.data_cleaner import DataCleaner
from transformers.data_validator import DataValidator
from transformers.feature_encoder import FeatureEncoder
from transformers.aggregator import (
    aggregate_student_vle,
    aggregate_student_assessments,
    build_student_profiler
)
from loaders.postgres_loader import save_features, upsert_features


# ==========================================
# DAG Configuration
# ==========================================
default_args = {
    'owner': 'prepadata',
    'depends_on_past': False,
    'email_on_failure': False,  # Désactivé temporairement pour éviter les erreurs SMTP
    'email': ['admin@example.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'prepadata_complete_etl',
    default_args=default_args,
    description='Complete ETL pipeline with all preprocessing steps',
    schedule_interval='*/15 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['prepadata', 'oulad', 'etl', 'ml-preprocessing']
)


# ==========================================
# PostgreSQL Configuration
# ==========================================
PG_CONFIG = {
    'host': os.getenv('PG_HOST', 'postgres'),
    'port': int(os.getenv('PG_PORT', 5432)),
    'user': os.getenv('PG_USER', 'prepadata'),
    'password': os.getenv('PG_PASSWORD', 'prepadata_pwd'),
    'dbname': os.getenv('PG_DB', 'prepadata_db')
}


# ==========================================
# Task 0: Create Schemas
# ==========================================
def create_schemas_task(**kwargs):
    """Create required PostgreSQL schemas if they don't exist"""
    print("=" * 60)
    print("TASK 0: CREATE SCHEMAS")
    print("=" * 60)

    from sqlalchemy import create_engine, text

    conn_str = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['dbname']}"
    engine = create_engine(conn_str)

    schemas = ['raw_data', 'staging', 'analytics']

    with engine.begin() as conn:
        for schema in schemas:
            try:
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))
                print(f"✅ Schema '{schema}' created/verified")
            except Exception as e:
                print(f"⚠️ Could not create schema '{schema}': {e}")

    engine.dispose()
    print("\n✅ Schema creation complete")


# ==========================================
# Task 1: Extract (PostgreSQL raw_learning_data → staging)
# ==========================================
def extract_task(**kwargs):
    """Extract data from PostgreSQL raw_learning_data schema"""
    print("=" * 60)
    print("TASK 1: EXTRACTION")
    print("=" * 60)

    extractor = Extractor(
        data_dir="/opt/prepadata/data/oulad",
        pg_config=PG_CONFIG
    )

    # Config spécifique pour la source LMS (lms_db)
    SOURCE_PG_CONFIG = PG_CONFIG.copy()
    SOURCE_PG_CONFIG['dbname'] = os.getenv('SOURCE_DB', 'lms_db')

    # 1. On tente d'extraire depuis PostgreSQL (données venant du LMS Connector)
    try:
        from extractors.extractor import load_source
        data = load_source(source='MOODLE', pg_cfg=SOURCE_PG_CONFIG)
        
        if not all(df.empty for df in data.values()):
            print("✅ Data successfully extracted from PostgreSQL (MOODLE)")
            extractor.save_to_raw_data(data)
            print("\n✅ Extraction from DB complete")
            return
    except Exception as e:
        print(f"⚠️ Could not load from PostgreSQL: {e}")

    # 2. Fallback vers les CSV OULAD si pas de données en base
    print("⚠️ No data found in PostgreSQL, falling back to CSV (OULAD)...")
    result = extractor.extract_and_load()
    extractor.close()

    # Pass data to next task via XCom
    kwargs['ti'].xcom_push(key='extraction_counts', value=result['row_counts'])

    print(f"\n✅ Extraction complete: {result['total_rows']} total rows")


# ==========================================
# Task 2: Validate (Data Quality Checks)
# ==========================================
def validate_task(**kwargs):
    """Perform comprehensive data quality validation"""
    print("=" * 60)
    print("TASK 2: VALIDATION")
    print("=" * 60)

    from sqlalchemy import create_engine, text
    import pandas as pd

    # Connect to PostgreSQL
    conn_str = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['dbname']}"
    engine = create_engine(conn_str)

    # Vérifier si la table existe
    with engine.begin() as conn:
        table_exists = conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'raw_data' AND table_name = 'student_info')")
        ).scalar()

    if not table_exists:
        print("❌ Table 'raw_data.student_info' does not exist. Skipping validation.")
        engine.dispose()
        return

    validator = DataValidator()
    validation_reports = {}

    # Validate each table
    tables_to_validate = [
        ('student_info', ['id_student', 'code_module', 'code_presentation']),
        ('student_vle', ['id_student', 'id_site', 'date']),
        ('student_assessment', ['id_assessment', 'id_student'])
    ]

    for table_name, key_cols in tables_to_validate:
        try:
            df = pd.read_sql(f"SELECT * FROM raw_data.{table_name} LIMIT 50000", engine)
            report = validator.validate_dataset(df, table_name, key_columns=key_cols)
            validation_reports[table_name] = report

            print(f"\n{table_name}: {report['status']}")
            if report.get('issues'):
                print(f"  Issues: {', '.join(report['issues'])}")
        except Exception as e:
            print(f"❌ Failed to validate {table_name}: {e}")

    engine.dispose()

    # Save validation report
    kwargs['ti'].xcom_push(key='validation_reports', value=validation_reports)

    if validation_reports:
        summary_df = validator.get_validation_summary(validation_reports)
        print(f"\n📊 Validation Summary:\n{summary_df.to_string()}")
    else:
        print("\n📊 No validation reports generated")

    print("\n✅ Validation complete")


# ==========================================
# Task 3: Clean (Duplicates, Missing, Outliers)
# ==========================================
def clean_task(**kwargs):
    """Clean data: remove duplicates, handle missing values, remove outliers"""
    print("=" * 60)
    print("TASK 3: CLEANING")
    print("=" * 60)

    from sqlalchemy import create_engine, text
    import pandas as pd

    conn_str = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['dbname']}"
    engine = create_engine(conn_str)

    # Créer le schéma staging s'il n'existe pas
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging;"))
        print("✅ Schema 'staging' created/verified")

    # Load raw data
    raw_data = {}
    tables = ['student_info', 'student_vle', 'student_assessment',
              'assessments', 'student_registration', 'vle', 'courses']

    for table in tables:
        try:
            raw_data[table] = pd.read_sql(f"SELECT * FROM raw_data.{table}", engine)
            print(f"✅ Loaded {table}: {len(raw_data[table])} rows")
        except Exception as e:
            print(f"⚠️ {table} not found or empty: {e}")
            raw_data[table] = pd.DataFrame()

    # Vérifier si nous avons des données
    total_rows = sum(len(df) for df in raw_data.values())
    if total_rows == 0:
        print("❌ No data to clean. Check extraction step.")
        engine.dispose()
        return

    # Clean data
    cleaner = DataCleaner()
    cleaned_data, cleaning_report = cleaner.clean_all(raw_data)

    # Save to staging schema
    for table_name, df in cleaned_data.items():
        if not df.empty:
            try:
                df.to_sql(
                    f'{table_name}_clean',
                    engine,
                    schema='staging',
                    if_exists='replace',
                    index=False,
                    method='multi',
                    chunksize=1000
                )
                print(f"✅ Saved staging.{table_name}_clean: {len(df)} rows")
            except Exception as e:
                print(f"❌ Failed to save {table_name}: {e}")

    engine.dispose()

    # Pass cleaning report
    kwargs['ti'].xcom_push(key='cleaning_report', value=cleaning_report['summary'])

    print("\n✅ Cleaning complete")


# ==========================================
# Task 4: Encode Features (Robust version)
# ==========================================
def encode_task(**kwargs):
    """Encode categorical features and target variable"""
    print("=" * 60)
    print("TASK 4: ENCODING")
    print("=" * 60)

    from sqlalchemy import create_engine, text
    import pandas as pd

    conn_str = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['dbname']}"
    engine = create_engine(conn_str)

    # Vérifier si la table clean existe
    with engine.begin() as conn:
        clean_table_exists = conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'staging' AND table_name = 'student_info_clean')")
        ).scalar()

        raw_table_exists = conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'raw_data' AND table_name = 'student_info')")
        ).scalar()

    # Charger les données
    if clean_table_exists:
        df = pd.read_sql("SELECT * FROM staging.student_info_clean", engine)
        print(f"✅ Loaded {len(df)} students from staging.student_info_clean")
    elif raw_table_exists:
        df = pd.read_sql("SELECT * FROM raw_data.student_info", engine)
        print(f"⚠️ Using raw_data.student_info (clean version not found): {len(df)} rows")
    else:
        print("❌ No student data found. Skipping encoding.")
        engine.dispose()
        return

    # Vérifier les colonnes requises
    required_cols = ['id_student', 'code_module', 'code_presentation']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"⚠️ Missing required columns: {missing_cols}. Adding placeholder values.")
        for col in missing_cols:
            df[col] = 0 if 'id' in col else 'unknown'

    encoder = FeatureEncoder()

    # 1. Encode target
    if 'final_result' not in df.columns:
        print("⚠️ Column 'final_result' not found. Using default value 'Pass'.")
        df['final_result'] = 'Pass'

    df, target_mapping = encoder.encode_target(df, 'final_result')
    print(f"✅ Target encoded: {target_mapping}")

    # 2. Encode categorical features
    categorical_cols = ['gender', 'region', 'highest_education',
                        'imd_band', 'age_band', 'disability']

    # Filtrer les colonnes qui existent
    existing_categorical_cols = [col for col in categorical_cols if col in df.columns]
    print(f"📊 Encoding {len(existing_categorical_cols)} categorical columns: {existing_categorical_cols}")

    if existing_categorical_cols:
        df, encoding_info = encoder.encode_categorical_features(df, existing_categorical_cols, method='label')
        print(f"✅ Encoded {len(encoding_info['columns_encoded'])} categorical features")
    else:
        encoding_info = {'columns_encoded': [], 'method': 'label'}
        print("⚠️ No categorical columns to encode")

    # 3. Sauvegarder les données encodées
    try:
        df.to_sql(
            'student_info_encoded',
            engine,
            schema='staging',
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )
        print(f"✅ Saved staging.student_info_encoded: {len(df)} rows")
    except Exception as e:
        print(f"❌ Failed to save encoded data: {e}")

    engine.dispose()

    # Sauvegarder la configuration d'encodage
    try:
        encoder.save_encoding_config('/opt/prepadata/config/encoding_config.json')
        print("✅ Encoding configuration saved")
    except Exception as e:
        print(f"⚠️ Could not save encoding config: {e}")

    kwargs['ti'].xcom_push(key='encoding_info', value=encoding_info)

    print(f"\n✅ Encoding complete: {len(df)} rows encoded")


# ==========================================
# Task 5: Aggregate Features
# ==========================================
def aggregate_task(**kwargs):
    """Build aggregated features (engagement, performance, progression)"""
    print("=" * 60)
    print("TASK 5: FEATURE AGGREGATION")
    print("=" * 60)

    from sqlalchemy import create_engine, text
    import pandas as pd

    conn_str = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['dbname']}"
    engine = create_engine(conn_str)

    # Vérifier si les tables nécessaires existent
    required_tables = ['staging.student_vle_clean', 'staging.student_assessment_clean',
                       'raw_data.student_registration', 'raw_data.courses']

    tables_exist = {}
    with engine.begin() as conn:
        for table in required_tables:
            schema, table_name = table.split('.')
            exists = conn.execute(
                text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = '{table_name}')")
            ).scalar()
            tables_exist[table] = exists

    # Charger les données disponibles
    data_frames = {}

    if tables_exist.get('staging.student_vle_clean'):
        data_frames['student_vle'] = pd.read_sql("SELECT * FROM staging.student_vle_clean", engine)
        print(f"✅ Loaded student_vle: {len(data_frames['student_vle'])} rows")
    else:
        data_frames['student_vle'] = pd.DataFrame()
        print("⚠️ staging.student_vle_clean not found")

    if tables_exist.get('staging.student_assessment_clean'):
        data_frames['student_assessment'] = pd.read_sql("SELECT * FROM staging.student_assessment_clean", engine)
        print(f"✅ Loaded student_assessment: {len(data_frames['student_assessment'])} rows")
    else:
        data_frames['student_assessment'] = pd.DataFrame()
        print("⚠️ staging.student_assessment_clean not found")

    if tables_exist.get('raw_data.student_registration'):
        data_frames['student_registration'] = pd.read_sql("SELECT * FROM raw_data.student_registration", engine)
        print(f"✅ Loaded student_registration: {len(data_frames['student_registration'])} rows")
    else:
        data_frames['student_registration'] = pd.DataFrame()
        print("⚠️ raw_data.student_registration not found")

    if tables_exist.get('raw_data.courses'):
        data_frames['courses'] = pd.read_sql("SELECT * FROM raw_data.courses", engine)
        print(f"✅ Loaded courses: {len(data_frames['courses'])} rows")
    else:
        data_frames['courses'] = pd.DataFrame()
        print("⚠️ raw_data.courses not found")

    # Vérifier si nous avons suffisamment de données
    if data_frames['student_vle'].empty and data_frames['student_assessment'].empty:
        print("❌ No student_vle or student_assessment data found. Skipping aggregation.")
        engine.dispose()
        return

    # Build features
    try:
        features_df = build_student_profiler(
            data_frames['student_vle'],
            data_frames['student_assessment'],
            data_frames['student_registration'],
            data_frames['courses']
        )

        if features_df.empty:
            print("❌ Feature aggregation produced empty DataFrame")
            engine.dispose()
            return

        print(f"\n✅ Aggregated features: {len(features_df)} students, {len(features_df.columns)} features")
        print(f"Features: {list(features_df.columns)}")

        # Save to staging
        features_df.to_sql(
            'student_features_aggregated',
            engine,
            schema='staging',
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )
        print(f"✅ Saved staging.student_features_aggregated: {len(features_df)} rows")

        kwargs['ti'].xcom_push(key='feature_count', value=len(features_df.columns))

    except Exception as e:
        print(f"❌ Error during feature aggregation: {e}")
        import traceback
        traceback.print_exc()

    engine.dispose()
    print("\n✅ Feature aggregation complete")


# ==========================================
# Task 6: Normalize Features (MinMax Scaling)
# ==========================================
def normalize_task(**kwargs):
    """Normalize numeric features (MinMax scaling)"""
    print("=" * 60)
    print("TASK 6: NORMALIZATION")
    print("=" * 60)

    from sqlalchemy import create_engine, text
    import pandas as pd

    conn_str = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['dbname']}"
    engine = create_engine(conn_str)

    # Vérifier si la table aggregated existe
    with engine.begin() as conn:
        table_exists = conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'staging' AND table_name = 'student_features_aggregated')")
        ).scalar()

    if not table_exists:
        print("❌ Table 'staging.student_features_aggregated' does not exist. Skipping normalization.")
        engine.dispose()
        return

    # Load aggregated features
    features_df = pd.read_sql("SELECT * FROM staging.student_features_aggregated", engine)

    if features_df.empty:
        print("❌ No features to normalize. Empty DataFrame.")
        engine.dispose()
        return

    encoder = FeatureEncoder()

    # Normalize numeric features
    numeric_cols = ['total_clicks', 'avg_clicks_per_activity', 'activity_count',
                    'engagement_intensity', 'mean_score', 'score_std',
                    'assessment_submissions_count', 'study_duration', 'progress_rate']

    # Filtrer les colonnes numériques qui existent
    existing_numeric_cols = [col for col in numeric_cols if col in features_df.columns]

    if not existing_numeric_cols:
        print("⚠️ No numeric columns found to normalize. Checking all numeric columns...")
        # Utiliser toutes les colonnes numériques
        existing_numeric_cols = features_df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    print(f"📊 Normalizing {len(existing_numeric_cols)} numeric columns: {existing_numeric_cols}")

    if existing_numeric_cols:
        features_df, scaling_info = encoder.normalize_features(
            features_df,
            existing_numeric_cols,
            method='minmax'
        )
        print(f"✅ Normalized {len(scaling_info['columns_normalized'])} features")
    else:
        print("⚠️ No numeric columns available for normalization")
        scaling_info = {'columns_normalized': [], 'method': 'minmax'}

    # Save normalized features
    try:
        features_df.to_sql(
            'student_features_normalized',
            engine,
            schema='staging',
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )
        print(f"✅ Saved staging.student_features_normalized: {len(features_df)} rows")
    except Exception as e:
        print(f"❌ Failed to save normalized features: {e}")

    engine.dispose()
    print("\n✅ Normalization complete")


# ==========================================
# Task 7: Load to Analytics
# ==========================================
def load_analytics_task(**kwargs):
    """Load final features to analytics.student_features"""
    print("=" * 60)
    print("TASK 7: LOAD TO ANALYTICS")
    print("=" * 60)

    from sqlalchemy import create_engine, text
    import pandas as pd

    conn_str = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['dbname']}"
    engine = create_engine(conn_str)

    # Vérifier si les tables nécessaires existent
    required_tables = ['staging.student_info_encoded', 'staging.student_features_normalized']

    tables_exist = {}
    with engine.begin() as conn:
        for table in required_tables:
            schema, table_name = table.split('.')
            exists = conn.execute(
                text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = '{table_name}')")
            ).scalar()
            tables_exist[table] = exists

    # Charger les données
    if tables_exist.get('staging.student_info_encoded'):
        student_info = pd.read_sql("SELECT * FROM staging.student_info_encoded", engine)
        print(f"✅ Loaded student_info: {len(student_info)} rows")
    else:
        print("❌ staging.student_info_encoded not found")
        student_info = pd.DataFrame()

    if tables_exist.get('staging.student_features_normalized'):
        features = pd.read_sql("SELECT * FROM staging.student_features_normalized", engine)
        print(f"✅ Loaded features: {len(features)} rows")
    else:
        print("❌ staging.student_features_normalized not found")
        features = pd.DataFrame()

    # Vérifier si nous avons des données
    if student_info.empty or features.empty:
        print("❌ Missing required data. Cannot load to analytics.")
        print(f"  student_info rows: {len(student_info)}")
        print(f"  features rows: {len(features)}")
        engine.dispose()
        return

    # Merge datasets
    try:
        # Vérifier les colonnes de jointure
        join_cols = ['id_student', 'code_module', 'code_presentation']
        missing_join_cols = [col for col in join_cols if col not in student_info.columns or col not in features.columns]

        if missing_join_cols:
            print(f"⚠️ Missing join columns: {missing_join_cols}. Using all common columns.")
            common_cols = list(set(student_info.columns) & set(features.columns))
            final_df = pd.merge(student_info, features, on=common_cols, how='inner')
        else:
            final_df = student_info.merge(
                features,
                on=join_cols,
                how='inner',
                suffixes=('', '_features')
            )

        print(f"✅ Merged dataset: {len(final_df)} rows, {len(final_df.columns)} columns")

        # Save to analytics schema
        final_df.to_sql(
            'student_features',
            engine,
            schema='analytics',
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )

        print(f"\n✅ Loaded {len(final_df)} rows to analytics.student_features")
        kwargs['ti'].xcom_push(key='final_row_count', value=len(final_df))

    except Exception as e:
        print(f"❌ Error loading to analytics: {e}")
        import traceback
        traceback.print_exc()

    engine.dispose()
    print("\n✅ Analytics loading complete")


# ==========================================
# Define Airflow Operators
# ==========================================

create_schemas_op = PythonOperator(
    task_id='create_schemas',
    python_callable=create_schemas_task,
    dag=dag
)

extract_op = PythonOperator(
    task_id='extract',
    python_callable=extract_task,
    dag=dag
)

validate_op = PythonOperator(
    task_id='validate',
    python_callable=validate_task,
    dag=dag
)

clean_op = PythonOperator(
    task_id='clean',
    python_callable=clean_task,
    dag=dag
)

encode_op = PythonOperator(
    task_id='encode',
    python_callable=encode_task,
    dag=dag
)

aggregate_op = PythonOperator(
    task_id='aggregate',
    python_callable=aggregate_task,
    dag=dag
)

normalize_op = PythonOperator(
    task_id='normalize',
    python_callable=normalize_task,
    dag=dag
)

load_analytics_op = PythonOperator(
    task_id='load_analytics',
    python_callable=load_analytics_task,
    dag=dag
)


# ==========================================
# ETL Pipeline Graph - COMPLETE
# ==========================================
create_schemas_op >> extract_op >> validate_op >> clean_op >> encode_op >> aggregate_op >> normalize_op >> load_analytics_op
