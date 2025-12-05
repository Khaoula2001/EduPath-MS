-- microservices/prepa-data/sql/02_create_tables.sql
-- =====================================================
-- Create all tables for PrepData microservice
-- =====================================================

-- =====================================================
-- RAW DATA SCHEMA (from CSV files)
-- =====================================================

-- Student information table
CREATE TABLE IF NOT EXISTS raw_data.student_info (
                                                     id SERIAL PRIMARY KEY,
                                                     id_student INTEGER NOT NULL,
                                                     code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    gender VARCHAR(20),
    region VARCHAR(100),
    highest_education VARCHAR(100),
    imd_band VARCHAR(50),
    age_band VARCHAR(50),
    num_of_prev_attempts INTEGER DEFAULT 0,
    studied_credits INTEGER DEFAULT 0,
    disability VARCHAR(10),
    final_result VARCHAR(50),
    imported_at TIMESTAMP DEFAULT NOW()
    );

-- Student VLE interactions
CREATE TABLE IF NOT EXISTS raw_data.student_vle (
                                                    id SERIAL PRIMARY KEY,
                                                    id_student INTEGER NOT NULL,
                                                    code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    id_site INTEGER NOT NULL,
    date INTEGER,
    sum_click INTEGER DEFAULT 0,
    imported_at TIMESTAMP DEFAULT NOW()
    );

-- Student assessments
CREATE TABLE IF NOT EXISTS raw_data.student_assessment (
                                                           id SERIAL PRIMARY KEY,
                                                           id_assessment INTEGER NOT NULL,
                                                           id_student INTEGER NOT NULL,
                                                           date_submitted INTEGER,
                                                           is_banked INTEGER DEFAULT 0,
                                                           score DECIMAL(5,2),
    imported_at TIMESTAMP DEFAULT NOW()
    );

-- Assessments metadata
CREATE TABLE IF NOT EXISTS raw_data.assessments (
                                                    id SERIAL PRIMARY KEY,
                                                    code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    id_assessment INTEGER NOT NULL,
    assessment_type VARCHAR(50),
    date INTEGER,
    weight INTEGER DEFAULT 0,
    imported_at TIMESTAMP DEFAULT NOW()
    );

-- Student registration
CREATE TABLE IF NOT EXISTS raw_data.student_registration (
                                                             id SERIAL PRIMARY KEY,
                                                             code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    id_student INTEGER NOT NULL,
    date_registration INTEGER,
    date_unregistration INTEGER,
    imported_at TIMESTAMP DEFAULT NOW()
    );

-- VLE materials
CREATE TABLE IF NOT EXISTS raw_data.vle (
                                            id SERIAL PRIMARY KEY,
                                            id_site INTEGER NOT NULL,
                                            code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    activity_type VARCHAR(100),
    week_from INTEGER,
    week_to INTEGER,
    imported_at TIMESTAMP DEFAULT NOW()
    );

-- Courses metadata
CREATE TABLE IF NOT EXISTS raw_data.courses (
                                                id SERIAL PRIMARY KEY,
                                                code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    length INTEGER,
    imported_at TIMESTAMP DEFAULT NOW()
    );

-- =====================================================
-- STAGING SCHEMA (cleaned data)
-- =====================================================

-- Cleaned student info
CREATE TABLE IF NOT EXISTS staging.student_info_clean (
                                                          id_student INTEGER NOT NULL,
                                                          code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    gender VARCHAR(20),
    region VARCHAR(100),
    highest_education VARCHAR(100),
    imd_band VARCHAR(50),
    age_band VARCHAR(50),
    num_of_prev_attempts INTEGER DEFAULT 0,
    studied_credits INTEGER DEFAULT 0,
    disability VARCHAR(10),
    final_result VARCHAR(50),
    final_result_encoded INTEGER,
    cleaned_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id_student, code_module, code_presentation)
    );

-- Cleaned student VLE
CREATE TABLE IF NOT EXISTS staging.student_vle_clean (
                                                         id_student INTEGER NOT NULL,
                                                         code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    id_site INTEGER NOT NULL,
    date INTEGER,
    sum_click INTEGER DEFAULT 0,
    cleaned_at TIMESTAMP DEFAULT NOW()
    );

