from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np
import boto3
import json
import uuid
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text

app = FastAPI(title="Iris Classifier")

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

CLASSES = ["setosa", "versicolor", "virginica"]
S3_BUCKET = "mlops-sprint-ravali"
s3 = boto3.client("s3")

# Postgres connection — reads from environment variable (injected via K8s secret)
DB_URL = os.getenv("DB_URL", "postgresql://postgres:mlopspass@localhost:5432/mlops")
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
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):
    features = np.array([[req.sepal_length, req.sepal_width, req.petal_length, req.petal_width]])
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0].max()

    result = {
        "prediction": CLASSES[prediction],
        "confidence": round(float(probability), 4),
        "model_version": "v2"
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
            "model_version": "v2",
            "timestamp": timestamp
        })
        conn.commit()

    # Log to S3
    log = {"timestamp": timestamp.isoformat(), "input": req.model_dump(), "output": result}
    key = f"predictions/{timestamp.strftime('%Y/%m/%d')}/{prediction_id}.json"
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(log))

    return result
