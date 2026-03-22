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
    description="AI Sales Agent for Langford International Institute - Voice & WhatsApp",
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
    return templates.TemplateResponse(request, "landing.html")

@app.get("/landing-ar", response_class=HTMLResponse)
async def landing_page_ar(request: Request):
    """Serve the Arabic landing page"""
    return templates.TemplateResponse(request, "landing_ar.html")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve the registration page"""
    return templates.TemplateResponse(request, "register.html")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page"""
    return templates.TemplateResponse(request, "login.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Serve the system admin panel"""
    return templates.TemplateResponse(request, "admin.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the main dashboard"""
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/call-logs", response_class=HTMLResponse)
async def call_logs_page(request: Request):
    """Serve the call logs page"""
    return templates.TemplateResponse(request, "call_logs.html")

@app.get("/real-estate", response_class=HTMLResponse)
async def real_estate_page(request: Request):
    """Serve the real estate dashboard"""
    return templates.TemplateResponse(request, "real_estate.html")

@app.get("/knowledge-base", response_class=HTMLResponse)
async def knowledge_base_page(request: Request):
    """Serve the knowledge base management page"""
    return templates.TemplateResponse(request, "knowledge_base.html")

@app.get("/agent-editor", response_class=HTMLResponse)
async def agent_editor_page(request: Request):
    """Serve the AI agent configuration page"""
    return templates.TemplateResponse(request, "agent_editor.html")

@app.get("/campaigns", response_class=HTMLResponse)
async def campaigns_page(request: Request):
    """Serve the campaign management page"""
    return templates.TemplateResponse(request, "campaigns.html")

@app.get("/campaign-builder", response_class=HTMLResponse)
async def campaign_builder_page(request: Request):
    """Serve the campaign builder wizard"""
    return templates.TemplateResponse(request, "campaign_builder.html")

@app.get("/billing", response_class=HTMLResponse)
async def billing_page(request: Request):
    """Serve the billing and subscriptions page"""
    return templates.TemplateResponse(request, "billing.html")

@app.get("/api-portal", response_class=HTMLResponse)
async def api_portal_page(request: Request):
    """Serve the developer API portal"""
    return templates.TemplateResponse(request, "api_portal.html")

@app.get("/call-analysis", response_class=HTMLResponse)
async def call_analysis_page(request: Request):
    """Serve the deep-dive call analysis page"""
    return templates.TemplateResponse(request, "call_analysis.html")

@app.get("/tenants", response_class=HTMLResponse)
async def tenants_page(request: Request):
    """Serve the tenant management page"""
    return templates.TemplateResponse(request, "tenants.html")

@app.get("/integrations", response_class=HTMLResponse)
async def integrations_page(request: Request):
    """Serve the CRM integration hub"""
    return templates.TemplateResponse(request, "integrations.html")

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
