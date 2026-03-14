# MLOps Sprint — End-to-End ML Pipeline

A production-style ML pipeline built in a 3-day intensive sprint, covering Docker, Kubernetes, AWS, Postgres, CI/CD, and Terraform.

## What It Does

A FastAPI app that serves predictions from a scikit-learn iris flower classifier. The infrastructure demonstrates real MLOps practices: containerization, orchestration, cloud storage, database logging, and automated deployments.

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

Deployed on: Kubernetes (minikube locally) → AWS EKS (production)
Provisioned with: Terraform
CI/CD: GitHub Actions
```

## Tech Stack

| Layer | Technology |
|---|---|
| ML Model | scikit-learn (iris classifier) |
| API | FastAPI + uvicorn |
| Containerization | Docker |
| Orchestration | Kubernetes (minikube) |
| Container Registry | Docker Hub + AWS ECR |
| Cloud Storage | AWS S3 |
| Database | Postgres |
| IaC | Terraform |
| CI/CD | GitHub Actions |

## How to Run Locally

**Prerequisites:** Docker, minikube, kubectl

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
# Start minikube
minikube start

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Get the URL
minikube service mlops-sprint --url

# Scale to 3 replicas
kubectl scale deployment mlops-sprint --replicas=3

# Rolling update to new version
kubectl set image deployment/mlops-sprint mlops-sprint=ravalikotha/mlops-sprint:v2
kubectl rollout status deployment/mlops-sprint
```

## Project Structure

```
mlops-sprint/
├── app/
│   ├── main.py        # FastAPI app + prediction endpoint
│   ├── train.py       # Model training script
│   └── model.pkl      # Trained scikit-learn model
├── k8s/
│   ├── deployment.yaml  # Kubernetes Deployment
│   └── service.yaml     # Kubernetes Service
├── Dockerfile           # Multi-stage Docker build
├── requirements.txt     # Python dependencies
└── README.md
```

## Day-by-Day Progress

- **Day 1** ✅ Docker + Kubernetes — containerized app deployed to minikube
- **Day 2** 🔄 AWS + Postgres — ECR, S3 logging, database integration
- **Day 3** 🔄 CI/CD + Terraform — automated pipelines, infrastructure as code
