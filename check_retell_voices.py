#!/usr/bin/env python3
"""
Check available Retell voice IDs
"""

from retell import Retell
from app.core.config import settings
import json

def check_retell_voices():
    """Check what voices are available in Retell"""
    
    print("Checking Available Retell Voice IDs")
    print("="*50)
    
    client = Retell(api_key=settings.RETELL_API_KEY)
    
    # Get an existing agent to see what voice IDs are used
    print("1. Checking voice IDs from existing agents...")
    agents = client.agent.list()
    
    voice_ids = set()
    for agent in agents[:10]:  # Check first 10 agents
        voice_ids.add(agent.voice_id)
    
    print(f"Found {len(voice_ids)} unique voice IDs in use:")
    for voice_id in sorted(voice_ids):
        print(f"  - {voice_id}")
    
    # Try to get voice information (if API supports it)
    print(f"\n2. Testing with valid voice ID: 11labs-Adrian")
    
    try:
        # Try creating an agent with a known good voice ID
        sample_agent = agents[0]
        test_agent = client.agent.create(
            agent_name="Voice Test Agent - DELETE ME",
            voice_id="11labs-Adrian",
            response_engine=sample_agent.response_engine
        )
        
        print(f"✓ SUCCESS: Voice ID '11labs-Adrian' works")
        print(f"Created test agent: {test_agent.agent_id}")
        
        # Clean up
        client.agent.delete(agent_id=test_agent.agent_id)
        print("✓ Test agent deleted")
        
    except Exception as e:
        print(f"✗ Voice test failed: {e}")
    
    # Test with the voice ID from the curl command
    print(f"\n3. Testing with curl voice ID: 11111111-1111-1111-1111-111111111111")
    
    try:
        test_agent2 = client.agent.create(
            agent_name="Bad Voice Test Agent - DELETE ME",
            voice_id="11111111-1111-1111-1111-111111111111",
            response_engine=sample_agent.response_engine
        )
        
        print(f"✓ Unexpected success with bad voice ID")
        client.agent.delete(agent_id=test_agent2.agent_id)
        
    except Exception as e:
        print(f"✗ Expected failure with bad voice ID: {e}")

if __name__ == "__main__":
    check_retell_voices()