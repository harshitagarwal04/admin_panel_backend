from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import re
import uuid


class LeadCreate(BaseModel):
    agent_id: str
    first_name: str = Field(..., min_length=1, max_length=255)
    phone_e164: str = Field(..., min_length=1, max_length=50)
    custom_fields: Optional[Dict[str, Any]] = {}
    schedule_at: Optional[datetime] = None
    
    @validator('phone_e164')
    def validate_phone(cls, v):
        # Basic E.164 format validation
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone number must be in E.164 format')
        return v


class LeadUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_e164: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[str] = Field(None, pattern="^(new|in_progress|done)$")
    custom_fields: Optional[Dict[str, Any]] = None
    schedule_at: Optional[datetime] = None
    disposition: Optional[str] = Field(None, pattern="^(not_interested|hung_up|completed|no_answer)$")
    
    @validator('phone_e164')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone number must be in E.164 format')
        return v


class LeadResponse(BaseModel):
    id: Union[str, uuid.UUID]
    agent_id: Union[str, uuid.UUID]
    first_name: str
    phone_e164: str
    status: str
    custom_fields: Dict[str, Any]
    schedule_at: Union[str, datetime]
    attempts_count: int
    disposition: Optional[str]
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]
    
    @field_validator('id', 'agent_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v
    
    @field_validator('schedule_at', 'created_at', 'updated_at', mode='before')
    @classmethod
    def convert_datetime_to_str(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    page: int
    per_page: int


class CSVImportRequest(BaseModel):
    agent_id: str
    column_mapping: Dict[str, str]  # CSV column -> field mapping
    data: List[Dict[str, str]]  # CSV rows


class CSVImportResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, str]]
    total_processed: int