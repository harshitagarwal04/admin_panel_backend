from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.db.deps import get_db, get_current_user
from app.schemas.call import (
    InteractionAttemptResponse, CallHistoryResponse, CallMetrics,
    CallScheduleRequest, WebhookPayload
)
from app.models.user import User
from app.models.company import Company
from app.models.agent import Agent
from app.models.lead import Lead
from app.models.interaction_attempt import InteractionAttempt
from app.services.call_scheduler import call_scheduler

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


@router.get("/history", response_model=CallHistoryResponse)
async def get_call_history(
    agent_id: Optional[str] = Query(None),
    outcome: Optional[str] = Query(None, pattern="^(answered|no_answer|failed)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    # Base query with joins
    query = db.query(
        InteractionAttempt,
        Lead.first_name.label("lead_name"),
        Lead.phone_e164.label("lead_phone"),
        Agent.name.label("agent_name")
    ).join(
        Lead, InteractionAttempt.lead_id == Lead.id
    ).join(
        Agent, InteractionAttempt.agent_id == Agent.id
    ).filter(
        Agent.company_id == company.id,
        Agent.is_deleted == False,
        Lead.is_deleted == False
    )
    
    # Apply filters
    if agent_id:
        query = query.filter(InteractionAttempt.agent_id == agent_id)
    
    if outcome:
        query = query.filter(InteractionAttempt.outcome == outcome)
    
    if start_date:
        query = query.filter(InteractionAttempt.created_at >= start_date)
    
    if end_date:
        query = query.filter(InteractionAttempt.created_at < end_date + timedelta(days=1))
    
    if search:
        query = query.filter(
            or_(
                Lead.first_name.ilike(f"%{search}%"),
                Lead.phone_e164.ilike(f"%{search}%"),
                Agent.name.ilike(f"%{search}%")
            )
        )
    
    # Order by creation date (newest first)
    query = query.order_by(desc(InteractionAttempt.created_at))
    
    total = query.count()
    results = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Format response
    calls = []
    for attempt, lead_name, lead_phone, agent_name in results:
        call_data = InteractionAttemptResponse(
            **attempt.__dict__,
            lead_name=lead_name,
            lead_phone=lead_phone,
            agent_name=agent_name
        )
        calls.append(call_data)
    
    return CallHistoryResponse(
        calls=calls,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/metrics", response_model=CallMetrics)
async def get_call_metrics(
    agent_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    # Base query
    query = db.query(InteractionAttempt).join(Agent).filter(
        Agent.company_id == company.id,
        Agent.is_deleted == False
    )
    
    # Apply filters
    if agent_id:
        query = query.filter(InteractionAttempt.agent_id == agent_id)
    
    if start_date:
        query = query.filter(InteractionAttempt.created_at >= start_date)
    
    if end_date:
        query = query.filter(InteractionAttempt.created_at < end_date + timedelta(days=1))
    
    # Calculate metrics
    total_calls = query.count()
    answered_calls = query.filter(InteractionAttempt.outcome == "answered").count()
    no_answer_calls = query.filter(InteractionAttempt.outcome == "no_answer").count()
    failed_calls = query.filter(InteractionAttempt.outcome == "failed").count()
    
    pickup_rate = (answered_calls / total_calls * 100) if total_calls > 0 else 0
    
    # Calculate average attempts per lead
    lead_attempts = db.query(
        Lead.id,
        func.count(InteractionAttempt.id).label("attempt_count")
    ).join(
        InteractionAttempt, Lead.id == InteractionAttempt.lead_id
    ).join(
        Agent, Lead.agent_id == Agent.id
    ).filter(
        Agent.company_id == company.id,
        Agent.is_deleted == False,
        Lead.is_deleted == False
    ).group_by(Lead.id).all()
    
    avg_attempts = sum(attempt.attempt_count for attempt in lead_attempts) / len(lead_attempts) if lead_attempts else 0
    
    # Count active agents
    active_agents = db.query(Agent).filter(
        Agent.company_id == company.id,
        Agent.status == "active",
        Agent.is_deleted == False
    ).count()
    
    return CallMetrics(
        total_calls=total_calls,
        answered_calls=answered_calls,
        no_answer_calls=no_answer_calls,
        failed_calls=failed_calls,
        pickup_rate=round(pickup_rate, 2),
        average_attempts_per_lead=round(avg_attempts, 2),
        active_agents=active_agents
    )


@router.post("/schedule")
async def schedule_call(
    request: CallScheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company = get_user_company(db, current_user)
    
    # Verify lead belongs to company
    lead = db.query(Lead).join(Agent).filter(
        Lead.id == request.lead_id,
        Agent.company_id == company.id,
        Agent.is_deleted == False,
        Lead.is_deleted == False
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Schedule the lead
    success = call_scheduler.schedule_lead_now(request.lead_id)
    
    if success:
        return {"message": "Lead scheduled successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule lead"
        )


@router.post("/run-scheduler")
async def run_scheduler():
    """Endpoint for Cloud Scheduler to trigger call scheduling"""
    try:
        stats = call_scheduler.run_schedule_cycle()
        return {
            "message": "Scheduler cycle completed",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scheduler failed: {str(e)}"
        )


@router.post("/webhook")
async def retell_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle webhooks from Retell AI"""
    try:
        # Get the raw body for signature verification
        body = await request.body()
        
        # TODO: Verify webhook signature
        # signature = request.headers.get("X-Retell-Signature")
        # if not verify_webhook_signature(body, signature):
        #     raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook data
        webhook_data = await request.json()
        
        # Find the interaction attempt
        call_id = webhook_data.get("call_id")
        attempt = db.query(InteractionAttempt).filter(
            InteractionAttempt.retell_call_id == call_id
        ).first()
        
        if not attempt:
            # Log unknown call but don't fail
            return {"status": "ignored", "reason": "Unknown call ID"}
        
        # Update attempt with webhook data
        attempt.status = "completed"
        attempt.outcome = webhook_data.get("outcome", "unknown")
        attempt.duration_seconds = webhook_data.get("duration_seconds")
        attempt.transcript_url = webhook_data.get("recording_url")
        attempt.summary = webhook_data.get("summary")
        attempt.raw_webhook_data = webhook_data
        
        # Update lead status based on outcome
        lead = db.query(Lead).filter(Lead.id == attempt.lead_id).first()
        if lead:
            if attempt.outcome == "answered":
                lead.status = "done"
                lead.disposition = "completed"
            elif lead.attempts_count >= lead.agent.max_attempts:
                lead.status = "done"
                lead.disposition = attempt.outcome
        
        db.commit()
        
        return {"status": "processed"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )