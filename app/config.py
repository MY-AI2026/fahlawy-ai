import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_API_KEY: str = os.getenv("TWILIO_API_KEY")
    TWILIO_API_SECRET: str = os.getenv("TWILIO_API_SECRET")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "+14642669684")
    
    # Google Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    
    # Deepgram (Speech-to-Text)
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY")
    
    # ElevenLabs (Text-to-Speech)
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
    
    # App
    APP_NAME: str = os.getenv("APP_NAME", "Langford AI Sales Agent")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Escalation
    ESCALATION_PHONE: str = os.getenv("ESCALATION_PHONE", "+96551600140")

settings = Settings()
