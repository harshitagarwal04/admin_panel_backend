"""Seed voices table with default voices"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.voice import Voice
import uuid


def seed_voices(db: Session):
    """Seed the voices table with default voices"""
    
    default_voices = [
        {
            "id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
            "name": "Sarah - American",
            "gender": "female",
            "language": "en-US",
            "voice_provider_id": "retell_sarah_en_us",
            "is_active": True
        },
        {
            "id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
            "name": "John - American",
            "gender": "male",
            "language": "en-US", 
            "voice_provider_id": "retell_john_en_us",
            "is_active": True
        },
        {
            "id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
            "name": "Emma - British",
            "gender": "female",
            "language": "en-GB",
            "voice_provider_id": "retell_emma_en_gb",
            "is_active": True
        },
        {
            "id": uuid.UUID("44444444-4444-4444-4444-444444444444"),
            "name": "David - British",
            "gender": "male",
            "language": "en-GB",
            "voice_provider_id": "retell_david_en_gb",
            "is_active": True
        },
        {
            "id": uuid.UUID("55555555-5555-5555-5555-555555555555"),
            "name": "Maria - Spanish",
            "gender": "female",
            "language": "es-ES",
            "voice_provider_id": "retell_maria_es_es",
            "is_active": True
        }
    ]
    
    for voice_data in default_voices:
        # Check if voice already exists
        existing_voice = db.query(Voice).filter(Voice.id == voice_data["id"]).first()
        if not existing_voice:
            voice = Voice(**voice_data)
            db.add(voice)
    
    db.commit()
    print(f"Seeded {len(default_voices)} voices")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_voices(db)
    finally:
        db.close()