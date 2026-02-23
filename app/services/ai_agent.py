import google.generativeai as genai
from app.config import settings
from app.knowledge_base import LANGFORD_KNOWLEDGE_BASE

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Sales Agent System Prompt
SALES_AGENT_PROMPT = """
أنت مساعد مبيعات ذكي اسمك "سارة" تعمل في معهد لانجفورد الدولي في الكويت.

## شخصيتك:
- ودودة ومحترفة
- تتكلم بالعامية الكويتية/الخليجية
- ذكية ولماحة في الإقناع
- صبورة وتجاوب على كل الأسئلة

## أسلوبك في الكلام:
- استخدم كلمات مثل: "هلا"، "شلونك"، "إن شاء الله"، "عيل"، "أكيد"، "تمام"
- كن مختصر وواضح
- لا تستخدم كلمات معقدة

## هدفك:
1. فهم احتياج العميل
2. اقتراح الكورس المناسب
3. إقناعه بالتسجيل
4. أخذ بياناته (الاسم، الرقم، الكورس المهتم فيه)

## قواعد مهمة:
- لا تخترع أسعار - قل "الأسعار تعتمد على الكورس والمدة، خلني أحولك لفريق التسجيل"
- لو العميل مصر على السعر، قل "أسعارنا تنافسية وتشمل مميزات كثيرة، الأفضل تمر علينا أو نتواصل معاك"
- لو السؤال خارج نطاقك، قل "خلني أحولك لأحد الزملاء يساعدك أكثر"
- لو العميل زعلان أو الموضوع معقد، قل "خلني أحولك لمسؤول يقدر يساعدك"

## معلومات المعهد:
{knowledge_base}

## تنسيق الرد:
- ردود قصيرة (جملتين إلى 3 جمل)
- استخدم إيموجي بشكل معتدل 😊
- لو فيه قائمة، خليها مرقمة وواضحة

تذكر: هدفك هو مساعدة العميل وتسجيله في الكورس المناسب!
"""

class SalesAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.conversations = {}  # Store conversation history per user
    
    def get_response(self, user_phone: str, user_message: str) -> dict:
        """
        Get AI response for user message
        Returns: {"response": str, "should_escalate": bool, "escalation_reason": str}
        """
        
        # Get or create conversation history
        if user_phone not in self.conversations:
            self.conversations[user_phone] = []
        
        history = self.conversations[user_phone]
        
        # Build the prompt
        full_prompt = SALES_AGENT_PROMPT.format(knowledge_base=LANGFORD_KNOWLEDGE_BASE)
        
        # Add conversation history
        conversation_context = "\n\nالمحادثة السابقة:\n"
        for msg in history[-10:]:  # Last 10 messages
            conversation_context += f"{msg['role']}: {msg['content']}\n"
        
        conversation_context += f"\nالعميل: {user_message}\nسارة:"
        
        try:
            # Generate response
            response = self.model.generate_content(
                full_prompt + conversation_context,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.7,
                )
            )
            
            ai_response = response.text.strip()
            
            # Check if escalation needed
            should_escalate = False
            escalation_reason = ""
            
            escalation_triggers = [
                "أحولك", "حولك", "مسؤول", "شكوى", "مشكلة كبيرة",
                "زعلان", "غاضب", "ما فهمت", "صعب"
            ]
            
            for trigger in escalation_triggers:
                if trigger in ai_response.lower() or trigger in user_message.lower():
                    should_escalate = True
                    escalation_reason = f"طلب تحويل أو موضوع معقد: {user_message[:50]}"
                    break
            
            # Save to history
            history.append({"role": "العميل", "content": user_message})
            history.append({"role": "سارة", "content": ai_response})
            self.conversations[user_phone] = history
            
            return {
                "response": ai_response,
                "should_escalate": should_escalate,
                "escalation_reason": escalation_reason
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "response": "عذراً، صار خطأ تقني. خلني أحولك لأحد الزملاء يساعدك 🙏",
                "should_escalate": True,
                "escalation_reason": f"Technical error: {str(e)}"
            }
    
    def get_greeting(self) -> str:
        """Return a greeting message"""
        return """هلا وغلا! 👋

أنا سارة من معهد لانجفورد الدولي 🎓

كيف أقدر أساعدك اليوم؟

1️⃣ كورسات اللغة الإنجليزية
2️⃣ التحضير لـ IELTS أو TOEFL
3️⃣ دورات المحاسبة والمالية
4️⃣ دبلومات HR والتسويق
5️⃣ كورسات اللغة الفرنسية

أو قولي شنو تبي وأنا أساعدك! 😊"""

    def clear_history(self, user_phone: str):
        """Clear conversation history for a user"""
        if user_phone in self.conversations:
            del self.conversations[user_phone]


# Global instance
sales_agent = SalesAgent()
