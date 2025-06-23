#!/usr/bin/env python3
"""
Debug agent creation issue
"""

from retell import Retell
from app.core.config import settings
import json

def debug_agent_creation():
    """Debug why agent creation is failing"""
    
    print("Debugging Agent Creation")
    print("="*50)
    
    client = Retell(api_key=settings.RETELL_API_KEY)
    
    # Check current agent count
    print("1. Current agent status...")
    agents = client.agent.list()
    print(f"Current agent count: {len(agents)}")
    
    # Try minimal agent creation
    print("\n2. Trying minimal agent creation...")
    try:
        # Get response engine from first existing agent
        sample_agent = agents[0] if agents else None
        if sample_agent:
            response_engine = sample_agent.response_engine
            print(f"Using response engine: {response_engine}")
            
            new_agent = client.agent.create(
                agent_name="Debug Test Agent",
                voice_id="11labs-Adrian",
                response_engine=response_engine
            )
            
            print(f"✓ SUCCESS: Created agent {new_agent.agent_id}")
            
            # Immediately delete it
            client.agent.delete(agent_id=new_agent.agent_id)
            print("✓ Cleaned up")
            
        else:
            print("✗ No existing agents found to copy response_engine from")
            
    except Exception as e:
        print(f"✗ Creation failed: {e}")
        
        # Try to understand the error better
        if hasattr(e, 'response'):
            print(f"Status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
            
        # Check if there are account limits
        print("\n3. Checking account limits...")
        try:
            # Try to get account info or quotas
            print("No direct quota API available")
            
        except Exception as quota_e:
            print(f"Quota check failed: {quota_e}")

def test_simple_list_and_get():
    """Test basic operations that should work"""
    print("\n" + "="*50)
    print("Testing Basic Operations")
    print("="*50)
    
    client = Retell(api_key=settings.RETELL_API_KEY)
    
    # List agents
    print("1. Listing agents...")
    agents = client.agent.list()
    print(f"✓ Listed {len(agents)} agents")
    
    if agents:
        # Get first agent
        first_agent = agents[0]
        print(f"\n2. Getting agent {first_agent.agent_id}...")
        retrieved = client.agent.retrieve(agent_id=first_agent.agent_id)
        print(f"✓ Retrieved agent: {retrieved.agent_name}")
        
        # Try to update it (with no changes)
        print(f"\n3. Testing update (no changes)...")
        try:
            updated = client.agent.update(
                agent_id=first_agent.agent_id,
                agent_name=first_agent.agent_name  # Same name
            )
            print(f"✓ Update successful")
        except Exception as e:
            print(f"✗ Update failed: {e}")

if __name__ == "__main__":
    debug_agent_creation()
    test_simple_list_and_get()