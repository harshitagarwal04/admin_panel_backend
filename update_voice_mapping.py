#!/usr/bin/env python3
"""
Update voice mapping to use valid Retell voice IDs
"""

from app.db.session import SessionLocal
from app.models.voice import Voice

def update_voice_mapping():
    """Update our voice database to use valid Retell voice IDs"""
    
    print("Updating Voice Mapping for Retell Integration")
    print("="*50)
    
    db = SessionLocal()
    
    try:
        # Get all voices
        voices = db.query(Voice).all()
        print(f"Found {len(voices)} voices in database")
        
        # Update mapping to use actual Retell voice IDs
        retell_voice_mapping = {
            "11111111-1111-1111-1111-111111111111": "11labs-Adrian",  # Sarah -> Adrian
            "22222222-2222-2222-2222-222222222222": "11labs-Adrian",  # John -> Adrian  
            "33333333-3333-3333-3333-333333333333": "11labs-Adrian",  # Emma -> Adrian
            "44444444-4444-4444-4444-444444444444": "11labs-Adrian",  # David -> Adrian
            "55555555-5555-5555-5555-555555555555": "11labs-Adrian",  # Maria -> Adrian
        }
        
        # Update voice provider IDs to use Retell voice IDs
        updated_count = 0
        for voice in voices:
            voice_id_str = str(voice.id)
            if voice_id_str in retell_voice_mapping:
                old_provider_id = voice.voice_provider_id
                new_provider_id = retell_voice_mapping[voice_id_str]
                
                voice.voice_provider_id = new_provider_id
                
                print(f"Updated voice '{voice.name}':")
                print(f"  ID: {voice_id_str}")
                print(f"  Provider ID: {old_provider_id} -> {new_provider_id}")
                
                updated_count += 1
        
        db.commit()
        print(f"\n✓ Successfully updated {updated_count} voices")
        
        # Show final mapping
        print(f"\nFinal voice mapping:")
        voices = db.query(Voice).all()
        for voice in voices:
            print(f"  {voice.id} ({voice.name}) -> {voice.voice_provider_id}")
        
    except Exception as e:
        print(f"✗ Error updating voices: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_voice_mapping()