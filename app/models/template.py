from sqlalchemy import Column, String, Text, JSON
from .base import BaseModel


class Template(BaseModel):
    __tablename__ = "templates"
    
    industry = Column(String(100), nullable=False)
    use_case = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    variables = Column(JSON, default=[])
    functions = Column(JSON, default=[])
    welcome_message = Column(Text)
    suggested_settings = Column(JSON, default={})