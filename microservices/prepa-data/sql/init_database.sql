-- =====================================================
-- PrepData PostgreSQL Initialization Script
-- =====================================================
-- Purpose: Create database, schemas, and user permissions
-- Location: microservices/prepa-data/sql/01_init_database.sql
-- =====================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw_data;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS features;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA raw_data TO prepadata;
GRANT ALL PRIVILEGES ON SCHEMA staging TO prepadata;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO prepadata;
GRANT ALL PRIVILEGES ON SCHEMA features TO prepadata;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA raw_data GRANT ALL ON TABLES TO prepadata;
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT ALL ON TABLES TO prepadata;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL ON TABLES TO prepadata;
ALTER DEFAULT PRIVILEGES IN SCHEMA features GRANT ALL ON TABLES TO prepadata;

-- Create metadata table for ETL tracking
CREATE TABLE IF NOT EXISTS analytics.etl_metadata (
                                                      id SERIAL PRIMARY KEY,
                                                      pipeline_name VARCHAR(100) NOT NULL,
    execution_date TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),
    records_processed INTEGER DEFAULT 0,
    duration_seconds INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
    );

-- Create data quality log table
CREATE TABLE IF NOT EXISTS analytics.data_quality_log (
                                                          id SERIAL PRIMARY KEY,
                                                          table_name VARCHAR(100) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    check_result BOOLEAN NOT NULL,
    details JSONB,
    checked_at TIMESTAMP DEFAULT NOW()
    );

COMMENT ON SCHEMA raw_data IS 'Raw data from CSV files (OULAD/Moodle)';
COMMENT ON SCHEMA staging IS 'Intermediate cleaned and validated data';
COMMENT ON SCHEMA analytics IS 'Aggregated analytics and features';
COMMENT ON SCHEMA features IS 'Final feature store for ML models';