#!/usr/bin/env python3
"""
Test script for Retell Agent CRUD operations
Run this to test agent creation, update, get, and delete
"""

import json
import time
from app.services.retell_service import retell_service
from app.core.config import settings

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)

def test_agent_crud():
    """Test complete CRUD cycle for agents"""
    
    print_section("Retell API Configuration Check")
    print(f"API Key configured: {retell_service.enabled}")
    print(f"Base URL: {retell_service.base_url}")
    
    if not retell_service.enabled:
        print("\n⚠️  WARNING: Running in MOCK mode - configure RETELL_API_KEY to test real API")
    
    # Test data
    test_agent = {
        "name": "Test Sales Agent - Demo",
        "prompt": """You are a professional sales agent for Acme Corp. 
        Your goal is to help customers understand our products and services.
        Be friendly, helpful, and professional.
        Always introduce yourself at the beginning of the call.""",
        "welcome_message": "Hello! This is Sarah from Acme Corp. How can I help you today?",
        "voice_id": "11labs-Adrian"  # You may need to use a valid voice ID from Retell
    }
    
    created_agent_id = None
    
    try:
        # 1. CREATE Agent
        print_section("1. CREATE Agent")
        print(f"Creating agent: {test_agent['name']}")
        
        created_agent_id = retell_service.create_agent(test_agent)
        
        if created_agent_id:
            print(f"✓ SUCCESS: Created agent with ID: {created_agent_id}")
        else:
            print("✗ FAILED: Could not create agent")
            return
        
        # Wait a bit for the API to process
        time.sleep(2)
        
        # 2. GET Agent
        print_section("2. GET Agent")
        print(f"Fetching agent details for ID: {created_agent_id}")
        
        agent_details = retell_service.get_agent(created_agent_id)
        if agent_details:
            print(f"✓ SUCCESS: Retrieved agent details")
            print(f"Details: {json.dumps(agent_details, indent=2)}")
        else:
            print("✗ FAILED: Could not retrieve agent details")
        
        # 3. LIST Agents
        print_section("3. LIST All Agents")
        print("Fetching all agents...")
        
        all_agents = retell_service.list_agents()
        if all_agents:
            print(f"✓ SUCCESS: Found {len(all_agents)} agents")
            # Print first few agents
            for i, agent in enumerate(all_agents[:3]):
                print(f"  Agent {i+1}: {agent}")
            if len(all_agents) > 3:
                print(f"  ... and {len(all_agents) - 3} more")
        else:
            print("✗ FAILED: Could not list agents")
        
        # 4. UPDATE Agent
        print_section("4. UPDATE Agent")
        update_data = {
            "name": "Updated Sales Agent - Demo",
            "prompt": "You are an experienced sales professional for Acme Corp. Be confident and knowledgeable.",
            "voice_temperature": 0.8,
            "voice_speed": 1.1
        }
        print(f"Updating agent name and prompt...")
        
        update_success = retell_service.update_agent(created_agent_id, update_data)
        if update_success:
            print(f"✓ SUCCESS: Agent updated")
            
            # Verify update
            time.sleep(1)
            updated_agent = retell_service.get_agent(created_agent_id)
            if updated_agent:
                print(f"Updated details: {json.dumps(updated_agent, indent=2)}")
        else:
            print("✗ FAILED: Could not update agent")
        
        # 5. DELETE Agent
        print_section("5. DELETE Agent")
        print(f"Deleting agent ID: {created_agent_id}")
        
        delete_confirm = input("Do you want to delete the test agent? (yes/no): ")
        if delete_confirm.lower() == 'yes':
            delete_success = retell_service.delete_agent(created_agent_id)
            if delete_success:
                print(f"✓ SUCCESS: Agent deleted")
            else:
                print("✗ FAILED: Could not delete agent")
        else:
            print("Skipping deletion - agent kept for further testing")
            print(f"Agent ID to use for other tests: {created_agent_id}")
    
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup if needed
        if created_agent_id and input("\nAttempt to delete the created agent? (yes/no): ").lower() == 'yes':
            try:
                retell_service.delete_agent(created_agent_id)
                print("Cleanup completed")
            except:
                print("Cleanup failed")
    
    print_section("Test Complete")

def test_phone_call(agent_id=None):
    """Test phone call creation"""
    print_section("Phone Call Test")
    
    if not agent_id:
        agent_id = input("Enter Retell Agent ID to use for call (or press Enter to skip): ").strip()
        if not agent_id:
            print("Skipping phone call test")
            return
    
    # Test call data
    test_call = {
        "from_number": "+1234567890",  # Replace with your Retell phone number
        "to_number": "+1987654321",     # Replace with test destination
        "retell_agent_id": agent_id,
        "metadata": {
            "test": True,
            "purpose": "CRUD test"
        },
        "variables": {
            "lead_name": "Test User",
            "company_name": "Test Company"
        }
    }
    
    print(f"Creating test call from {test_call['from_number']} to {test_call['to_number']}")
    print("Note: This will initiate a real phone call if API key is configured!")
    
    proceed = input("Proceed with call? (yes/no): ")
    if proceed.lower() == 'yes':
        call_id = retell_service.create_phone_call(test_call)
        if call_id:
            print(f"✓ SUCCESS: Call created with ID: {call_id}")
            
            # Get call details
            time.sleep(2)
            call_details = retell_service.get_call(call_id)
            if call_details:
                print(f"Call details: {json.dumps(call_details, indent=2)}")
        else:
            print("✗ FAILED: Could not create call")

if __name__ == "__main__":
    print("RETELL AI AGENT CRUD TEST")
    print("========================")
    print()
    print("This script will test:")
    print("1. Create a new agent")
    print("2. Get agent details") 
    print("3. List all agents")
    print("4. Update the agent")
    print("5. Delete the agent (optional)")
    print()
    
    proceed = input("Continue with test? (yes/no): ")
    if proceed.lower() == 'yes':
        test_agent_crud()
        
        # Optional: test phone call
        print("\n" + "="*50)
        test_call = input("\nDo you want to test phone call creation? (yes/no): ")
        if test_call.lower() == 'yes':
            test_phone_call()
    else:
        print("Test cancelled")