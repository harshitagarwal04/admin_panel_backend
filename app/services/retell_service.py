from typing import Dict, Any, Optional
from retell import Retell
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RetellService:
    def __init__(self):
        if settings.RETELL_API_KEY and settings.RETELL_API_KEY != "your-retell-api-key-here":
            self.client = Retell(api_key=settings.RETELL_API_KEY)
            self.enabled = True
        else:
            logger.warning("Retell API key not configured - running in mock mode")
            self.client = None
            self.enabled = False
    
    def create_agent(self, agent_data: Dict[str, Any]) -> Optional[str]:
        """Create an agent in Retell and return the agent ID"""
        if not self.enabled:
            return f"mock_agent_{agent_data['name'][:10]}"
        
        try:
            response = self.client.agent.create(
                agent_name=agent_data["name"],
                voice_id=agent_data.get("voice_id", "default"),
                system_prompt=agent_data["prompt"],
                initial_message=agent_data.get("welcome_message", "Hello!"),
                # Add other Retell-specific configurations
            )
            return response.agent_id
        except Exception as e:
            logger.error(f"Error creating Retell agent: {e}")
            return None
    
    def update_agent(self, retell_agent_id: str, agent_data: Dict[str, Any]) -> bool:
        """Update an agent in Retell"""
        if not self.enabled:
            return True
        
        try:
            self.client.agent.update(
                agent_id=retell_agent_id,
                agent_name=agent_data["name"],
                voice_id=agent_data.get("voice_id", "default"),
                system_prompt=agent_data["prompt"],
                initial_message=agent_data.get("welcome_message", "Hello!"),
            )
            return True
        except Exception as e:
            logger.error(f"Error updating Retell agent: {e}")
            return False
    
    def delete_agent(self, retell_agent_id: str) -> bool:
        """Delete an agent from Retell"""
        if not self.enabled:
            return True
        
        try:
            self.client.agent.delete(agent_id=retell_agent_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting Retell agent: {e}")
            return False
    
    def create_phone_call(self, call_data: Dict[str, Any]) -> Optional[str]:
        """Create a phone call and return the call ID"""
        if not self.enabled:
            return f"mock_call_{call_data.get('to_number', 'unknown')[-4:]}"
        
        try:
            response = self.client.call.create_phone_call(
                from_number=call_data["from_number"],
                to_number=call_data["to_number"],
                agent_id=call_data["agent_id"],
                # Add other call configurations
            )
            return response.call_id
        except Exception as e:
            logger.error(f"Error creating phone call: {e}")
            return None
    
    def register_webhook(self, webhook_url: str) -> bool:
        """Register webhook URL with Retell"""
        if not self.enabled:
            return True
        
        try:
            # Implementation depends on Retell SDK webhook registration
            return True
        except Exception as e:
            logger.error(f"Error registering webhook: {e}")
            return False


retell_service = RetellService()