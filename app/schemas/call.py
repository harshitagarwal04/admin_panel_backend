from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import uuid


class InteractionAttemptResponse(BaseModel):
    id: Union[str, uuid.UUID]
    lead_id: Union[str, uuid.UUID]
    agent_id: Union[str, uuid.UUID]
    attempt_number: int
    status: Optional[str]
    outcome: Optional[str]
    summary: Optional[str]
    duration_seconds: Optional[int]
    transcript_url: Optional[str]
    retell_call_id: Optional[str]
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]
    
    # Related data
    lead_name: Optional[str]
    lead_phone: Optional[str]
    agent_name: Optional[str]
    
    @field_validator('id', 'lead_id', 'agent_id', mode='before')
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


class CallHistoryResponse(BaseModel):
    calls: List[InteractionAttemptResponse]
    total: int
    page: int
    per_page: int


class CallMetrics(BaseModel):
    total_calls: int
    answered_calls: int
    no_answer_calls: int
    failed_calls: int
    pickup_rate: float
    average_attempts_per_lead: float
    active_agents: int


class CallScheduleRequest(BaseModel):
    lead_id: str


class WebhookPayload(BaseModel):
    call_id: str
    agent_id: str
    call_type: str
    call_status: str
    outcome: Optional[str]
    duration_seconds: Optional[int]
    recording_url: Optional[str]
    transcript: Optional[str]
    summary: Optional[str]
    metadata: Optional[Dict[str, Any]]