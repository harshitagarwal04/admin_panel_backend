from sqlalchemy import Column, String, ForeignKey, JSON, Integer, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Lead(BaseModel):
    __tablename__ = "leads"
    
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    first_name = Column(String(255), nullable=False)
    phone_e164 = Column(String(50), nullable=False, index=True)
    status = Column(String(20), default="new", nullable=False, index=True)
    custom_fields = Column(JSON, default={})
    schedule_at = Column(DateTime, nullable=False, index=True)
    attempts_count = Column(Integer, default=0)
    disposition = Column(String(50))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('new', 'in_progress', 'done')", name="check_lead_status"),
        CheckConstraint("disposition IN ('not_interested', 'hung_up', 'completed', 'no_answer')", name="check_lead_disposition"),
        UniqueConstraint("agent_id", "phone_e164", name="uq_agent_phone"),
    )
    
    # Relationships
    agent = relationship("Agent", back_populates="leads")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_leads")
    updater = relationship("User", foreign_keys=[updated_by], back_populates="updated_leads")
    interaction_attempts = relationship("InteractionAttempt", back_populates="lead")