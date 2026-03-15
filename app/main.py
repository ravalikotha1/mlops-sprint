from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import boto3
import json
import uuid
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
import mlflow.sklearn

app = FastAPI(title="Iris Classifier")

CLASSES = ["setosa", "versicolor", "virginica"]
S3_BUCKET = "mlops-sprint-ravali"
s3 = boto3.client("s3")

# Load model from MLflow registry — falls back to local model.pkl if MLflow unavailable
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

try:
    model = mlflow.sklearn.load_model("models:/iris-classifier@production")
    model_version = "mlflow-production"
    print(f"Loaded model from MLflow registry")
except Exception as e:
    print(f"MLflow unavailable ({e}), falling back to local model.pkl")
    import pickle
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    model_version = "local-pkl"

# Postgres connection
DB_URL = os.getenv("DB_URL", "postgresql://postgres:mlopspass@host.minikube.internal:5432/mlops")
engine = create_engine(DB_URL)

# Create predictions table on startup
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS predictions (
            id UUID PRIMARY KEY,
            input JSONB,
            output JSONB,
            model_version TEXT,
            timestamp TIMESTAMPTZ
        )
    """))
    conn.commit()

class PredictRequest(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.get("/health")
def health():
    return {"status": "ok", "model_version": model_version}

@app.post("/predict")
def predict(req: PredictRequest):
    features = np.array([[req.sepal_length, req.sepal_width, req.petal_length, req.petal_width]])
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0].max()

    result = {
        "prediction": CLASSES[prediction],
        "confidence": round(float(probability), 4),
        "model_version": model_version
    }

    timestamp = datetime.now(timezone.utc)
    prediction_id = str(uuid.uuid4())

    # Log to Postgres
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO predictions (id, input, output, model_version, timestamp)
            VALUES (:id, :input, :output, :model_version, :timestamp)
        """), {
            "id": prediction_id,
            "input": json.dumps(req.model_dump()),
            "output": json.dumps(result),
            "model_version": model_version,
            "timestamp": timestamp
        })
        conn.commit()

    # Log to S3
    log = {"timestamp": timestamp.isoformat(), "input": req.model_dump(), "output": result}
    key = f"predictions/{timestamp.strftime('%Y/%m/%d')}/{prediction_id}.json"
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(log))

    return result
