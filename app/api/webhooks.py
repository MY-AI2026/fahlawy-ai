from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import PlainTextResponse
from app.services.ai_agent import sales_agent
from app.services.whatsapp import whatsapp_service

router = APIRouter()

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(None),
    MessageSid: str = Form(None)
):
    """
    Webhook endpoint for incoming WhatsApp messages from Twilio
    """
    try:
        # Extract phone number (remove 'whatsapp:' prefix)
        user_phone = From.replace("whatsapp:", "")
        user_message = Body.strip()
        
        print(f"📱 Received message from {user_phone}: {user_message}")
        
        # Check for greeting/start commands
        if user_message.lower() in ["hi", "hello", "هلا", "السلام", "مرحبا", "start", "ابدأ"]:
            response_text = sales_agent.get_greeting()
        else:
            # Get AI response
            ai_result = sales_agent.get_response(user_phone, user_message)
            response_text = ai_result["response"]
            
            # Check if escalation needed
            if ai_result["should_escalate"]:
                print(f"⚠️ Escalating conversation for {user_phone}")
                whatsapp_service.send_escalation_notification(
                    user_phone, 
                    ai_result["escalation_reason"]
                )
                # Add escalation note to response
                response_text += "\n\n✨ تم إبلاغ فريقنا وبيتواصلون معاك قريباً!"
        
        # Send response via WhatsApp
        result = whatsapp_service.send_message(From, response_text)
        
        if result["success"]:
            print(f"✅ Response sent successfully")
        else:
            print(f"❌ Failed to send response: {result['error']}")
        
        # Return empty response (Twilio expects 200 OK)
        return PlainTextResponse("", status_code=200)
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        # Still return 200 to prevent Twilio retries
        return PlainTextResponse("", status_code=200)


@router.get("/webhook/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """
    Verification endpoint for Twilio webhook setup
    """
    return PlainTextResponse("Webhook is active!", status_code=200)


@router.post("/test/send")
async def test_send_message(phone: str, message: str):
    """
    Test endpoint to send a message
    """
    result = whatsapp_service.send_message(phone, message)
    return result


@router.get("/test/greeting")
async def test_greeting():
    """
    Test endpoint to get greeting message
    """
    return {"greeting": sales_agent.get_greeting()}


@router.post("/test/chat")
async def test_chat(phone: str, message: str, dialect: str = None, instructions: str = None):
    """
    Test endpoint to simulate a chat
    """
    result = sales_agent.get_response(phone, message, dialect=dialect, instructions=instructions)
    return result

@router.post("/agent/config")
async def update_agent_config(dialect: str = None, instructions: str = None):
    """
    Update the global agent configuration
    """
    sales_agent.update_config(dialect=dialect, instructions=instructions)
    return {"status": "success", "config": sales_agent.config}
