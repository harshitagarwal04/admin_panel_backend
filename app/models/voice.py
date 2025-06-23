from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Voice(BaseModel):
    __tablename__ = "voices"
    
    name = Column(String(100), nullable=False)
    language = Column(String(50), nullable=False)
    gender = Column(String(20), nullable=False)
    voice_provider_id = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    agents = relationship("Agent", back_populates="voice")