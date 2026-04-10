"""Simple test dashboard - no database dependencies"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="HIVE-SDR Test")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_leads": 0,
        "avg_score": 0,
        "emails_sent": 0,
        "follow_ups": 0,
        "recent_leads": [],
        "campaigns": []
    })

@app.get("/health")
async def health():
    return {"status": "ok"}
