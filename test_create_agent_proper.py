#!/usr/bin/env python3
"""
Test creating an agent with proper parameters based on existing agents
"""

from retell import Retell
from app.core.config import settings
import json

def test_create_agent():
    """Test creating an agent using proper SDK parameters"""
    
    print("Testing Agent Creation with Retell SDK")
    print("="*50)
    
    # Initialize client
    client = Retell(api_key=settings.RETELL_API_KEY)
    
    # First, let's see what an existing agent looks like
    print("1. Checking existing agent structure...")
    agents = client.agent.list()
    
    if agents and len(agents) > 0:
        sample_agent = agents[0]
        print(f"\nSample existing agent:")
        print(f"  ID: {sample_agent.agent_id}")
        print(f"  Name: {sample_agent.agent_name}")
        print(f"  Voice ID: {sample_agent.voice_id}")
        print(f"  Language: {sample_agent.language}")
        print(f"  Response Engine: {sample_agent.response_engine}")
        
        # Print full structure
        print("\nFull agent data:")
        agent_dict = sample_agent.model_dump()
        print(json.dumps(agent_dict, indent=2, default=str))
    
    # Now try to create a new agent
    print("\n" + "="*50)
    print("2. Creating new test agent...")
    
    try:
        # Basic agent creation with minimal parameters
        new_agent = client.agent.create(
            agent_name="Test SDK Agent - Delete Me",
            voice_id="11labs-Adrian",
            language="en-US"
        )
        
        print(f"\n✓ SUCCESS! Created agent:")
        print(f"  ID: {new_agent.agent_id}")
        print(f"  Name: {new_agent.agent_name}")
        
        # Try to get the agent
        print("\n3. Retrieving created agent...")
        retrieved = client.agent.retrieve(agent_id=new_agent.agent_id)
        print(f"✓ Retrieved successfully")
        print(f"  Response Engine: {retrieved.response_engine}")
        
        # Delete the test agent
        print("\n4. Cleaning up - deleting test agent...")
        client.agent.delete(agent_id=new_agent.agent_id)
        print("✓ Test agent deleted")
        
    except Exception as e:
        print(f"\n✗ ERROR creating agent: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Try with different parameters
        print("\n5. Trying with response_engine parameter...")
        try:
            # Get response engine from existing agent
            if agents and len(agents) > 0:
                sample_response_engine = agents[0].response_engine
                print(f"Using response engine: {sample_response_engine}")
                
                new_agent = client.agent.create(
                    agent_name="Test SDK Agent v2 - Delete Me",
                    voice_id="11labs-Adrian",
                    response_engine=sample_response_engine,
                    language="en-US"
                )
                
                print(f"\n✓ SUCCESS with response_engine!")
                print(f"  ID: {new_agent.agent_id}")
                
                # Clean up
                client.agent.delete(agent_id=new_agent.agent_id)
                print("✓ Cleaned up test agent")
                
        except Exception as e2:
            print(f"✗ Still failed: {e2}")

if __name__ == "__main__":
    test_create_agent()