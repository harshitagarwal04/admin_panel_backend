from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Company(BaseModel):
    __tablename__ = "companies"
    
    name = Column(String(255), nullable=False)
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    max_agents_limit = Column(Integer, default=100)
    max_concurrent_calls = Column(Integer, default=5)
    total_minutes_limit = Column(Integer)
    total_minutes_used = Column(Integer, default=0)
    settings = Column(JSON, default={})
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    admin_user = relationship("User", foreign_keys=[admin_user_id], back_populates="companies")
    agents = relationship("Agent", back_populates="company")
    phone_providers = relationship("PhoneProvider", back_populates="company")
    api_keys = relationship("ApiKey", back_populates="company")