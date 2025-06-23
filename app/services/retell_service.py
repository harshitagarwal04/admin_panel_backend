from typing import Dict, Any, Optional, List
from retell import Retell
from app.core.config import settings
from app.core.retell_template import (
    MASTER_AGENT_CONFIG, 
    build_dynamic_variables, 
    get_voice_id_for_agent
)
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class RetellService:
    def __init__(self):
        self.api_key = getattr(settings, 'RETELL_API_KEY', None)
        self.master_agent_id = None  # Will be set after creating master template
        
        if self.api_key and self.api_key != "your-retell-api-key-here":
            self.enabled = True
            self.client = Retell(api_key=self.api_key)
            # Initialize master template agent on first use
            self._initialize_master_agent()
        else:
            logger.warning("Retell API key not configured - running in mock mode")
            self.enabled = False
            self.client = None
    
    def _initialize_master_agent(self):
        """Initialize the master template agent if it doesn't exist"""
        try:
            # Check if we have the master agent ID stored somewhere
            # For now, we'll create one if it doesn't exist
            if not self.master_agent_id:
                self.master_agent_id = self._create_or_get_master_agent()
        except Exception as e:
            logger.error(f"Failed to initialize master agent: {e}")
            # Fall back to legacy mode if template creation fails
            self.master_agent_id = None
    
    def _create_or_get_master_agent(self) -> str:
        """Create or retrieve the master template agent"""
        try:
            # List existing agents to see if we have a master template
            existing_agents = self.client.agent.list()
            
            # Look for existing master template agent
            for agent in existing_agents:
                if agent.agent_name == "Universal AI Assistant":
                    logger.info(f"Found existing master template agent: {agent.agent_id}")
                    return agent.agent_id
            
            # Create new master template agent
            logger.info("Creating new master template agent")
            response = self.client.agent.create(**MASTER_AGENT_CONFIG)
            logger.info(f"Created master template agent: {response.agent_id}")
            return response.agent_id
            
        except Exception as e:
            logger.error(f"Error creating master template agent: {e}")
            raise
    
    def create_agent(self, agent_data: Dict[str, Any]) -> Optional[str]:
        """
        LEGACY METHOD - Template-based approach doesn't create individual agents.
        Returns master agent ID for backward compatibility.
        """
        if not self.enabled:
            return f"mock_agent_{agent_data['name'][:10]}"
        
        logger.info(f"Template-based mode: Agent '{agent_data['name']}' will use master template")
        return self.master_agent_id or "master_template_agent"
    
    def update_agent(self, retell_agent_id: str, agent_data: Dict[str, Any]) -> bool:
        """
        LEGACY METHOD - Template-based approach doesn't update individual agents.
        Agent changes are applied per-call via dynamic variables.
        """
        if not self.enabled:
            return True
        
        logger.info(f"Template-based mode: Agent updates applied via dynamic variables per call")
        return True
    
    def delete_agent(self, retell_agent_id: str) -> bool:
        """
        LEGACY METHOD - Template-based approach doesn't delete individual agents.
        Only the master template agent exists in Retell.
        """
        if not self.enabled:
            return True
        
        logger.info(f"Template-based mode: No individual agents to delete")
        return True
    
    def get_agent(self, retell_agent_id: str) -> Optional[Dict]:
        """Get agent details from Retell"""
        if not self.enabled:
            return {"mock": True, "agent_id": retell_agent_id}
        
        try:
            agent = self.client.agent.retrieve(agent_id=retell_agent_id)
            # Convert to dict for compatibility
            return {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "voice_id": agent.voice_id,
                "language": agent.language,
                "created_at": str(agent.created_at) if hasattr(agent, 'created_at') else None
            }
        except Exception as e:
            logger.error(f"Error getting agent via SDK: {e}")
            return None
    
    def list_agents(self) -> List[Dict]:
        """List all agents from Retell"""
        if not self.enabled:
            return []
        
        try:
            agents = self.client.agent.list()
            # Convert to list of dicts
            return [
                {
                    "agent_id": agent.agent_id,
                    "agent_name": agent.agent_name,
                    "voice_id": agent.voice_id,
                    "language": agent.language
                }
                for agent in agents
            ]
        except Exception as e:
            logger.error(f"Error listing agents via SDK: {e}")
            return []
    
    def create_template_call(self, agent_config: dict, lead_data: dict, call_context: dict = None) -> Optional[str]:
        """Create a phone call using the template-based approach"""
        if not self.enabled:
            return f"mock_call_{lead_data.get('phone', 'unknown')[-4:]}"
        
        if not self.master_agent_id:
            logger.error("Master template agent not initialized")
            return None
        
        try:
            # Build dynamic variables for this specific call
            dynamic_vars = build_dynamic_variables(agent_config, lead_data, call_context)
            
            # Get the appropriate voice for this agent
            voice_id = get_voice_id_for_agent(agent_config)
            
            # Create call with template agent and dynamic variables
            response = self.client.call.create_phone_call(
                retell_agent_id=self.master_agent_id,
                from_number=agent_config.get("outbound_phone"),
                to_number=lead_data["phone"],
                retell_llm_dynamic_variables=dynamic_vars,
                metadata={
                    "agent_id": agent_config.get("id"),
                    "agent_name": agent_config.get("name"),
                    "lead_id": lead_data.get("id"),
                    "lead_name": lead_data.get("name"),
                    "call_type": call_context.get("type", "outbound") if call_context else "outbound",
                    "created_at": datetime.utcnow().isoformat(),
                    "source": "admin_panel_template"
                }
            )
            
            logger.info(f"Successfully created template call: {response.call_id}")
            return response.call_id
            
        except Exception as e:
            logger.error(f"Error creating template call: {e}")
            if hasattr(e, 'response'):
                logger.error(f"Response details: {getattr(e.response, 'text', 'No response text')}")
            return None
    
    async def create_concurrent_calls(self, agent_config: dict, leads: List[dict], call_context: dict = None) -> List[str]:
        """Create multiple concurrent calls using the template approach"""
        if not self.enabled:
            return [f"mock_call_{i}" for i in range(len(leads))]
        
        if not leads:
            return []
        
        # Limit concurrent calls to prevent rate limiting
        max_concurrent = 50  # Adjust based on your Retell plan
        call_batches = [leads[i:i + max_concurrent] for i in range(0, len(leads), max_concurrent)]
        
        all_call_ids = []
        
        for batch in call_batches:
            # Create tasks for concurrent execution
            tasks = []
            for lead in batch:
                task = asyncio.create_task(
                    self._create_template_call_async(agent_config, lead, call_context)
                )
                tasks.append(task)
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and add successful call IDs
            for result in batch_results:
                if isinstance(result, str) and not isinstance(result, Exception):
                    all_call_ids.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Failed to create call in batch: {result}")
        
        return all_call_ids
    
    async def _create_template_call_async(self, agent_config: dict, lead_data: dict, call_context: dict = None) -> Optional[str]:
        """Async wrapper for template call creation"""
        return self.create_template_call(agent_config, lead_data, call_context)
    
    def create_phone_call(self, call_data: Dict[str, Any]) -> Optional[str]:
        """Create a phone call and return the call ID"""
        if not self.enabled:
            return f"mock_call_{call_data.get('to_number', 'unknown')[-4:]}"
        
        try:
            # Use SDK to create phone call
            response = self.client.call.create_phone_call(
                from_number=call_data["from_number"],
                to_number=call_data["to_number"],
                override_agent_id=call_data.get("retell_agent_id"),
                metadata=call_data.get("metadata"),
                retell_llm_dynamic_variables=call_data.get("variables")
            )
            
            logger.info(f"Successfully created phone call: {response.call_id}")
            return response.call_id
            
        except Exception as e:
            logger.error(f"Error creating phone call via SDK: {e}")
            return None
    
    def get_call(self, call_id: str) -> Optional[Dict]:
        """Get call details from Retell"""
        if not self.enabled:
            return {
                "mock": True,
                "call_id": call_id,
                "call_status": "completed",
                "outcome": "answered"
            }
        
        try:
            call = self.client.call.retrieve(call_id=call_id)
            # Convert to dict
            return {
                "call_id": call.call_id,
                "agent_id": call.agent_id,
                "call_status": call.call_status,
                "from_number": call.from_number,
                "to_number": call.to_number,
                "metadata": call.metadata
            }
        except Exception as e:
            logger.error(f"Error getting call via SDK: {e}")
            return None
    
    def list_calls(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List calls with optional filters"""
        if not self.enabled:
            return []
        
        try:
            # SDK list method may accept different parameters
            calls = self.client.call.list()
            return [
                {
                    "call_id": call.call_id,
                    "agent_id": call.agent_id,
                    "call_status": call.call_status,
                    "from_number": call.from_number,
                    "to_number": call.to_number
                }
                for call in calls
            ]
        except Exception as e:
            logger.error(f"Error listing calls via SDK: {e}")
            return []
    
    def create_phone_call_for_lead(self, lead_id: str, agent_id: str, 
                                  from_number: str, to_number: str, 
                                  lead_name: str, variables: Optional[Dict] = None) -> Optional[str]:
        """Create a phone call for a specific lead using template approach"""
        
        # Get agent configuration from database
        from app.db.session import SessionLocal
        from app.models.agent import Agent
        
        db = SessionLocal()
        try:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                logger.error(f"Agent {agent_id} not found")
                return None
            
            # Convert agent to dict format
            agent_config = {
                "id": str(agent.id),
                "name": agent.name,
                "prompt": agent.prompt,
                "welcome_message": agent.welcome_message,
                "voice_id": str(agent.voice_id) if agent.voice_id else None,
                "functions": agent.functions or [],
                "variables": agent.variables or {},
                "outbound_phone": from_number,
                "business_hours_start": str(agent.business_hours_start) if agent.business_hours_start else None,
                "business_hours_end": str(agent.business_hours_end) if agent.business_hours_end else None,
                "timezone": agent.timezone,
                "max_call_duration_minutes": agent.max_call_duration_minutes
            }
            
            # Add custom variables
            if variables:
                agent_config["variables"].update(variables)
            
            # Lead data
            lead_data = {
                "id": lead_id,
                "name": lead_name,
                "phone": to_number
            }
            
            # Call context
            call_context = {
                "type": "outbound",
                "source": "admin_panel"
            }
            
            return self.create_template_call(agent_config, lead_data, call_context)
            
        finally:
            db.close()
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature from Retell"""
        # TODO: Implement signature verification using webhook secret
        # This would use HMAC-SHA256 with the webhook secret
        return True  # For now, always return True


retell_service = RetellService()