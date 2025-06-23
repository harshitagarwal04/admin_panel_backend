from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db, get_current_user
from app.schemas.auth import GoogleTokenRequest, TestLoginRequest, UserProfileUpdate, Token, UserResponse, CompanyCreate, CompanyResponse
from app.services.google_auth import google_auth_service
from app.core.security import create_access_token
from app.core.config import settings
from app.models.user import User
from app.models.company import Company
import hashlib

router = APIRouter()


@router.post("/google-login", response_model=Token)
async def google_login(
    request: GoogleTokenRequest,
    db: Session = Depends(get_db)
):
    # Verify Google token
    user_info = google_auth_service.verify_token(request.token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    # Check if user exists
    user = db.query(User).filter(
        User.google_id == user_info["google_id"],
        User.is_deleted == False
    ).first()
    
    if not user:
        # Create new user
        user = User(
            email=user_info["email"],
            name=user_info["name"],
            google_id=user_info["google_id"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate JWT token
    access_token = create_access_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/test-login", response_model=Token)
async def test_login(
    request: TestLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Test login endpoint for development - bypasses Google OAuth
    Only creates user with email, name/phone collected later
    """
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test login only available in development"
        )
    
    # Generate a fake google_id from email for testing
    fake_google_id = hashlib.md5(request.email.encode()).hexdigest()
    
    # Check if user exists
    user = db.query(User).filter(
        User.email == request.email,
        User.is_deleted == False
    ).first()
    
    if not user:
        # Create new user with email only (Google OAuth style)
        user = User(
            email=request.email,
            name=None,  # Will be collected in onboarding
            phone=None,  # Will be collected in onboarding
            google_id=fake_google_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate JWT token
    access_token = create_access_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user has completed profile
    is_profile_complete = bool(current_user.name)
    
    # Check if user has a company
    has_company = db.query(Company).filter(
        Company.admin_user_id == current_user.id,
        Company.is_deleted == False
    ).first() is not None
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "phone": current_user.phone,
        "is_profile_complete": is_profile_complete,
        "has_company": has_company
    }


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete user onboarding - update profile AND create company
    This is the single onboarding step after login
    """
    # Update user profile
    current_user.name = profile_data.name
    current_user.phone = profile_data.phone
    
    # Check if user already has a company
    existing_company = db.query(Company).filter(
        Company.admin_user_id == current_user.id,
        Company.is_deleted == False
    ).first()
    
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a company"
        )
    
    # Create company
    company = Company(
        name=profile_data.company_name,
        admin_user_id=current_user.id,
        created_by=current_user.id
    )
    db.add(company)
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "phone": current_user.phone,
        "is_profile_complete": True,
        "has_company": True
    }


@router.post("/company", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user already has a company
    existing_company = db.query(Company).filter(
        Company.admin_user_id == current_user.id,
        Company.is_deleted == False
    ).first()
    
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a company"
        )
    
    # Create new company
    company = Company(
        name=company_data.name,
        admin_user_id=current_user.id,
        created_by=current_user.id
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return company


@router.get("/company", response_model=CompanyResponse)
async def get_user_company(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = db.query(Company).filter(
        Company.admin_user_id == current_user.id,
        Company.is_deleted == False
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company