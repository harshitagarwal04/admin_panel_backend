# Template-Based Retell AI Integration

## Overview

The template-based approach uses a single master agent in Retell AI that dynamically adapts to different agent personalities using variables. This eliminates the need to create/sync individual agents while maintaining unlimited scalability.

## Architecture

```
Database Agents (Your System)     Retell AI
┌─────────────────────────┐       ┌──────────────────────┐
│ Real Estate Agent       │       │                      │
│ Healthcare Agent        │ ───── │  Master Template     │
│ Insurance Agent         │       │      Agent           │
│ Custom Agent Type N     │       │                      │
└─────────────────────────┘       └──────────────────────┘
                                           │
                                   Dynamic Variables
                                     Per Call
                                           │
                          ┌─────────────────────────────────┐
                          │  Call 1: "You are Sarah..."     │
                          │  Call 2: "You are Dr. Johnson..." │
                          │  Call 3: "You are Mike..."       │
                          └─────────────────────────────────┘
```

## Benefits

### ✅ Scalability
- **Unlimited agent types** without Retell limits
- **Concurrent calls** with different personalities  
- **No pre-creation** required for new agent types

### ✅ Simplicity
- **No sync issues** between systems
- **Single source of truth** in your database
- **Instant deployment** of new agent personalities

### ✅ Cost Efficiency
- **One Retell agent** serves all use cases
- **Reduced API calls** for agent management
- **Lower operational overhead**

### ✅ Flexibility
- **Real-time customization** per call
- **Dynamic voice selection** per agent type
- **Context-aware conversations**

## How It Works

### 1. Master Template Agent
A single agent in Retell with a flexible prompt template:

```
You are {{agent_name}} calling from {{company_name}}.

ROLE & INSTRUCTIONS:
{{prompt}}

LEAD INFORMATION:
- Name: {{lead_name}}
- Company: {{lead_company}}
- Context: {{lead_context}}

CONVERSATION FLOW:
1. Start with: {{welcome_message}}
2. Follow your role instructions above
3. Use available functions: {{available_functions}}
```

### 2. Dynamic Variables
Each call gets personalized variables:

```python
dynamic_vars = {
    "agent_name": "Sarah Real Estate Expert",
    "company_name": "Premium Realty", 
    "prompt": "You are a professional real estate agent...",
    "welcome_message": "Hi! This is Sarah from Premium Realty...",
    "lead_name": "John Smith",
    "lead_company": "Tech Startup Inc",
    "available_functions": "- Check calendar availability\n- Book appointments"
}
```

### 3. Call Creation
```python
call_id = retell_service.create_template_call(
    agent_config=your_db_agent,
    lead_data=lead_info,
    call_context={"type": "outbound"}
)
```

## Implementation

### Core Files

1. **`app/core/retell_template.py`** - Template configuration and helpers
2. **`app/services/retell_service.py`** - Updated service with template methods
3. **`initialize_template_agent.py`** - Setup script
4. **`test_template_concurrent_calls.py`** - Testing and examples

### Key Methods

#### Create Single Call
```python
def create_template_call(self, agent_config: dict, lead_data: dict, call_context: dict = None) -> str:
    """Create a call using template approach with dynamic variables"""
```

#### Create Concurrent Calls  
```python
async def create_concurrent_calls(self, agent_config: dict, leads: List[dict], call_context: dict = None) -> List[str]:
    """Create multiple concurrent calls with the same agent personality"""
```

#### Build Dynamic Variables
```python
def build_dynamic_variables(agent_config: dict, lead_data: dict, call_context: dict = None) -> dict:
    """Build personalized variables for each call"""
```

## Setup Instructions

### 1. Initialize Master Agent
```bash
python3 initialize_template_agent.py
```

This will:
- Create/verify the master template agent in Retell
- Test the template functionality
- Show cleanup options for old agents

### 2. Update Your Code
Replace old agent creation:
```python
# OLD WAY (deprecated)
retell_agent_id = retell_service.create_agent(agent_data)
call_id = retell_service.create_phone_call(call_data)

# NEW WAY (template-based)
call_id = retell_service.create_template_call(agent_config, lead_data)
```

### 3. Test Concurrent Calls
```bash
python3 test_template_concurrent_calls.py
```

## Usage Examples

### Single Agent Call
```python
# Your database agent
agent_config = {
    "id": "agent-123",
    "name": "Sarah Real Estate Expert",
    "prompt": "You are a professional real estate agent...",
    "welcome_message": "Hi! This is Sarah from Premium Realty...",
    "voice_id": "11labs-Adrian",
    "functions": ["end_call", "check_calendar_availability"],
    "variables": {"property_type": "condos", "location": "SF"},
    "outbound_phone": "+14155551234"
}

# Lead information
lead_data = {
    "id": "lead-456", 
    "name": "John Smith",
    "phone": "+14155559999",
    "company": "Tech Startup"
}

# Create the call
call_id = retell_service.create_template_call(agent_config, lead_data)
```

