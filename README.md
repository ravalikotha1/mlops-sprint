# MLOps Sprint — End-to-End ML Pipeline

A production-style ML pipeline built in a 3-day intensive sprint, covering Docker, Kubernetes, AWS, Postgres, CI/CD, and Terraform.

## What It Does

A FastAPI app that serves predictions from a scikit-learn iris flower classifier. The infrastructure demonstrates real MLOps practices: containerization, orchestration, cloud storage, database logging, automated deployments, and infrastructure as code.

## Architecture

```
┌─────────────┐     HTTP POST /predict     ┌──────────────────────┐
│   Client    │ ─────────────────────────► │  FastAPI ML App      │
└─────────────┘                            │  (scikit-learn model) │
                                           └──────────┬───────────┘
                                                      │
                                  ┌───────────────────┼───────────────────┐
                                  │                   │                   │
                           ┌──────▼──────┐   ┌────────▼──────┐  ┌────────▼──────┐
                           │  Postgres   │   │   AWS S3      │  │  AWS ECR      │
                           │  (logging)  │   │  (JSON logs)  │  │  (image repo) │
                           └─────────────┘   └───────────────┘  └───────────────┘

CI/CD:     GitHub Actions → build → test → push to ECR → update K8s manifest
IaC:       Terraform provisions S3 + ECR
Deployed:  Kubernetes (minikube locally)
```

## Tech Stack

| Layer | Technology |
|---|---|
| ML Model | scikit-learn (iris classifier) |
| API | FastAPI + uvicorn |
| Containerization | Docker |
| Orchestration | Kubernetes (minikube) |
| Container Registry | AWS ECR |
| Cloud Storage | AWS S3 |
| Database | Postgres |
| Analytics | DuckDB (queries S3 logs with SQL) |
| IaC | Terraform |
| CI/CD | GitHub Actions |

## How to Run Locally

**Prerequisites:** Docker, minikube, kubectl, AWS CLI configured

```bash
# Clone the repo
git clone https://github.com/ravalikotha1/mlops-sprint.git
cd mlops-sprint

# Run with Docker
docker pull ravalikotha/mlops-sprint:v2
docker run -p 8000:8000 ravalikotha/mlops-sprint:v2

# Test the prediction endpoint
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

## Deploy to Kubernetes

```bash
minikube start
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
minikube service mlops-sprint --url
```

## CI/CD Pipeline

Every push to `main` automatically:
1. Runs pytest tests
2. Builds Docker image tagged with git commit SHA
3. Pushes image to AWS ECR
4. Updates `k8s/deployment.yaml` with the new image tag (GitOps)

## Infrastructure as Code

```bash
cd terraform
terraform init
terraform plan
terraform apply   # provisions S3 bucket + ECR repository
```

## Query Prediction Logs with DuckDB

```bash
python3 query_s3.py   # runs SQL directly against S3 JSON files
```

## Project Structure

```
mlops-sprint/
├── app/
│   ├── main.py          # FastAPI app — logs to Postgres + S3
│   ├── train.py         # Model training script
│   └── model.pkl        # Trained scikit-learn model
├── k8s/
│   ├── deployment.yaml  # Kubernetes Deployment (auto-updated by CI/CD)
│   └── service.yaml     # Kubernetes Service
├── terraform/
│   └── main.tf          # S3 + ECR provisioning
├── tests/
│   └── test_app.py      # pytest tests
├── .github/workflows/
│   └── ci.yml           # GitHub Actions CI/CD pipeline
├── query_s3.py          # DuckDB S3 query script
├── Dockerfile           # Multi-stage Docker build
└── requirements.txt
```

## Day-by-Day Progress

- **Day 1** ✅ Docker + Kubernetes — containerized app deployed to minikube with rolling updates
- **Day 2** ✅ AWS + Postgres — ECR, S3 logging, Postgres integration, K8s secrets
- **Day 3** ✅ CI/CD + Terraform — automated pipeline, infrastructure as code
