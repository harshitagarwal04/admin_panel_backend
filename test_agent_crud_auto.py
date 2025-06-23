#!/usr/bin/env python3
"""
Automated test script for Retell Agent CRUD operations
No user input required - runs all tests automatically
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
    
    print("RETELL AI AGENT CRUD TEST (AUTOMATED)")
    print("=====================================")
    
    print_section("Retell API Configuration Check")
    print(f"API Key configured: {retell_service.enabled}")
    
    if retell_service.api_key:
        print(f"API Key (first 10 chars): {retell_service.api_key[:10]}...")
    
    if not retell_service.enabled:
        print("\n⚠️  WARNING: Running in MOCK mode - configure RETELL_API_KEY to test real API")
    else:
        print("\n✓ Running with REAL Retell API")
    
    # Test data
    test_agent = {
        "name": "Test Sales Agent - Auto Test",
        "prompt": """You are a professional sales agent for Acme Corp. 
        Your goal is to help customers understand our products and services.
        Be friendly, helpful, and professional.
        Always introduce yourself at the beginning of the call.""",
        "welcome_message": "Hello! This is Sarah from Acme Corp. How can I help you today?",
        "voice_id": "11labs-Adrian"
    }
    
    created_agent_id = None
    
    try:
        # 1. CREATE Agent
        print_section("1. CREATE Agent")
        print(f"Creating agent: {test_agent['name']}")
        print(f"Voice ID: {test_agent['voice_id']}")
        
        created_agent_id = retell_service.create_agent(test_agent)
        
        if created_agent_id:
            print(f"✓ SUCCESS: Created agent with ID: {created_agent_id}")
        else:
            print("✗ FAILED: Could not create agent")
            print("Check if:")
            print("  - API key is valid")
            print("  - Voice ID is correct")
            print("  - You have available agent slots")
            return
        
        # Wait a bit for the API to process
        print("Waiting 2 seconds for API processing...")
        time.sleep(2)
        
        # 2. GET Agent
        print_section("2. GET Agent")
        print(f"Fetching agent details for ID: {created_agent_id}")
        
        agent_details = retell_service.get_agent(created_agent_id)
        if agent_details:
            print(f"✓ SUCCESS: Retrieved agent details")
            if not agent_details.get("mock"):
                print(f"Agent Name: {agent_details.get('agent_name', 'N/A')}")
                print(f"Voice ID: {agent_details.get('voice_id', 'N/A')}")
            else:
                print("(Mock response)")
        else:
            print("✗ FAILED: Could not retrieve agent details")
        
        # 3. LIST Agents
        print_section("3. LIST All Agents")
        print("Fetching all agents...")
        
        all_agents = retell_service.list_agents()
        if isinstance(all_agents, list):
            print(f"✓ SUCCESS: Found {len(all_agents)} agents")
            # Print first 3 agents
            for i, agent in enumerate(all_agents[:3]):
                if isinstance(agent, dict):
                    agent_info = f"ID: {agent.get('agent_id', 'N/A')}, Name: {agent.get('agent_name', 'N/A')}"
                else:
                    agent_info = str(agent)
                print(f"  Agent {i+1}: {agent_info}")
            if len(all_agents) > 3:
                print(f"  ... and {len(all_agents) - 3} more")
        else:
            print("✗ FAILED: Could not list agents or unexpected response format")
        
        # 4. UPDATE Agent
        print_section("4. UPDATE Agent")
        update_data = {
            "name": "Updated Sales Agent - Auto Test",
            "prompt": "You are an experienced sales professional for Acme Corp. Be confident and knowledgeable."
        }
        print(f"Updating agent name to: {update_data['name']}")
        
        update_success = retell_service.update_agent(created_agent_id, update_data)
        if update_success:
            print(f"✓ SUCCESS: Agent updated")
            
            # Verify update
            print("Waiting 1 second before verification...")
            time.sleep(1)
            updated_agent = retell_service.get_agent(created_agent_id)
            if updated_agent and not updated_agent.get("mock"):
                print(f"Verified - New name: {updated_agent.get('agent_name', 'N/A')}")
        else:
            print("✗ FAILED: Could not update agent")
        
        # 5. DELETE Agent (Auto cleanup)
        print_section("5. DELETE Agent (Auto Cleanup)")
        print(f"Deleting test agent ID: {created_agent_id}")
        
        delete_success = retell_service.delete_agent(created_agent_id)
        if delete_success:
            print(f"✓ SUCCESS: Test agent deleted")
        else:
            print("✗ FAILED: Could not delete agent")
            print(f"Manual cleanup may be required for agent: {created_agent_id}")
    
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        
        # Attempt cleanup
        if created_agent_id:
            print("\nAttempting cleanup...")
            try:
                retell_service.delete_agent(created_agent_id)
                print("✓ Cleanup completed")
            except:
                print("✗ Cleanup failed")
                print(f"Manual cleanup required for agent: {created_agent_id}")
    
    print_section("Test Complete")
    print("\nSummary:")
    print(f"- API Mode: {'REAL' if retell_service.enabled else 'MOCK'}")
    print(f"- Created Agent ID: {created_agent_id or 'None'}")
    print("- All CRUD operations tested")

if __name__ == "__main__":
    test_agent_crud()