#!/bin/bash

# Test agent creation with voice mapping
echo "Testing Agent Creation with Voice UUID Mapping"
echo "=============================================="

# Set API token (replace with your actual token)
export API_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMDRjODgxZi01N2I1LTQyZDgtYmMzOC04M2MzODk2OGE1YTIiLCJleHAiOjE3MzI2MjQ0NDl9.P4_9GjQgQJ_RiZrYi4W3Lf0UNGJUf1WgOcqFKX3xEMA"

echo "1. Testing with voice UUID that should map to 11labs-Adrian..."

curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Voice Mapping Agent",
    "prompt": "You are a test agent for voice mapping.",
    "voice_id": "11111111-1111-1111-1111-111111111111"
  }' | jq '.'

echo -e "\n2. Testing with direct Retell voice ID..."

curl -X POST "http://localhost:8080/api/v1/agents/" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Direct Voice Agent",
    "prompt": "You are a test agent with direct voice ID.",
    "voice_id": "11labs-Adrian"
  }' | jq '.'

echo -e "\nDone!"