# Stage 1: Builder
# Use a full Python image to install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy and install dependencies into a separate directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final image
# Start fresh with a clean slim image — keeps the final image small
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy app code and trained model
COPY app/ .

# Expose port 8000 so traffic can reach the app
EXPOSE 8000

# Run the FastAPI app when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
