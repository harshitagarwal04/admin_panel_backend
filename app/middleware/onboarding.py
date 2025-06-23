from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.core.security import verify_token
from app.db.session import SessionLocal
from app.models.user import User
from app.models.company import Company
import logging

logger = logging.getLogger(__name__)


class OnboardingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce onboarding completion for business logic endpoints.
    
    Rules:
    1. Allow all /auth/* endpoints (needed for onboarding)
    2. Allow /health, /docs, /openapi.json (public endpoints)
    3. For all other /api/v1/* endpoints, require:
       - User has completed profile (name is not None)
       - User has a company
    """
    
    # Endpoints that don't require onboarding completion
    EXCLUDED_PATHS = {
        "/health",
        "/docs",
        "/openapi.json",
        "/api/v1/openapi.json",
        "/redoc",
        "/favicon.ico"
    }
    
    # Path prefixes that don't require onboarding
    EXCLUDED_PREFIXES = (
        "/api/v1/auth/",
        "/static/",
        "/docs",
        "/redoc"
    )
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Get the request path
        path = request.url.path
        
        # Skip onboarding check for excluded paths
        if self._is_excluded_path(path):
            return await call_next(request)
        
        # Skip onboarding check for non-API routes
        if not path.startswith("/api/v1/"):
            return await call_next(request)
        
        # Check if this is a protected route (has Authorization header)
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # No auth header - let the endpoint handle authentication
            return await call_next(request)
        
        # Extract and verify token
        token = auth_header.split(" ")[1]
        user_id = verify_token(token)
        
        if not user_id:
            # Invalid token - let the endpoint handle this
            return await call_next(request)
        
        # Check onboarding status
        db = SessionLocal()
        try:
            user = db.query(User).filter(
                User.id == user_id, 
                User.is_deleted == False
            ).first()
            
            if not user:
                # User not found - let endpoint handle this
                return await call_next(request)
            
            # Check if onboarding is complete (profile + company created together)
            if not user.name:
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "detail": "ONBOARDING_INCOMPLETE",
                        "message": "Please complete your profile and company setup before accessing this feature",
                        "onboarding_step": "profile",
                        "required_fields": ["name", "phone", "company_name"]
                    },
                    headers={"X-Onboarding-Step": "profile"}
                )
            
            # Double-check that user has a company (should exist if name exists after our flow)
            company = db.query(Company).filter(
                Company.admin_user_id == user.id,
                Company.is_deleted == False
            ).first()
            
            if not company:
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "detail": "COMPANY_MISSING", 
                        "message": "Company setup incomplete. Please contact support.",
                        "onboarding_step": "profile",
                        "required_fields": ["company_name"]
                    },
                    headers={"X-Onboarding-Step": "profile"}
                )
            
            # User is fully onboarded, proceed
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Error in onboarding middleware: {e}")
            # Return error response instead of continuing
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error during onboarding check",
                    "message": "An unexpected error occurred. Please try again."
                }
            )
        finally:
            db.close()
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if the path should be excluded from onboarding checks"""
        # Check exact matches
        if path in self.EXCLUDED_PATHS:
            return True
        
        # Check prefixes
        for prefix in self.EXCLUDED_PREFIXES:
            if path.startswith(prefix):
                return True
        
        return False