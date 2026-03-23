terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Reads credentials from ~/.aws/credentials
provider "aws" {
  region = "us-east-1"
}

# S3 bucket for storing prediction logs
resource "aws_s3_bucket" "predictions" {
  bucket = "mlops-sprint-ravali"

  tags = {
    Project = "mlops-sprint"
  }
}

# ECR repository for storing Docker images
resource "aws_ecr_repository" "mlops_sprint" {
  name                 = "mlops-sprint"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = "mlops-sprint"
  }
}

# ECR repository for MLflow custom image
resource "aws_ecr_repository" "mlflow" {
  name                 = "mlflow"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = "mlops-sprint"
  }
}

# S3 bucket path for MLflow artifacts (same bucket, different prefix)
# mlops-sprint-ravali/mlflow-artifacts/

# Print key resource identifiers after apply
output "s3_bucket_name" {
  value = aws_s3_bucket.predictions.bucket
}

output "ecr_repository_url" {
  value = aws_ecr_repository.mlops_sprint.repository_url
}
