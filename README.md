# ML Platform — End-to-End MLOps Infrastructure

A production-style ML platform covering Docker, Kubernetes, AWS, Postgres, CI/CD, Terraform, MLflow, and JupyterHub.

## What It Does

A FastAPI app serving predictions from a scikit-learn iris classifier, backed by a full MLOps platform:
- **MLflow** for experiment tracking and model registry
- **Postgres** for prediction logging
- **AWS S3** for artifact storage and prediction logs
- **Kubernetes** for container orchestration
- **GitHub Actions** for CI/CD
- **Terraform** for infrastructure as code

## Architecture

```
Data Scientist
    │
    │  logs into JupyterHub → runs training notebook
    ▼
MLflow Tracking Server (Kubernetes)
    ├── logs metrics/params → Postgres
    └── logs model artifacts → S3
    │
    │  promotes model to "production" alias
    ▼
FastAPI ML App (Kubernetes)
    ├── loads model from MLflow registry (S3)
    ├── logs predictions → Postgres
    └── logs predictions → S3

CI/CD (GitHub Actions)
    └── git push → test → build → push to ECR → update K8s manifest

Infrastructure (Terraform)
    └── provisions S3, ECR (mlops-sprint + mlflow)
```

## Tech Stack

| Layer | Technology |
|---|---|
| ML Model | scikit-learn (iris classifier) |
| Experiment Tracking | MLflow |
| Model Registry | MLflow + S3 |
| API | FastAPI + uvicorn |
| Containerization | Docker |
| Orchestration | Kubernetes (minikube) |
| Container Registry | AWS ECR |
| Cloud Storage | AWS S3 |
| Database | Postgres |
| Analytics | DuckDB (SQL queries on S3 logs) |
| Notebook Environment | JupyterHub |
| IaC | Terraform |
| CI/CD | GitHub Actions |

## How to Run Locally

**Prerequisites:** Docker, minikube, kubectl, AWS CLI configured

```bash
git clone https://github.com/ravalikotha1/mlops-sprint.git
cd mlops-sprint

# Start minikube
minikube start

# Create required secrets
kubectl create secret generic db-secret \
  --from-literal=password=mlopspass \
  --from-literal=db-url=postgresql://postgres:mlopspass@host.minikube.internal:5432/mlops

kubectl create secret docker-registry ecr-secret \
  --docker-server=<your-ecr-registry> \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password --region us-east-1)

kubectl create secret generic aws-secret \
  --from-literal=access_key_id=$(aws configure get aws_access_key_id) \
  --from-literal=secret_access_key=$(aws configure get aws_secret_access_key)

# Deploy app and MLflow
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/mlflow/deployment.yaml
kubectl apply -f k8s/mlflow/service.yaml

# Start Postgres
docker run -d --name mlops-postgres \
  -e POSTGRES_PASSWORD=mlopspass \
  -e POSTGRES_DB=mlops \
  -p 5432:5432 postgres:16
```

## MLflow Workflow

```bash
# Train and log experiment to MLflow
cd app
MLFLOW_TRACKING_URI=http://$(minikube service mlflow --url) python3 train.py

# Open MLflow UI
minikube service mlflow --url
# → Go to Models tab → iris-classifier → Add alias "production"

# App automatically loads the production model on next restart
kubectl rollout restart deployment/mlops-sprint
```

## Test the API

```bash
# Get the app URL
minikube service mlops-sprint --url

# Check which model version is loaded
curl http://<URL>/health

# Make a prediction
curl -X POST http://<URL>/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

## CI/CD Pipeline

Every push to `main` automatically:
1. Runs pytest tests
2. Builds Docker image tagged with git commit SHA
3. Pushes to AWS ECR
4. Updates `k8s/deployment.yaml` with the new image tag (GitOps)

## Infrastructure as Code

```bash
cd terraform
terraform init
terraform plan
terraform apply   # provisions S3 + ECR repositories
```

## Query Prediction Logs with DuckDB

```bash
python3 query_s3.py   # SQL queries directly against S3 JSON files
```

## Project Structure

```
mlops-sprint/
├── app/
│   ├── main.py          # FastAPI app — loads model from MLflow, logs to Postgres + S3
│   ├── train.py         # Training script — logs experiments to MLflow
│   └── model.pkl        # Local model fallback
├── k8s/
│   ├── deployment.yaml  # App deployment (auto-updated by CI/CD)
│   ├── service.yaml     # App service
│   ├── mlflow/
│   │   ├── deployment.yaml  # MLflow server deployment
│   │   └── service.yaml     # MLflow service
│   └── jupyterhub/
│       └── values.yaml      # JupyterHub Helm configuration
├── notebooks/
│   └── iris_training.ipynb  # Data scientist training notebook
├── terraform/
│   └── main.tf          # S3 + ECR provisioning
├── tests/
│   └── test_app.py      # pytest tests
├── .github/workflows/
│   └── ci.yml           # GitHub Actions CI/CD pipeline
├── mlflow.Dockerfile    # Custom MLflow image with psycopg2 + boto3
├── query_s3.py          # DuckDB S3 query script
├── Dockerfile           # Multi-stage app Docker build
└── requirements.txt
```

## Key Engineering Decisions & Learnings

**Networking**
- Pods can't reach the host machine via `localhost` — use `host.minikube.internal` instead; on EKS this is handled via VPC routing
- Cross-namespace communication requires full DNS: `service.namespace.svc.cluster.local` — learned this when JupyterHub couldn't resolve the MLflow service

**Security**
- AWS ECR tokens expire every 12 hours — recreate `imagePullSecrets` when pods show `ImagePullBackOff`; on EKS this is eliminated with IAM roles for service accounts
- Credentials are injected via Kubernetes Secrets, never hardcoded in manifests or application code

**CI/CD & GitOps**
- The CI/CD pipeline owns the image tag in `deployment.yaml` — manually editing it causes merge conflicts; let automation handle it
- Mocking the database in tests hid a real connection bug — integration tests against a real database would have caught it earlier

**MLflow**
- MLflow server stores metadata (metrics, params) in Postgres; the client writes model artifacts directly to S3 — the server just provides the artifact location
- MLflow v2.9+ uses aliases (e.g. `@production`) instead of deprecated stages
- Version mismatch between MLflow client and server causes API errors — always pin client version to match server

