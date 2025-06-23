# Authentication API Documentation

## Base URL
```
http://localhost:8080/api/v1
```

## Authentication Flow Overview

The authentication process is a 2-step flow:
1. **Login/Register**: User logs in with email (or Google OAuth in production)
2. **Complete Profile**: User provides name, phone, and company name

After completing both steps, users can access all business endpoints.

## 1. Test Login (Development Only)
**POST** `/auth/test-login`

This endpoint is only available in development environment for testing without Google OAuth.

```bash
# Login with email (creates new user if doesn't exist)
curl -X POST "http://localhost:8080/api/v1/auth/test-login" \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com"}'
```

### Request Body
```json
{
  "email": "user@example.com"
}
```

### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the `access_token` as it's required for all subsequent API calls.

## 2. Google Login (Production)
**POST** `/auth/google-login`

Login using Google OAuth token.

```bash
curl -X POST "http://localhost:8080/api/v1/auth/google-login" \
  -H "Content-Type: application/json" \
  -d '{"token": "google-oauth-token-here"}'
```

### Request Body
```json
{
  "token": "google-oauth-token"
}
```

### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 3. Get Current User Info
**GET** `/auth/me`

Check current user's profile status and determine next onboarding step.

```bash
curl -X GET "http://localhost:8080/api/v1/auth/me" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response (New User)
```json
{
  "id": "e04c881f-57b5-42d8-bc38-83c38968a5a2",
  "email": "newuser@example.com",
  "name": null,
  "phone": null,
  "is_profile_complete": false,
  "has_company": false
}
```

### Response (Completed Profile)
```json
{
  "id": "e04c881f-57b5-42d8-bc38-83c38968a5a2",
  "email": "newuser@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "is_profile_complete": true,
  "has_company": true
}
```

## 4. Complete Profile + Create Company
**PUT** `/auth/profile`

Complete user profile and create company in a single step. This must be done before accessing business endpoints.

```bash
curl -X PUT "http://localhost:8080/api/v1/auth/profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "name": "John Doe",
    "phone": "+1234567890", 
    "company_name": "My AI Company"
  }'
```

### Request Body
```json
{
  "name": "string (required)",
  "phone": "string (optional)",
  "company_name": "string (required)"
}
```

### Response
```json
{
  "id": "e04c881f-57b5-42d8-bc38-83c38968a5a2",
  "email": "newuser@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "is_profile_complete": true,
  "has_company": true
}
```

## 5. Get User's Company
**GET** `/auth/company`

Get details of the user's company.

```bash
curl -X GET "http://localhost:8080/api/v1/auth/company" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "id": "3f343ee3-bb0d-4eba-9b8a-af763c6d92b5",
  "name": "My AI Company",
  "max_agents_limit": 10,
  "max_concurrent_calls": 2,
  "total_minutes_limit": null,
  "total_minutes_used": 0
}
```

## Complete Onboarding Flow Example

```bash
# Step 1: Login/Register (Email Only)
RESPONSE=$(curl -s -X POST "http://localhost:8080/api/v1/auth/test-login" \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com"}')

# Extract token
export API_TOKEN=$(echo $RESPONSE | jq -r '.access_token')

# Step 2: Check user status
curl -X GET "http://localhost:8080/api/v1/auth/me" \
  -H "Authorization: Bearer $API_TOKEN"

# Step 3: Complete Profile + Company (Single Step)
curl -X PUT "http://localhost:8080/api/v1/auth/profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "name": "John Doe",
    "phone": "+1234567890", 
    "company_name": "My AI Company"
  }'

# Step 4: Verify completion
curl -X GET "http://localhost:8080/api/v1/auth/me" \
  -H "Authorization: Bearer $API_TOKEN"

# Now you can access business endpoints like agents, leads, etc.
curl -X GET "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN"
```

## JWT Token Details

- **Expiry**: 60 days from creation
- **Format**: Bearer token in Authorization header
- **Usage**: Required for all endpoints except login endpoints

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 400 Bad Request (User Already Has Company)
```json
{
  "detail": "User already has a company"
}
```

### 422 Unprocessable Entity (Onboarding Incomplete)
When trying to access business endpoints without completing profile:
```json
{
  "detail": "ONBOARDING_INCOMPLETE",
  "message": "Please complete your profile and company setup before accessing this feature",
  "onboarding_step": "profile",
  "required_fields": ["name", "phone", "company_name"]
}
```

### 404 Not Found
```json
{
  "detail": "Company not found"
}
```

## Onboarding Enforcement

The system uses middleware to enforce onboarding completion:

1. **Excluded Endpoints** (No onboarding required):
   - `/auth/*` - All auth endpoints
   - `/health` - Health check
   - `/docs`, `/redoc` - API documentation
   - `/openapi.json` - OpenAPI schema

2. **Protected Endpoints** (Requires completed profile):
   - `/agents/*` - Agent management
   - `/leads/*` - Lead management
   - `/calls/*` - Call operations
   - All other business endpoints

## Security Notes

1. **Test Login**: Only available when `ENVIRONMENT=development`
2. **Google OAuth**: Required in production environment
3. **Token Storage**: Store tokens securely, never expose in logs or URLs
4. **Token Refresh**: Currently no refresh mechanism, users must login again after 60 days

## Quick Testing Script

Save this as `test_auth.sh`:

```bash
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing Authentication Flow..."

# Step 1: Login
echo -e "${GREEN}Step 1: Login${NC}"
RESPONSE=$(curl -s -X POST "http://localhost:8080/api/v1/auth/test-login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}')

export API_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
echo "Token obtained: ${API_TOKEN:0:20}..."

# Step 2: Check status
echo -e "\n${GREEN}Step 2: Check User Status${NC}"
curl -s -X GET "http://localhost:8080/api/v1/auth/me" \
  -H "Authorization: Bearer $API_TOKEN" | jq '.'

# Step 3: Complete profile
echo -e "\n${GREEN}Step 3: Complete Profile${NC}"
curl -s -X PUT "http://localhost:8080/api/v1/auth/profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "name": "Test User",
    "phone": "+1234567890", 
    "company_name": "Test Company"
  }' | jq '.'

# Step 4: Try accessing protected endpoint
echo -e "\n${GREEN}Step 4: Access Protected Endpoint${NC}"
curl -s -X GET "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" | jq '.'
```

Make it executable and run:
```bash
chmod +x test_auth.sh
./test_auth.sh
```