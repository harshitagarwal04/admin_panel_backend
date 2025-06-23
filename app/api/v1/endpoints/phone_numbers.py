from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.deps import get_db, get_current_user
from app.schemas.phone_number import (
    PhoneProviderCreate, PhoneProviderUpdate, PhoneProviderResponse,
    PhoneNumberCreate, PhoneNumberResponse, PhoneNumberListResponse
)
from app.models.user import User
from app.models.company import Company
from app.models.phone_provider import PhoneProvider
from app.services.phone_service import phone_service
from app.services.twilio_service import twilio_service
from app.services.plivo_service import plivo_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def get_user_company(db: Session, user: User) -> Company:
    """Get the user's company or raise 404"""
    company = db.query(Company).filter(
        Company.admin_user_id == user.id,
        Company.is_deleted == False
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


@router.post("/providers", response_model=PhoneProviderResponse)
async def create_phone_provider(
    provider_data: PhoneProviderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add or update phone provider credentials for the company"""
    company = get_user_company(db, current_user)
    
    # Check if provider already exists for this company
    existing_provider = db.query(PhoneProvider).filter(
        PhoneProvider.company_id == company.id,
        PhoneProvider.provider == provider_data.provider,
        PhoneProvider.is_deleted == False
    ).first()
    
    if existing_provider:
        # Update existing provider
        existing_provider.credentials = provider_data.credentials
        db.commit()
        db.refresh(existing_provider)
        return existing_provider
    else:
        # Create new provider
        phone_provider = PhoneProvider(
            company_id=company.id,
            provider=provider_data.provider,
            credentials=provider_data.credentials,
            created_by=current_user.id
        )
        db.add(phone_provider)
        db.commit()
        db.refresh(phone_provider)
        return phone_provider


@router.get("/providers", response_model=List[PhoneProviderResponse])
async def list_phone_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all phone providers configured for the company"""
    company = get_user_company(db, current_user)
    
    providers = db.query(PhoneProvider).filter(
        PhoneProvider.company_id == company.id,
        PhoneProvider.is_deleted == False
    ).all()
    
    return providers


@router.delete("/providers/{provider}")
async def delete_phone_provider(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove phone provider credentials"""
    company = get_user_company(db, current_user)
    
    provider_record = db.query(PhoneProvider).filter(
        PhoneProvider.company_id == company.id,
        PhoneProvider.provider == provider,
        PhoneProvider.is_deleted == False
    ).first()
    
    if not provider_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone provider not found"
        )
    
    provider_record.is_deleted = True
    db.commit()
    
    return {"message": f"{provider} provider removed"}


@router.get("/available", response_model=PhoneNumberListResponse)
async def list_available_phone_numbers(
    provider: str = Query(..., description="Provider name (twilio or plivo)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List available phone numbers from the provider"""
    company = get_user_company(db, current_user)
    
    # Check if provider credentials exist
    provider_record = db.query(PhoneProvider).filter(
        PhoneProvider.company_id == company.id,
        PhoneProvider.provider == provider,
        PhoneProvider.is_deleted == False
    ).first()
    
    if not provider_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {provider} credentials found. Please add provider credentials first."
        )
    
    try:
        if provider == "twilio":
            numbers = twilio_service.list_available_numbers(provider_record.credentials)
        elif provider == "plivo":
            numbers = plivo_service.list_available_numbers(provider_record.credentials)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid provider. Use 'twilio' or 'plivo'"
            )
        
        return PhoneNumberListResponse(
            numbers=numbers,
            total=len(numbers),
            provider=provider
        )
        
    except Exception as e:
        logger.error(f"Error fetching available numbers from {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch numbers from {provider}: {str(e)}"
        )


@router.post("/purchase", response_model=PhoneNumberResponse)
async def purchase_phone_number(
    number_data: PhoneNumberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Purchase a phone number from the provider"""
    company = get_user_company(db, current_user)
    
    # Check if provider credentials exist
    provider_record = db.query(PhoneProvider).filter(
        PhoneProvider.company_id == company.id,
        PhoneProvider.provider == number_data.provider,
        PhoneProvider.is_deleted == False
    ).first()
    
    if not provider_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {number_data.provider} credentials found"
        )
    
    # Validate phone number format
    normalized_number = phone_service.normalize_phone(number_data.phone_number)
    if not normalized_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format"
        )
    
    try:
        if number_data.provider == "twilio":
            result = twilio_service.purchase_number(
                provider_record.credentials,
                normalized_number,
                number_data.capabilities
            )
        elif number_data.provider == "plivo":
            result = plivo_service.purchase_number(
                provider_record.credentials,
                normalized_number,
                number_data.capabilities
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid provider"
            )
        
        # Return the purchased number details
        return PhoneNumberResponse(
            phone_number=normalized_number,
            provider=number_data.provider,
            capabilities=number_data.capabilities,
            status="active",
            provider_number_id=result.get("sid") or result.get("number_id"),
            monthly_cost=result.get("monthly_cost", 0.0)
        )
        
    except Exception as e:
        logger.error(f"Error purchasing number from {number_data.provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to purchase number: {str(e)}"
        )


@router.get("/owned", response_model=PhoneNumberListResponse)
async def list_owned_phone_numbers(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all phone numbers owned by the company"""
    company = get_user_company(db, current_user)
    
    # Get all provider credentials for the company
    providers = db.query(PhoneProvider).filter(
        PhoneProvider.company_id == company.id,
        PhoneProvider.is_deleted == False
    ).all()
    
    if provider:
        providers = [p for p in providers if p.provider == provider]
    
    all_numbers = []
    
    for provider_record in providers:
        try:
            if provider_record.provider == "twilio":
                numbers = twilio_service.list_owned_numbers(provider_record.credentials)
            elif provider_record.provider == "plivo":
                numbers = plivo_service.list_owned_numbers(provider_record.credentials)
            else:
                continue
            
            # Add provider info to each number
            for number in numbers:
                number["provider"] = provider_record.provider
            
            all_numbers.extend(numbers)
            
        except Exception as e:
            logger.error(f"Error fetching owned numbers from {provider_record.provider}: {e}")
            # Continue with other providers if one fails
            continue
    
    return PhoneNumberListResponse(
        numbers=all_numbers,
        total=len(all_numbers),
        provider=provider or "all"
    )


@router.delete("/{phone_number}")
async def release_phone_number(
    phone_number: str,
    provider: str = Query(..., description="Provider name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Release a phone number back to the provider"""
    company = get_user_company(db, current_user)
    
    # Check if provider credentials exist
    provider_record = db.query(PhoneProvider).filter(
        PhoneProvider.company_id == company.id,
        PhoneProvider.provider == provider,
        PhoneProvider.is_deleted == False
    ).first()
    
    if not provider_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {provider} credentials found"
        )
    
    # Normalize phone number
    normalized_number = phone_service.normalize_phone(phone_number)
    if not normalized_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format"
        )
    
    try:
        if provider == "twilio":
            success = twilio_service.release_number(provider_record.credentials, normalized_number)
        elif provider == "plivo":
            success = plivo_service.release_number(provider_record.credentials, normalized_number)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid provider"
            )
        
        if success:
            return {"message": f"Phone number {normalized_number} released successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to release phone number"
            )
            
    except Exception as e:
        logger.error(f"Error releasing number from {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to release number: {str(e)}"
        )