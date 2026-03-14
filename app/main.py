from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np

app = FastAPI(title="Iris Classifier")

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

CLASSES = ["setosa", "versicolor", "virginica"]

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
    return {
        "prediction": CLASSES[prediction],
        "confidence": round(float(probability), 4),
        "model_version": "v2"
    }
