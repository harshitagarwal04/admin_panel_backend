# Lead Management & Scheduling API Documentation

## Base URL
```
http://localhost:8080/api/v1
```

## Authentication
All lead endpoints require JWT token in the Authorization header:
```
Authorization: Bearer $API_TOKEN
```

## 1. Create Lead
**POST** `/leads/`

Create a new lead for calling. The lead will be scheduled for calling at the specified time or immediately if no schedule_at is provided.

```bash
# Full example with all fields
curl -X POST "http://localhost:8080/api/v1/leads/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "53420311-13b0-44c5-93df-30f38985e7a0",
    "first_name": "John",
    "phone_e164": "+14155552670",
    "custom_fields": {
      "company": "Acme Corp",
      "position": "Manager",
      "notes": "Interested in premium plan"
    },
    "schedule_at": "2025-06-24T14:00:00Z"
  }'

# Minimal example (only required fields)
curl -X POST "http://localhost:8080/api/v1/leads/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "53420311-13b0-44c5-93df-30f38985e7a0",
    "first_name": "Jane",
    "phone_e164": "+14155552672"
  }'
```

### Request Body
```json
{
  "agent_id": "string (UUID)",
  "first_name": "string",
  "phone_e164": "string (E.164 format: +1234567890)",
  "custom_fields": {
    "key": "value"
  },
  "schedule_at": "ISO 8601 datetime (optional, defaults to now)"
}
```

### Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "agent_id": "fe3e7b28-a9d5-4967-a78c-1e18bad870c4",
  "first_name": "John",
  "phone_e164": "+14155552671",
  "status": "new",
  "custom_fields": {
    "company": "Acme Corp",
    "position": "Manager",
    "notes": "Interested in premium plan"
  },
  "schedule_at": "2025-06-24T14:00:00Z",
  "attempts_count": 0,
  "disposition": null,
  "created_at": "2025-06-23T10:00:00Z",
  "updated_at": "2025-06-23T10:00:00Z"
}
```

## 2. List Leads
**GET** `/leads/`

### Query Parameters
- `agent_id` (optional): Filter by specific agent
- `status_filter` (optional): Filter by status ("new", "in_progress", "done")
- `search` (optional): Search by name or phone number
- `page` (optional, default: 1): Page number
- `per_page` (optional, default: 10, max: 100): Items per page

```bash
# List all leads
curl -X GET "http://localhost:8080/api/v1/leads/" \
  -H "Authorization: Bearer $API_TOKEN"

# Filter by agent
curl -X GET "http://localhost:8080/api/v1/leads/?agent_id=fe3e7b28-a9d5-4967-a78c-1e18bad870c4" \
  -H "Authorization: Bearer $API_TOKEN"

# Filter by status
curl -X GET "http://localhost:8080/api/v1/leads/?status_filter=new" \
  -H "Authorization: Bearer $API_TOKEN"

# Search leads
curl -X GET "http://localhost:8080/api/v1/leads/?search=john" \
  -H "Authorization: Bearer $API_TOKEN"

# With pagination
curl -X GET "http://localhost:8080/api/v1/leads/?page=2&per_page=20" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "leads": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "agent_id": "fe3e7b28-a9d5-4967-a78c-1e18bad870c4",
      "first_name": "John",
      "phone_e164": "+14155552671",
      "status": "new",
      "custom_fields": {},
      "schedule_at": "2025-06-24T14:00:00Z",
      "attempts_count": 0,
      "disposition": null,
      "created_at": "2025-06-23T10:00:00Z",
      "updated_at": "2025-06-23T10:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10
}
```

## 3. Get Single Lead
**GET** `/leads/{lead_id}`

```bash
curl -X GET "http://localhost:8080/api/v1/leads/dbc86e86-1d91-477f-aa2f-a1abd387eb6b" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
Same as Create Lead response

## 4. Update Lead
**PUT** `/leads/{lead_id}`

Update lead information. All fields are optional.

