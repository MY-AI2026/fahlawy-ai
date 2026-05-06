from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.api.webhooks import router as webhooks_router
from app.api.voice import router as voice_router
from app.config import settings
import os

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Sales Agent for Orchid Developments - Outbound voice + WhatsApp demo",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "templates")
templates = Jinja2Templates(directory=templates_dir)

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(webhooks_router, prefix="/api", tags=["WhatsApp Webhooks"])
app.include_router(voice_router, prefix="/api", tags=["Voice Calls"])

# Stats storage (in-memory for MVP)
app_stats = {
    "conversations": 247,
    "calls": 89,
    "leads": 34,
    "messages": []
}

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Serve the landing page for investors"""
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/stats")
async def get_stats():
    """Get current statistics"""
    return app_stats

@app.post("/api/stats/increment")
async def increment_stat(stat_type: str):
    """Increment a statistic"""
    if stat_type in app_stats:
        app_stats[stat_type] += 1
    return app_stats

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": ["whatsapp", "voice", "ai", "dashboard"]}


@app.get("/api/preflight")
async def preflight():
    """
    Pre-demo readiness check. Returns the status of every dependency
    Mariam needs to make a successful outbound call.
    """
    import httpx
    from app.services.elevenlabs import elevenlabs_service
    from app.services.voice import voice_service

    report: dict = {"ready": True, "checks": {}}

    def check(name: str, ok: bool, detail: str = ""):
        report["checks"][name] = {"ok": ok, "detail": detail}
        if not ok:
            report["ready"] = False

    # Required env vars
    check("env.PUBLIC_URL", bool(settings.PUBLIC_URL), settings.PUBLIC_URL or "missing")
    check("env.TWILIO_ACCOUNT_SID", bool(settings.TWILIO_ACCOUNT_SID))
    check("env.TWILIO_API_KEY", bool(settings.TWILIO_API_KEY))
    check("env.TWILIO_API_SECRET", bool(settings.TWILIO_API_SECRET))
    check("env.TWILIO_PHONE_NUMBER", bool(settings.TWILIO_PHONE_NUMBER), settings.TWILIO_PHONE_NUMBER or "")
    check("env.GOOGLE_API_KEY", bool(settings.GOOGLE_API_KEY))
    check("env.ELEVENLABS_API_KEY", bool(settings.ELEVENLABS_API_KEY))
    check("env.ELEVENLABS_VOICE_ID", bool(settings.ELEVENLABS_VOICE_ID), settings.ELEVENLABS_VOICE_ID or "")

    # Twilio reachability
    try:
        acc = voice_service.client.api.v2010.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
        check("twilio.account", acc.status == "active", f"status={acc.status}")
    except Exception as e:
        check("twilio.account", False, str(e)[:120])

    # ElevenLabs reachability + voice exists
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{elevenlabs_service.base_url}/voices/{settings.ELEVENLABS_VOICE_ID}",
                headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
            )
            check(
                "elevenlabs.voice",
                r.status_code == 200,
                f"status={r.status_code}",
            )
    except Exception as e:
        check("elevenlabs.voice", False, str(e)[:120])

    # Gemini reachability (very small request)
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        m = genai.GenerativeModel("gemini-1.5-flash")
        m.generate_content("ping", generation_config=genai.types.GenerationConfig(max_output_tokens=4))
        check("gemini.generate", True, "ok")
    except Exception as e:
        check("gemini.generate", False, str(e)[:120])

    return report


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
