#!/bin/bash

# Voice AI Admin Panel - Deployment Script
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
SERVICE_NAME="voice-ai-admin-api"

echo "🚀 Deploying Voice AI Admin Panel API to $ENVIRONMENT"

# Build and push Docker image
echo "📦 Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

echo "🔄 Pushing image to Container Registry..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 100 \
  --timeout 300 \
  --set-env-vars ENVIRONMENT=$ENVIRONMENT

# Setup Cloud Scheduler for call scheduling
echo "⏰ Setting up Cloud Scheduler..."
gcloud scheduler jobs create http call-scheduler \
  --schedule="* * * * *" \
  --uri="https://$SERVICE_NAME-$PROJECT_ID.a.run.app/api/v1/calls/run-scheduler" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --location=$REGION \
  --max-retry-attempts=3 \
  --max-retry-duration=300s \
  --time-zone="UTC" || echo "Scheduler job already exists"

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: https://$SERVICE_NAME-$PROJECT_ID.a.run.app"
echo "📚 API Docs: https://$SERVICE_NAME-$PROJECT_ID.a.run.app/docs"