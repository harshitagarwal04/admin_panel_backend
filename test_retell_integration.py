#!/usr/bin/env python3
"""
Test script for Retell AI integration
Demonstrates how to use the RetellService class
"""

from app.services.retell_service import retell_service
import json

def test_agent_operations():
    """Test agent CRUD operations"""
    print("=== Testing Agent Operations ===")
    
    # Create agent
    agent_data = {
        "name": "Test Sales Agent",
        "prompt": "You are a professional sales agent for Acme Corp. Be friendly and helpful.",
        "welcome_message": "Hello! Thank you for your interest in Acme Corp. How can I help you today?",
        "voice_id": "11labs-Adrian"
    }
    
    print("1. Creating agent...")
    agent_id = retell_service.create_agent(agent_data)
    print(f"   Created agent with ID: {agent_id}")
    
    if agent_id:
        # Get agent details
        print("2. Getting agent details...")
        agent_details = retell_service.get_agent(agent_id)
        print(f"   Agent details: {json.dumps(agent_details, indent=2)}")
        
        # Update agent
        print("3. Updating agent...")
        update_data = {
            "name": "Updated Sales Agent",
            "prompt": "You are an experienced sales professional. Be confident and persuasive."
        }
        success = retell_service.update_agent(agent_id, update_data)
        print(f"   Update success: {success}")
        
        # List agents
        print("4. Listing all agents...")
        agents = retell_service.list_agents()
        print(f"   Found {len(agents)} agents")
        
        return agent_id
    
    return None

def test_call_operations(agent_id):
    """Test call operations"""
    print("\n=== Testing Call Operations ===")
    
    if not agent_id:
        print("No agent ID provided, skipping call tests")
        return
    
    # Create phone call
    print("1. Creating phone call...")
    call_id = retell_service.create_phone_call_for_lead(
        lead_id="test-lead-123",
        agent_retell_id=agent_id,
        from_number="+1234567890",
        to_number="+1987654321",
        lead_name="John Doe",
        variables={
            "company_name": "Acme Corp",
            "product": "AI Voice Assistant"
        }
    )
    print(f"   Created call with ID: {call_id}")
    
    if call_id:
        # Get call details
        print("2. Getting call details...")
        call_details = retell_service.get_call(call_id)
        print(f"   Call details: {json.dumps(call_details, indent=2)}")
        
        # List calls
        print("3. Listing recent calls...")
        calls = retell_service.list_calls({"limit": 10})
        print(f"   Found {len(calls)} recent calls")

def test_webhook_verification():
    """Test webhook signature verification"""
    print("\n=== Testing Webhook Verification ===")
    
    # Mock webhook payload and signature
    payload = '{"event": "call_ended", "call_id": "test-call-123"}'
    signature = "mock-signature"
    
    is_valid = retell_service.verify_webhook_signature(payload, signature)
    print(f"Webhook signature valid: {is_valid}")

def main():
    """Run all tests"""
    print("Testing Retell AI Integration")
    print("============================")
    
    # Check if service is enabled
    if retell_service.enabled:
        print("✓ Retell service is enabled (API key configured)")
    else:
        print("⚠ Retell service is in MOCK mode (no API key)")
    
    print(f"Base URL: {retell_service.base_url}")
    print()
    
    # Test agent operations
    agent_id = test_agent_operations()
    
    # Test call operations
    test_call_operations(agent_id)
    
    # Test webhook verification
    test_webhook_verification()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()