### Concurrent Campaign
```python
# Multiple leads for the same agent
leads = [
    {"id": "lead-1", "name": "Alice", "phone": "+14155551001"},
    {"id": "lead-2", "name": "Bob", "phone": "+14155551002"},
    {"id": "lead-3", "name": "Carol", "phone": "+14155551003"}
]

# Create all calls concurrently
call_ids = await retell_service.create_concurrent_calls(agent_config, leads)
```

### Different Agent Types
```python
# Real Estate Agent
real_estate_agent = {
    "name": "Sarah Real Estate",
    "prompt": "You are a real estate professional...",
    "voice_id": "11labs-Adrian"
}

# Healthcare Agent  
healthcare_agent = {
    "name": "Dr. Johnson Assistant",
    "prompt": "You are a healthcare assistant...", 
    "voice_id": "11labs-Bella"
}

# Both use the same master template but with different personalities
call_1 = retell_service.create_template_call(real_estate_agent, lead_1)
call_2 = retell_service.create_template_call(healthcare_agent, lead_2)
```

## Migration from Individual Agents

### Backward Compatibility
- Existing agent endpoints continue to work
- `retell_agent_id` now stores the master template ID
- No database schema changes required

### Legacy Method Behavior
```python
# These methods now use template approach internally:
retell_service.create_agent(agent_data)       # Returns master template ID
retell_service.update_agent(id, data)         # No-op (changes applied per-call)
retell_service.delete_agent(id)               # No-op (only soft delete in DB)
```

### Migration Steps
1. ✅ Run `initialize_template_agent.py` 
2. ✅ Update call creation code to use `create_template_call()`
3. ✅ Test with `test_template_concurrent_calls.py`
4. 🔄 Optionally clean up old individual agents in Retell dashboard

## Performance Characteristics

### Concurrent Call Limits
- **Master agent capacity**: 100+ concurrent calls
- **Rate limiting**: Based on your Retell plan, not per-agent
- **Batch processing**: 50 calls per batch (configurable)

### Example Performance
```
Real Estate Campaign: 10 leads → 3.2 calls/second
Healthcare Follow-ups: 15 leads → 4.1 calls/second  
Insurance Outreach: 20 leads → 3.8 calls/second

Total: 45 concurrent calls in ~12 seconds
```

## Troubleshooting

### Master Agent Not Found
```bash
# Re-initialize the master agent
python3 initialize_template_agent.py
```

### Template Variables Missing
Check that `build_dynamic_variables()` includes all required fields:
- `agent_name`, `prompt`, `welcome_message`
- `lead_name`, `lead_phone`  
- `available_functions`, `business_hours`

### Concurrent Call Failures
- Check Retell API rate limits
- Reduce `max_concurrent` in `create_concurrent_calls()`
- Verify master agent ID is valid

## Advanced Configuration

### Custom Voice Per Agent Type
```python
def get_voice_for_agent_type(agent_type: str) -> str:
    voice_mapping = {
        "real_estate": "11labs-Adrian",
        "healthcare": "11labs-Bella", 
        "insurance": "11labs-Charlie"
    }
    return voice_mapping.get(agent_type, "11labs-Adrian")
```

### Context-Aware Variables
```python
def build_context_variables(lead_data: dict) -> dict:
    # Customize based on lead source, previous interactions, etc.
    context = {}
    
    if lead_data.get("source") == "website":
        context["lead_context"] = "interested via website form"
    elif lead_data.get("previous_calls", 0) > 0:
        context["lead_context"] = "follow-up call"
    
    return context
```

### Function Availability Per Agent
```python
AGENT_FUNCTIONS = {
    "real_estate": ["end_call", "check_calendar", "book_appointment"],
    "healthcare": ["end_call", "check_calendar", "transfer_to_nurse"],
    "insurance": ["end_call", "send_quote", "transfer_to_agent"]
}
```

## Best Practices

### 1. Agent Design
- ✅ Keep prompts focused and specific
- ✅ Use clear role definitions
- ✅ Include context-relevant variables
- ❌ Don't make prompts too generic

### 2. Variable Management
- ✅ Validate all required variables before calls
- ✅ Use descriptive variable names
- ✅ Include fallback values for optional fields
- ❌ Don't pass sensitive data in variables

### 3. Performance Optimization
- ✅ Batch concurrent calls appropriately  
- ✅ Monitor Retell rate limits
- ✅ Use async operations for large campaigns
- ❌ Don't create unbounded concurrent calls

### 4. Error Handling
- ✅ Log template variable generation errors
- ✅ Handle master agent initialization failures
- ✅ Provide meaningful error messages
- ❌ Don't fail silently on template issues

## Conclusion

The template-based approach provides:
- **Unlimited scalability** for agent personalities
- **Simplified architecture** with no sync issues  
- **Cost-effective** single-agent solution
- **Concurrent call** capabilities
- **Easy maintenance** and deployment

This approach is ideal for businesses that need multiple agent types without the complexity of managing individual agents in Retell AI.