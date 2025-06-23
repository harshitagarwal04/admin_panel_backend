from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class InteractionAttemptResponse(BaseModel):
    id: str
    lead_id: str
    agent_id: str
    attempt_number: int
    status: Optional[str]
    outcome: Optional[str]
    summary: Optional[str]
    duration_seconds: Optional[int]
    transcript_url: Optional[str]
    retell_call_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    lead_name: Optional[str]
    lead_phone: Optional[str]
    agent_name: Optional[str]
    
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