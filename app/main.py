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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
