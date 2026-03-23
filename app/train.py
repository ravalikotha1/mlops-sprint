"""
Train the iris classifier and log the experiment to MLflow.
Run: python train.py
"""
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import pickle
import mlflow
import mlflow.sklearn
import os

# Point to your MLflow tracking server
MLFLOW_URL = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_URL)
mlflow.set_experiment("iris-classifier")

# Load data
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

# Tweak these to compare runs in MLflow
params = {
    "n_estimators": 100,
    "max_depth": 5,
    "random_state": 42
}

with mlflow.start_run():
    # Log parameters
    mlflow.log_params(params)

    # Train model
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # Evaluate
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    f1 = f1_score(y_test, predictions, average="weighted")

    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)

    # Log model to MLflow registry
    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        registered_model_name="iris-classifier"
    )

    # Also save locally for backward compatibility
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Model logged to MLflow and saved to model.pkl")
