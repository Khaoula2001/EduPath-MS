CREATE TABLE IF NOT EXISTS student_features (
    id_student BIGINT NOT NULL,
    code_module VARCHAR(50) NOT NULL,
    code_presentation VARCHAR(20) NOT NULL,
    gender CHAR(1),
    region VARCHAR(100),
    age_band VARCHAR(20),
    highest_education VARCHAR(100),
    disability BOOLEAN DEFAULT FALSE,
    total_clicks INT DEFAULT 0,
    activity_count INT DEFAULT 0,
    avg_clicks_per_activity FLOAT DEFAULT 0,
    click_std FLOAT DEFAULT 0,
    first_activity_day DATE,
    last_activity_day DATE,
    active_days INT DEFAULT 0,
    days_without_activity INT DEFAULT 0,
    regularity_index FLOAT DEFAULT 0,
    engagement_intensity FLOAT DEFAULT 0,
    mean_score FLOAT,
    score_std FLOAT,
    assessment_submissions_count INT DEFAULT 0,
    latest_assessment_score FLOAT,
    study_duration INT DEFAULT 0,
    progress_rate FLOAT DEFAULT 0,
    unregistered BOOLEAN DEFAULT FALSE,
    dropout_risk_signal INT DEFAULT 0,
    engagement_drop_rate FLOAT DEFAULT 0,
    synced_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id_student, code_module, code_presentation)
);
CREATE INDEX idx_student_module ON student_features(id_student, code_module);
CREATE INDEX idx_dropout_risk ON student_features(dropout_risk_signal);

CREATE TABLE IF NOT EXISTS raw_learning_data (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    raw_json JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Grant privileges to prepadata user (if exists, or ensure user creation elsewhere)
-- We assume the user 'lms' owns this, but prepadata needs access if it connects here.
-- In the architecture, prepadata connects to lmsdb.
-- GRANT ALL PRIVILEGES ON TABLE raw_learning_data TO prepadata;
