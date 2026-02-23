import httpx
import json
from app.config import settings


class DeepgramService:
    """Speech-to-Text service using Deepgram API"""
    
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY
        self.base_url = "https://api.deepgram.com/v1"
    
    async def transcribe_audio(self, audio_url: str) -> dict:
        """
        Transcribe audio from URL
        Returns: {"text": str, "confidence": float}
        """
        url = f"{self.base_url}/listen"
        
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Deepgram parameters optimized for Arabic
        params = {
            "model": "nova-2",
            "language": "ar",  # Arabic
            "smart_format": True,
            "punctuate": True,
            "diarize": False,
        }
        
        data = {
            "url": audio_url
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, 
                json=data, 
                headers=headers, 
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0]
                return {
                    "text": transcript.get("transcript", ""),
                    "confidence": transcript.get("confidence", 0)
                }
            else:
                print(f"Deepgram error: {response.status_code} - {response.text}")
                return {"text": "", "confidence": 0}
    
    async def transcribe_audio_bytes(self, audio_bytes: bytes, mimetype: str = "audio/wav") -> dict:
        """
        Transcribe audio from bytes
        """
        url = f"{self.base_url}/listen"
        
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": mimetype
        }
        
        params = {
            "model": "nova-2",
            "language": "ar",
            "smart_format": True,
            "punctuate": True,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                content=audio_bytes,
                headers=headers,
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0]
                return {
                    "text": transcript.get("transcript", ""),
                    "confidence": transcript.get("confidence", 0)
                }
            else:
                print(f"Deepgram error: {response.status_code} - {response.text}")
                return {"text": "", "confidence": 0}
    
    def get_websocket_url(self) -> str:
        """Get WebSocket URL for real-time transcription"""
        return f"wss://api.deepgram.com/v1/listen?model=nova-2&language=ar&smart_format=true&encoding=mulaw&sample_rate=8000"
    
    def get_websocket_headers(self) -> dict:
        """Get headers for WebSocket connection"""
        return {
            "Authorization": f"Token {self.api_key}"
        }


# Global instance
deepgram_service = DeepgramService()
