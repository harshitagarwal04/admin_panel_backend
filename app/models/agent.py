from sqlalchemy import Column, String, Text, ForeignKey, JSON, Integer, Time, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Agent(BaseModel):
    __tablename__ = "agents"
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(20), default="active", nullable=False)
    prompt = Column(Text, nullable=False)
    variables = Column(JSON, default={})
    welcome_message = Column(Text)
    voice_id = Column(UUID(as_uuid=True), ForeignKey("voices.id"))
    functions = Column(JSON, default=[])
    inbound_phone = Column(String(50))
    outbound_phone = Column(String(50))
    
    # Call Flow Configuration Fields
    max_attempts = Column(Integer, default=3)
    retry_delay_minutes = Column(Integer, default=30)
    business_hours_start = Column(Time)
    business_hours_end = Column(Time)
    timezone = Column(String(50), default="UTC")
    max_call_duration_minutes = Column(Integer, default=20)
    
    # Retell Integration Fields
    retell_agent_id = Column(String(255))
    retell_llm_id = Column(String(255))
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive')", name="check_agent_status"),
    )
    
    # Relationships
    company = relationship("Company", back_populates="agents")
    voice = relationship("Voice", back_populates="agents")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_agents")
    updater = relationship("User", foreign_keys=[updated_by], back_populates="updated_agents")
    leads = relationship("Lead", back_populates="agent")
    interaction_attempts = relationship("InteractionAttempt", back_populates="agent")