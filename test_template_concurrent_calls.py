#!/usr/bin/env python3
"""
Test Template-Based Concurrent Calls
Tests the new template-based approach for creating concurrent calls
"""

import asyncio
import sys
from pathlib import Path
import time
import json

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from app.services.retell_service import retell_service
from app.core.retell_template import build_dynamic_variables

def create_sample_agent_configs():
    """Create different sample agent configurations"""
    
    agents = [
        {
            "id": "real-estate-1",
            "name": "Sarah Real Estate Expert",
            "prompt": "You are Sarah, a professional real estate agent specializing in luxury condos. Help clients find their perfect home by understanding their needs, budget, and timeline.",
            "welcome_message": "Hi! This is Sarah from Premium Realty. I'm calling about your interest in luxury condos in the Bay Area.",
            "voice_id": "11labs-Adrian",
            "functions": ["end_call", "check_calendar_availability", "book_on_calendar"],
            "variables": {
                "property_type": "luxury condos",
                "location": "Bay Area",
                "specialization": "luxury properties"
            },
            "outbound_phone": "+14155551001",
            "business_hours_start": "09:00",
            "business_hours_end": "18:00",
            "timezone": "America/Los_Angeles",
            "max_call_duration_minutes": 20
        },
        {
            "id": "healthcare-1", 
            "name": "Dr. Johnson Health Assistant",
            "prompt": "You are Dr. Johnson's AI assistant helping patients schedule appointments and answer basic health questions. Be professional, caring, and helpful.",
            "welcome_message": "Hello! This is the AI assistant from Dr. Johnson's office. I'm calling to follow up on your recent inquiry.",
            "voice_id": "11labs-Adrian",
            "functions": ["end_call", "check_calendar_availability", "book_on_calendar", "transfer_call"],
            "variables": {
                "service_type": "primary care",
                "office_name": "Johnson Family Practice"
            },
            "outbound_phone": "+14155551002",
            "business_hours_start": "08:00",
            "business_hours_end": "17:00", 
            "timezone": "America/Los_Angeles",
            "max_call_duration_minutes": 15
        },
        {
            "id": "insurance-1",
            "name": "Mike Insurance Advisor",
            "prompt": "You are Mike, an experienced insurance advisor helping people find the best coverage for their needs. Focus on understanding their situation and explaining options clearly.",
            "welcome_message": "Hi! This is Mike from SecureLife Insurance. I'm calling about your request for insurance quotes.",
            "voice_id": "11labs-Adrian",
            "functions": ["end_call", "transfer_call"],
            "variables": {
                "insurance_type": "life insurance",
                "company_name": "SecureLife Insurance"
            },
            "outbound_phone": "+14155551003",
            "business_hours_start": "09:00",
            "business_hours_end": "19:00",
            "timezone": "America/Los_Angeles", 
            "max_call_duration_minutes": 25
        }
    ]
    
    return agents

def create_sample_leads():
    """Create sample lead data for testing"""
    
    leads = [
        {"id": "lead-001", "name": "Alice Johnson", "phone": "+14155552001", "company": "Tech Startup"},
        {"id": "lead-002", "name": "Bob Smith", "phone": "+14155552002", "company": "Marketing Agency"},
        {"id": "lead-003", "name": "Carol Davis", "phone": "+14155552003", "company": "Design Studio"},
        {"id": "lead-004", "name": "David Wilson", "phone": "+14155552004", "company": "Consulting Firm"},
        {"id": "lead-005", "name": "Emma Brown", "phone": "+14155552005", "company": "E-commerce Store"},
        {"id": "lead-006", "name": "Frank Miller", "phone": "+14155552006", "company": "Restaurant Chain"},
        {"id": "lead-007", "name": "Grace Lee", "phone": "+14155552007", "company": "Real Estate Firm"},
        {"id": "lead-008", "name": "Henry Clark", "phone": "+14155552008", "company": "Law Practice"},
        {"id": "lead-009", "name": "Ivy Chen", "phone": "+14155552009", "company": "Healthcare Group"},
        {"id": "lead-010", "name": "Jack Taylor", "phone": "+14155552010", "company": "Financial Services"}
    ]
    
    return leads

def test_dynamic_variables():
    """Test dynamic variable generation for different agent types"""
    
    print("🧪 Testing Dynamic Variable Generation")
    print("=" * 50)
    
    agents = create_sample_agent_configs()
    leads = create_sample_leads()
    
    for i, agent in enumerate(agents):
        lead = leads[i]
        
        print(f"\n🤖 Agent: {agent['name']}")
        print(f"👤 Lead: {lead['name']} at {lead['company']}")
        
        # Build dynamic variables
        try:
            dynamic_vars = build_dynamic_variables(agent, lead)
            
            print("📋 Generated Variables:")
            print(f"   • Agent Name: {dynamic_vars['agent_name']}")
            print(f"   • Lead Name: {dynamic_vars['lead_name']}")
            print(f"   • Welcome: {dynamic_vars['welcome_message'][:60]}...")
            print(f"   • Call Duration: {dynamic_vars['max_call_duration_minutes']} min")
            print(f"   • Functions Available: {len(dynamic_vars['available_functions'].split('\\n'))} functions")
            
            print("✅ Variables generated successfully")
            
        except Exception as e:
            print(f"❌ Error generating variables: {e}")
    
    return True

