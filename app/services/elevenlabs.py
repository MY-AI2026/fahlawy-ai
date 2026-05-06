import httpx
import base64
from app.config import settings


class ElevenLabsService:
    """Text-to-Speech service using ElevenLabs API.

    Tuned for natural conversational Egyptian Arabic on phone calls.
    """

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID
        self.base_url = "https://api.elevenlabs.io/v1"

        # Conversational voice settings:
        #   stability 0.45  -> enough variation for natural cadence
        #   similarity 0.85 -> stay close to the cloned voice
        #   style     0.55  -> moderate expressiveness for sales tone
        self.voice_settings = {
            "stability": 0.45,
            "similarity_boost": 0.85,
            "style": 0.55,
            "use_speaker_boost": True,
        }

        # multilingual_v2 = highest-quality Arabic. Switch to eleven_turbo_v2_5
        # for lower latency on real-time calls if needed.
        self.model_id = settings.ELEVENLABS_MODEL_ID or "eleven_multilingual_v2"
        # 44.1 kHz / 128 kbps MP3 — a good balance of quality and bandwidth for
        # Twilio playback. Twilio downsamples to 8 kHz on the call anyway, but
        # better source = clearer downsampled audio.
        self.output_format = "mp3_44100_128"

    async def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech audio. Returns MP3 bytes."""
        url = (
            f"{self.base_url}/text-to-speech/{self.voice_id}"
            f"?output_format={self.output_format}"
        )

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }

        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": self.voice_settings,
            "language_code": "ar",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)

            if response.status_code == 200:
                return response.content
            print(f"ElevenLabs error: {response.status_code} - {response.text}")
            raise Exception(f"ElevenLabs API error: {response.status_code}")

    async def text_to_speech_base64(self, text: str) -> str:
        audio_bytes = await self.text_to_speech(text)
        return base64.b64encode(audio_bytes).decode("utf-8")

    async def get_available_voices(self) -> list:
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get("voices", [])
            return []


elevenlabs_service = ElevenLabsService()
