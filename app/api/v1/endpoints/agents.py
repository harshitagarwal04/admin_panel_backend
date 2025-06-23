from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.deps import get_db, get_current_user, get_user_company
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentListResponse, VoiceResponse
from app.models.user import User
from app.models.company import Company
from app.models.agent import Agent
from app.models.voice import Voice
from app.services.retell_service import retell_service
import uuid
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


@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Creating agent with data: {agent_data.dict()}")
    company = get_user_company(db, current_user)
    
    # Check agent limit
    agent_count = db.query(Agent).filter(
        Agent.company_id == company.id,
        Agent.is_deleted == False
    ).count()
    
    if agent_count >= company.max_agents_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent limit reached"
        )
    
    # In template-based mode, get master agent ID for reference
    retell_data = {
        "name": agent_data.name,
        "prompt": agent_data.prompt,
        "welcome_message": agent_data.welcome_message,
        "voice_id": agent_data.voice_id
    }
    
    retell_agent_id = retell_service.create_agent(retell_data)
    # Note: This now returns master template agent ID, not individual agent ID
    
    # Create agent in database
    try:
        agent = Agent(
            company_id=company.id,
            name=agent_data.name,
            prompt=agent_data.prompt,
            variables=agent_data.variables or {},
            welcome_message=agent_data.welcome_message,
            voice_id=uuid.UUID(agent_data.voice_id) if agent_data.voice_id else None,
            functions=agent_data.functions or [],
            inbound_phone=agent_data.inbound_phone,
            outbound_phone=agent_data.outbound_phone,
            max_attempts=agent_data.max_attempts,
            retry_delay_minutes=agent_data.retry_delay_minutes,
            business_hours_start=agent_data.business_hours_start,
            business_hours_end=agent_data.business_hours_end,
            timezone=agent_data.timezone,
            max_call_duration_minutes=agent_data.max_call_duration_minutes,
            retell_agent_id=retell_agent_id,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        logger.info(f"Agent created successfully: {agent.id}")
        
        # Debug: Check what we're returning
        logger.debug(f"Returning agent with voice_id type: {type(agent.voice_id)}, value: {agent.voice_id}")
        logger.debug(f"Agent dict: {agent.__dict__}")
        
        return agent
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}", exc_info=True)
        db.rollback()
        # If it's a foreign key error, provide a helpful message
        if "foreign key constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reference in request. Please check voice_id exists. Error: {str(e)}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, pattern="^(active|inactive)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    query = db.query(Agent).filter(
        Agent.company_id == company.id,
        Agent.is_deleted == False
    )
    
    if status_filter:
        query = query.filter(Agent.status == status_filter)
    
    total = query.count()
    agents = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Add phone status to each agent
    agent_responses = []
    for agent in agents:
        agent_dict = agent.__dict__.copy()
        
        # Compute phone status
        has_inbound = bool(agent.inbound_phone)
        has_outbound = bool(agent.outbound_phone)
        
        if has_inbound and has_outbound:
            agent_dict['phone_status'] = 'complete'
            agent_dict['phone_numbers_configured'] = True
        elif has_inbound or has_outbound:
            agent_dict['phone_status'] = 'partial'
            agent_dict['phone_numbers_configured'] = True
        else:
            agent_dict['phone_status'] = 'not_configured'
            agent_dict['phone_numbers_configured'] = False
        
        agent_responses.append(agent_dict)
    
    return AgentListResponse(
        agents=agent_responses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.company_id == company.id,
        Agent.is_deleted == False
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.company_id == company.id,
        Agent.is_deleted == False
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Update fields that are provided
    update_data = agent_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    agent.updated_by = current_user.id
    
    # In template-based mode, agent updates are applied per-call via dynamic variables
    # No need to update Retell agent directly
    logger.info(f"Agent {agent_id} updated - changes will be applied per-call via template variables")
    
    db.commit()
    db.refresh(agent)
    
    return agent


@router.patch("/{agent_id}/status")
async def toggle_agent_status(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.company_id == company.id,
        Agent.is_deleted == False
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Toggle status
    agent.status = "inactive" if agent.status == "active" else "active"
    agent.updated_by = current_user.id
    
    db.commit()
    
    return {"status": agent.status}


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.company_id == company.id,
        Agent.is_deleted == False
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Soft delete
    agent.is_deleted = True
    agent.updated_by = current_user.id
    
    # In template-based mode, no individual agents to delete from Retell
    logger.info(f"Agent {agent_id} soft deleted from database")
    
    db.commit()
    
    return {"message": "Agent deleted"}


@router.get("/voices/", response_model=List[VoiceResponse])
async def list_voices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    voices = db.query(Voice).filter(Voice.is_active == True).all()
    return voices