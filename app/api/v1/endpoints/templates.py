from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.deps import get_db, get_current_user
from app.schemas.template import TemplateResponse, TemplateListResponse, IndustryResponse
from app.models.user import User
from app.models.template import Template

router = APIRouter()


@router.get("/", response_model=TemplateListResponse)
async def list_templates(
    industry: Optional[str] = Query(None),
    use_case: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Template)
    
    if industry:
        query = query.filter(Template.industry == industry)
    
    if use_case:
        query = query.filter(Template.use_case == use_case)
    
    templates = query.all()
    
    return TemplateListResponse(
        templates=templates,
        total=len(templates)
    )


@router.get("/industries", response_model=List[IndustryResponse])
async def list_templates_by_industry(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all templates grouped by industry
    templates = db.query(Template).all()
    
    # Group templates by industry
    industries = {}
    for template in templates:
        if template.industry not in industries:
            industries[template.industry] = []
        industries[template.industry].append(template)
    
    # Convert to response format
    result = []
    for industry, industry_templates in industries.items():
        result.append(IndustryResponse(
            industry=industry,
            templates=industry_templates
        ))
    
    return result


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = db.query(Template).filter(Template.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template