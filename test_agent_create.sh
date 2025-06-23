#!/bin/bash

# Option 1: Using a JSON file
cat > agent_data.json << 'EOF'
{
  "name": "Sales Agent",
  "prompt": "You are a professional sales agent. Be friendly and helpful.",
  "welcome_message": "Hello! How can I help you today?",
  "voice_id": "6e62cfb4-ea68-417a-af22-2969de4a4894",
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
}
EOF

echo "Option 1: Using JSON file"
curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @agent_data.json

echo -e "\n\nOption 2: Using direct JSON string"
curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Sales Agent","prompt":"You are a professional sales agent. Be friendly and helpful.","welcome_message":"Hello! How can I help you today?","voice_id":"6e62cfb4-ea68-417a-af22-2969de4a4894","variables":{"company_name":"{{company_name}}","product":"{{product}}"},"functions":["transfer_call","end_call"],"inbound_phone":"+1234567890","outbound_phone":"+0987654321","max_attempts":3,"retry_delay_minutes":60,"business_hours_start":"09:00","business_hours_end":"18:00","timezone":"America/New_York","max_call_duration_minutes":30}'

echo -e "\n\nOption 3: Minimal agent (only required fields)"
curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Simple Agent","prompt":"You are a helpful assistant."}'

# Clean up
rm -f agent_data.json