#!/usr/bin/env python3
"""
Simple test to verify Retell API key and list existing agents
"""

from app.services.retell_service import retell_service
import json

def test_list_agents():
    """Test listing agents to verify API key works"""
    print("Testing Retell API Connection")
    print("="*50)
    
    print(f"API Key configured: {retell_service.enabled}")
    
    if not retell_service.enabled:
        print("⚠️  Retell API key not configured!")
        print("Please add RETELL_API_KEY to your .env file")
        return
    
    print(f"API Key (first 10 chars): {retell_service.api_key[:10]}...")
    
    print("\nTesting: List existing agents...")
    
    try:
        agents = retell_service.list_agents()
        
        if isinstance(agents, list):
            print(f"\n✓ SUCCESS: API key is valid!")
            print(f"Found {len(agents)} existing agents:")
            
            for i, agent in enumerate(agents[:5]):  # Show first 5
                print(f"\nAgent {i+1}:")
                print(f"  ID: {agent.get('agent_id', 'N/A')}")
                print(f"  Name: {agent.get('agent_name', 'N/A')}")
                print(f"  Voice: {agent.get('voice_id', 'N/A')}")
                
            if len(agents) > 5:
                print(f"\n... and {len(agents) - 5} more agents")
                
            # Show a sample agent structure
            if agents:
                print("\nSample agent structure:")
                print(json.dumps(agents[0], indent=2, default=str))
        else:
            print("✗ Unexpected response format")
            print(f"Response: {agents}")
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # More detailed error info
        if hasattr(e, '__dict__'):
            print(f"Error details: {e.__dict__}")

def test_retell_client_direct():
    """Test Retell client directly"""
    print("\n" + "="*50)
    print("Testing Retell Client Directly")
    print("="*50)
    
    if not retell_service.enabled:
        print("Skipping - API not enabled")
        return
        
    try:
        from retell import Retell
        client = Retell(api_key=retell_service.api_key)
        
        # Try to list agents directly
        print("Attempting to list agents via direct client...")
        agents = client.agent.list()
        
        print(f"Direct client returned: {type(agents)}")
        
        # Try to iterate if it's an iterator
        agent_list = []
        for agent in agents:
            agent_list.append(agent)
            if len(agent_list) >= 3:  # Just get first 3
                break
                
        print(f"Retrieved {len(agent_list)} agents via direct client")
        
        if agent_list:
            print("\nFirst agent details:")
            first_agent = agent_list[0]
            print(f"Type: {type(first_agent)}")
            print(f"Attributes: {dir(first_agent)}")
            if hasattr(first_agent, 'agent_id'):
                print(f"Agent ID: {first_agent.agent_id}")
            if hasattr(first_agent, 'agent_name'):
                print(f"Agent Name: {first_agent.agent_name}")
                
    except Exception as e:
        print(f"Direct client error: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_list_agents()
    test_retell_client_direct()