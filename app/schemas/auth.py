from pydantic import BaseModel, EmailStr
from typing import Optional


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
    id: str
    email: str
    name: Optional[str]
    phone: Optional[str]
    is_profile_complete: bool
    has_company: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class CompanyCreate(BaseModel):
    name: str


class CompanyResponse(BaseModel):
    id: str
    name: str
    max_agents_limit: int
    max_concurrent_calls: int
    total_minutes_limit: Optional[int]
    total_minutes_used: int
    
    class Config:
        from_attributes = True