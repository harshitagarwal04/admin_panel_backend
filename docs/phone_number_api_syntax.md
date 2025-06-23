# Phone Number Management API Documentation

## Base URL
```
http://localhost:8080/api/v1
```

## Authentication
All phone number endpoints require JWT token in the Authorization header:
```
Authorization: Bearer $API_TOKEN
```

## Overview

Phone number management allows you to:
1. Configure Twilio and Plivo provider credentials
2. Browse and purchase available phone numbers
3. Manage owned phone numbers
4. Assign numbers to agents for inbound/outbound calling

## Provider Setup Flow

### 1. Add Provider Credentials
**POST** `/phone-numbers/providers`

Configure Twilio or Plivo credentials for your company.

```bash
# Add Twilio credentials
curl -X POST "http://localhost:8080/api/v1/phone-numbers/providers" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "twilio",
    "credentials": {
      "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "auth_token": "your_twilio_auth_token"
    }
  }'

# Add Plivo credentials
curl -X POST "http://localhost:8080/api/v1/phone-numbers/providers" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "plivo",
    "credentials": {
      "auth_id": "MAxxxxxxxxxxxxxxx",
      "auth_token": "your_plivo_auth_token"
    }
  }'
```

### Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "company_id": "3f343ee3-bb0d-4eba-9b8a-af763c6d92b5",
  "provider": "twilio",
  "credentials": {
    "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "auth_token": "your_twilio_auth_token"
  },
  "created_at": "2025-06-23T10:00:00Z",
  "updated_at": "2025-06-23T10:00:00Z"
}
```

### 2. List Provider Credentials
**GET** `/phone-numbers/providers`

View configured phone providers for your company.

```bash
curl -X GET "http://localhost:8080/api/v1/phone-numbers/providers" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "company_id": "3f343ee3-bb0d-4eba-9b8a-af763c6d92b5",
    "provider": "twilio",
    "credentials": {
      "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "auth_token": "***masked***"
    },
    "created_at": "2025-06-23T10:00:00Z",
    "updated_at": "2025-06-23T10:00:00Z"
  }
]
```

### 3. Remove Provider
**DELETE** `/phone-numbers/providers/{provider}`

Remove provider credentials.

```bash
curl -X DELETE "http://localhost:8080/api/v1/phone-numbers/providers/twilio" \
  -H "Authorization: Bearer $API_TOKEN"
```

## Phone Number Management

### 4. Browse Available Numbers
**GET** `/phone-numbers/available`

Search for available phone numbers to purchase.

#### Query Parameters
- `provider` (required): "twilio" or "plivo"
- `country_code` (optional): Default "US"
- `area_code` (optional): Specific area code
- `limit` (optional): Number of results (default 20, max 100)

```bash
# Browse available Twilio numbers
curl -X GET "http://localhost:8080/api/v1/phone-numbers/available?provider=twilio" \
  -H "Authorization: Bearer $API_TOKEN"

# Browse with area code filter
curl -X GET "http://localhost:8080/api/v1/phone-numbers/available?provider=twilio&area_code=415" \
  -H "Authorization: Bearer $API_TOKEN"

# Browse Plivo numbers
curl -X GET "http://localhost:8080/api/v1/phone-numbers/available?provider=plivo&limit=10" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "numbers": [
    {
      "phone_number": "+14155552001",
      "provider": "twilio",
      "capabilities": ["voice", "sms", "mms"],
      "status": "available",
      "friendly_name": "(415) 555-2001",
      "country_code": "US",
      "number_type": "local",
      "monthly_cost": 1.00
    },
    {
      "phone_number": "+14155552002",
      "provider": "twilio",
      "capabilities": ["voice", "sms"],
      "status": "available",
      "friendly_name": "(415) 555-2002",
      "country_code": "US",
      "number_type": "local",
      "monthly_cost": 1.00
    }
  ],
  "total": 2,
  "provider": "twilio"
}
```

### 5. Purchase Phone Number
**POST** `/phone-numbers/purchase`

Purchase a phone number from the provider.

```bash
curl -X POST "http://localhost:8080/api/v1/phone-numbers/purchase" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+14155552001",
    "provider": "twilio",
    "capabilities": ["voice", "sms"]
  }'
```

### Response
```json
{
  "phone_number": "+14155552001",
  "provider": "twilio",
  "capabilities": ["voice", "sms"],
  "status": "active",
  "provider_number_id": "PN1234567890abcdef",
  "monthly_cost": 1.00,
  "friendly_name": "(415) 555-2001",
  "country_code": "US",
  "number_type": "local"
}
```

### 6. List Owned Numbers
**GET** `/phone-numbers/owned`

View all phone numbers owned by your company.

#### Query Parameters
- `provider` (optional): Filter by "twilio" or "plivo"

```bash
# List all owned numbers
curl -X GET "http://localhost:8080/api/v1/phone-numbers/owned" \
  -H "Authorization: Bearer $API_TOKEN"

