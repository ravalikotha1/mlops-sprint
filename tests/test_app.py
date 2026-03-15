from fastapi.testclient import TestClient
import sys
import os

# Point to the app directory and set working directory so model.pkl is found
app_dir = os.path.join(os.path.dirname(__file__), "..", "app")
sys.path.insert(0, app_dir)
os.chdir(app_dir)

# Mock boto3 and sqlalchemy so tests don't need real AWS/Postgres
from unittest.mock import MagicMock, patch
import importlib

with patch("boto3.client", return_value=MagicMock()), \
     patch("sqlalchemy.create_engine", return_value=MagicMock()):
    import main
    app = main.app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_version" in data


def test_predict_valid_input():
    with patch.object(main, "s3", MagicMock()), \
         patch.object(main, "engine", MagicMock()) as mock_engine:
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        response = client.post("/predict", json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        })
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert data["prediction"] in ["setosa", "versicolor", "virginica"]
        assert "confidence" in data
