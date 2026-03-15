# MLOps Sprint — End-to-End ML Platform

A production-style ML platform built in a hands-on sprint, covering Docker, Kubernetes, AWS, Postgres, CI/CD, Terraform, and MLflow.

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
    │  runs train.py from notebook
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
│   └── mlflow/
│       ├── deployment.yaml  # MLflow server deployment
│       └── service.yaml     # MLflow service
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

## Key Learnings

- **localhost vs host.minikube.internal** — pods can't reach the host machine via localhost; use `host.minikube.internal` instead
- **ECR token expiry** — AWS ECR tokens expire every 12 hours; on EKS this is solved with IAM roles
- **GitOps discipline** — never manually edit the image tag in deployment.yaml; let CI/CD own it
- **Mock vs integration tests** — mocking the DB in tests hid a real connection bug; integration tests against a real DB would have caught it
- **MLflow aliases vs stages** — MLflow v2.9+ uses aliases (e.g. `@production`) instead of deprecated stages

## Day-by-Day Progress

- **Day 1** ✅ Docker + Kubernetes — containerized app, minikube deployment, rolling updates
- **Day 2** ✅ AWS + Postgres — ECR, S3 logging, Postgres integration, K8s secrets
- **Day 3** ✅ CI/CD + Terraform — GitHub Actions pipeline, infrastructure as code
- **Bonus** ✅ MLflow — experiment tracking, model registry, platform thinking
