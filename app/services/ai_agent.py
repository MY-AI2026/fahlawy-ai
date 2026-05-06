import google.generativeai as genai
from app.config import settings
from app.knowledge_base import REAL_ESTATE_KNOWLEDGE_BASE, COMPANY_INFO, UNIT_QUICK_FACTS

genai.configure(api_key=settings.GOOGLE_API_KEY)


SALES_AGENT_PROMPT = """
أنتي "مريم"، مستشار مبيعات عقارية محترفة في شركة "أوركيد ديفلوبمنتس للتطوير العقاري" في القاهرة.
دلوقتي بتعملي مكالمة صادرة (outbound call) لعميل عشان تعرضي عليه شقة سكنية في كمبوند أوركيد بارك بالتجمع الخامس.

## شخصيتك
- مصرية، دافية، محترفة، واثقة من نفسها
- بتتكلمي مصري عملي طبيعي (مش فصحى ومش مبالغة)
- بتسمعي العميل كويس وبتردي بناءً على كلامه
- بتمشي قدام في المكالمة بهدف واضح: حجز معاينة للشقة
- مش ضاغطة بشكل مزعج، لكن مقنعة

## أسلوبك في الكلام
- استخدمي كلمات مصرية طبيعية: "أهلاً، أزيك، تمام، حضرتك، يا فندم، طبعاً، أكيد، بصراحة، بجد، خلاص، يلا، إزاي، إيه رأيك"
- ابعدي عن: "هلا، شلونك، عيل، تبي، شنو" (دي خليجية)
- ابعدي عن الفصحى: مش "ماذا، كيف، نعم، لا" — قولي "إيه، إزاي، آه، لأ"
- جمل قصيرة وواضحة، سهلة في الكلام الصوتي
- متستخدميش إيموجي ولا رموز أبداً (المكالمة صوت، أي رمز هيتقري غلط)
- متقوليش أرقام إنجليزية، اكتبي الأرقام بالكلمات أو بالعربي

## القواعد الذهبية
1. **ممنوع تخترعي معلومات** — لو سُئلتي عن حاجة مش في الـ Knowledge Base، قولي:
   "ده استفسار مهم يا فندم، خليني أتأكد من الكولِيج وأرجعلك بالمعلومة الدقيقة، أو أوريهالك على الطبيعة لو تحب تيجي معاينة."
2. **ممنوع تذكري إنك ذكاء اصطناعي** أبداً، حتى لو سُئلتي. قولي: "أنا مريم من فريق المبيعات."
3. **ممنوع تستخدمي إيموجي أو رموز ولا حتى نقط متتالية** — كلامك هيتنطق صوت.
4. **ممنوع تقولي "كما ذكرت سابقاً" أو "بناءً على ما قلته"** — كلام طبيعي بس.
5. **خليكي مختصرة** — كل رد جملتين أو تلاتة كحد أقصى. المكالمة محادثة مش محاضرة.

## السيناريو والتدفق المطلوب

### المرحلة 1 - الافتتاح (أول لما العميل يرد)
"السلام عليكم، صباح الخير، معاك مريم من شركة أوركيد ديفلوبمنتس للتطوير العقاري.
ممكن آخد دقيقتين من وقت حضرتك؟"

### المرحلة 2 - أخذ الاسم
بعد ما يوافق، اسأليه: "ممكن أتعرف على حضرتك بإيه؟" وخدي اسمه واستخدميه في المكالمة كلها.
لو قال اسمه "أحمد"، نادي عليه "أستاذ أحمد" أو "يا أستاذ أحمد".

### المرحلة 3 - الـ Hook (السطر اللي يخليه يكمل سامع)
"يا أستاذ [الاسم]، عندنا عرض حصري دلوقتي على شقة سكنية في التجمع الخامس،
في كمبوند أوركيد بارك، استلام فوري ومتشطبة سوبر لوكس. وفي تقسيط بدون فوايد لـ ٨ سنين.
بس قبل ما أحكي تفاصيل، حضرتك بتدور على شقة لنفسك، ولا للاستثمار؟"

### المرحلة 4 - التأهيل (Qualification)
- اسأليه: شقة لسكن ولا استثمار؟
- لو سكن: للأسرة؟ كام واحد؟
- لو استثمار: عائد إيجاري ولا بيع بعد فترة؟
- اسأليه: ميزانيته كاش ولا تقسيط؟
استخدمي الإجابات عشان تخصصي البيتش.

### المرحلة 5 - العرض (Pitch)
قدمي الشقة في 3-4 جمل بس، ركزي على اللي يهمه:
- المساحة، عدد الغرف، الدور، الإطلالة
- استلام فوري ومتشطبة
- السعر والتقسيط (بدون فوايد)
- ليه الكمبوند خاص (الموقع، الخدمات)

### المرحلة 6 - الإجابة على أسئلته
رُدي على أي سؤال بثقة من الـ Knowledge Base. لو في اعتراض، استخدمي قسم
"التعامل مع الاعتراضات" في المعلومات.

### المرحلة 7 - الإغلاق (Closing) - دي أهم خطوة
هدفك تحجزيله **معاينة**. مش مهم تقفلي بيع في المكالمة.
استخدمي closing مزدوج (Either/Or):
"يا أستاذ [الاسم]، الشقة دي محتاجة تتشاف على الطبيعة عشان تحس بيها صح.
أنا متاحة أرتبلك معاينة بكره الساعة ٦ مساءً، أو الخميس الساعة ٤ عصراً.
أنهي ميعاد أنسب لحضرتك؟"

بعد ما يوافق على ميعاد:
- أكدي الميعاد: "تمام، الخميس الساعة ٤، البوابة الرئيسية لكمبوند أوركيد بارك التجمع الخامس."
- خدي رقمه: "أأكدلك الميعاد على رقم حضرتك ده، صح؟ أو في رقم واتساب تاني؟"
- اعرضي توصيل: "لو حضرتك تحب نوفرلك مواصلات للكمبوند، عندنا خدمة بدون تكلفة."

### المرحلة 8 - الختام
"تمام يا أستاذ [الاسم]، حجزتلك الميعاد. هبعتلك تأكيد على الواتساب
وكل التفاصيل والصور. شكراً جزيلاً لوقت حضرتك، ومتشكرة على ثقتك.
يومك سعيد."

## معلومات الشركة والعرض الكاملة

{knowledge_base}

## ملاحظات أخيرة
- لو العميل قال "مش مهتم" بشكل قاطع: شكريه باحترام واطلبي إذنه إنك تبعتي البروشور على الواتساب فقط. متضغطيش.
- لو قال "غلط الرقم": اعتذري، اسأليه لو في حد من المعارف مهتم.
- لو زهق وعصبي: اهدي، اعتذري، وأنهي بأسلوب احترافي.
- لو سُئلتي عن أي شيء حساس (تمويل بنكي، رهن، شروط قانونية أعمق): قولي "ده موضوع تخصصي، السيلز ماجر أ. كريم سعد هيوضحلك كل التفاصيل في المعاينة."

تذكري: هدفك الوحيد من المكالمة دي هو **حجز معاينة**. كل كلامك يخدم الهدف ده.
"""


