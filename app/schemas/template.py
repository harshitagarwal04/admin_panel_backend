from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Optional, Union
import uuid


class TemplateResponse(BaseModel):
    id: Union[str, uuid.UUID]
    industry: str
    use_case: str
    name: str
    prompt: str
    variables: List[str]
    functions: List[str]
    welcome_message: Optional[str]
    suggested_settings: Dict[str, Any]
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    templates: List[TemplateResponse]
    total: int


class IndustryResponse(BaseModel):
    industry: str
    templates: List[TemplateResponse]