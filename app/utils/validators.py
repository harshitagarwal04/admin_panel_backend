import re
from typing import Optional
from datetime import time


def validate_phone_e164(phone: str) -> bool:
    """Validate phone number in E.164 format"""
    return bool(re.match(r'^\+[1-9]\d{1,14}$', phone))


def validate_business_hours(start_time: Optional[time], end_time: Optional[time]) -> bool:
    """Validate business hours format"""
    if not start_time or not end_time:
        return True  # Optional fields
    
    return start_time < end_time


def validate_call_flow_settings(max_attempts: int, retry_delay: int, max_duration: int) -> bool:
    """Validate call flow configuration ranges"""
    return (
        1 <= max_attempts <= 10 and
        15 <= retry_delay <= 480 and
        5 <= max_duration <= 60
    )