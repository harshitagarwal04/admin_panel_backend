from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class TemplateResponse(BaseModel):
    id: str
    industry: str
    use_case: str
    name: str
    prompt: str
    variables: List[str]
    functions: List[str]
    welcome_message: Optional[str]
    suggested_settings: Dict[str, Any]
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    templates: List[TemplateResponse]
    total: int


class IndustryResponse(BaseModel):
    industry: str
    templates: List[TemplateResponse]