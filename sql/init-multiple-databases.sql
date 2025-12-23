SELECT 'CREATE DATABASE prepadata_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'prepadata_db')\gexec
SELECT 'CREATE DATABASE lms_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lms_db')\gexec
SELECT 'CREATE DATABASE profiler_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'profiler_db')\gexec
SELECT 'CREATE DATABASE predictor_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'predictor_db')\gexec
SELECT 'CREATE DATABASE reco_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'reco_db')\gexec
SELECT 'CREATE DATABASE teacher_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'teacher_db')\gexec
SELECT 'CREATE DATABASE student_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'student_db')\gexec
