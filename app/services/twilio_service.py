from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TwilioService:
    """Service for managing Twilio phone numbers"""
    
    def __init__(self):
        self.enabled = True  # Set to False if Twilio SDK not available
    
    def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Validate Twilio credentials"""
        required_fields = ['account_sid', 'auth_token']
        return all(field in credentials for field in required_fields)
    
    def list_available_numbers(self, credentials: Dict[str, str], 
                             country_code: str = "US", 
                             area_code: Optional[str] = None,
                             limit: int = 20) -> List[Dict[str, Any]]:
        """List available phone numbers for purchase"""
        if not self.enabled:
            return self._mock_available_numbers()
        
        try:
            from twilio.rest import Client
            
            client = Client(credentials['account_sid'], credentials['auth_token'])
            
            # Search for available local numbers
            search_params = {
                'country_code': country_code,
                'limit': limit
            }
            
            if area_code:
                search_params['area_code'] = area_code
            
            available_numbers = client.available_phone_numbers(country_code).local.list(**search_params)
            
            return [
                {
                    'phone_number': number.phone_number,
                    'friendly_name': number.friendly_name,
                    'region': number.region,
                    'iso_country': number.iso_country,
                    'capabilities': {
                        'voice': getattr(number.capabilities, 'voice', False),
                        'sms': getattr(number.capabilities, 'sms', False),
                        'mms': getattr(number.capabilities, 'mms', False)
                    },
                    'monthly_cost': 1.00  # Twilio standard rate
                }
                for number in available_numbers
            ]
            
        except Exception as e:
            logger.error(f"Error listing available Twilio numbers: {e}")
            raise
    
    def purchase_number(self, credentials: Dict[str, str], 
                       phone_number: str, 
                       capabilities: List[str]) -> Dict[str, Any]:
        """Purchase a phone number"""
        if not self.enabled:
            return self._mock_purchase_result(phone_number)
        
        try:
            from twilio.rest import Client
            
            client = Client(credentials['account_sid'], credentials['auth_token'])
            
            # Purchase the number
            purchased_number = client.incoming_phone_numbers.create(
                phone_number=phone_number
            )
            
            return {
                'sid': purchased_number.sid,
                'phone_number': purchased_number.phone_number,
                'friendly_name': purchased_number.friendly_name,
                'monthly_cost': 1.00,
                'status': 'active'
            }
            
        except Exception as e:
            logger.error(f"Error purchasing Twilio number {phone_number}: {e}")
            raise
    
    def list_owned_numbers(self, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """List phone numbers owned by the account"""
        if not self.enabled:
            return self._mock_owned_numbers()
        
        try:
            from twilio.rest import Client
            
            client = Client(credentials['account_sid'], credentials['auth_token'])
            
            incoming_numbers = client.incoming_phone_numbers.list()
            
            return [
                {
                    'phone_number': number.phone_number,
                    'friendly_name': number.friendly_name,
                    'capabilities': {
                        'voice': getattr(number.capabilities, 'voice', False),
                        'sms': getattr(number.capabilities, 'sms', False),
                        'mms': getattr(number.capabilities, 'mms', False)
                    },
                    'status': number.status,
                    'provider_number_id': number.sid,
                    'monthly_cost': 1.00
                }
                for number in incoming_numbers
            ]
            
        except Exception as e:
            logger.error(f"Error listing owned Twilio numbers: {e}")
            raise
    
    def release_number(self, credentials: Dict[str, str], phone_number: str) -> bool:
        """Release a phone number"""
        if not self.enabled:
            return True  # Mock success
        
        try:
            from twilio.rest import Client
            
            client = Client(credentials['account_sid'], credentials['auth_token'])
            
            # Find the number by phone number
            incoming_numbers = client.incoming_phone_numbers.list(phone_number=phone_number)
            
            if incoming_numbers:
                # Delete the first matching number
                incoming_numbers[0].delete()
                return True
            else:
                logger.warning(f"Twilio number {phone_number} not found for release")
                return False
                
        except Exception as e:
            logger.error(f"Error releasing Twilio number {phone_number}: {e}")
            raise
    
    def _mock_available_numbers(self) -> List[Dict[str, Any]]:
        """Mock available numbers for development"""
        return [
            {
                'phone_number': '+14155552001',
                'friendly_name': '(415) 555-2001',
                'region': 'CA',
                'iso_country': 'US',
                'capabilities': {'voice': True, 'sms': True, 'mms': True},
                'monthly_cost': 1.00
            },
            {
                'phone_number': '+14155552002',
                'friendly_name': '(415) 555-2002',
                'region': 'CA',
                'iso_country': 'US',
                'capabilities': {'voice': True, 'sms': True, 'mms': False},
                'monthly_cost': 1.00
            }
        ]
    
    def _mock_owned_numbers(self) -> List[Dict[str, Any]]:
        """Mock owned numbers for development"""
        return [
            {
                'phone_number': '+14155559999',
                'friendly_name': '(415) 555-9999',
                'capabilities': {'voice': True, 'sms': True, 'mms': True},
                'status': 'in-use',
                'provider_number_id': 'PN1234567890',
                'monthly_cost': 1.00
            }
        ]
    
    def _mock_purchase_result(self, phone_number: str) -> Dict[str, Any]:
        """Mock purchase result for development"""
        return {
            'sid': f'PN{phone_number[-10:]}',
            'phone_number': phone_number,
            'friendly_name': phone_number,
            'monthly_cost': 1.00,
            'status': 'active'
        }


twilio_service = TwilioService()