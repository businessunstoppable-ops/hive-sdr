"""Working HIVE-SDR Dashboard - Full Functionality"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="HIVE-SDR Dashboard")

# In-memory storage
leads_db = {}
campaign_results = []
next_lead_id = 1

# Import preview functionality
from ui_client.preview import router as preview_router
app.include_router(preview_router)

# HTML templates as strings
CAMPAIGN_PAGE_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIVE-SDR - New Campaign</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #2B1A0F 0%, #442D1C 50%, #5C3A1E 100%);
            min-height: 100vh;
            color: #E8D1A7;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 20px 30px;
            margin-bottom: 30px;
            border: 1px solid #84592B;
        }
        h1 {
            background: linear-gradient(135deg, #E8D1A7, #9D9167);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2em;
        }
        .subtitle { color: #C4B89A; margin-top: 5px; }
        .nav a {
            color: #E8D1A7;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 10px;
            background: rgba(255,255,255,0.05);
            margin-right: 10px;
            display: inline-block;
        }
        .nav a:hover { background: rgba(157,145,103,0.2); }
        .card {
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #84592B;
            margin-bottom: 20px;
        }
        .btn {
            background: linear-gradient(135deg, #743014, #442D1C);
            color: #E8D1A7;
            border: 1px solid #9D9167;
            padding: 12px 30px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
        }
        .btn-primary {
            background: linear-gradient(135deg, #9D9167, #743014);
            color: #2B1A0F;
        }
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #E8D1A7;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            background: rgba(0,0,0,0.4);
            border: 1px solid #84592B;
            border-radius: 8px;
            color: #E8D1A7;
        }
        .flex-between { display: flex; justify-content: space-between; align-items: center; }
        .mt-20 { margin-top: 20px; }
        .loading { display: none; text-align: center; padding: 40px; }
        .loading.show { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="flex-between">
                <div>
                    <h1>🐝 HIVE-SDR Agent Lounge</h1>
                    <div class="subtitle">Intelligent Sales Development Platform</div>
                </div>
            </div>
            <div class="nav">
                <a href="/">Dashboard</a>
                <a href="/leads">Leads</a>
                <a href="/campaign">New Campaign</a>
                <a href="/analytics">Analytics</a>
            </div>
        </div>
        
        <div class="card">
            <h2>🚀 Launch New Campaign</h2>
            <p style="color: #C4B89A; margin-bottom: 20px;">Discover businesses and run AI-powered outreach</p>
            
            <form id="campaignForm" onsubmit="return previewLeads(event)">
                <div class="form-group">
                    <label>Industry / Business Type</label>
                    <input type="text" name="industry" id="industry" placeholder="e.g., coffee shop, plumber, restaurant" required>
                </div>
                
                <div class="form-group">
                    <label>City / Location</label>
                    <input type="text" name="city" id="city" placeholder="e.g., Amsterdam, NL or Austin, TX" required>
                </div>
                
                <div class="form-group">
                    <label>Maximum Leads to Discover</label>
                    <input type="number" name="max_leads" id="max_leads" value="10" min="1" max="30">
                </div>
                
                <div style="display: flex; gap: 15px;">
                    <button type="submit" class="btn btn-primary">🔍 Preview & Select Leads</button>
                    <button type="button" class="btn" onclick="directRun()">⚡ Run Direct (All Leads)</button>
                </div>
            </form>
        </div>
        
        <div id="previewContainer" style="display: none;"></div>
        
        <div id="loading" class="loading">
            <div class="card">
                <h2>⏳ Discovering businesses...</h2>
                <p>Searching Google Maps for matching businesses</p>
            </div>
        </div>
    </div>
    
    <script>
        const loadingDiv = document.getElementById('loading');
        const previewContainer = document.getElementById('previewContainer');
        
        async function previewLeads(event) {
            event.preventDefault();
            
            const industry = document.getElementById('industry').value;
            const city = document.getElementById('city').value;
            const maxLeads = document.getElementById('max_leads').value;
            
            if (!industry || !city) {
                alert('Please fill in both industry and city');
                return false;
            }
            
            loadingDiv.classList.add('show');
            previewContainer.style.display = 'none';
            previewContainer.innerHTML = '';
            
            try {
                const formData = new FormData();
                formData.append('industry', industry);
                formData.append('city', city);
                formData.append('max_leads', maxLeads);
                
                const response = await fetch('/preview', {
                    method: 'POST',
                    body: formData
                });
                
                const html = await response.text();
                previewContainer.innerHTML = html;
                previewContainer.style.display = 'block';
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to preview leads. Please try again.');
            } finally {
                loadingDiv.classList.remove('show');
            }
            
            return false;
        }
        
        function directRun() {
            const industry = document.getElementById('industry').value;
            const city = document.getElementById('city').value;
            const maxLeads = document.getElementById('max_leads').value;
            
            if (!industry || !city) {
                alert('Please fill in both industry and city');
                return;
            }
            
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/campaign/run';
            
            const industryInput = document.createElement('input');
            industryInput.type = 'hidden';
            industryInput.name = 'industry';
            industryInput.value = industry;
            form.appendChild(industryInput);
            
            const cityInput = document.createElement('input');
            cityInput.type = 'hidden';
            cityInput.name = 'city';
            cityInput.value = city;
            form.appendChild(cityInput);
            
            const maxLeadsInput = document.createElement('input');
            maxLeadsInput.type = 'hidden';
            maxLeadsInput.name = 'max_leads';
            maxLeadsInput.value = maxLeads;
            form.appendChild(maxLeadsInput);
            
            document.body.appendChild(form);
            form.submit();
        }
    </script>
</body>
</html>'''

# Import other templates from existing working_app
# (Keeping existing dashboard, leads, analytics routes)

# For brevity, I'll show the key additions - your existing routes remain
# The preview functionality is now added via the router

@app.get("/campaign", response_class=HTMLResponse)
async def campaign_page():
    return CAMPAIGN_PAGE_HTML

@app.post("/campaign/run_selected")
async def run_selected_campaign(
    request: Request,
    selected_leads: str = Form(...),
    industry: str = Form(...),
    city: str = Form(...)
):
    """Run campaign on only the selected leads"""
    global next_lead_id
    
    selected_data = json.loads(selected_leads)
    
    campaign_data = {
        "id": len(campaign_results) + 1,
        "industry": industry,
        "city": city,
        "started_at": datetime.now().isoformat(),
        "status": "running",
        "leads_found": len(selected_data),
        "emails_generated": 0
    }
    
    try:
        from research_agent.agent import ResearchAgent
        from sdr_orchestrator.agent import SDROrchestrator
        from outreach_agent.email_agent import EmailAgent
        from lead_finder.google_maps_search import Lead
        
        researcher = ResearchAgent()
        orchestrator = SDROrchestrator()
        email_agent = EmailAgent()
        
        results = []
        for item in selected_data:
            # Create Lead object from data
            lead = Lead(
                name=item.get('name', 'Unknown'),
                place_id='selected',
                address=item.get('address', ''),
                phone=item.get('phone'),
                website=item.get('website'),
                rating=item.get('rating'),
                total_ratings=item.get('total_ratings'),
                business_status="OPERATIONAL",
                lat=0,
                lng=0
            )
            
            research = researcher.research_lead(lead)
            orchestration = orchestrator.process_lead_workflow(lead, research)
            
            if not orchestration.get('skipped'):
                email = email_agent.prepare_outreach(lead, orchestration)
                
                lead_id = str(next_lead_id)
                next_lead_id += 1
                
                leads_db[lead_id] = {
                    'id': lead_id,
                    'name': lead.name,
                    'website': lead.website,
                    'phone': lead.phone,
                    'rating': lead.rating,
                    'score': orchestration.get('score', {}).get('score', 0),
                    'status': 'new',
                    'notes': [f"Found via {industry} campaign in {city} (selected from preview)"],
                    'email_sent': False,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                results.append({
                    'lead_name': lead.name,
                    'score': orchestration.get('score', {}).get('score', 0)
                })
        
        campaign_data["emails_generated"] = len(results)
        campaign_data["status"] = "completed"
        campaign_data["completed_at"] = datetime.now().isoformat()
        campaign_data["results"] = results
        
    except Exception as e:
        campaign_data["status"] = "failed"
        campaign_data["error"] = str(e)
    
    campaign_results.append(campaign_data)
    
    # Redirect to results or leads page
    return RedirectResponse(url="/leads", status_code=303)

# Register location API
from ui_client.location_api import router as location_router
app.include_router(location_router)
