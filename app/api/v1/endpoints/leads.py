from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
import csv
import io
from app.db.deps import get_db, get_current_user
from app.schemas.lead import (
    LeadCreate, LeadUpdate, LeadResponse, LeadListResponse, 
    CSVImportRequest, CSVImportResponse
)
from app.models.user import User
from app.models.company import Company
from app.models.agent import Agent
from app.models.lead import Lead
from app.services.phone_service import phone_service
import uuid

router = APIRouter()


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


def get_agent_by_id(db: Session, agent_id: str, company_id: str) -> Agent:
    """Get agent by ID within company scope"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.company_id == company_id,
        Agent.is_deleted == False
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    agent = get_agent_by_id(db, lead_data.agent_id, str(company.id))
    
    # Normalize phone number
    normalized_phone = phone_service.normalize_phone(lead_data.phone_e164)
    if not normalized_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format"
        )
    
    # Check for duplicates
    existing_lead = db.query(Lead).filter(
        Lead.agent_id == agent.id,
        Lead.phone_e164 == normalized_phone,
        Lead.is_deleted == False
    ).first()
    
    if existing_lead:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lead with this phone number already exists for this agent"
        )
    
    # Create lead
    lead = Lead(
        agent_id=uuid.UUID(lead_data.agent_id),
        first_name=lead_data.first_name,
        phone_e164=normalized_phone,
        custom_fields=lead_data.custom_fields or {},
        schedule_at=lead_data.schedule_at or datetime.utcnow(),
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return lead


@router.get("/", response_model=LeadListResponse)
async def list_leads(
    agent_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, pattern="^(new|in_progress|done)$"),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    # Base query - only leads for agents in this company
    query = db.query(Lead).join(Agent).filter(
        Agent.company_id == company.id,
        Agent.is_deleted == False,
        Lead.is_deleted == False
    )
    
    # Apply filters
    if agent_id:
        query = query.filter(Lead.agent_id == agent_id)
    
    if status_filter:
        query = query.filter(Lead.status == status_filter)
    
    if search:
        query = query.filter(
            or_(
                Lead.first_name.ilike(f"%{search}%"),
                Lead.phone_e164.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    leads = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return LeadListResponse(
        leads=leads,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    lead = db.query(Lead).join(Agent).filter(
        Lead.id == lead_id,
        Agent.company_id == company.id,
        Agent.is_deleted == False,
        Lead.is_deleted == False
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    lead = db.query(Lead).join(Agent).filter(
        Lead.id == lead_id,
        Agent.company_id == company.id,
        Agent.is_deleted == False,
        Lead.is_deleted == False
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Update fields that are provided
    update_data = lead_data.dict(exclude_unset=True)
    
    # Normalize phone if provided
    if 'phone_e164' in update_data:
        normalized_phone = phone_service.normalize_phone(update_data['phone_e164'])
        if not normalized_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )
        update_data['phone_e164'] = normalized_phone
    
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    lead.updated_by = current_user.id
    
    db.commit()
    db.refresh(lead)
    
    return lead


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    lead = db.query(Lead).join(Agent).filter(
        Lead.id == lead_id,
        Agent.company_id == company.id,
        Agent.is_deleted == False,
        Lead.is_deleted == False
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Soft delete
    lead.is_deleted = True
    lead.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Lead deleted"}


@router.post("/csv-import", response_model=CSVImportResponse)
async def import_leads_csv(
    file: UploadFile = File(...),
    agent_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    agent = get_agent_by_id(db, agent_id, str(company.id))
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Read CSV content
    try:
        content = await file.read()
        csv_data = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        success_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
            try:
                # Extract required fields
                first_name = row.get('first_name', '').strip()
                phone = row.get('phone', '').strip()
                
                if not first_name or not phone:
                    errors.append({
                        "row": row_num,
                        "error": "Missing required fields: first_name or phone"
                    })
                    error_count += 1
                    continue
                
                # Normalize phone
                normalized_phone = phone_service.normalize_phone(phone)
                if not normalized_phone:
                    errors.append({
                        "row": row_num,
                        "error": f"Invalid phone number format: {phone}"
                    })
                    error_count += 1
                    continue
                
                # Check for duplicates
                existing_lead = db.query(Lead).filter(
                    Lead.agent_id == agent.id,
                    Lead.phone_e164 == normalized_phone,
                    Lead.is_deleted == False
                ).first()
                
                if existing_lead:
                    errors.append({
                        "row": row_num,
                        "error": f"Duplicate phone number: {normalized_phone}"
                    })
                    error_count += 1
                    continue
                
                # Extract custom fields (all other columns)
                custom_fields = {}
                for key, value in row.items():
                    if key not in ['first_name', 'phone', 'schedule_at'] and value:
                        custom_fields[key] = value
                
                # Parse schedule_at if provided
                schedule_at = datetime.utcnow()
                if row.get('schedule_at'):
                    try:
                        schedule_at = datetime.fromisoformat(row['schedule_at'])
                    except ValueError:
                        pass  # Use default if invalid format
                
                # Create lead
                lead = Lead(
                    agent_id=agent.id,
                    first_name=first_name,
                    phone_e164=normalized_phone,
                    custom_fields=custom_fields,
                    schedule_at=schedule_at,
                    created_by=current_user.id,
                    updated_by=current_user.id
                )
                
                db.add(lead)
                success_count += 1
                
            except Exception as e:
                errors.append({
                    "row": row_num,
                    "error": str(e)
                })
                error_count += 1
        
        # Commit all successful leads
        if success_count > 0:
            db.commit()
        
        return CSVImportResponse(
            success_count=success_count,
            error_count=error_count,
            errors=errors,
            total_processed=success_count + error_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV file: {str(e)}"
        )