from sqlalchemy import Column, String, ForeignKey, Text, Integer, JSON, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class InteractionAttempt(BaseModel):
    __tablename__ = "interaction_attempts"
    
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)
    status = Column(String(20))
    outcome = Column(String(20))
    summary = Column(Text)
    duration_seconds = Column(Integer)
    transcript_url = Column(String(500))
    raw_webhook_data = Column(JSON)
    retell_call_id = Column(String(255))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'failed')", name="check_attempt_status"),
        CheckConstraint("outcome IN ('answered', 'no_answer', 'failed')", name="check_attempt_outcome"),
    )
    
    # Relationships
    lead = relationship("Lead", back_populates="interaction_attempts")
    agent = relationship("Agent", back_populates="interaction_attempts")