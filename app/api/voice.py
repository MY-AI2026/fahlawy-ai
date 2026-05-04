from fastapi import APIRouter, Request, Form, HTTPException, Query
from fastapi.responses import Response, PlainTextResponse
from app.services.ai_agent import sales_agent
from app.services.voice import voice_service
from app.services.elevenlabs import elevenlabs_service
from app.services.whatsapp import whatsapp_service
from app.config import settings
import urllib.parse

router = APIRouter()

# Per-call session metadata. Cleared on call end.
call_sessions: dict[str, dict] = {}


def _resolve_base_url(request: Request) -> str:
    """Return the public base URL Twilio can reach."""
    if settings.PUBLIC_URL and settings.PUBLIC_URL.strip():
        return settings.PUBLIC_URL.rstrip("/")
    return str(request.base_url).rstrip("/")


@router.post("/voice/incoming")
async def handle_call_start(
    request: Request,
    CallSid: str = Form(None),
    From: str = Form(None),
    To: str = Form(None),
    customer_name: str | None = Query(default=None),
):
    """
    Entry point for both inbound calls and the outbound demo call.

    For the demo, this is what Twilio fetches the moment the customer
    picks up — Mariam introduces herself and the company immediately.
    """
    print(f"📞 Call started — CallSid={CallSid} From={From} To={To} name={customer_name}")

    if CallSid:
        call_sessions[CallSid] = {
            "from": From,
            "to": To,
            "customer_name": customer_name,
            "messages": [],
        }
        sales_agent.init_session(CallSid, customer_name)

    base_url = _resolve_base_url(request)
    twiml = voice_service.create_outbound_opening(base_url, customer_name)
    return Response(content=twiml, media_type="application/xml")


@router.post("/voice/process")
async def process_voice_input(
    request: Request,
    CallSid: str = Form(None),
    From: str = Form(None),
    SpeechResult: str = Form(None),
    Confidence: float = Form(None),
):
    """Process customer speech and produce Mariam's next reply."""
    print(f"🎤 SpeechResult='{SpeechResult}' confidence={Confidence}")

    base_url = _resolve_base_url(request)
    session = call_sessions.get(CallSid) or {"from": From, "messages": []}

    if not SpeechResult or not SpeechResult.strip():
        twiml = voice_service.create_response_twiml(
            "معذرة يا فندم، الصوت قطع شوية. ممكن تعيد آخر كلمة؟",
            base_url,
            use_elevenlabs=True,
        )
        return Response(content=twiml, media_type="application/xml")

    goodbye_keywords = [
        "مع السلامة", "باي", "يلا باي", "خلاص شكراً",
        "اقفلي", "اقفل المكالمة", "مش مهتم خالص",
    ]
    if any(k in SpeechResult for k in goodbye_keywords):
        twiml = voice_service.create_goodbye_twiml()
        sales_agent.end_session(CallSid)
        return Response(content=twiml, media_type="application/xml")

    session_id = CallSid or From or "anonymous"
    ai_result = sales_agent.get_response(session_id, SpeechResult)
    response_text = ai_result["response"]
    print(f"🤖 Mariam: {response_text}")

    if ai_result["should_escalate"]:
        print(f"⚠️ Escalating: {ai_result['escalation_reason']}")
        try:
            whatsapp_service.send_escalation_notification(
                From or "Unknown",
                f"مكالمة عقارية - {ai_result['escalation_reason']}",
            )
        except Exception as e:
            print(f"WhatsApp notify failed: {e}")

        twiml = voice_service.create_escalation_twiml(response_text)
        return Response(content=twiml, media_type="application/xml")

    # Track the exchange in the session log.
    session.setdefault("messages", []).append(
        {"customer": SpeechResult, "agent": response_text}
    )
    if CallSid:
        call_sessions[CallSid] = session

    twiml = voice_service.create_response_twiml(
        response_text, base_url, use_elevenlabs=True
    )
    return Response(content=twiml, media_type="application/xml")


@router.get("/voice/tts")
async def text_to_speech(text: str):
    """Stream MP3 audio from ElevenLabs back to Twilio."""
    try:
        decoded_text = urllib.parse.unquote(text)
        audio_bytes = await elevenlabs_service.text_to_speech(decoded_text)
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "public, max-age=3600",
            },
        )
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/outbound")
async def make_outbound_call(
    request: Request,
    to_number: str = Query(..., description="رقم العميل بصيغة دولية، مثال: +201001234567"),
    customer_name: str | None = Query(default=None, description="اسم العميل (اختياري)"),
):
    """
    Trigger Mariam to call a customer.

    Example:
      POST /api/voice/outbound?to_number=%2B201001234567&customer_name=أحمد
    """
    base_url = _resolve_base_url(request)
    twiml_url = f"{base_url}/api/voice/incoming"
    if customer_name:
        twiml_url += f"?customer_name={urllib.parse.quote(customer_name)}"

    result = voice_service.make_outbound_call(to_number, twiml_url, customer_name)
    return result


@router.get("/voice/status")
async def voice_status(CallSid: str | None = None):
    if CallSid and CallSid in call_sessions:
        return call_sessions[CallSid]
    return {"status": "no session found"}


@router.post("/voice/status-callback")
async def voice_status_callback(
    CallSid: str = Form(None),
    CallStatus: str = Form(None),
    CallDuration: int = Form(None),
    From: str = Form(None),
):
    print(f"📊 Call {CallSid} status={CallStatus} duration={CallDuration}s")
    if CallStatus in ["completed", "failed", "busy", "no-answer"]:
        if CallSid:
            call_sessions.pop(CallSid, None)
            sales_agent.end_session(CallSid)
    return PlainTextResponse("OK")
