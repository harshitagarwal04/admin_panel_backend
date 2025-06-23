from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import time
import uuid


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    prompt: str = Field(..., min_length=1)
    variables: Optional[Dict[str, Any]] = {}
    welcome_message: Optional[str] = None
    voice_id: Optional[str] = None
    functions: Optional[List[str]] = []
    inbound_phone: Optional[str] = None
    outbound_phone: Optional[str] = None
    max_attempts: Optional[int] = Field(3, ge=1, le=10)
    retry_delay_minutes: Optional[int] = Field(30, ge=15, le=480)
    business_hours_start: Optional[time] = None
    business_hours_end: Optional[time] = None
    timezone: Optional[str] = "UTC"
    max_call_duration_minutes: Optional[int] = Field(20, ge=5, le=60)


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    prompt: Optional[str] = Field(None, min_length=1)
    variables: Optional[Dict[str, Any]] = None
    welcome_message: Optional[str] = None
    voice_id: Optional[str] = None
    functions: Optional[List[str]] = None
    inbound_phone: Optional[str] = None
    outbound_phone: Optional[str] = None
    max_attempts: Optional[int] = Field(None, ge=1, le=10)
    retry_delay_minutes: Optional[int] = Field(None, ge=15, le=480)
    business_hours_start: Optional[time] = None
    business_hours_end: Optional[time] = None
    timezone: Optional[str] = None
    max_call_duration_minutes: Optional[int] = Field(None, ge=5, le=60)


class AgentResponse(BaseModel):
    id: str
    company_id: str
    name: str
    status: str
    prompt: str
    variables: Dict[str, Any]
    welcome_message: Optional[str]
    voice_id: Optional[str]
    functions: List[str]
    inbound_phone: Optional[str]
    outbound_phone: Optional[str]
    max_attempts: int
    retry_delay_minutes: int
    business_hours_start: Optional[time]
    business_hours_end: Optional[time]
    timezone: str
    max_call_duration_minutes: int
    retell_agent_id: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    agents: List[AgentResponse]
    total: int
    page: int
    per_page: int


class VoiceResponse(BaseModel):
    id: str
    name: str
    language: str
    gender: str
    voice_provider_id: str
    is_active: bool
    
    class Config:
        from_attributes = True