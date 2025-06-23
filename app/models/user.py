from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)  # Allow null for onboarding flow
    phone = Column(String(50), nullable=True)
    google_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Relationships
    companies = relationship("Company", foreign_keys="Company.admin_user_id", back_populates="admin_user")
    created_agents = relationship("Agent", foreign_keys="Agent.created_by", back_populates="creator")
    updated_agents = relationship("Agent", foreign_keys="Agent.updated_by", back_populates="updater")
    created_leads = relationship("Lead", foreign_keys="Lead.created_by", back_populates="creator")
    updated_leads = relationship("Lead", foreign_keys="Lead.updated_by", back_populates="updater")