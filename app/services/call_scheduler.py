from typing import List, Optional, Dict
from datetime import datetime, time, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.db.session import SessionLocal
from app.models.lead import Lead
from app.models.agent import Agent
from app.models.company import Company
from app.models.interaction_attempt import InteractionAttempt
from app.services.retell_service import retell_service
import logging
import pytz

logger = logging.getLogger(__name__)


class CallScheduler:
    def __init__(self):
        self.db = SessionLocal()
    
    def run_schedule_cycle(self) -> Dict[str, int]:
        """Run a complete scheduling cycle"""
        try:
            stats = {
                "eligible_leads": 0,
                "calls_initiated": 0,
                "calls_failed": 0,
                "calls_skipped": 0
            }
            
            # Get eligible leads
            eligible_leads = self._get_eligible_leads()
            stats["eligible_leads"] = len(eligible_leads)
            
            # Process each lead
            for lead in eligible_leads:
                result = self._process_lead(lead)
                stats[result] += 1
            
            self.db.commit()
            return stats
            
        except Exception as e:
            logger.error(f"Error in schedule cycle: {e}")
            self.db.rollback()
            return {"error": str(e)}
        finally:
            self.db.close()
    
    def _get_eligible_leads(self) -> List[Lead]:
        """Get leads eligible for calling right now"""
        now = datetime.utcnow()
        
        # Query for eligible leads
        eligible_leads = self.db.query(Lead).join(Agent).join(Company).filter(
            and_(
                Lead.is_deleted == False,
                Agent.is_deleted == False,
                Agent.status == "active",
                Company.is_deleted == False,
                Lead.status.in_(["new", "in_progress"]),
                Lead.schedule_at <= now,
                # Haven't exceeded max attempts
                Lead.attempts_count < Agent.max_attempts,
                # Check if enough time has passed since last attempt
                self._retry_delay_check(Lead.id, Agent.retry_delay_minutes)
            )
        ).all()
        
        # Filter by business hours and concurrent limits
        filtered_leads = []
        for lead in eligible_leads:
            if (self._is_within_business_hours(lead.agent) and 
                self._check_concurrent_limit(lead.agent.company_id)):
                filtered_leads.append(lead)
        
        # Sort by priority (new leads first, then by schedule time)
        filtered_leads.sort(key=lambda x: (
            0 if x.status == "new" else 1,
            x.schedule_at
        ))
        
        return filtered_leads
    
    def _retry_delay_check(self, lead_id: str, retry_delay_minutes: int):
        """Check if enough time has passed since last attempt"""
        last_attempt = self.db.query(InteractionAttempt).filter(
            InteractionAttempt.lead_id == lead_id
        ).order_by(InteractionAttempt.created_at.desc()).first()
        
        if not last_attempt:
            return True  # No previous attempts
        
        retry_after = last_attempt.created_at + timedelta(minutes=retry_delay_minutes)
        return datetime.utcnow() >= retry_after
    
    def _is_within_business_hours(self, agent: Agent) -> bool:
        """Check if current time is within agent's business hours"""
        if not agent.business_hours_start or not agent.business_hours_end:
            return True  # No business hours restriction
        
        # Convert to agent's timezone
        tz = pytz.timezone(agent.timezone)
        now_local = datetime.now(tz).time()
        
        return agent.business_hours_start <= now_local <= agent.business_hours_end
    
    def _check_concurrent_limit(self, company_id: str) -> bool:
        """Check if company is within concurrent call limits"""
        active_calls = self.db.query(InteractionAttempt).join(Agent).filter(
            and_(
                Agent.company_id == company_id,
                InteractionAttempt.status == "in_progress"
            )
        ).count()
        
        company = self.db.query(Company).filter(Company.id == company_id).first()
        return active_calls < company.max_concurrent_calls
    
    def _process_lead(self, lead: Lead) -> str:
        """Process a single lead and initiate call"""
        try:
            # Create interaction attempt record
            attempt = InteractionAttempt(
                lead_id=lead.id,
                agent_id=lead.agent_id,
                attempt_number=lead.attempts_count + 1,
                status="pending"
            )
            self.db.add(attempt)
            self.db.flush()  # Get the ID
            
            # Prepare call data
            call_data = {
                "from_number": lead.agent.outbound_phone,
                "to_number": lead.phone_e164,
                "agent_id": lead.agent.retell_agent_id,
                "metadata": {
                    "lead_id": str(lead.id),
                    "attempt_id": str(attempt.id),
                    "custom_fields": lead.custom_fields
                }
            }
            
            # Initiate call via Retell
            call_id = retell_service.create_phone_call(call_data)
            
            if call_id:
                # Update attempt with call ID and status
                attempt.retell_call_id = call_id
                attempt.status = "in_progress"
                
                # Update lead status and attempt count
                lead.status = "in_progress"
                lead.attempts_count += 1
                
                return "calls_initiated"
            else:
                # Mark attempt as failed
                attempt.status = "failed"
                attempt.outcome = "failed"
                return "calls_failed"
                
        except Exception as e:
            logger.error(f"Error processing lead {lead.id}: {e}")
            return "calls_failed"
    
    def schedule_lead_now(self, lead_id: str) -> bool:
        """Schedule a specific lead for immediate calling"""
        try:
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return False
            
            lead.schedule_at = datetime.utcnow()
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling lead {lead_id}: {e}")
            self.db.rollback()
            return False


call_scheduler = CallScheduler()