```bash
curl -X PUT "http://localhost:8080/api/v1/leads/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John Smith",
    "custom_fields": {
      "company": "Acme Corp",
      "position": "Senior Manager",
      "notes": "Very interested, schedule follow-up"
    },
    "schedule_at": "2025-06-25T10:00:00Z"
  }'
```

### Request Body
```json
{
  "first_name": "string (optional)",
  "phone_e164": "string (optional, E.164 format)",
  "status": "string (optional: new|in_progress|done)",
  "custom_fields": "object (optional)",
  "schedule_at": "ISO 8601 datetime (optional)",
  "disposition": "string (optional: not_interested|hung_up|completed|no_answer)"
}
```

## 5. Delete Lead
**DELETE** `/leads/{lead_id}`

Soft delete a lead (marks as deleted but keeps in database).

```bash
curl -X DELETE "http://localhost:8080/api/v1/leads/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "message": "Lead deleted"
}
```

## 6. Import Leads from CSV
**POST** `/leads/csv-import`

Import multiple leads from a CSV file.

### CSV Format
Required columns:
- `first_name`: Lead's first name
- `phone`: Phone number (will be normalized to E.164)

Optional columns:
- `schedule_at`: ISO 8601 datetime for scheduling
- Any other columns will be stored as custom fields

Example CSV:
```csv
first_name,phone,company,position,notes,schedule_at
John,+14155552671,Acme Corp,Manager,Interested in premium,2025-06-24T14:00:00Z
Jane,415-555-2672,TechCo,Director,Follow up next week,
Bob,(415) 555-2673,StartupInc,CEO,High priority,
```

```bash
curl -X POST "http://localhost:8080/api/v1/leads/csv-import?agent_id=fe3e7b28-a9d5-4967-a78c-1e18bad870c4" \
  -H "Authorization: Bearer $API_TOKEN" \
  -F "file=@leads.csv"
```

### Response
```json
{
  "success_count": 2,
  "error_count": 1,
  "errors": [
    {
      "row": 4,
      "error": "Invalid phone number format: (415) 555-invalid"
    }
  ],
  "total_processed": 3
}
```

## 7. Schedule Call for Lead
**POST** `/calls/schedule`

Immediately schedule a lead for calling (bypasses normal scheduling).

```bash
curl -X POST "http://localhost:8080/api/v1/calls/schedule" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "dbc86e86-1d91-477f-aa2f-a1abd387eb6b"
  }'
```

### Response
```json
{
  "message": "Lead scheduled successfully"
}
```

## 8. Get Call History
**GET** `/calls/history`

Retrieve call history with filtering options.

### Query Parameters
- `agent_id` (optional): Filter by agent
- `outcome` (optional): Filter by outcome ("answered", "no_answer", "failed")
- `start_date` (optional): Filter by date range (YYYY-MM-DD)
- `end_date` (optional): Filter by date range (YYYY-MM-DD)
- `search` (optional): Search by lead name, phone, or agent name
- `page` (optional, default: 1): Page number
- `per_page` (optional, default: 10, max: 100): Items per page

```bash
# Get all call history
curl -X GET "http://localhost:8080/api/v1/calls/history" \
  -H "Authorization: Bearer $API_TOKEN"

# Filter by agent and outcome
curl -X GET "http://localhost:8080/api/v1/calls/history?agent_id=fe3e7b28-a9d5-4967-a78c-1e18bad870c4&outcome=answered" \
  -H "Authorization: Bearer $API_TOKEN"

# Filter by date range
curl -X GET "http://localhost:8080/api/v1/calls/history?start_date=2025-06-01&end_date=2025-06-30" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "calls": [
    {
      "id": "789e4567-e89b-12d3-a456-426614174000",
      "lead_id": "123e4567-e89b-12d3-a456-426614174000",
      "agent_id": "fe3e7b28-a9d5-4967-a78c-1e18bad870c4",
      "lead_name": "John",
      "lead_phone": "+14155552671",
      "agent_name": "Sales Agent",
      "status": "completed",
      "outcome": "answered",
      "duration_seconds": 180,
      "transcript_url": "https://example.com/transcript/123",
      "summary": "Customer interested in premium plan, scheduled demo for next week",
      "created_at": "2025-06-23T14:15:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 10
}
```

