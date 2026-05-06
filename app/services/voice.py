from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.config import settings
from app.services.ai_agent import sales_agent
import urllib.parse


# Egyptian Arabic locale used by Twilio's speech recognition.
SPEECH_LANG = "ar-EG"
# Twilio fallback voice for emergencies (Hala = Egyptian neural Polly voice).
FALLBACK_VOICE = "Polly.Hala-Neural"


class VoiceService:
    """Voice call handling service using Twilio."""

    def __init__(self):
        self.client = Client(
            settings.TWILIO_API_KEY,
            settings.TWILIO_API_SECRET,
            settings.TWILIO_ACCOUNT_SID,
        )
        self.phone_number = settings.TWILIO_PHONE_NUMBER

    def _get_base_url(self, request_base_url: str) -> str:
        """Always prefer the public URL so Twilio can reach our webhooks."""
        if settings.PUBLIC_URL and settings.PUBLIC_URL.strip():
            return settings.PUBLIC_URL.rstrip("/")
        return request_base_url.rstrip("/")

    def _tts_url(self, base_url: str, text: str) -> str:
        return f"{base_url}/api/voice/tts?text={urllib.parse.quote(text)}"

    def create_outbound_opening(
        self, base_url: str, customer_name: str | None = None
    ) -> str:
        """
        TwiML for the FIRST moment of an outbound call: Mariam introduces
        herself and the company, then waits for the customer to respond.
        """
        resolved_url = self._get_base_url(base_url)
        opening_text = sales_agent.get_opening_message(customer_name)

        response = VoiceResponse()
        # Tiny pause so the customer's "أيوه؟" doesn't get cut off.
        response.pause(length=1)

        gather = Gather(
            input="speech",
            language=SPEECH_LANG,
            speech_timeout="auto",
            speech_model="phone_call",
            action=f"{resolved_url}/api/voice/process",
            method="POST",
        )
        gather.play(self._tts_url(resolved_url, opening_text))
        response.append(gather)

        # If the line is silent, try once more before giving up.
        retry_text = "ألو، حضرتك معايا؟"
        retry = Gather(
            input="speech",
            language=SPEECH_LANG,
            speech_timeout="auto",
            speech_model="phone_call",
            action=f"{resolved_url}/api/voice/process",
            method="POST",
        )
        retry.play(self._tts_url(resolved_url, retry_text))
        response.append(retry)

        response.hangup()
        return str(response)

    # Kept for backwards compatibility with any external callers.
    def create_greeting_response(
        self, base_url: str, customer_name: str | None = None
    ) -> str:
        return self.create_outbound_opening(base_url, customer_name)

    def create_response_twiml(
        self, response_text: str, base_url: str, use_elevenlabs: bool = True
    ) -> str:
        """TwiML for the AI's reply mid-conversation."""
        resolved_url = self._get_base_url(base_url)
        response = VoiceResponse()

        gather = Gather(
            input="speech",
            language=SPEECH_LANG,
            speech_timeout="auto",
            speech_model="phone_call",
            action=f"{resolved_url}/api/voice/process",
            method="POST",
        )

        if use_elevenlabs:
            gather.play(self._tts_url(resolved_url, response_text))
        else:
            gather.say(response_text, language=SPEECH_LANG, voice=FALLBACK_VOICE)

        response.append(gather)

        # Re-prompt if the customer doesn't answer at all.
        nudge = "حضرتك معايا؟ ممكن أكمل؟"
        response.play(self._tts_url(resolved_url, nudge))
        response.hangup()
        return str(response)

    def create_escalation_twiml(self, escalation_message: str) -> str:
        response = VoiceResponse()
        response.say(
            "حاضر يا فندم، خليني أحولك لزميلي عشان يساعد حضرتك. لحظة من فضلك.",
            language=SPEECH_LANG,
            voice=FALLBACK_VOICE,
        )
        response.dial(
            settings.ESCALATION_PHONE,
            caller_id=self.phone_number,
            timeout=30,
        )
        response.say(
            "للأسف ما قدرناش نوصل بحضرتك دلوقتي، هنتواصل معاك في أقرب وقت.",
            language=SPEECH_LANG,
            voice=FALLBACK_VOICE,
        )
        return str(response)

    def create_goodbye_twiml(self) -> str:
        response = VoiceResponse()
        response.say(
            "متشكرة جداً لوقت حضرتك يا فندم. يومك سعيد، مع السلامة.",
            language=SPEECH_LANG,
            voice=FALLBACK_VOICE,
        )
        response.hangup()
        return str(response)

    def make_outbound_call(
        self,
        to_number: str,
        twiml_url: str,
        customer_name: str | None = None,
    ) -> dict:
        """Initiate the outbound call. Twilio will fetch TwiML from twiml_url."""
        try:
            if settings.PUBLIC_URL and settings.PUBLIC_URL.strip():
                public_base = settings.PUBLIC_URL.rstrip("/")
                twiml_url = f"{public_base}/api/voice/incoming"
                if customer_name:
                    twiml_url += (
                        f"?customer_name={urllib.parse.quote(customer_name)}"
                    )

            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=twiml_url,
                method="POST",
            )

            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status,
            }
        except Exception as e:
            print(f"Error making call: {e}")
            return {"success": False, "error": str(e)}


voice_service = VoiceService()
