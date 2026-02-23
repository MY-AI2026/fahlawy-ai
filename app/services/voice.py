from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather, Say, Play
from app.config import settings
import urllib.parse


class VoiceService:
    """Voice call handling service using Twilio"""
    
    def __init__(self):
        self.client = Client(
            settings.TWILIO_API_KEY,
            settings.TWILIO_API_SECRET,
            settings.TWILIO_ACCOUNT_SID
        )
        self.phone_number = settings.TWILIO_PHONE_NUMBER
    
    def create_greeting_response(self, base_url: str) -> str:
        """
        Create TwiML response for incoming call greeting
        """
        response = VoiceResponse()
        
        # Initial greeting using ElevenLabs audio
        greeting_text = "هلا وغلا! معاك سارة من معهد لانجفورد الدولي. كيف أقدر أساعدك اليوم؟"
        
        # Use Gather to collect speech input
        gather = Gather(
            input='speech',
            language='ar-SA',  # Arabic (Saudi) - closest to Kuwaiti
            speech_timeout='auto',
            action=f'{base_url}/api/voice/process',
            method='POST'
        )
        
        # Play TTS greeting (will be replaced with ElevenLabs)
        gather.say(
            greeting_text,
            language='ar-SA',
            voice='Polly.Zeina'  # Arabic voice fallback
        )
        
        response.append(gather)
        
        # If no input, repeat
        response.redirect(f'{base_url}/api/voice/incoming')
        
        return str(response)
    
    def create_response_twiml(self, response_text: str, base_url: str, use_elevenlabs: bool = True) -> str:
        """
        Create TwiML response with AI-generated text
        """
        response = VoiceResponse()
        
        if use_elevenlabs:
            # Use ElevenLabs audio URL
            audio_url = f"{base_url}/api/voice/tts?text={urllib.parse.quote(response_text)}"
            
            gather = Gather(
                input='speech',
                language='ar-SA',
                speech_timeout='auto',
                action=f'{base_url}/api/voice/process',
                method='POST'
            )
            gather.play(audio_url)
            response.append(gather)
        else:
            # Fallback to Twilio TTS
            gather = Gather(
                input='speech',
                language='ar-SA',
                speech_timeout='auto',
                action=f'{base_url}/api/voice/process',
                method='POST'
            )
            gather.say(response_text, language='ar-SA', voice='Polly.Zeina')
            response.append(gather)
        
        # If no input, ask again
        response.say("هل تحتاج مساعدة في شي ثاني؟", language='ar-SA', voice='Polly.Zeina')
        response.redirect(f'{base_url}/api/voice/incoming')
        
        return str(response)
    
    def create_escalation_twiml(self, escalation_message: str) -> str:
        """
        Create TwiML to transfer call to human agent
        """
        response = VoiceResponse()
        
        response.say(
            "حاضر، خلني أحولك لأحد الزملاء يساعدك. لحظة من فضلك.",
            language='ar-SA',
            voice='Polly.Zeina'
        )
        
        # Transfer to human
        response.dial(
            settings.ESCALATION_PHONE,
            caller_id=self.phone_number,
            timeout=30
        )
        
        # If no answer
        response.say(
            "للأسف ما قدرنا نوصلك. بنتواصل معاك قريباً إن شاء الله.",
            language='ar-SA',
            voice='Polly.Zeina'
        )
        
        return str(response)
    
    def create_goodbye_twiml(self) -> str:
        """
        Create TwiML for ending the call
        """
        response = VoiceResponse()
        
        response.say(
            "شكراً لتواصلك مع معهد لانجفورد. نتشرف بخدمتك دائماً. مع السلامة!",
            language='ar-SA',
            voice='Polly.Zeina'
        )
        
        response.hangup()
        
        return str(response)
    
    def make_outbound_call(self, to_number: str, twiml_url: str) -> dict:
        """
        Make an outbound call
        """
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=twiml_url,
                method='POST'
            )
            
            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status
            }
        except Exception as e:
            print(f"Error making call: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
voice_service = VoiceService()
