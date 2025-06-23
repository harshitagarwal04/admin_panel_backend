"""
Retell AI Template Configuration
Master template agent configuration for dynamic agent behavior
"""

# Master template agent prompt with dynamic variables
MASTER_TEMPLATE_PROMPT = """You are {{agent_name}} calling from {{company_name}}.

ROLE & INSTRUCTIONS:
{{prompt}}

LEAD INFORMATION:
- Name: {{lead_name}}
- Company: {{lead_company}}
- Phone: {{lead_phone}}
- Context: {{lead_context}}

CONVERSATION VARIABLES:
{{#each variables}}
- {{@key}}: {{this}}
{{/each}}

CONVERSATION FLOW:
1. Start with: {{welcome_message}}
2. Follow your role instructions above
3. Ask relevant qualifying questions
4. Use available functions when appropriate
5. Be professional and maintain the conversation flow

AVAILABLE FUNCTIONS:
{{available_functions}}

BUSINESS CONTEXT:
- Business Hours: {{business_hours_start}} - {{business_hours_end}} ({{timezone}})
- Maximum Call Duration: {{max_call_duration_minutes}} minutes
- Call Type: {{call_type}}

IMPORTANT RULES:
- Stay in character as {{agent_name}} throughout the call
- Be professional, friendly, and helpful
- Listen actively and respond appropriately
- Follow up on important points
- End the call gracefully when objectives are met
- If asked about technical issues, transfer to support

Remember: You are representing {{company_name}} - maintain their brand voice and values."""

# Default response engine configuration for the master template
DEFAULT_RESPONSE_ENGINE = {
    "type": "retell-llm",
    "llm_websocket_url": "wss://api.retellai.com/llm-websocket",
    "begin_message": "Hello! This is {{agent_name}} from {{company_name}}. How are you doing today?",
    "general_prompt": MASTER_TEMPLATE_PROMPT,
    "general_tools": [
        {
            "type": "end_call",
            "name": "end_call",
            "description": "End the current phone call"
        },
        {
            "type": "transfer_call", 
            "name": "transfer_call",
            "description": "Transfer call to human agent or support"
        }
    ],
    "inbound_dynamic_variables_webhook_url": None,
    "webhook_url": None
}

# Master agent configuration
MASTER_AGENT_CONFIG = {
    "agent_name": "Universal AI Assistant",
    "voice_id": "11labs-Adrian",  # Default voice
    "response_engine": DEFAULT_RESPONSE_ENGINE,
    "language": "en-US",
    "voice_temperature": 1.0,
    "voice_speed": 1.0,
    "enable_backchannel": True,
    "backchannel_frequency": 0.9,
    "ambient_sound": None,
    "responsiveness": 1.0,
    "interruption_sensitivity": 1.0,
    "enable_voicemail_detection": True,
    "opt_out_sensitive_data_storage": False,
    "pronunciation_dictionary": [],
    "normalize_for_speech": True
}

def build_dynamic_variables(agent_config: dict, lead_data: dict, call_context: dict = None) -> dict:
    """Build dynamic variables for the template agent call"""
    
    # Format business hours
    business_hours = "Not specified"
    if agent_config.get("business_hours_start") and agent_config.get("business_hours_end"):
        business_hours = f"{agent_config['business_hours_start']} - {agent_config['business_hours_end']}"
    
    # Format available functions
    available_functions = "Standard call functions (end call, transfer)"
    if agent_config.get("functions"):
        functions_list = []
        for func in agent_config["functions"]:
            if func == "end_call":
                functions_list.append("End call when conversation is complete")
            elif func == "transfer_call":
                functions_list.append("Transfer to human agent if needed")
            elif func == "check_calendar_availability":
                functions_list.append("Check available appointment times")
            elif func == "book_on_calendar":
                functions_list.append("Schedule appointments")
            else:
                functions_list.append(f"Use {func} function when appropriate")
        available_functions = "\n".join([f"- {func}" for func in functions_list])
    
    # Build the dynamic variables dictionary
    dynamic_vars = {
        # Agent identity
        "agent_name": agent_config.get("name", "AI Assistant"),
        "company_name": lead_data.get("company_name", agent_config.get("company_name", "Our Company")),
        
        # Agent behavior
        "prompt": agent_config.get("prompt", "You are a helpful AI assistant."),
        "welcome_message": agent_config.get("welcome_message", "Hello! How can I help you today?"),
        
        # Lead information
        "lead_name": lead_data.get("name", "there"),
        "lead_company": lead_data.get("company", ""),
        "lead_phone": lead_data.get("phone", ""),
        "lead_context": lead_data.get("context", "general inquiry"),
        
        # Business context
        "business_hours_start": agent_config.get("business_hours_start", "9:00 AM"),
        "business_hours_end": agent_config.get("business_hours_end", "5:00 PM"),
        "timezone": agent_config.get("timezone", "UTC"),
        "max_call_duration_minutes": agent_config.get("max_call_duration_minutes", 20),
        
        # Functions and capabilities
        "available_functions": available_functions,
        
        # Call context
        "call_type": call_context.get("type", "outbound") if call_context else "outbound",
        
        # Custom variables from agent configuration
        "variables": agent_config.get("variables", {})
    }
    
    # Add any custom variables from the agent config
    if agent_config.get("variables"):
        for key, value in agent_config["variables"].items():
            if key not in dynamic_vars:  # Don't override system variables
                dynamic_vars[key] = value
    
    return dynamic_vars

def get_voice_id_for_agent(agent_config: dict) -> str:
    """Get the appropriate voice ID for an agent"""
    voice_id = agent_config.get("voice_id", "11labs-Adrian")
    
    # If it's a UUID from our database, map it to provider ID
    if voice_id and len(voice_id) == 36 and voice_id.count('-') == 4:
        from app.db.session import SessionLocal
        from app.models.voice import Voice
        
        db = SessionLocal()
        try:
            voice = db.query(Voice).filter(Voice.id == voice_id).first()
            if voice and voice.voice_provider_id:
                return voice.voice_provider_id
        finally:
            db.close()
    
    return voice_id or "11labs-Adrian"