# Filter by provider
curl -X GET "http://localhost:8080/api/v1/phone-numbers/owned?provider=twilio" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "numbers": [
    {
      "phone_number": "+14155559999",
      "provider": "twilio",
      "capabilities": ["voice", "sms", "mms"],
      "status": "active",
      "provider_number_id": "PN1234567890",
      "monthly_cost": 1.00,
      "friendly_name": "(415) 555-9999",
      "number_type": "local"
    },
    {
      "phone_number": "+14155558888",
      "provider": "plivo",
      "capabilities": ["voice", "sms"],
      "status": "active",
      "provider_number_id": "+14155558888",
      "monthly_cost": 0.80,
      "friendly_name": "+14155558888",
      "number_type": "local"
    }
  ],
  "total": 2,
  "provider": "all"
}
```

### 7. Release Phone Number
**DELETE** `/phone-numbers/{phone_number}`

Release a phone number back to the provider.

#### Query Parameters
- `provider` (required): "twilio" or "plivo"

```bash
curl -X DELETE "http://localhost:8080/api/v1/phone-numbers/+14155552001?provider=twilio" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "message": "Phone number +14155552001 released successfully"
}
```

## Agent Integration

### 8. Assign Numbers to Agents

Once you have purchased phone numbers, assign them to agents via the agent creation/update API:

```bash
# Create agent with phone numbers
curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Agent with Phone",
    "prompt": "You are a professional sales agent.",
    "voice_id": "11111111-1111-1111-1111-111111111111",
    "inbound_phone": "+14155559999",
    "outbound_phone": "+14155558888"
  }'

# Update existing agent with phone numbers
curl -X PUT "http://localhost:8080/api/v1/agents/agent_id_here" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inbound_phone": "+14155559999",
    "outbound_phone": "+14155558888"
  }'
```

## Complete Phone Setup Flow

```bash
# Step 1: Add Twilio credentials
curl -X POST "http://localhost:8080/api/v1/phone-numbers/providers" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "twilio",
    "credentials": {
      "account_sid": "your_account_sid",
      "auth_token": "your_auth_token"
    }
  }'

# Step 2: Browse available numbers
curl -X GET "http://localhost:8080/api/v1/phone-numbers/available?provider=twilio&area_code=415" \
  -H "Authorization: Bearer $API_TOKEN"

# Step 3: Purchase a number
curl -X POST "http://localhost:8080/api/v1/phone-numbers/purchase" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+14155552001",
    "provider": "twilio",
    "capabilities": ["voice", "sms"]
  }'

# Step 4: Verify ownership
curl -X GET "http://localhost:8080/api/v1/phone-numbers/owned" \
  -H "Authorization: Bearer $API_TOKEN"

# Step 5: Assign to agent
curl -X PUT "http://localhost:8080/api/v1/agents/your_agent_id" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inbound_phone": "+14155552001",
    "outbound_phone": "+14155552001"
  }'
```

## Error Responses

### 404 Not Found (No Provider Credentials)
```json
{
  "detail": "No twilio credentials found. Please add provider credentials first."
}
```

### 400 Bad Request (Invalid Provider)
```json
{
  "detail": "Invalid provider. Use 'twilio' or 'plivo'"
}
```

### 500 Internal Server Error (Provider API Error)
```json
{
  "detail": "Failed to fetch numbers from twilio: Authentication Error"
}
```

## Provider Comparison

| Feature | Twilio | Plivo |
|---------|--------|-------|
| **Monthly Cost** | $1.00/month | $0.80/month |
| **Voice Calls** | ✅ High quality | ✅ Good quality |
| **SMS Support** | ✅ Full support | ✅ Full support |
| **MMS Support** | ✅ Yes | ⚠️ Limited |
| **International** | ✅ 100+ countries | ✅ 190+ countries |
| **Setup Complexity** | 🟡 Medium | 🟢 Simple |
| **Documentation** | ✅ Excellent | ✅ Good |

## Phone Number Types

- **Local Numbers**: Standard local phone numbers ($1.00/month Twilio, $0.80/month Plivo)
- **Toll-Free**: 1-800, 1-888, etc. (Higher cost, better for business)
- **Mobile**: Mobile-originated numbers (Limited availability)

## Best Practices

1. **Provider Selection**: 
   - Use Twilio for maximum reliability and features
   - Use Plivo for cost optimization

2. **Number Assignment**:
   - Assign dedicated inbound numbers per agent for call tracking
   - Use shared outbound numbers to maintain consistent caller ID

3. **Cost Management**:
   - Monitor monthly number costs
   - Release unused numbers promptly
   - Consider toll-free numbers for professional appearance

4. **Compliance**:
   - Ensure proper caller ID information
   - Follow local regulations for cold calling
   - Implement opt-out mechanisms for SMS

## Integration with Retell AI

Phone numbers from Twilio/Plivo are used with Retell AI for actual call routing:

1. **Inbound Calls**: Customer calls your Twilio/Plivo number → Routes to Retell → Your agent handles the call
2. **Outbound Calls**: Agent initiates call → Retell uses your Twilio/Plivo number as caller ID → Connects to lead

The phone number APIs manage the telephony infrastructure, while Retell AI handles the conversational AI layer.