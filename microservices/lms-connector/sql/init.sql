\c lms_db;

CREATE TABLE IF NOT EXISTS raw_learning_data (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    raw_json JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

GRANT ALL PRIVILEGES ON TABLE raw_learning_data TO prepadata;
