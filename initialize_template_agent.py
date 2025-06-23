#!/usr/bin/env python3
"""
Initialize Retell Template Agent
Creates or verifies the master template agent in Retell AI
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from app.services.retell_service import retell_service
from app.core.retell_template import MASTER_AGENT_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Initialize the master template agent"""
    
    if not retell_service.enabled:
        logger.error("Retell service is not enabled. Please check your RETELL_API_KEY in .env")
        return False
    
    try:
        logger.info("Initializing master template agent...")
        
        # Get or create master agent
        master_agent_id = retell_service._create_or_get_master_agent()
        
        if master_agent_id:
            logger.info(f"✅ Master template agent ready: {master_agent_id}")
            
            # Verify the agent exists and is working
            agent_details = retell_service.get_agent(master_agent_id)
            if agent_details:
                logger.info(f"📋 Agent details: {agent_details.get('agent_name', 'Unknown')}")
                logger.info("🎉 Template-based system is ready for concurrent calls!")
                
                # Show benefits
                print("\n" + "="*60)
                print("🚀 TEMPLATE-BASED RETELL INTEGRATION READY")
                print("="*60)
                print("✅ One master agent handles all personality types")
                print("✅ No sync issues between database and Retell")
                print("✅ Unlimited concurrent calls with different agent personalities")
                print("✅ Easy scaling - no need to pre-create agents")
                print("✅ Cost effective - one Retell agent for all use cases")
                print("\n📞 To make calls:")
                print("   retell_service.create_template_call(agent_config, lead_data)")
                print("\n🔄 For concurrent calls:")
                print("   await retell_service.create_concurrent_calls(agent_config, leads)")
                print("="*60)
                
                return True
            else:
                logger.error("❌ Failed to verify master agent details")
                return False
        else:
            logger.error("❌ Failed to create/get master template agent")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error initializing template agent: {e}")
        return False

def test_template_functionality():
    """Test the template functionality with sample data"""
    
    logger.info("🧪 Testing template functionality...")
    
    # Sample agent configuration
    sample_agent = {
        "id": "test-agent-id",
        "name": "Sarah Real Estate Agent",
        "prompt": "You are a professional real estate agent helping clients find their dream home.",
        "welcome_message": "Hi! This is Sarah from Dream Homes Realty. I'm calling about your interest in properties.",
        "voice_id": "11labs-Adrian",
        "functions": ["end_call", "check_calendar_availability", "book_on_calendar"],
        "variables": {
            "property_type": "condos",
            "location": "San Francisco",
            "budget_range": "$500k-$800k"
        },
        "outbound_phone": "+14155551234",
        "business_hours_start": "09:00",
        "business_hours_end": "17:00",
        "timezone": "America/Los_Angeles",
        "max_call_duration_minutes": 15
    }
    
    # Sample lead data
    sample_lead = {
        "id": "lead-123",
        "name": "John Smith",
        "phone": "+14155559999",
        "company": "Tech Startup Inc"
    }
    
    # Test dynamic variable building
    from app.core.retell_template import build_dynamic_variables
    
    try:
        dynamic_vars = build_dynamic_variables(sample_agent, sample_lead)
        logger.info("✅ Dynamic variables built successfully")
        
        # Show sample dynamic variables
        print("\n" + "="*50)
        print("📋 SAMPLE DYNAMIC VARIABLES")
        print("="*50)
        for key, value in dynamic_vars.items():
            if key != "variables":  # Skip nested dict for readability
                print(f"   {key}: {value}")
        print("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing template functionality: {e}")
        return False

def cleanup_old_agents():
    """Optionally clean up old individual agents (use with caution)"""
    
    print("\n⚠️  CLEANUP OPTIONS")
    print("="*40)
    print("The template-based approach means you no longer need")
    print("individual agents in Retell. You can:")
    print("1. Keep old agents (they won't interfere)")
    print("2. Manually delete them from Retell dashboard")
    print("3. Use this script to list them for review")
    print("="*40)
    
    try:
        agents = retell_service.list_agents()
        if agents:
            print(f"\n📋 Found {len(agents)} agents in Retell:")
            for agent in agents:
                name = agent.get('agent_name', 'Unknown')
                agent_id = agent.get('agent_id', 'Unknown')
                if name != "Universal AI Assistant":  # Don't list our template agent
                    print(f"   • {name} ({agent_id})")
            
            print("\n💡 These agents can be safely deleted if you're fully")
            print("   migrating to the template-based approach.")
        else:
            print("\n✅ No old agents found to clean up")
            
    except Exception as e:
        logger.error(f"Error listing agents: {e}")

if __name__ == "__main__":
    print("🚀 Retell Template Agent Initialization")
    print("=" * 50)
    
    # Initialize master template agent
    success = main()
    
    if success:
        # Test functionality
        test_template_functionality()
        
        # Show cleanup options
        cleanup_old_agents()
        
        print("\n🎉 Template-based Retell integration is ready!")
        print("   Your agents will now use dynamic variables for calls.")
    else:
        print("\n❌ Failed to initialize template system")
        sys.exit(1)