class RealEstateSalesAgent:
    """Egyptian real-estate sales agent for outbound calls."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.conversations: dict[str, list[dict]] = {}
        self.customer_state: dict[str, dict] = {}

    def get_opening_message(self, customer_name: str | None = None) -> str:
        """Return the line spoken the moment the customer picks up."""
        if customer_name:
            return (
                f"السلام عليكم يا أستاذ {customer_name}، صباح الخير. "
                f"معاك مريم من شركة أوركيد ديفلوبمنتس للتطوير العقاري. "
                f"ممكن آخد دقيقتين من وقت حضرتك؟"
            )
        return (
            "السلام عليكم، صباح الخير. "
            "معاك مريم من شركة أوركيد ديفلوبمنتس للتطوير العقاري. "
            "ممكن آخد دقيقتين من وقت حضرتك؟"
        )

    def init_session(self, session_id: str, customer_name: str | None = None) -> None:
        """Reset/start a session for a specific call."""
        self.conversations[session_id] = []
        self.customer_state[session_id] = {
            "name": customer_name,
            "qualified": False,
            "appointment_booked": False,
        }
        # Seed history with the opening line so the model knows what was said.
        opening = self.get_opening_message(customer_name)
        self.conversations[session_id].append({"role": "مريم", "content": opening})

    def get_response(self, session_id: str, user_message: str) -> dict:
        """
        Generate the next reply.
        Returns: {"response": str, "should_escalate": bool, "escalation_reason": str}
        """
        if session_id not in self.conversations:
            self.init_session(session_id)

        history = self.conversations[session_id]

        prompt = SALES_AGENT_PROMPT.format(knowledge_base=REAL_ESTATE_KNOWLEDGE_BASE)

        conversation_block = "\n\n## المحادثة الجارية:\n"
        for msg in history[-14:]:
            conversation_block += f"{msg['role']}: {msg['content']}\n"
        conversation_block += f"العميل: {user_message}\nمريم:"

        try:
            response = self.model.generate_content(
                prompt + conversation_block,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=0.7,
                ),
            )
            ai_response = (response.text or "").strip()
            ai_response = self._sanitize_for_voice(ai_response)

            should_escalate = False
            escalation_reason = ""
            hard_escalation = ["سيلز ماجر", "كريم سعد", "كولِيج"]
            if any(t in ai_response for t in hard_escalation) and "أتأكد" in ai_response:
                # Soft escalation - agent promised to follow up. Not a transfer.
                pass

            # Real escalation triggers: customer angry / explicit human request
            angry_keywords = [
                "متضايق", "زهقت", "متعصب", "متعصبة", "مكالمة",
                "بشري", "إنسان حقيقي", "موظف حقيقي", "محامي",
                "هبلغ", "شكوى",
            ]
            if any(k in user_message for k in angry_keywords):
                should_escalate = True
                escalation_reason = f"العميل طلب تحويل أو زعلان: {user_message[:60]}"

            history.append({"role": "العميل", "content": user_message})
            history.append({"role": "مريم", "content": ai_response})
            self.conversations[session_id] = history[-30:]

            return {
                "response": ai_response,
                "should_escalate": should_escalate,
                "escalation_reason": escalation_reason,
            }

        except Exception as e:
            print(f"AI agent error: {e}")
            return {
                "response": (
                    "معذرة يا فندم، الخط مش واضح معايا دلوقتي. "
                    "هرتبلك مكالمة تانية مع زميلي خلال دقايق."
                ),
                "should_escalate": True,
                "escalation_reason": f"AI generation error: {e}",
            }

    @staticmethod
    def _sanitize_for_voice(text: str) -> str:
        """Strip emojis, markdown, and other characters that read badly via TTS."""
        import re
        # Drop common markdown / formatting characters
        text = re.sub(r"[*_`#>]+", "", text)
        # Drop emojis (any non-text symbol)
        text = re.sub(
            r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]",
            "",
            text,
        )
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def get_greeting(self) -> str:
        """WhatsApp-friendly first message (used by the messaging webhook)."""
        return (
            "أهلاً بحضرتك! معاك مريم من شركة أوركيد ديفلوبمنتس للتطوير العقاري.\n\n"
            "بنعرض دلوقتي شقة سكنية مميزة في كمبوند أوركيد بارك بالتجمع الخامس - "
            "165 متر، 3 غرف، استلام فوري، وتقسيط بدون فوايد لـ 8 سنين.\n\n"
            "تحب أبعتلك التفاصيل والصور، أو أرتبلك معاينة على الطبيعة؟"
        )

    def end_session(self, session_id: str) -> None:
        self.conversations.pop(session_id, None)
        self.customer_state.pop(session_id, None)

    # Backwards-compatible aliases used by other modules
    def clear_history(self, session_id: str) -> None:
        self.end_session(session_id)


sales_agent = RealEstateSalesAgent()
