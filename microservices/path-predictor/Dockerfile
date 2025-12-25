FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
# Install packages without hash verification due to network instability
RUN pip install --default-timeout=1000 --retries=10 --no-cache-dir --disable-pip-version-check fastapi uvicorn scikit-learn joblib numpy pandas pika requests
RUN pip install --default-timeout=1000 --retries=10 --no-cache-dir --disable-pip-version-check xgboost
COPY app ./app
EXPOSE 8002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
