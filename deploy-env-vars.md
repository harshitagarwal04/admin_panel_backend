# Environment Variables Setup for Cloud Run

## Security Best Practices

### 1. **Never commit sensitive data to git**
- `.env` file should be in `.gitignore`
- Use Google Secret Manager for sensitive values
- Use Cloud Run environment variables for non-sensitive config

### 2. **Recommended Approach: Google Secret Manager**

```bash
# Create secrets in Google Secret Manager
gcloud secrets create database-url --data-file=- <<< "postgresql://postgres:PASSWORD@HOST:5432/voiceai?sslmode=require"
gcloud secrets create secret-key --data-file=- <<< "your-secret-key"
gcloud secrets create google-client-secret --data-file=- <<< "GOCSPX-xxx"
gcloud secrets create retell-api-key --data-file=- <<< "key_xxx"

# Grant Cloud Run service access to secrets
gcloud secrets add-iam-policy-binding database-url \
    --member="serviceAccount:PROJECT-NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 3. **Alternative: Manual Environment Variables**

Set environment variables through Google Cloud Console:
1. Go to Cloud Run → voice-ai-admin-api → Edit & Deploy New Revision
2. Go to "Variables & Secrets" tab
3. Add environment variables one by one

### 4. **Current Status**
Only `ENVIRONMENT=production` is currently set. You need to add:
- DATABASE_URL
- SECRET_KEY  
- GOOGLE_CLIENT_ID (can be public)
- GOOGLE_CLIENT_SECRET (should be secret)
- RETELL_API_KEY (should be secret)

### 5. **Verification**
```bash
# Check current env vars
gcloud run services describe voice-ai-admin-api --region=us-central1 --format="yaml(spec.template.spec.containers[0].env)"
```

## Security Notes
- Database passwords should use Google Secret Manager
- API keys should never be in source code
- Use least-privilege IAM policies
- Rotate secrets regularly