-- Cleaned student assessment
CREATE TABLE IF NOT EXISTS staging.student_assessment_clean (
                                                                id_assessment INTEGER NOT NULL,
                                                                id_student INTEGER NOT NULL,
                                                                date_submitted INTEGER,
                                                                is_banked INTEGER DEFAULT 0,
                                                                score DECIMAL(5,2),
    cleaned_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id_assessment, id_student)
    );

-- Cleaned assessments
CREATE TABLE IF NOT EXISTS staging.assessments_clean (
                                                         code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    id_assessment INTEGER NOT NULL,
    assessment_type VARCHAR(50),
    date INTEGER,
    weight INTEGER DEFAULT 0,
    cleaned_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id_assessment)
    );

-- =====================================================
-- ANALYTICS SCHEMA (features for ML)
-- =====================================================

-- Final student features
CREATE TABLE IF NOT EXISTS analytics.student_features (
                                                          id_student INTEGER NOT NULL,
                                                          code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,

    -- Demographic features
    gender_encoded INTEGER,
    region_encoded INTEGER,
    highest_education_encoded INTEGER,
    imd_band_encoded INTEGER,
    age_band_encoded INTEGER,
    disability_encoded INTEGER,
    num_of_prev_attempts INTEGER,
    studied_credits INTEGER,

    -- Engagement features
    total_clicks INTEGER,
    avg_clicks_per_activity DECIMAL(10,2),
    activity_count INTEGER,
    engagement_intensity DECIMAL(10,2),
    active_days INTEGER,
    first_activity_day INTEGER,
    last_activity_day INTEGER,
    days_without_activity INTEGER,
    regularity_index DECIMAL(10,2),
    late_start_days INTEGER,

    -- Performance features
    mean_score DECIMAL(10,2),
    score_std DECIMAL(10,2),
    assessment_submissions_count INTEGER,
    latest_assessment_score DECIMAL(10,2),

    -- Progression features
    study_duration INTEGER,
    progress_rate DECIMAL(10,2),
    unregistered INTEGER,
    dropout_risk_signal INTEGER,
    engagement_drop_rate DECIMAL(10,2),

    -- Target variable
    final_result_encoded INTEGER,

    -- Timestamps
    feature_created_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (id_student, code_module, code_presentation)
    );

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_features_id_student ON analytics.student_features(id_student);
CREATE INDEX IF NOT EXISTS idx_features_module ON analytics.student_features(code_module, code_presentation);
CREATE INDEX IF NOT EXISTS idx_features_result ON analytics.student_features(final_result_encoded);

-- =====================================================
-- Create foreign keys and constraints
-- =====================================================

-- Add foreign key constraints
ALTER TABLE raw_data.student_vle
    ADD CONSTRAINT fk_student_vle_student
        FOREIGN KEY (id_student) REFERENCES raw_data.student_info(id_student) ON DELETE CASCADE;

ALTER TABLE raw_data.student_assessment
    ADD CONSTRAINT fk_student_assessment_student
        FOREIGN KEY (id_student) REFERENCES raw_data.student_info(id_student) ON DELETE CASCADE;

ALTER TABLE raw_data.student_assessment
    ADD CONSTRAINT fk_student_assessment_assessment
        FOREIGN KEY (id_assessment) REFERENCES raw_data.assessments(id_assessment) ON DELETE CASCADE;

-- =====================================================
-- Comments for documentation
-- =====================================================

COMMENT ON TABLE raw_data.student_info IS 'Raw student demographic and academic information from OULAD/Moodle';
COMMENT ON TABLE raw_data.student_vle IS 'Raw VLE interaction logs (clicks, views)';
COMMENT ON TABLE raw_data.student_assessment IS 'Raw student assessment scores and submissions';
COMMENT ON TABLE staging.student_info_clean IS 'Cleaned student information with encoded target variable';
COMMENT ON TABLE staging.student_vle_clean IS 'Cleaned VLE interactions with outliers removed';
COMMENT ON TABLE analytics.student_features IS 'Final feature set for machine learning models (StudentProfiler, PathPredictor)';

COMMENT ON COLUMN analytics.student_features.final_result_encoded IS 'Encoded target: 0=Pass, 1=Fail, 2=Withdrawn, 3=Distinction';
COMMENT ON COLUMN analytics.student_features.engagement_intensity IS 'Total clicks per active day (engagement metric)';
COMMENT ON COLUMN analytics.student_features.dropout_risk_signal IS 'Binary indicator of dropout risk (0=low, 1=high)';