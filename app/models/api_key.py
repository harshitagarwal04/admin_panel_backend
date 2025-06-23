from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class ApiKey(BaseModel):
    __tablename__ = "api_keys"
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    key_prefix = Column(String(10), nullable=False)
    key_hash = Column(String(255), nullable=False)  # Store hashed version
    name = Column(String(255))
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="api_keys")