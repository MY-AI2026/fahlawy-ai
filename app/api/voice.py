from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import Response, PlainTextResponse
from app.services.ai_agent import sales_agent
from app.services.voice import voice_service
from app.services.elevenlabs import elevenlabs_service
from app.services.deepgram import deepgram_service
from app.services.whatsapp import whatsapp_service
from app.config import settings
import urllib.parse

router = APIRouter()

# Store call sessions
call_sessions = {}


@router.post("/voice/incoming")
async def handle_incoming_call(
    request: Request,
    CallSid: str = Form(None),
    From: str = Form(None),
    To: str = Form(None)
):
    """
    Handle incoming voice calls
    """
    print(f"📞 Incoming call from {From} (CallSid: {CallSid})")
    
    # Initialize session for this call
    if CallSid:
        call_sessions[CallSid] = {
            "from": From,
            "messages": []
        }
    
    # Get base URL from request
    base_url = str(request.base_url).rstrip('/')
    
    # Create greeting response
    twiml = voice_service.create_greeting_response(base_url)
    
    return Response(content=twiml, media_type="application/xml")


@router.post("/voice/process")
async def process_voice_input(
    request: Request,
    CallSid: str = Form(None),
    From: str = Form(None),
    SpeechResult: str = Form(None),
    Confidence: float = Form(None)
):
    """
    Process speech input from caller and generate AI response
    """
    print(f"🎤 Speech received: '{SpeechResult}' (Confidence: {Confidence})")
    
    base_url = str(request.base_url).rstrip('/')
    
    # Get or create session
    session = call_sessions.get(CallSid, {"from": From, "messages": []})
    
    if not SpeechResult or SpeechResult.strip() == "":
        # No speech detected, ask again
        twiml = voice_service.create_response_twiml(
            "عذراً ما سمعتك. ممكن تعيد من فضلك؟",
            base_url,
            use_elevenlabs=False
        )
        return Response(content=twiml, media_type="application/xml")
    
    # Check for goodbye keywords
    goodbye_keywords = ["مع السلامة", "باي", "شكرا", "يلا باي", "خلاص"]
    if any(keyword in SpeechResult.lower() for keyword in goodbye_keywords):
        twiml = voice_service.create_goodbye_twiml()
        return Response(content=twiml, media_type="application/xml")
    
    # Get AI response
    ai_result = sales_agent.get_response(From or CallSid, SpeechResult)
    response_text = ai_result["response"]
    
    print(f"🤖 AI Response: {response_text}")
    
    # Check if escalation needed
    if ai_result["should_escalate"]:
        print(f"⚠️ Escalating call for {From}")
        
        # Notify via WhatsApp
        whatsapp_service.send_escalation_notification(
            From or "Unknown",
            f"مكالمة صوتية - {ai_result['escalation_reason']}"
        )
        
        # Transfer call
        twiml = voice_service.create_escalation_twiml(response_text)
        return Response(content=twiml, media_type="application/xml")
    
    # Generate response TwiML
    twiml = voice_service.create_response_twiml(response_text, base_url, use_elevenlabs=True)
    
    return Response(content=twiml, media_type="application/xml")


@router.get("/voice/tts")
async def text_to_speech(text: str):
    """
    Convert text to speech using ElevenLabs
    Returns MP3 audio
    """
    try:
        # Decode URL-encoded text
        decoded_text = urllib.parse.unquote(text)
        
        # Generate audio
        audio_bytes = await elevenlabs_service.text_to_speech(decoded_text)
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "public, max-age=3600"
            }
        )
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/outbound")
async def make_outbound_call(
    request: Request,
    to_number: str,
    message: str = None
):
    """
    Initiate an outbound call
    """
    base_url = str(request.base_url).rstrip('/')
    twiml_url = f"{base_url}/api/voice/incoming"
    
    result = voice_service.make_outbound_call(to_number, twiml_url)
    
    return result


@router.get("/voice/status")
async def voice_status(CallSid: str = None):
    """
    Get call status and session info
    """
    if CallSid and CallSid in call_sessions:
        return call_sessions[CallSid]
    return {"status": "no session found"}


@router.post("/voice/status-callback")
async def voice_status_callback(
    CallSid: str = Form(None),
    CallStatus: str = Form(None),
    CallDuration: int = Form(None),
    From: str = Form(None)
):
    """
    Callback for call status updates
    """
    print(f"📊 Call {CallSid} status: {CallStatus}, Duration: {CallDuration}s")
    
    # Clean up session when call ends
    if CallStatus in ["completed", "failed", "busy", "no-answer"]:
        if CallSid in call_sessions:
            del call_sessions[CallSid]
    
    return PlainTextResponse("OK")
