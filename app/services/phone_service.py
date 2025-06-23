import re
import phonenumbers
from phonenumbers import PhoneNumberFormat
from typing import Optional


class PhoneService:
    @staticmethod
    def normalize_phone(phone: str, country_code: str = "US") -> Optional[str]:
        """Normalize phone number to E.164 format"""
        try:
            # Parse the phone number
            parsed = phonenumbers.parse(phone, country_code)
            
            # Check if it's valid
            if phonenumbers.is_valid_number(parsed):
                # Format to E.164
                return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
            else:
                return None
        except phonenumbers.NumberParseException:
            return None
    
    @staticmethod
    def is_valid_e164(phone: str) -> bool:
        """Check if phone number is in valid E.164 format"""
        return bool(re.match(r'^\+[1-9]\d{1,14}$', phone))


phone_service = PhoneService()