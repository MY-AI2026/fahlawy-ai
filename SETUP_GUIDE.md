# 📖 دليل التشغيل خطوة بخطوة

## 🎯 الهدف
تشغيل فهلوي AI على الإنترنت ليعمل 24/7

---

## 📋 المتطلبات (عندك كلها ✅)

| الخدمة | الحالة |
|--------|--------|
| Twilio Account | ✅ |
| WhatsApp Sandbox | ✅ |
| Gemini API | ✅ |
| Deepgram API | ✅ |
| ElevenLabs API | ✅ |

---

# 🚀 الخطوات

## الخطوة 1: إنشاء حساب GitHub

1. افتح: **https://github.com/signup**
2. سجل بإيميلك
3. أكد الإيميل

---

## الخطوة 2: رفع المشروع على GitHub

### الطريقة السهلة (من المتصفح):

1. **سجل دخول GitHub**

2. **اضغط "+" في أعلى اليمين → "New repository"**

3. **املأ البيانات:**
   - Repository name: `fahlawy-ai`
   - Description: `AI Sales Agent`
   - اختر: **Public**
   - ✅ Add a README file
   
4. **اضغط "Create repository"**

5. **ارفع الملفات:**
   - اضغط "Add file" → "Upload files"
   - اسحب كل ملفات المشروع
   - اضغط "Commit changes"

---

## الخطوة 3: إنشاء حساب Railway

1. **افتح: https://railway.app**

2. **اضغط "Login" → "Login with GitHub"**

3. **وافق على الصلاحيات**

---

## الخطوة 4: ربط المشروع بـ Railway

1. **في Railway، اضغط "New Project"**

2. **اختر "Deploy from GitHub repo"**

3. **اختر `fahlawy-ai`**

4. **انتظر... Railway يبني المشروع تلقائياً**

---

## الخطوة 5: إضافة المتغيرات (مهم جداً!)

1. **في Railway، اضغط على المشروع**

2. **اذهب إلى "Variables" أو "Settings → Environment"**

3. **أضف كل المتغيرات التالية (انسخ والصق):**

```
TWILIO_ACCOUNT_SID=AC961606bc87050409
TWILIO_API_KEY=SK0e544a79162dab9547baaf7c4bf2ef1d
TWILIO_API_SECRET=WHs5z5r0BW0wgqpdExXwZi1YBydrsaMl
TWILIO_WHATSAPP_NUMBER=+14155238886
TWILIO_PHONE_NUMBER=+14642669684
GOOGLE_API_KEY=AIzaSyBYmyco1mFnpxKuXQR7FhyaWpaulTH6PCc
DEEPGRAM_API_KEY=e6aa62cb509a4b91a7eb7e5ab5fc38df68fa5420
ELEVENLABS_API_KEY=sk_23e90de5bad54b7e8e1445199eb62a36aa701074ad92d99f
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL
ESCALATION_PHONE=+96551600140
APP_NAME=Fahlawy AI
DEBUG=False
PUBLIC_URL=https://fahlawy-ai-production.up.railway.app
```

4. **اضغط "Save" أو "Add"**

---

## الخطوة 6: الحصول على الرابط

1. **بعد اكتمال الـ Deploy، اذهب إلى "Settings"**

2. **ابحث عن "Domains" أو "Generate Domain"**

3. **اضغط "Generate Domain"**

4. **ستحصل على رابط مثل:**
   ```
   https://fahlawy-ai-production.up.railway.app
   ```

5. **📝 احفظ هذا الرابط!**

---

## الخطوة 7: إعداد Twilio للمكالمات

1. **افتح Twilio Console: https://console.twilio.com**

2. **اذهب إلى: Phone Numbers → Manage → Active Numbers**

3. **اضغط على رقمك: `+14642669684`**

4. **في قسم "Voice & Fax":**
   - **A CALL COMES IN:** اختر Webhook
   - **URL:** الصق رابطك + `/api/voice/incoming`
   
   مثال:
   ```
   https://fahlawy-ai-production.up.railway.app/api/voice/incoming
   ```
   
   - **HTTP:** اختر POST

5. **اضغط "Save"**

---

## الخطوة 8: إعداد Twilio للواتساب

1. **في Twilio، اذهب إلى: Messaging → Try it out → Send a WhatsApp message**

2. **اضغط "Sandbox settings"**

3. **في "WHEN A MESSAGE COMES IN":**
   - الصق رابطك + `/api/webhook/whatsapp`
   
   مثال:
   ```
   https://fahlawy-ai-production.up.railway.app/api/webhook/whatsapp
   ```

4. **اضغط "Save"**

---

## ✅ تم! جرب الآن

### تجربة الموقع:
افتح رابطك في المتصفح:
```
https://fahlawy-ai-production.up.railway.app
```

### تجربة الواتساب:
1. من موبايلك، ابعت للرقم: `+1 415 523 8886`
2. الرسالة: `join girl-slipped`
3. بعدين قول: `هلا`

### تجربة المكالمات:
اتصل على: `+1 464 266 9684`

---

## 🆘 حل المشاكل

### المشكلة: الموقع لا يعمل
- تأكد من إضافة كل المتغيرات في Railway
- انتظر 2-3 دقائق بعد الـ Deploy

### المشكلة: الواتساب لا يرد
- تأكد من رابط الـ Webhook في Twilio
- تأكد أنك متصل بالـ Sandbox

### المشكلة: المكالمات لا تعمل
- تأكد من رابط Voice Webhook في Twilio
- تأكد أن الرقم صحيح

### ⚠️ المشكلة: الذكاء الاصطناعي يرد على المكالمة لكن لا يتكلم (عند الاتصال من الموقع)
**السبب:** عند الاتصال من الموقع (Outbound Call)، Twilio يحاول يجيب ملف TwiML من السيرفر.
إذا الرابط المُرسل لـ Twilio كان عنوان داخلي (مثل `http://localhost` أو عنوان Railway الداخلي)،
Twilio ما يقدر يوصله، فالمكالمة تتصل بدون صوت.

**الحل:** أضف هذا المتغير في Railway:
```
PUBLIC_URL=https://fahlawy-ai-production.up.railway.app
```
⚠️ **استبدل الرابط برابط مشروعك الفعلي على Railway**

---

## 📞 تحتاج مساعدة؟

لو واجهتك أي مشكلة:
1. خذ screenshot للخطأ
2. ابعثها وأنا أساعدك!

---

**🎉 مبروك! فهلوي AI يعمل الآن 24/7**
