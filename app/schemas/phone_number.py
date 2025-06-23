from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid


class PhoneProviderCreate(BaseModel):
    provider: str = Field(..., description="Provider name: twilio or plivo")
    credentials: Dict[str, str] = Field(..., description="Provider credentials")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v):
        if v not in ['twilio', 'plivo']:
            raise ValueError('Provider must be either "twilio" or "plivo"')
        return v


class PhoneProviderUpdate(BaseModel):
    credentials: Dict[str, str] = Field(..., description="Updated provider credentials")


class PhoneProviderResponse(BaseModel):
    id: Union[str, uuid.UUID]
    company_id: Union[str, uuid.UUID]
    provider: str
    credentials: Dict[str, str]  # Note: In production, this should be masked
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]
    
    @field_validator('id', 'company_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v
    
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def convert_datetime_to_str(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    class Config:
        from_attributes = True


class PhoneNumberCreate(BaseModel):
    phone_number: str = Field(..., description="Phone number to purchase")
    provider: str = Field(..., description="Provider name: twilio or plivo")
    capabilities: List[str] = Field(
        default=["voice"], 
        description="Number capabilities: voice, sms, mms"
    )
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v):
        if v not in ['twilio', 'plivo']:
            raise ValueError('Provider must be either "twilio" or "plivo"')
        return v
    
    @field_validator('capabilities')
    @classmethod
    def validate_capabilities(cls, v):
        valid_capabilities = ['voice', 'sms', 'mms']
        for cap in v:
            if cap not in valid_capabilities:
                raise ValueError(f'Invalid capability: {cap}. Must be one of {valid_capabilities}')
        return v


class PhoneNumberResponse(BaseModel):
    phone_number: str
    provider: str
    capabilities: List[str]
    status: str = "active"
    provider_number_id: Optional[str] = None
    monthly_cost: Optional[float] = None
    friendly_name: Optional[str] = None
    country_code: Optional[str] = None
    number_type: Optional[str] = None  # local, toll-free, mobile
    
    class Config:
        from_attributes = True


class PhoneNumberListResponse(BaseModel):
    numbers: List[PhoneNumberResponse]
    total: int
    provider: str


class AvailableNumberSearch(BaseModel):
    country_code: str = Field(default="US", description="Country code for number search")
    area_code: Optional[str] = Field(None, description="Specific area code")
    contains: Optional[str] = Field(None, description="Pattern the number should contain")
    number_type: str = Field(default="local", description="Type: local, toll-free, mobile")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results to return")
    
    @field_validator('number_type')
    @classmethod
    def validate_number_type(cls, v):
        if v not in ['local', 'toll-free', 'mobile']:
            raise ValueError('number_type must be one of: local, toll-free, mobile')
        return v


# For displaying numbers in agent lists and dashboard
class AgentPhoneNumberInfo(BaseModel):
    inbound_phone: Optional[str] = None
    outbound_phone: Optional[str] = None
    inbound_provider: Optional[str] = None
    outbound_provider: Optional[str] = None
    phone_number_status: str = "not_configured"  # not_configured, partial, complete
    
    class Config:
        from_attributes = True