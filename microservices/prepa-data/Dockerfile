FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --default-timeout=1000 --retries=10 --no-cache-dir \
    apache-airflow==2.6.3 \
    pandas \
    scikit-learn \
    sqlalchemy \
    psycopg2-binary

USER root
RUN mkdir -p /opt/airflow/dags /opt/prepadata/src
WORKDIR /opt/airflow