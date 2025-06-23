from typing import Dict, Any, Optional, List
from retell import Retell
from app.core.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RetellService:
    def __init__(self):
        self.api_key = getattr(settings, 'RETELL_API_KEY', None)
        
        if self.api_key and self.api_key != "your-retell-api-key-here":
            self.enabled = True
            self.client = Retell(api_key=self.api_key)
        else:
            logger.warning("Retell API key not configured - running in mock mode")
            self.enabled = False
            self.client = None
    
    def create_agent(self, agent_data: Dict[str, Any]) -> Optional[str]:
        """Create an agent in Retell and return the agent ID"""
        if not self.enabled:
            return f"mock_agent_{agent_data['name'][:10]}"
        
        try:
            # Get a sample response engine from existing agents
            existing_agents = self.client.agent.list()
            if not existing_agents:
                raise Exception("No existing agents found to copy response_engine from")
            
            sample_response_engine = existing_agents[0].response_engine
            
            # Resolve voice_id - if it's a UUID from our database, get the provider ID
            voice_id = agent_data.get("voice_id", "11labs-Adrian")
            if voice_id and len(voice_id) == 36 and voice_id.count('-') == 4:  # Looks like UUID
                # Get the voice from our database to find the provider ID
                from app.db.session import SessionLocal
                from app.models.voice import Voice
                
                db = SessionLocal()
                try:
                    voice = db.query(Voice).filter(Voice.id == voice_id).first()
                    if voice and voice.voice_provider_id:
                        voice_id = voice.voice_provider_id
                        logger.info(f"Mapped voice UUID {agent_data.get('voice_id')} to provider ID {voice_id}")
                    else:
                        logger.warning(f"Voice UUID {agent_data.get('voice_id')} not found, using default")
                        voice_id = "11labs-Adrian"
                finally:
                    db.close()
            
            # Build create kwargs based on what's provided
            create_kwargs = {
                "agent_name": agent_data["name"],
                "voice_id": voice_id,
                "response_engine": sample_response_engine,  # Use existing response engine
                "language": "en-US"
            }
            
            # Add optional parameters if specified
            if "enable_backchannel" in agent_data:
                create_kwargs["enable_backchannel"] = agent_data["enable_backchannel"]
            if "responsiveness" in agent_data:
                create_kwargs["responsiveness"] = agent_data["responsiveness"]
            if "voice_temperature" in agent_data:
                create_kwargs["voice_temperature"] = agent_data["voice_temperature"]
            if "voice_speed" in agent_data:
                create_kwargs["voice_speed"] = agent_data["voice_speed"]
            
            # Add webhook URL if configured
            if hasattr(settings, 'WEBHOOK_URL') and settings.WEBHOOK_URL:
                create_kwargs["webhook_url"] = settings.WEBHOOK_URL
            
            # Create agent using SDK
            response = self.client.agent.create(**create_kwargs)
            
            logger.info(f"Successfully created agent: {response.agent_id}")
            return response.agent_id
            
        except Exception as e:
            logger.error(f"Error creating agent via SDK: {e}")
            # Log more details about the error
            if hasattr(e, 'response'):
                logger.error(f"Response details: {getattr(e.response, 'text', 'No response text')}")
            return None
    
    def update_agent(self, retell_agent_id: str, agent_data: Dict[str, Any]) -> bool:
        """Update an agent in Retell"""
        if not self.enabled:
            return True
        
        try:
            # Build update kwargs with only provided fields
            update_kwargs = {}
            if "name" in agent_data:
                update_kwargs["agent_name"] = agent_data["name"]
            if "voice_id" in agent_data:
                voice_id = agent_data["voice_id"]
                # Resolve voice_id if it's a UUID from our database
                if voice_id and len(voice_id) == 36 and voice_id.count('-') == 4:  # Looks like UUID
                    from app.db.session import SessionLocal
                    from app.models.voice import Voice
                    
                    db = SessionLocal()
                    try:
                        voice = db.query(Voice).filter(Voice.id == voice_id).first()
                        if voice and voice.voice_provider_id:
                            voice_id = voice.voice_provider_id
                            logger.info(f"Mapped voice UUID {agent_data['voice_id']} to provider ID {voice_id}")
                        else:
                            logger.warning(f"Voice UUID {agent_data['voice_id']} not found, using default")
                            voice_id = "11labs-Adrian"
                    finally:
                        db.close()
                
                update_kwargs["voice_id"] = voice_id
            if "voice_temperature" in agent_data:
                update_kwargs["voice_temperature"] = agent_data["voice_temperature"]
            if "voice_speed" in agent_data:
                update_kwargs["voice_speed"] = agent_data["voice_speed"]
            
            logger.info(f"Updating agent {retell_agent_id} with kwargs: {update_kwargs}")
            
            self.client.agent.update(
                agent_id=retell_agent_id,
                **update_kwargs
            )
            logger.info(f"Successfully updated agent: {retell_agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating agent via SDK: {e}")
            # Log more details about the error
            if hasattr(e, 'response'):
                logger.error(f"Response details: {getattr(e.response, 'text', 'No response text')}")
            if hasattr(e, 'status_code'):
                logger.error(f"Status code: {e.status_code}")
            return False
    
    def delete_agent(self, retell_agent_id: str) -> bool:
        """Delete an agent from Retell"""
        if not self.enabled:
            return True
        
        try:
            self.client.agent.delete(agent_id=retell_agent_id)
            logger.info(f"Successfully deleted agent: {retell_agent_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting agent via SDK: {e}")
            return False
    
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
    
    def create_phone_call_for_lead(self, lead_id: str, agent_retell_id: str, 
                                  from_number: str, to_number: str, 
                                  lead_name: str, variables: Optional[Dict] = None) -> Optional[str]:
        """Create a phone call for a specific lead with our standard metadata"""
        
        call_data = {
            "from_number": from_number,
            "to_number": to_number,
            "retell_agent_id": agent_retell_id,
            "metadata": {
                "lead_id": lead_id,
                "created_at": datetime.utcnow().isoformat(),
                "source": "admin_panel"
            },
            "variables": {
                "lead_name": lead_name,
                **(variables or {})
            }
        }
        
        return self.create_phone_call(call_data)
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature from Retell"""
        # TODO: Implement signature verification using webhook secret
        # This would use HMAC-SHA256 with the webhook secret
        return True  # For now, always return True


retell_service = RetellService()