from sqlalchemy import Column, String, ForeignKey, JSON, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class PhoneProvider(BaseModel):
    __tablename__ = "phone_providers"
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    provider = Column(String(20), nullable=False)
    credentials = Column(JSON, nullable=False)  # Should be encrypted in production
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("provider IN ('twilio', 'plivo')", name="check_provider_type"),
        UniqueConstraint("company_id", "provider", name="uq_company_provider"),
    )
    
    # Relationships
    company = relationship("Company", back_populates="phone_providers")