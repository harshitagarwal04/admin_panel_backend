# Retell AI API Integration Documentation

## Overview

This document outlines the main Retell AI APIs we use for our Voice AI Sales Agent platform and the specific parameters we utilize.

## Base Configuration

**Base URL**: `https://api.retellai.com`
**Authentication**: Bearer token in Authorization header
**API Version**: v2

## 1. Agent Management APIs

### Create Agent
**POST** `/create-agent`

Creates a new voice AI agent with specified configuration.

#### Our Implementation Parameters:
```json
{
  "agent_name": "string (our agent name)",
  "response_engine": {
    "type": "retell-llm",
    "llm_id": "retell-provided-llm-id"
  },
  "voice_id": "string (voice selection)",
  "voice_model": "eleven_turbo_v2",
  "language": "en-US",
  "voice_temperature": 1.0,
  "voice_speed": 1.0,
  "responsiveness": 0.8,
  "enable_backchannel": true,
  "webhook_url": "https://our-domain.com/api/v1/calls/webhook"
}
```

#### Response:
```json
{
  "agent_id": "oBeDLoLOeuAbiuaMFXRtDOLriTJ5tSxD",
  "agent_name": "Sales Agent",
  "voice_id": "11labs-Adrian",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Agent
**PATCH** `/update-agent/{agent_id}`

Updates existing agent configuration.

#### Our Update Parameters:
```json
{
  "agent_name": "string (optional)",
  "voice_id": "string (optional)", 
  "voice_temperature": "number (optional)",
  "voice_speed": "number (optional)",
  "responsiveness": "number (optional)"
}
```

### Get Agent
**GET** `/get-agent/{agent_id}`

Retrieves agent details.

### Delete Agent
**DELETE** `/delete-agent/{agent_id}`

Deletes an agent.

## 2. Phone Call APIs

### Create Phone Call
**POST** `/v2/create-phone-call`

Initiates a phone call with a specific agent.

#### Our Implementation Parameters:
```json
{
  "from_number": "+1234567890 (our registered phone number)",
  "to_number": "+1987654321 (lead's phone number)",
  "override_agent_id": "agent_id_from_our_db",
  "metadata": {
    "lead_id": "uuid-from-our-db",
    "agent_id": "uuid-from-our-db", 
    "company_id": "uuid-from-our-db",
    "attempt_number": 1
  },
  "retell_llm_dynamic_variables": {
    "lead_name": "John Doe",
    "company_name": "Acme Corp",
    "product": "AI Voice Assistant"
  }
}
```

#### Response:
```json
{
  "call_id": "11bea5d1e4e847b58e24ef83b94d1c52",
  "agent_id": "oBeDLoLOeuAbiuaMFXRtDOLriTJ5tSxD", 
  "call_status": "registered"
}
```

### List Calls
**GET** `/v2/list-calls`

Retrieves call history with filtering.

#### Our Query Parameters:
- `agent_id`: Filter by specific agent
- `limit`: Number of calls to return (max 1000)
- `pagination_key`: For pagination
- `filter_criteria`: JSON object with filters
  - `call_successful`: boolean
  - `start_timestamp`: ISO datetime
  - `end_timestamp`: ISO datetime

#### Example Request:
```
GET /v2/list-calls?agent_id=oBeDLoLOeuAbiuaMFXRtDOLriTJ5tSxD&limit=50
```

## 3. Webhook Events

### Call Events We Handle

Retell sends webhooks to our `/api/v1/calls/webhook` endpoint for:

#### Call Started
```json
{
  "event": "call_started",
  "call": {
    "call_id": "11bea5d1e4e847b58e24ef83b94d1c52",
    "agent_id": "oBeDLoLOeuAbiuaMFXRtDOLriTJ5tSxD",
    "from_number": "+1234567890",
    "to_number": "+1987654321",
    "metadata": {...}
  }
}
```

#### Call Ended
```json
{
  "event": "call_ended",
  "call": {
    "call_id": "11bea5d1e4e847b58e24ef83b94d1c52",
    "agent_id": "oBeDLoLOeuAbiuaMFXRtDOLriTJ5tSxD",
    "call_analysis": {
      "call_successful": true,
      "call_summary": "Customer interested in premium plan",
      "user_sentiment": "Positive"
    },
    "recording_url": "https://storage.retellai.com/...",
    "transcript": "Full conversation transcript",
    "duration": 180
  }
}
```

## 4. Error Handling

### Common HTTP Status Codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (invalid API key)
- `404`: Not Found (agent/call doesn't exist)
- `429`: Rate Limited
- `500`: Internal Server Error

### Error Response Format:
```json
{
  "error": {
    "type": "validation_error",
    "message": "Invalid phone number format",
    "details": {...}
  }
}
```

## 5. Rate Limits

- **Agent Operations**: 10 requests per minute
- **Call Creation**: 100 requests per minute
- **Call Listing**: 60 requests per minute

## 6. Our Integration Flow

1. **Agent Creation**: Create Retell agent → Store `retell_agent_id` in our DB
2. **Lead Scheduling**: When lead is due → Call Retell API to initiate call
3. **Call Tracking**: Store `retell_call_id` in our interaction attempts
4. **Webhook Processing**: Receive call results → Update lead status and metrics
5. **Metrics**: Use List Calls API for reporting and analytics

## 7. Environment Variables Required

```bash
RETELL_API_KEY=your_retell_api_key_here
RETELL_WEBHOOK_SECRET=webhook_signature_verification_key
RETELL_BASE_URL=https://api.retellai.com
```

## 8. Mock Mode

For development/testing without real calls:
- Return mock responses when `RETELL_API_KEY` is not configured
- Log call attempts without making actual API calls
- Simulate webhook events for testing