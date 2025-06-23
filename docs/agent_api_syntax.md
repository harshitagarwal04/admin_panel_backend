# Agent API Syntax Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All agent endpoints require JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## 1. Create Agent
**POST** `/agents/`

```bash
# Full example with all fields
curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Sales Agent\",\"prompt\":\"You are a professional sales agent. Be friendly and helpful.\",\"welcome_message\":\"Hello! How can I help you today?\",\"voice_id\":\"11111111-1111-1111-1111-111111111111\",\"variables\":{\"company_name\":\"{{company_name}}\",\"product\":\"{{product}}\"},\"functions\":[\"transfer_call\",\"end_call\"],\"inbound_phone\":\"+1234567890\",\"outbound_phone\":\"+0987654321\",\"max_attempts\":3,\"retry_delay_minutes\":60,\"business_hours_start\":\"09:00\",\"business_hours_end\":\"18:00\",\"timezone\":\"America/New_York\",\"max_call_duration_minutes\":30}"


# Minimal example (only required fields)
curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple Agent",
    "prompt": "You are a helpful assistant."
  }'
```

### Response
```json
{
  "id": "uuid",
  "company_id": "uuid",
  "name": "Sales Agent",
  "prompt": "You are a professional sales agent. Be friendly and helpful.",
  "welcome_message": "Hello! How can I help you today?",
  "voice_id": "11111111-1111-1111-1111-111111111111",
  "status": "active",
  "variables": {
    "company_name": "{{company_name}}",
    "product": "{{product}}"
  },
  "functions": ["transfer_call", "end_call"],
  "inbound_phone": "+1234567890",
  "outbound_phone": "+0987654321",
  "max_attempts": 3,
  "retry_delay_minutes": 60,
  "business_hours_start": "09:00",
  "business_hours_end": "18:00",
  "timezone": "America/New_York",
  "max_call_duration_minutes": 30,
  "retell_agent_id": "retell_agent_123",
  "created_at": "2025-06-23T10:00:00Z",
  "updated_at": "2025-06-23T10:00:00Z"
}
```

## 2. List Agents
**GET** `/agents/`

### Query Parameters
- `page` (optional, default: 1): Page number
- `per_page` (optional, default: 10, max: 100): Items per page
- `status_filter` (optional): Filter by status ("active" or "inactive")

```bash
# List all agents
curl -X GET "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN"

# With pagination
curl -X GET "http://localhost:8000/api/v1/agents/?page=2&per_page=20" \
  -H "Authorization: Bearer <your_jwt_token>"

# Filter by status
curl -X GET "http://localhost:8000/api/v1/agents/?status_filter=active" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### Response
```json
{
  "agents": [
    {
      "id": "uuid",
      "company_id": "uuid",
      "name": "Sales Agent",
      "prompt": "You are a professional sales agent...",
      "status": "active",
      "voice_id": "11111111-1111-1111-1111-111111111111",
      "created_at": "2025-06-23T10:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 10
}
```

## 3. Get Single Agent
**GET** `/agents/{agent_id}`

```bash
curl -X GET "http://localhost:8080/api/v1/agents/fe3e7b28-a9d5-4967-a78c-1e18bad870c4" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
Same as Create Agent response

## 4. Update Agent
**PUT** `/agents/{agent_id}`

```bash
curl -X PUT "http://localhost:8080/api/v1/agents/fe3e7b28-a9d5-4967-a78c-1e18bad870c4" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Sales Agent",
    "prompt": "You are an experienced sales professional...",
    "max_attempts": 5,
    "business_hours_end": "20:00"
  }'
```

### Request Body
All fields are optional - only include fields you want to update:
```json
{
  "name": "string",
  "prompt": "string",
  "welcome_message": "string",
  "voice_id": "uuid",
  "variables": {},
  "functions": [],
  "inbound_phone": "string",
  "outbound_phone": "string",
  "max_attempts": 0,
  "retry_delay_minutes": 0,
  "business_hours_start": "string",
  "business_hours_end": "string",
  "timezone": "string",
  "max_call_duration_minutes": 0
}
```

### Response
Same as Create Agent response

## 5. Toggle Agent Status
**PATCH** `/agents/{agent_id}/status`

Toggles between "active" and "inactive" status.

```bash
curl -X PATCH "http://localhost:8080/api/v1/agents/fe3e7b28-a9d5-4967-a78c-1e18bad870c4/status" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "status": "inactive"
}
```

## 6. Delete Agent
**DELETE** `/agents/{agent_id}`

Soft deletes the agent (marks as deleted but keeps in database).

```bash
curl -X DELETE "http://localhost:8080/api/v1/agents/fe3e7b28-a9d5-4967-a78c-1e18bad870c4" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "message": "Agent deleted"
}
```

## 7. List Available Voices
**GET** `/agents/voices/`

Get all available voices for agents.

```bash
curl -X GET "http://localhost:8080/api/v1/agents/voices/" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
[
  {
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "Sarah",
    "provider": "retell",
    "gender": "female",
    "language": "en-US",
    "accent": "american",
    "sample_url": "https://example.com/voice-sample.mp3",
    "is_active": true
  },
  {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "John",
    "provider": "retell",
    "gender": "male",
    "language": "en-US",
    "accent": "american",
    "sample_url": "https://example.com/voice-sample-2.mp3",
    "is_active": true
  }
]
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden (Onboarding Incomplete)
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
  "detail": "Agent not found"
}
```

### 400 Bad Request (Agent Limit Reached)
```json
{
  "detail": "Agent limit reached"
}
```

### 422 Unprocessable Entity (Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Example: Complete Agent Creation Flow

```bash
# Step 1: Login and get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/test-login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}' | jq -r '.access_token')

# Step 2: Complete profile (if new user)
curl -X PUT "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "+1234567890",
    "company_name": "Acme Corp"
  }'

# Step 3: Get available voices (IMPORTANT: Do this before creating agent)
curl -X GET "http://localhost:8000/api/v1/agents/voices/" \
  -H "Authorization: Bearer $TOKEN"

# Step 4: Create agent with valid voice_id from step 3
curl -X POST "http://localhost:8000/api/v1/agents/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Support Agent",
    "prompt": "You are a helpful customer support agent for Acme Corp.",
    "welcome_message": "Hello! Welcome to Acme Corp support. How can I assist you today?",
    "voice_id": "11111111-1111-1111-1111-111111111111"
  }'

# Step 5: List your agents
curl -X GET "http://localhost:8000/api/v1/agents/" \
  -H "Authorization: Bearer $TOKEN"
```

## Available Voice IDs (after seeding)

**Note**: You can use either our database UUIDs or direct Retell voice IDs. Our system automatically maps UUIDs to the correct Retell voice IDs.

| Voice ID (UUID) | Name | Maps to Retell ID | Language |
|-----------------|------|--------------------|----------|
| 11111111-1111-1111-1111-111111111111 | Sarah - American | 11labs-Adrian | en-US |
| 22222222-2222-2222-2222-222222222222 | John - American | 11labs-Adrian | en-US |
| 33333333-3333-3333-3333-333333333333 | Emma - British | 11labs-Adrian | en-GB |
| 44444444-4444-4444-4444-444444444444 | David - British | 11labs-Adrian | en-GB |
| 55555555-5555-5555-5555-555555555555 | Maria - Spanish | 11labs-Adrian | es-ES |

**Direct Retell Voice IDs** (can be used directly):
- `11labs-Adrian` - Professional male voice (recommended)