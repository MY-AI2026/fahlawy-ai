# 🎓 Langford AI Sales Agent

مساعد مبيعات بالذكاء الاصطناعي لمعهد لانجفورد الدولي - يعمل على WhatsApp والمكالمات الصوتية.

![Dashboard Preview](https://img.shields.io/badge/Status-Active-green) ![Python](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal)

---

## ✨ المميزات

- 💬 **WhatsApp Bot** - يرد على رسائل العملاء تلقائياً
- 📞 **Voice Calls** - يستقبل المكالمات ويرد بصوت عربي واقعي
- 🤖 **AI Sales Agent** - يفهم ويقنع بالعربي الكويتي
- 🎤 **ElevenLabs TTS** - صوت عربي واقعي عالي الجودة
- 👂 **Deepgram STT** - يفهم كلام العميل بدقة
- 🔄 **Human Escalation** - يحول للموظف في الحالات المعقدة
- 📊 **Dashboard** - لوحة تحكم لمتابعة المحادثات

---

## 🚀 النشر على Railway (أسهل طريقة!)

### الخطوة 1: Fork هذا المشروع
اضغط على "Fork" في GitHub

### الخطوة 2: اربط بـ Railway
1. اذهب إلى [railway.app](https://railway.app)
2. سجل دخول بحساب GitHub
3. اضغط "New Project" → "Deploy from GitHub repo"
4. اختر مشروع `langford-ai`

### الخطوة 3: أضف المتغيرات
في Railway، اذهب إلى Settings → Variables وأضف:

```
TWILIO_ACCOUNT_SID=AC961606bc87050409
TWILIO_API_KEY=SK0e544a79162dab9547baaf7c4bf2ef1d
TWILIO_API_SECRET=WHs5z5r0BW0wgqpdExXwZi1YBydrsaMl
TWILIO_WHATSAPP_NUMBER=+14155238886
TWILIO_PHONE_NUMBER=+14642669684
GOOGLE_API_KEY=AIzaSyBYmyco1mFnpxKuXQR7FhyaWpaulTH6PCc
DEEPGRAM_API_KEY=e6aa62cb509a4b91a7eb7e5ab5fc38df68fa5420
ELEVENLABS_API_KEY=sk_23e90de5bad54b7e8e1445199eb62a36aa701074ad92d99f
ESCALATION_PHONE=+96551600140
```

### الخطوة 4: احصل على الرابط
بعد الـ Deploy، Railway هيعطيك رابط مثل:
```
https://langford-ai-production.up.railway.app
```

### الخطوة 5: إعداد Twilio Webhooks

#### للواتساب:
1. Twilio Console → Messaging → WhatsApp Sandbox
2. When message comes in: `https://رابطك.railway.app/api/webhook/whatsapp`

#### للمكالمات:
1. Twilio Console → Phone Numbers → +14642669684
2. Voice Webhook: `https://رابطك.railway.app/api/voice/incoming`

---

## 🖥️ Dashboard

افتح الرابط في المتصفح:
```
https://رابطك.railway.app
```

ستجد:
- 📊 إحصائيات المحادثات والمكالمات
- 💬 آخر المحادثات
- 🧪 تجربة البوت مباشرة
- ⚙️ الإعدادات

---

## 📁 هيكل المشروع

```
langford-ai/
├── app/
│   ├── main.py              # التطبيق الرئيسي + Dashboard
│   ├── config.py            # الإعدادات
│   ├── knowledge_base.py    # معلومات المعهد
│   ├── api/
│   │   ├── webhooks.py      # WhatsApp
│   │   └── voice.py         # المكالمات
│   └── services/
│       ├── ai_agent.py      # الذكاء الاصطناعي
│       ├── whatsapp.py      # خدمة الواتساب
│       ├── voice.py         # خدمة المكالمات
│       ├── elevenlabs.py    # تحويل النص لصوت
│       └── deepgram.py      # تحويل الصوت لنص
├── frontend/
│   └── templates/
│       └── dashboard.html   # واجهة المستخدم
├── requirements.txt
├── Procfile
├── railway.json
└── README.md
```

---

## 🔧 التشغيل المحلي

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/langford-ai.git
cd langford-ai

# 2. Create .env
cp .env.example .env
# Edit .env with your keys

# 3. Install
pip install -r requirements.txt

# 4. Run
uvicorn app.main:app --reload --port 8000

# 5. Open
# http://localhost:8000
```

---

## 📞 كيف تعمل المكالمات

```
العميل يتصل 📞
     ↓
Twilio يستقبل → /api/voice/incoming
     ↓
سارة ترد: "هلا وغلا!" (ElevenLabs)
     ↓
العميل يتكلم → Deepgram يحول لنص
     ↓
Gemini AI يفهم ويرد
     ↓
ElevenLabs يحول الرد لصوت
     ↓
العميل يسمع 🔊
```

---

## 💬 كيف يعمل WhatsApp

```
العميل يرسل رسالة 💬
     ↓
Twilio Webhook → /api/webhook/whatsapp
     ↓
Gemini AI يفهم ويرد
     ↓
الرد يرجع للعميل ✅
```

---

## 🎯 أمثلة المحادثات

| العميل يقول | سارة ترد |
|-------------|----------|
| "هلا" | "هلا وغلا! أنا سارة من معهد لانجفورد. كيف أقدر أساعدك؟" |
| "ابي انجليزي" | "عندنا كورسات إنجليزي ممتازة! من A1 لـ C1. تبي كورس عام ولا IELTS؟" |
| "كم السعر" | "الأسعار تعتمد على الكورس. تبي أحولك لفريق التسجيل؟" |
| "وين موقعكم" | "موقعنا في صباح السالم، بلوك 1. تقدر تزورنا أو ندرسك أونلاين!" |

---

## ⚙️ الإعدادات

| المتغير | الوصف |
|---------|-------|
| `TWILIO_ACCOUNT_SID` | معرف حساب Twilio |
| `TWILIO_API_KEY` | مفتاح API |
| `TWILIO_API_SECRET` | السر |
| `GOOGLE_API_KEY` | مفتاح Gemini |
| `DEEPGRAM_API_KEY` | مفتاح Deepgram |
| `ELEVENLABS_API_KEY` | مفتاح ElevenLabs |
| `ESCALATION_PHONE` | رقم التحويل |

---

## 📊 APIs

| Endpoint | Method | الوصف |
|----------|--------|-------|
| `/` | GET | Dashboard |
| `/health` | GET | فحص الصحة |
| `/api/webhook/whatsapp` | POST | WhatsApp Webhook |
| `/api/voice/incoming` | POST | Voice Webhook |
| `/api/test/chat` | POST | تجربة المحادثة |
| `/api/stats` | GET | الإحصائيات |

---

## 🆘 المساعدة

لو واجهتك مشكلة:
1. تأكد من المتغيرات في Railway
2. تأكد من Twilio Webhooks
3. جرب `/health` للتأكد إن السيرفر شغال

---

## 📄 License

MIT License - استخدمه زي ما تبي!

---

**صنع بـ ❤️ لمعهد لانجفورد الدولي**
