from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Union
import uuid


class GoogleTokenRequest(BaseModel):
    token: str


class TestLoginRequest(BaseModel):
    email: EmailStr


class UserProfileUpdate(BaseModel):
    name: str
    phone: Optional[str] = None
    company_name: str


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    google_id: str


class UserResponse(BaseModel):
    id: Union[str, uuid.UUID]
    email: str
    name: Optional[str]
    phone: Optional[str]
    is_profile_complete: bool
    has_company: bool
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class CompanyCreate(BaseModel):
    name: str


class CompanyResponse(BaseModel):
    id: Union[str, uuid.UUID]
    name: str
    max_agents_limit: int
    max_concurrent_calls: int
    total_minutes_limit: Optional[int]
    total_minutes_used: int
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v
    
    class Config:
        from_attributes = True