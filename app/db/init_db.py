from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.models import *


def init_db() -> None:
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Initialize seed data
        db = SessionLocal()
        try:
            init_voices(db)
            init_templates(db)
            db.commit()
            print("✅ Database initialized successfully")
        except Exception as e:
            db.rollback()
            print(f"⚠️ Error initializing database seed data: {e}")
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("🔄 Server will start without database - API will return errors until DB is connected")
        # Don't crash the server, just warn about the database issue


def init_voices(db: Session) -> None:
    # Check if voices already exist
    if db.query(Voice).first():
        return
    
    voices = [
        Voice(name="US English Male", language="en-US", gender="male", voice_provider_id="en-US-male-1"),
        Voice(name="US English Female", language="en-US", gender="female", voice_provider_id="en-US-female-1"),
        Voice(name="UK English Male", language="en-GB", gender="male", voice_provider_id="en-GB-male-1"),
        Voice(name="UK English Female", language="en-GB", gender="female", voice_provider_id="en-GB-female-1"),
        Voice(name="Hinglish Male", language="hi-IN", gender="male", voice_provider_id="hi-IN-male-1"),
        Voice(name="Hinglish Female", language="hi-IN", gender="female", voice_provider_id="hi-IN-female-1"),
    ]
    
    for voice in voices:
        db.add(voice)


def init_templates(db: Session) -> None:
    # Check if templates already exist
    if db.query(Template).first():
        return
    
    templates = [
        # Healthcare Templates
        Template(
            industry="Healthcare",
            use_case="Lead Qualification",
            name="Healthcare Lead Qualifier",
            prompt="You are a friendly healthcare assistant. Qualify leads for {{service_type}} services. Ask about their {{health_concern}} and schedule appointments.",
            variables=["service_type", "health_concern"],
            functions=["end_call", "check_calendar_availability", "book_on_calendar"],
            welcome_message="Hello! I'm calling from {{company_name}} regarding your interest in our healthcare services. Do you have a moment to discuss how we can help you?",
            suggested_settings={"max_attempts": 5, "retry_delay_minutes": 60, "business_hours_start": "09:00", "business_hours_end": "17:00", "max_call_duration_minutes": 15}
        ),
        Template(
            industry="Healthcare",
            use_case="Appointment Setting",
            name="Medical Appointment Scheduler",
            prompt="You are scheduling medical appointments for {{doctor_name}} at {{clinic_name}}. Help patients book consultations for {{specialty}}.",
            variables=["doctor_name", "clinic_name", "specialty"],
            functions=["end_call", "check_calendar_availability", "book_on_calendar"],
            welcome_message="Hi {{first_name}}! This is {{agent_name}} from {{clinic_name}}. I'm calling to help schedule your {{specialty}} consultation.",
            suggested_settings={"max_attempts": 4, "retry_delay_minutes": 90, "business_hours_start": "08:00", "business_hours_end": "18:00", "max_call_duration_minutes": 12}
        ),
        
        # Real Estate Templates
        Template(
            industry="Real Estate",
            use_case="Appointment Setting",
            name="Real Estate Appointment Setter",
            prompt="You are a professional real estate agent. Schedule property viewings for {{property_type}} in {{location}}. Qualify budget and timeline.",
            variables=["property_type", "location", "budget_range"],
            functions=["end_call", "check_calendar_availability", "book_on_calendar", "transfer_call"],
            welcome_message="Hi! This is {{agent_name}} from {{company_name}}. I'm calling about your interest in properties in {{location}}. Is this a good time to chat?",
            suggested_settings={"max_attempts": 4, "retry_delay_minutes": 45, "business_hours_start": "08:00", "business_hours_end": "19:00", "max_call_duration_minutes": 20}
        ),
        Template(
            industry="Real Estate",
            use_case="Lead Qualification",
            name="Property Lead Qualifier",
            prompt="You're qualifying leads interested in {{property_type}} properties. Assess their timeline, budget, and location preferences.",
            variables=["property_type", "price_range", "timeline"],
            functions=["end_call", "transfer_call", "check_calendar_availability"],
            welcome_message="Hello {{first_name}}! I'm {{agent_name}} from {{company_name}}. Thank you for your interest in {{property_type}} properties.",
            suggested_settings={"max_attempts": 3, "retry_delay_minutes": 60, "business_hours_start": "09:00", "business_hours_end": "20:00", "max_call_duration_minutes": 18}
        ),
        
        # Insurance Templates
        Template(
            industry="Insurance",
            use_case="Lead Qualification",
            name="Insurance Lead Qualifier",
            prompt="You are an insurance specialist calling about {{insurance_type}} coverage. Assess their current situation and qualifying factors.",
            variables=["insurance_type", "current_coverage", "family_size"],
            functions=["end_call", "check_calendar_availability", "book_on_calendar"],
            welcome_message="Hello! This is {{agent_name}} from {{company_name}}. I'm following up on your interest in {{insurance_type}} insurance. Do you have a few minutes to discuss your coverage needs?",
            suggested_settings={"max_attempts": 4, "retry_delay_minutes": 90, "business_hours_start": "09:00", "business_hours_end": "18:00", "max_call_duration_minutes": 25}
        ),
        
        # E-commerce Templates
        Template(
            industry="E-commerce",
            use_case="Follow-up",
            name="E-commerce Cart Recovery Agent",
            prompt="You are a helpful customer service agent following up on abandoned carts. Offer assistance and incentives for {{product_category}}.",
            variables=["product_category", "cart_value", "discount_code"],
            functions=["end_call", "transfer_call"],
            welcome_message="Hi {{first_name}}! This is {{agent_name}} from {{company_name}}. I noticed you were interested in our {{product_category}} products. I'd love to help you complete your purchase!",
            suggested_settings={"max_attempts": 3, "retry_delay_minutes": 30, "business_hours_start": "08:00", "business_hours_end": "20:00", "max_call_duration_minutes": 10}
        ),
        
        # Education Templates
        Template(
            industry="Education",
            use_case="Appointment Setting",
            name="Education Enrollment Advisor",
            prompt="You are an enrollment advisor for {{program_type}} programs. Qualify prospects and schedule enrollment consultations.",
            variables=["program_type", "education_level", "career_goals"],
            functions=["end_call", "check_calendar_availability", "book_on_calendar"],
            welcome_message="Hello! This is {{agent_name}} from {{company_name}}. Thank you for your interest in our {{program_type}} program. I'd love to discuss how we can help you achieve your career goals.",
            suggested_settings={"max_attempts": 5, "retry_delay_minutes": 120, "business_hours_start": "09:00", "business_hours_end": "17:00", "max_call_duration_minutes": 30}
        ),
        
        # SaaS Templates
        Template(
            industry="SaaS",
            use_case="Lead Qualification",
            name="SaaS Demo Scheduler",
            prompt="You are a sales development representative for {{company_name}}. Qualify prospects for {{product_name}} and schedule product demos.",
            variables=["product_name", "company_size", "current_solution", "pain_points"],
            functions=["end_call", "check_calendar_availability", "book_on_calendar", "transfer_call"],
            welcome_message="Hi {{first_name}}! This is {{agent_name}} from {{company_name}}. I saw you downloaded our {{product_name}} guide. I'd love to show you how it can solve your {{pain_points}}.",
            suggested_settings={"max_attempts": 4, "retry_delay_minutes": 45, "business_hours_start": "08:00", "business_hours_end": "18:00", "max_call_duration_minutes": 20}
        ),
    ]
    
    for template in templates:
        db.add(template)