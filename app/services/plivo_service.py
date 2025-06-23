from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PlivoService:
    """Service for managing Plivo phone numbers"""
    
    def __init__(self):
        self.enabled = True  # Set to False if Plivo SDK not available
    
    def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Validate Plivo credentials"""
        required_fields = ['auth_id', 'auth_token']
        return all(field in credentials for field in required_fields)
    
    def list_available_numbers(self, credentials: Dict[str, str], 
                             country_code: str = "US", 
                             area_code: Optional[str] = None,
                             limit: int = 20) -> List[Dict[str, Any]]:
        """List available phone numbers for purchase"""
        if not self.enabled:
            return self._mock_available_numbers()
        
        try:
            import plivo
            
            client = plivo.RestClient(credentials['auth_id'], credentials['auth_token'])
            
            # Search for available numbers
            search_params = {
                'country_iso': country_code,
                'limit': limit,
                'type': 'local'
            }
            
            if area_code:
                search_params['region'] = area_code
            
            response = client.phone_numbers.search(**search_params)
            
            return [
                {
                    'phone_number': number['number'],
                    'friendly_name': number['number'],
                    'region': number.get('region', ''),
                    'iso_country': country_code,
                    'capabilities': {
                        'voice': True,  # Plivo numbers generally support voice
                        'sms': True,    # and SMS
                        'mms': False    # MMS support varies
                    },
                    'monthly_cost': float(number.get('monthly_rental_rate', 0.80))
                }
                for number in response.get('objects', [])
            ]
            
        except Exception as e:
            logger.error(f"Error listing available Plivo numbers: {e}")
            raise
    
    def purchase_number(self, credentials: Dict[str, str], 
                       phone_number: str, 
                       capabilities: List[str]) -> Dict[str, Any]:
        """Purchase a phone number"""
        if not self.enabled:
            return self._mock_purchase_result(phone_number)
        
        try:
            import plivo
            
            client = plivo.RestClient(credentials['auth_id'], credentials['auth_token'])
            
            # Purchase the number
            response = client.phone_numbers.buy(number=phone_number)
            
            return {
                'number_id': response.get('number'),
                'phone_number': phone_number,
                'friendly_name': phone_number,
                'monthly_cost': 0.80,  # Plivo standard rate
                'status': response.get('status', 'active')
            }
            
        except Exception as e:
            logger.error(f"Error purchasing Plivo number {phone_number}: {e}")
            raise
    
    def list_owned_numbers(self, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """List phone numbers owned by the account"""
        if not self.enabled:
            return self._mock_owned_numbers()
        
        try:
            import plivo
            
            client = plivo.RestClient(credentials['auth_id'], credentials['auth_token'])
            
            response = client.phone_numbers.list()
            
            return [
                {
                    'phone_number': number['number'],
                    'friendly_name': number['number'],
                    'capabilities': {
                        'voice': number.get('voice_enabled', True),
                        'sms': number.get('sms_enabled', True),
                        'mms': number.get('mms_enabled', False)
                    },
                    'status': number.get('status', 'active'),
                    'provider_number_id': number['number'],
                    'monthly_cost': float(number.get('monthly_rental_rate', 0.80)),
                    'number_type': number.get('type', 'local')
                }
                for number in response.get('objects', [])
            ]
            
        except Exception as e:
            logger.error(f"Error listing owned Plivo numbers: {e}")
            raise
    
    def release_number(self, credentials: Dict[str, str], phone_number: str) -> bool:
        """Release a phone number"""
        if not self.enabled:
            return True  # Mock success
        
        try:
            import plivo
            
            client = plivo.RestClient(credentials['auth_id'], credentials['auth_token'])
            
            # Release the number
            response = client.phone_numbers.delete(number=phone_number)
            
            return response.get('status_code') == 204
                
        except Exception as e:
            logger.error(f"Error releasing Plivo number {phone_number}: {e}")
            raise
    
    def _mock_available_numbers(self) -> List[Dict[str, Any]]:
        """Mock available numbers for development"""
        return [
            {
                'phone_number': '+14155553001',
                'friendly_name': '+14155553001',
                'region': 'CA',
                'iso_country': 'US',
                'capabilities': {'voice': True, 'sms': True, 'mms': False},
                'monthly_cost': 0.80
            },
            {
                'phone_number': '+14155553002',
                'friendly_name': '+14155553002',
                'region': 'CA',
                'iso_country': 'US',
                'capabilities': {'voice': True, 'sms': True, 'mms': False},
                'monthly_cost': 0.80
            }
        ]
    
    def _mock_owned_numbers(self) -> List[Dict[str, Any]]:
        """Mock owned numbers for development"""
        return [
            {
                'phone_number': '+14155558888',
                'friendly_name': '+14155558888',
                'capabilities': {'voice': True, 'sms': True, 'mms': False},
                'status': 'active',
                'provider_number_id': '+14155558888',
                'monthly_cost': 0.80,
                'number_type': 'local'
            }
        ]
    
    def _mock_purchase_result(self, phone_number: str) -> Dict[str, Any]:
        """Mock purchase result for development"""
        return {
            'number_id': phone_number,
            'phone_number': phone_number,
            'friendly_name': phone_number,
            'monthly_cost': 0.80,
            'status': 'active'
        }


plivo_service = PlivoService()