# Google Cloud Platform Commands Reference

This file contains all the successful GCP commands used for deploying and managing the Voice AI Admin API.

## 1. Docker Image Building and Deployment

### Build Docker image with Cloud Build
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/voice-ai-admin-api:latest .
```

### Build optimized Docker image
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/voice-ai-admin-api:optimized .
```

### Check build status
```bash
gcloud builds describe BUILD_ID --region=global
```

## 2. Cloud Run Deployment

### Deploy to Cloud Run
```bash
gcloud run deploy voice-ai-admin-api \
  --image gcr.io/PROJECT_ID/voice-ai-admin-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 100 \
  --timeout 300 \
  --set-env-vars ENVIRONMENT=production
```

### Deploy with specific image tag
```bash
gcloud run deploy voice-ai-admin-api \
  --image gcr.io/PROJECT_ID/voice-ai-admin-api:optimized \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 3. Environment Variable Management

### Set individual environment variables
```bash
gcloud run services update voice-ai-admin-api \
  --region=us-central1 \
  --set-env-vars="ENVIRONMENT=production"

gcloud run services update voice-ai-admin-api \
  --region=us-central1 \
  --set-env-vars="DATABASE_URL=postgresql://username:password@host:port/database"

gcloud run services update voice-ai-admin-api \
  --region=us-central1 \
  --set-env-vars="SECRET_KEY=your-secret-key"

gcloud run services update voice-ai-admin-api \
  --region=us-central1 \
  --set-env-vars="GOOGLE_CLIENT_ID=your-google-client-id"

gcloud run services update voice-ai-admin-api \
  --region=us-central1 \
  --set-env-vars="GOOGLE_CLIENT_SECRET=your-google-client-secret"

gcloud run services update voice-ai-admin-api \
  --region=us-central1 \
  --set-env-vars="RETELL_API_KEY=your-retell-api-key"
```

### Set multiple environment variables at once
```bash
gcloud run services update voice-ai-admin-api \
  --region=us-central1 \
  --set-env-vars="VAR1=value1,VAR2=value2,VAR3=value3"
```

## 4. Service Management and Monitoring

### Describe Cloud Run service
```bash
gcloud run services describe voice-ai-admin-api \
  --region=us-central1
```

### Get service URL
```bash
gcloud run services describe voice-ai-admin-api \
  --region=us-central1 \
  --format="value(status.url)"
```

### Check environment variables
```bash
gcloud run services describe voice-ai-admin-api \
  --region=us-central1 \
  --format="yaml(spec.template.spec.containers[0].env)"
```

### List Cloud Run services
```bash
gcloud run services list --region=us-central1
```

### Check service status and URL
```bash
gcloud run services list \
  --region=us-central1 \
  --filter="metadata.name=voice-ai-admin-api" \
  --format="table(status.url,status.conditions[0].message)"
```

## 5. Container Registry Management

### List container images
```bash
gcloud container images list --repository=gcr.io/PROJECT_ID
```

### List image tags with metadata
```bash
gcloud container images list-tags gcr.io/PROJECT_ID/voice-ai-admin-api \
  --format="table(tags,timestamp,digest,size_mb)"
```

### Describe specific image
```bash
gcloud container images describe gcr.io/PROJECT_ID/voice-ai-admin-api:latest
```

## 6. Logging and Troubleshooting

### View Cloud Run logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=voice-ai-admin-api" \
  --limit=10 \
  --format=json
```

### View recent logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=voice-ai-admin-api" \
  --limit=5 \
  --format=json | jq -r '.[].textPayload' | grep -v "null"
```

## 7. Cloud Scheduler (Optional)

### Create scheduled job for call scheduler
```bash
gcloud scheduler jobs create http call-scheduler \
  --schedule="* * * * *" \
  --uri="https://SERVICE_URL/api/v1/calls/run-scheduler" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --location=us-central1 \
  --max-retry-attempts=3 \
  --max-retry-duration=300s \
  --time-zone="UTC"
```

## 8. IAM and Security

### Grant service account access to secrets (if using Secret Manager)
```bash
gcloud secrets add-iam-policy-binding SECRET_NAME \
    --member="serviceAccount:PROJECT-NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## 9. Project Configuration

### Set default project
```bash
gcloud config set project PROJECT_ID
```

### Set default region
```bash
gcloud config set run/region us-central1
```

## Important Notes

1. Replace `PROJECT_ID` with your actual Google Cloud project ID
2. Replace credential values with your actual values when using these commands
3. Use `--format` flags to customize output format (json, yaml, table, value)
4. Add `--quiet` flag to suppress interactive prompts in scripts
5. Use `--dry-run` flag to preview changes before applying them

## Environment Variables Used
- `ENVIRONMENT=production`
- `DATABASE_URL=postgresql://...` (with actual database credentials)
- `SECRET_KEY=...` (your JWT secret)
- `GOOGLE_CLIENT_ID=...` (your Google OAuth client ID)
- `GOOGLE_CLIENT_SECRET=...` (your Google OAuth client secret)
- `RETELL_API_KEY=...` (your Retell AI API key)

## Service URL
Production service is running at: `https://voice-ai-admin-api-762279639608.us-central1.run.app`