## 9. Get Call Metrics
**GET** `/calls/metrics`

Get aggregated call metrics and statistics.

### Query Parameters
- `agent_id` (optional): Filter by agent
- `start_date` (optional): Filter by date range (YYYY-MM-DD)
- `end_date` (optional): Filter by date range (YYYY-MM-DD)

```bash
# Get overall metrics
curl -X GET "http://localhost:8080/api/v1/calls/metrics" \
  -H "Authorization: Bearer $API_TOKEN"

# Get metrics for specific agent
curl -X GET "http://localhost:8080/api/v1/calls/metrics?agent_id=fe3e7b28-a9d5-4967-a78c-1e18bad870c4" \
  -H "Authorization: Bearer $API_TOKEN"

# Get metrics for date range
curl -X GET "http://localhost:8080/api/v1/calls/metrics?start_date=2025-06-01&end_date=2025-06-30" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "total_calls": 500,
  "answered_calls": 350,
  "no_answer_calls": 120,
  "failed_calls": 30,
  "pickup_rate": 70.0,
  "average_attempts_per_lead": 1.8,
  "active_agents": 5
}
```

## Error Responses

### 400 Bad Request (Invalid Phone Number)
```json
{
  "detail": "Invalid phone number format"
}
```

### 400 Bad Request (Duplicate Lead)
```json
{
  "detail": "Lead with this phone number already exists for this agent"
}
```

### 404 Not Found
```json
{
  "detail": "Lead not found"
}
```

### 422 Unprocessable Entity (Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "phone_e164"],
      "msg": "Phone number must be in E.164 format",
      "type": "value_error"
    }
  ]
}
```

## Lead Status Flow

1. **new**: Lead is created and waiting to be called
2. **in_progress**: Lead is currently being called or scheduled for retry
3. **done**: Lead has been called successfully or max attempts reached

## Lead Disposition Values

- **completed**: Call was answered and completed successfully
- **no_answer**: Call was not answered after max attempts
- **not_interested**: Lead indicated they're not interested
- **hung_up**: Lead hung up during the call

## Example: Complete Lead Creation and Calling Flow

```bash
# Step 1: Get your agents
curl -X GET "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN"

# Step 2: Create a lead
LEAD_ID=$(curl -X POST "http://localhost:8080/api/v1/leads/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "fe3e7b28-a9d5-4967-a78c-1e18bad870c4",
    "first_name": "John",
    "phone_e164": "+14155552671",
    "custom_fields": {
      "company": "Acme Corp"
    }
  }' | jq -r '.id')

# Step 3: Schedule the lead for immediate calling
curl -X POST "http://localhost:8080/api/v1/calls/schedule" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"lead_id\": \"$LEAD_ID\"}"

# Step 4: Check call history
curl -X GET "http://localhost:8080/api/v1/calls/history?search=John" \
  -H "Authorization: Bearer $API_TOKEN"

# Step 5: Get metrics
curl -X GET "http://localhost:8080/api/v1/calls/metrics" \
  -H "Authorization: Bearer $API_TOKEN"
```

## Scheduling Notes

1. **Business Hours**: Calls are only made during the agent's configured business hours
2. **Retry Logic**: Failed calls are retried based on agent's `max_attempts` and `retry_delay_minutes`
3. **Immediate Scheduling**: Use `/calls/schedule` endpoint to bypass normal scheduling
4. **Scheduler Service**: The system runs a scheduler every minute to process leads

## Phone Number Format

All phone numbers must be in E.164 format:
- Starts with `+`
- Country code (1-3 digits)
- Subscriber number (up to 12 digits)
- Total length: 1-15 digits

Examples:
- US: `+14155552671`
- UK: `+442071838750`
- India: `+919876543210`