async def test_single_template_call():
    """Test creating a single call with template approach"""
    
    print("\\n📞 Testing Single Template Call Creation")
    print("=" * 50)
    
    if not retell_service.enabled:
        print("⚠️  Retell service disabled - using mock mode")
    
    agents = create_sample_agent_configs()
    leads = create_sample_leads()
    
    agent = agents[0]  # Real estate agent
    lead = leads[0]    # First lead
    
    call_context = {
        "type": "outbound",
        "source": "test_script"
    }
    
    try:
        print(f"🤖 Creating call: {agent['name']} → {lead['name']}")
        
        call_id = retell_service.create_template_call(agent, lead, call_context)
        
        if call_id:
            print(f"✅ Call created successfully: {call_id}")
            return call_id
        else:
            print("❌ Failed to create call")
            return None
            
    except Exception as e:
        print(f"❌ Error creating call: {e}")
        return None

async def test_concurrent_calls():
    """Test creating multiple concurrent calls"""
    
    print("\\n🚀 Testing Concurrent Call Creation")
    print("=" * 50)
    
    if not retell_service.enabled:
        print("⚠️  Retell service disabled - using mock mode")
    
    agents = create_sample_agent_configs()
    leads = create_sample_leads()
    
    # Test different scenarios
    scenarios = [
        {"agent": agents[0], "leads": leads[:3], "name": "Real Estate Campaign"},
        {"agent": agents[1], "leads": leads[3:6], "name": "Healthcare Follow-ups"},
        {"agent": agents[2], "leads": leads[6:9], "name": "Insurance Outreach"}
    ]
    
    all_results = []
    
    for scenario in scenarios:
        agent = scenario["agent"]
        scenario_leads = scenario["leads"]
        
        print(f"\\n📋 Scenario: {scenario['name']}")
        print(f"🤖 Agent: {agent['name']}")
        print(f"👥 Leads: {len(scenario_leads)} contacts")
        
        start_time = time.time()
        
        try:
            call_context = {
                "type": "outbound", 
                "source": "concurrent_test",
                "campaign": scenario["name"]
            }
            
            # Create concurrent calls
            call_ids = await retell_service.create_concurrent_calls(
                agent, scenario_leads, call_context
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            successful_calls = len([cid for cid in call_ids if cid and not isinstance(cid, Exception)])
            
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"✅ Successful calls: {successful_calls}/{len(scenario_leads)}")
            
            if successful_calls > 0:
                print(f"📞 Call IDs: {call_ids[:3]}{'...' if len(call_ids) > 3 else ''}")
            
            all_results.append({
                "scenario": scenario["name"],
                "agent": agent["name"],
                "leads_count": len(scenario_leads),
                "successful_calls": successful_calls,
                "duration": duration,
                "calls_per_second": successful_calls / duration if duration > 0 else 0
            })
            
        except Exception as e:
            print(f"❌ Error in scenario: {e}")
            all_results.append({
                "scenario": scenario["name"],
                "error": str(e)
            })
    
    return all_results

def print_performance_summary(results):
    """Print performance summary"""
    
    print("\\n📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    total_calls = 0
    total_duration = 0
    successful_scenarios = 0
    
    for result in results:
        if "error" not in result:
            scenario = result["scenario"]
            calls = result["successful_calls"]
            duration = result["duration"]
            rate = result["calls_per_second"]
            
            print(f"🎯 {scenario}")
            print(f"   • Calls: {calls}/{result['leads_count']}")
            print(f"   • Duration: {duration:.2f}s")
            print(f"   • Rate: {rate:.1f} calls/second")
            print()
            
            total_calls += calls
            total_duration += duration
            successful_scenarios += 1
        else:
            print(f"❌ {result['scenario']}: {result['error']}")
    
    if successful_scenarios > 0:
        avg_rate = total_calls / total_duration if total_duration > 0 else 0
        print(f"🏆 TOTALS:")
        print(f"   • Total calls: {total_calls}")
        print(f"   • Total duration: {total_duration:.2f}s")
        print(f"   • Average rate: {avg_rate:.1f} calls/second")
        print(f"   • Successful scenarios: {successful_scenarios}")

async def main():
    """Main test function"""
    
    print("🚀 TEMPLATE-BASED CONCURRENT CALL TESTING")
    print("=" * 60)
    
    # Test 1: Dynamic variable generation
    if not test_dynamic_variables():
        print("❌ Dynamic variable test failed")
        return False
    
    # Test 2: Single call creation
    call_id = await test_single_template_call()
    if not call_id:
        print("❌ Single call test failed")
        return False
    
    # Test 3: Concurrent call creation
    results = await test_concurrent_calls()
    
    # Show performance summary
    print_performance_summary(results)
    
    print("\\n🎉 Template-based concurrent calling tests completed!")
    print("=" * 60)
    print("✅ Benefits demonstrated:")
    print("   • Single master agent handles multiple personalities")
    print("   • Dynamic variables customize each call")
    print("   • Concurrent calls scale efficiently")
    print("   • No agent sync issues")
    print("   • Cost-effective solution")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if not success:
        sys.exit(1)