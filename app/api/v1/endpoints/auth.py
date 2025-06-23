from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db, get_current_user
from app.schemas.auth import GoogleTokenRequest, Token, UserResponse, CompanyCreate, CompanyResponse
from app.services.google_auth import google_auth_service
from app.core.security import create_access_token
from app.models.user import User
from app.models.company import Company

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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user


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