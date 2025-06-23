#!/bin/bash

echo "Testing Fixed CURL Command for Agent Creation"
echo "============================================="

# Note: Replace with your actual token
API_TOKEN="your-jwt-token-here"

echo "Using voice UUID (will be mapped to 11labs-Adrian)..."

curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Agent",
    "prompt": "You are a professional sales agent. Be friendly and helpful.",
    "welcome_message": "Hello! How can I help you today?",
    "voice_id": "11111111-1111-1111-1111-111111111111",
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
    "max_call_duration_minutes": 30
  }' | jq '.'

echo -e "\n\nAlternatively, using direct Retell voice ID:"

curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Agent Direct Voice",
    "prompt": "You are a professional sales agent. Be friendly and helpful.",
    "voice_id": "11labs-Adrian"
  }' | jq '.'