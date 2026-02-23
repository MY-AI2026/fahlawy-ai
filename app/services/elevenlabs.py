import httpx
import base64
from app.config import settings


class ElevenLabsService:
    """Text-to-Speech service using ElevenLabs API"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Arabic-optimized voice settings
        self.voice_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.5,
            "use_speaker_boost": True
        }
    
    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech audio
        Returns: MP3 audio bytes
        """
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # Best for Arabic
            "voice_settings": self.voice_settings
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"ElevenLabs error: {response.status_code} - {response.text}")
                raise Exception(f"ElevenLabs API error: {response.status_code}")
    
    async def text_to_speech_base64(self, text: str) -> str:
        """
        Convert text to speech and return base64 encoded audio
        """
        audio_bytes = await self.text_to_speech(text)
        return base64.b64encode(audio_bytes).decode('utf-8')
    
    async def get_available_voices(self) -> list:
        """Get list of available voices"""
        url = f"{self.base_url}/voices"
        
        headers = {
            "xi-api-key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("voices", [])
            else:
                return []


# Global instance
elevenlabs_service = ElevenLabsService()
