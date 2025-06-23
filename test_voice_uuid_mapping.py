#!/usr/bin/env python3
"""
Test voice UUID mapping for agent creation
"""

from app.services.retell_service import retell_service
import json

def test_voice_mapping():
    """Test agent creation with voice UUID mapping"""
    
    print("Testing Voice UUID Mapping")
    print("="*50)
    
    # Test 1: Agent with UUID voice_id (should be mapped)
    print("1. Testing with voice UUID (should map to 11labs-Adrian)...")
    agent_data_uuid = {
        "name": "Test Voice Mapping Agent",
        "prompt": "You are a test agent for voice mapping.",
        "voice_id": "11111111-1111-1111-1111-111111111111"  # Our UUID
    }
    
    agent_id_1 = retell_service.create_agent(agent_data_uuid)
    if agent_id_1:
        print(f"✓ SUCCESS: Created agent with UUID voice mapping: {agent_id_1}")
        
        # Get agent details to verify voice ID
        agent_details = retell_service.get_agent(agent_id_1)
        if agent_details:
            print(f"  Mapped voice_id: {agent_details.get('voice_id')}")
    else:
        print("✗ FAILED: Could not create agent with UUID voice mapping")
    
    # Test 2: Agent with direct voice_id
    print("\n2. Testing with direct Retell voice ID...")
    agent_data_direct = {
        "name": "Test Direct Voice Agent", 
        "prompt": "You are a test agent with direct voice ID.",
        "voice_id": "11labs-Adrian"  # Direct Retell voice ID
    }
    
    agent_id_2 = retell_service.create_agent(agent_data_direct)
    if agent_id_2:
        print(f"✓ SUCCESS: Created agent with direct voice ID: {agent_id_2}")
        
        # Get agent details
        agent_details = retell_service.get_agent(agent_id_2)
        if agent_details:
            print(f"  Voice_id: {agent_details.get('voice_id')}")
    else:
        print("✗ FAILED: Could not create agent with direct voice ID")
    
    # Test 3: Invalid voice UUID (should fallback to default)
    print("\n3. Testing with invalid voice UUID (should use default)...")
    agent_data_invalid = {
        "name": "Test Invalid Voice Agent",
        "prompt": "You are a test agent with invalid voice ID.",
        "voice_id": "99999999-9999-9999-9999-999999999999"  # Invalid UUID
    }
    
    agent_id_3 = retell_service.create_agent(agent_data_invalid)
    if agent_id_3:
        print(f"✓ SUCCESS: Created agent with fallback voice: {agent_id_3}")
        
        # Get agent details
        agent_details = retell_service.get_agent(agent_id_3)
        if agent_details:
            print(f"  Fallback voice_id: {agent_details.get('voice_id')}")
    else:
        print("✗ FAILED: Could not create agent with fallback voice")
    
    # Cleanup
    print("\n4. Cleaning up test agents...")
    cleanup_count = 0
    for agent_id in [agent_id_1, agent_id_2, agent_id_3]:
        if agent_id:
            if retell_service.delete_agent(agent_id):
                cleanup_count += 1
                print(f"  ✓ Deleted agent: {agent_id}")
            else:
                print(f"  ✗ Failed to delete agent: {agent_id}")
    
    print(f"\n✓ Cleaned up {cleanup_count} test agents")
    
    print(f"\nSummary:")
    print(f"- UUID mapping: {'✓' if agent_id_1 else '✗'}")
    print(f"- Direct voice ID: {'✓' if agent_id_2 else '✗'}")
    print(f"- Invalid fallback: {'✓' if agent_id_3 else '✗'}")

if __name__ == "__main__":
    test_voice_mapping()