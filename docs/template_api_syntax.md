# Template API Documentation

## Base URL
```
http://localhost:8080/api/v1
```

## Authentication
All template endpoints require JWT token in the Authorization header:
```
Authorization: Bearer $API_TOKEN
```

## Overview

Templates provide pre-built agent configurations for different industries and use cases. Each template includes optimized prompts, suggested variables, functions, and settings for specific business scenarios.

## 1. List All Templates
**GET** `/templates/`

Retrieve all available templates with optional filtering.

### Query Parameters
- `industry` (optional): Filter by industry (e.g., "Healthcare", "Real Estate")
- `use_case` (optional): Filter by use case (e.g., "Lead Qualification", "Appointment Scheduling")

```bash
# Get all templates
curl -X GET "http://localhost:8080/api/v1/templates/" \
  -H "Authorization: Bearer $API_TOKEN"

# Filter by industry
curl -X GET "http://localhost:8080/api/v1/templates/?industry=Healthcare" \
  -H "Authorization: Bearer $API_TOKEN"

# Filter by use case
curl -X GET "http://localhost:8080/api/v1/templates/?use_case=Lead%20Qualification" \
  -H "Authorization: Bearer $API_TOKEN"

# Filter by both
curl -X GET "http://localhost:8080/api/v1/templates/?industry=Healthcare&use_case=Appointment%20Scheduling" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "templates": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "industry": "Healthcare",
      "use_case": "Lead Qualification",
      "name": "Healthcare Lead Qualifier",
      "prompt": "You are a professional healthcare lead qualifier. Your role is to...",
      "variables": [
        "company_name",
        "service_type",
        "location"
      ],
      "functions": [
        "schedule_appointment",
        "transfer_to_specialist",
        "end_call"
      ],
      "welcome_message": "Hello! Thank you for your interest in our healthcare services.",
      "suggested_settings": {
        "max_call_duration_minutes": 15,
        "max_attempts": 2,
        "voice_temperature": 0.7,
        "business_hours_start": "08:00",
        "business_hours_end": "18:00"
      }
    }
  ],
  "total": 1
}
```

## 2. Get Templates by Industry
**GET** `/templates/industries`

Get all templates grouped by industry.

```bash
curl -X GET "http://localhost:8080/api/v1/templates/industries" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
[
  {
    "industry": "Healthcare",
    "templates": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "industry": "Healthcare",
        "use_case": "Lead Qualification",
        "name": "Healthcare Lead Qualifier",
        "prompt": "You are a professional healthcare lead qualifier...",
        "variables": ["company_name", "service_type"],
        "functions": ["schedule_appointment", "transfer_to_specialist"],
        "welcome_message": "Hello! Thank you for your interest...",
        "suggested_settings": {
          "max_call_duration_minutes": 15
        }
      },
      {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "industry": "Healthcare",
        "use_case": "Appointment Scheduling",
        "name": "Medical Appointment Scheduler",
        "prompt": "You are a medical appointment scheduler...",
        "variables": ["clinic_name", "doctor_name"],
        "functions": ["check_availability", "book_appointment"],
        "welcome_message": "Hi! I'm here to help you schedule...",
        "suggested_settings": {
          "max_call_duration_minutes": 10
        }
      }
    ]
  },
  {
    "industry": "Real Estate",
    "templates": [
      {
        "id": "789e0123-e89b-12d3-a456-426614174002",
        "industry": "Real Estate",
        "use_case": "Lead Qualification",
        "name": "Real Estate Lead Qualifier",
        "prompt": "You are a real estate lead qualifier...",
        "variables": ["agency_name", "property_type"],
        "functions": ["schedule_viewing", "send_listings"],
        "welcome_message": "Hello! Thank you for your interest in real estate...",
        "suggested_settings": {
          "max_call_duration_minutes": 20
        }
      }
    ]
  }
]
```

## 3. Get Single Template
**GET** `/templates/{template_id}`

Retrieve detailed information about a specific template.

```bash
curl -X GET "http://localhost:8080/api/v1/templates/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer $API_TOKEN"
```

### Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "industry": "Healthcare",
  "use_case": "Lead Qualification",
  "name": "Healthcare Lead Qualifier",
  "prompt": "You are a professional healthcare lead qualifier working for {{company_name}}. Your role is to:\n\n1. Warmly greet potential patients\n2. Understand their healthcare needs\n3. Qualify them for {{service_type}} services\n4. Schedule appropriate consultations\n5. Provide helpful information about our {{location}} facility\n\nAlways be empathetic, professional, and HIPAA-compliant. If someone has urgent medical needs, direct them to emergency services immediately.",
  "variables": [
    "company_name",
    "service_type",
    "location",
    "doctor_name",
    "specialties"
  ],
  "functions": [
    "schedule_appointment",
    "transfer_to_specialist",
    "send_information_packet",
    "check_insurance",
    "end_call"
  ],
  "welcome_message": "Hello! Thank you for your interest in {{company_name}} healthcare services. I'm here to help you find the right care for your needs. How can I assist you today?",
  "suggested_settings": {
    "max_call_duration_minutes": 15,
    "max_attempts": 2,
    "retry_delay_minutes": 240,
    "voice_temperature": 0.7,
    "voice_speed": 1.0,
    "responsiveness": 0.8,
    "business_hours_start": "08:00",
    "business_hours_end": "18:00",
    "timezone": "America/New_York"
  }
}
```

## 4. Create Agent from Template
**POST** `/agents/` (using template data)

You can use template data to create an agent by copying the template's configuration.

```bash
# First, get the template
TEMPLATE=$(curl -s -X GET "http://localhost:8080/api/v1/templates/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer $API_TOKEN")

# Extract template data and create agent
curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Healthcare Agent",
    "prompt": "You are a professional healthcare lead qualifier working for Acme Medical. Your role is to...",
    "welcome_message": "Hello! Thank you for your interest in Acme Medical healthcare services...",
    "voice_id": "11111111-1111-1111-1111-111111111111",
    "variables": {
      "company_name": "Acme Medical",
      "service_type": "Primary Care",
      "location": "Downtown Clinic"
    },
    "functions": ["schedule_appointment", "transfer_to_specialist", "end_call"],
    "max_call_duration_minutes": 15,
    "max_attempts": 2,
    "retry_delay_minutes": 240,
    "business_hours_start": "08:00",
    "business_hours_end": "18:00",
    "timezone": "America/New_York"
  }'
```

## Available Industries

Based on the current database, available industries include:
- **Healthcare** - Medical services, clinics, telehealth
- **Real Estate** - Property sales, rentals, management
- **E-commerce** - Online stores, customer support
- **SaaS** - Software companies, lead qualification
- **Insurance** - Policy sales, claims support
- **Education** - Schools, training programs
- **Finance** - Financial services, banking
- **Fitness** - Gyms, personal training

## Available Use Cases

Common use cases across industries:
- **Lead Qualification** - Initial prospect screening
- **Appointment Scheduling** - Booking consultations/meetings
- **Customer Support** - Handling inquiries and issues
- **Follow-up Calls** - Post-service check-ins
- **Survey Collection** - Gathering feedback
- **Event Registration** - Webinar/event sign-ups

## Template Structure

Each template contains:

| Field | Description |
|-------|-------------|
| `id` | Unique template identifier |
| `industry` | Business vertical (Healthcare, Real Estate, etc.) |
| `use_case` | Specific application (Lead Qualification, etc.) |
| `name` | Human-readable template name |
| `prompt` | Optimized AI agent prompt with variables |
| `variables` | List of customizable variables |
| `functions` | Available agent functions/actions |
| `welcome_message` | Opening message template |
| `suggested_settings` | Recommended agent configuration |

## Error Responses

### 404 Not Found
```json
{
  "detail": "Template not found"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

## Example: Complete Template Usage Flow

```bash
# Step 1: Browse templates by industry
curl -X GET "http://localhost:8080/api/v1/templates/industries" \
  -H "Authorization: Bearer $API_TOKEN" | jq '.'

# Step 2: Get specific template details
curl -X GET "http://localhost:8080/api/v1/templates/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer $API_TOKEN" | jq '.'

# Step 3: Create agent using template configuration
curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom Agent",
    "prompt": "Template prompt with custom variables...",
    "voice_id": "11111111-1111-1111-1111-111111111111"
  }' | jq '.'

# Step 4: Verify agent creation
curl -X GET "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" | jq '.'
```

## Pro Tips

1. **Variable Substitution**: Replace `{{variable_name}}` placeholders in prompts with your actual values
2. **Settings Optimization**: Use suggested_settings as a starting point, then customize based on your needs
3. **Industry Best Practices**: Templates are optimized for industry-specific compliance and effectiveness
4. **Function Selection**: Not all functions may be available - check your agent capabilities
5. **Prompt Customization**: Feel free to modify template prompts to match your brand voice