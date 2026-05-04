from twilio.rest import Client
from app.config import settings

class WhatsAppService:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_API_KEY,
            settings.TWILIO_API_SECRET,
            settings.TWILIO_ACCOUNT_SID
        )
        self.whatsapp_number = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
    
    def send_message(self, to_number: str, message: str) -> dict:
        """
        Send WhatsApp message
        to_number: phone number with country code (e.g., +201001234567)
        """
        try:
            # Ensure proper format
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            msg = self.client.messages.create(
                body=message,
                from_=self.whatsapp_number,
                to=to_number
            )
            
            return {
                "success": True,
                "message_sid": msg.sid,
                "status": msg.status
            }
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_escalation_notification(self, customer_phone: str, reason: str):
        """Send notification to human agent about escalation"""
        escalation_message = f"""🚨 تحويل محادثة جديدة

📱 رقم العميل: {customer_phone}
📝 السبب: {reason}

الرجاء التواصل مع العميل في أقرب وقت."""

        # Send to escalation phone
        self.send_message(settings.ESCALATION_PHONE, escalation_message)


# Global instance
whatsapp_service = WhatsAppService()
