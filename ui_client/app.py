from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import os
import sys
from datetime import datetime
import asyncio
import json
import uuid
import io
import csv
import hmac
import hashlib
import stripe

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lead_manager.agent import LeadManagerAgent

app = FastAPI(title="HIVE-SDR")
manager = LeadManagerAgent()
campaign_results = []
pending_campaigns = {}

app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- Stripe ----------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:54609")

# ---------- WebSocket ----------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager_ws = ConnectionManager()

async def broadcast_stats():
    stats = manager.get_dashboard()
    await manager_ws.broadcast({"type": "stats", "data": stats})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager_ws.connect(websocket)
    try:
        stats = manager.get_dashboard()
        await websocket.send_json({"type": "stats", "data": stats})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager_ws.disconnect(websocket)

# ---------- Helper ----------
def calculate_lead_price(lead):
    base_price = 20
    score = lead.get("score", 5)
    rating = lead.get("rating", 0)
    if score >= 8:
        base_price += 30
    elif score >= 6:
        base_price += 10
    if rating >= 4.5:
        base_price += 20
    elif rating >= 4.0:
        base_price += 10
    return min(base_price, 100)

# ---------- HTML header with themes ----------
def html_header(title="HIVE-SDR"):
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --bg-body: #532D1C;
            --bg-nav: #583924;
            --bg-card: #876635;
            --text-primary: #C29666;
            --text-secondary: #532D1C;
            --border: #C29666;
            --hover-bg: #6B3A2F;
            --btn-bg: #C29666;
            --btn-color: #532D1C;
            --btn-hover-bg: #876635;
            --btn-hover-color: #C29666;
        }}
        body.theme-neutral {{
            --bg-body: #F5F1EA;
            --bg-nav: #4A342A;
            --bg-card: #B2967D;
            --text-primary: #7D5A44;
            --text-secondary: #F5F1EA;
            --border: #D7C9B8;
            --hover-bg: #D7C9B8;
            --btn-bg: #7D5A44;
            --btn-color: #F5F1EA;
            --btn-hover-bg: #4A342A;
            --btn-hover-color: #D7C9B8;
        }}
        body.theme-dark {{
            --bg-body: #1F1611;
            --bg-nav: #523828;
            --bg-card: #946E4B;
            --text-primary: #D4A569;
            --text-secondary: #F9F0D6;
            --border: #D4A569;
            --hover-bg: #D4A569;
            --btn-bg: #D4A569;
            --btn-color: #1F1611;
            --btn-hover-bg: #946E4B;
            --btn-hover-color: #F9F0D6;
        }}
        body.theme-forest {{
            --bg-body: #051F20;
            --bg-nav: #0B2B26;
            --bg-card: #163832;
            --text-primary: #8EB69B;
            --text-secondary: #DAF1DE;
            --border: #8EB69B;
            --hover-bg: #8EB69B;
            --btn-bg: #8EB69B;
            --btn-color: #051F20;
            --btn-hover-bg: #DAF1DE;
            --btn-hover-color: #0B2B26;
        }}
        body.theme-om {{
            --bg-body: #154230;
            --bg-nav: #5D1E21;
            --bg-card: #5D1E21;
            --text-primary: #A6824A;
            --text-secondary: #E6E2DA;
            --border: #A6824A;
            --hover-bg: #A6824A;
            --btn-bg: #A6824A;
            --btn-color: #154230;
            --btn-hover-bg: #E6E2DA;
            --btn-hover-color: #101111;
        }}
        body.theme-cool {{
            --bg-body: #022E4C;
            --bg-nav: #517493;
            --bg-card: #517493;
            --text-primary: #E2D9CB;
            --text-secondary: #022E4C;
            --border: #E2D9CB;
            --hover-bg: #56061D;
            --btn-bg: #56061D;
            --btn-color: #E2D9CB;
            --btn-hover-bg: #E2D9CB;
            --btn-hover-color: #022E4C;
        }}
        body {{
            font-family: 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--bg-body);
            color: var(--text-primary);
            transition: all 0.3s;
        }}
        .container {{ max-width: 1400px; margin: auto; }}
        .nav {{
            background: var(--bg-nav);
            padding: 15px 20px;
            border-radius: 16px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .nav-links a {{
            color: var(--text-primary);
            text-decoration: none;
            margin-right: 25px;
            font-weight: 600;
            transition: 0.2s;
        }}
        .nav-links a:hover {{ color: var(--hover-bg); text-decoration: underline; }}
        .theme-btn, .refresh-btn {{
            background: var(--btn-bg);
            color: var(--btn-color);
            border: none;
            padding: 6px 14px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: bold;
            margin-left: 8px;
            transition: 0.2s;
        }}
        .theme-btn:hover, .refresh-btn:hover {{
            background: var(--btn-hover-bg);
            color: var(--btn-hover-color);
            transform: scale(1.02);
        }}
        .card {{
            background: var(--bg-card);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 25px;
            color: var(--text-secondary);
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            transition: transform 0.2s;
        }}
        .card:hover {{ transform: translateY(-2px); }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat {{
            background: var(--bg-nav);
            padding: 20px;
            border-radius: 20px;
            text-align: center;
            transition: 0.2s;
        }}
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--text-primary);
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ color: var(--text-primary); }}
        tr:hover {{ background: var(--hover-bg); cursor: pointer; }}
        button, .btn {{
            background: var(--btn-bg);
            color: var(--btn-color);
            border: none;
            padding: 10px 24px;
            border-radius: 40px;
            cursor: pointer;
            font-weight: bold;
            transition: 0.2s;
        }}
        button:hover, .btn:hover {{
            background: var(--btn-hover-bg);
            color: var(--btn-hover-color);
        }}
        input, select, textarea {{
            background: var(--bg-nav);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 10px;
            border-radius: 12px;
            width: 100%;
            margin-bottom: 15px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 30px;
            font-size: 0.75rem;
            font-weight: bold;
        }}
        .badge-new {{ background: #3b82f6; color: white; }}
        .badge-contacted {{ background: #f59e0b; color: white; }}
        .badge-qualified {{ background: #10b981; color: white; }}
        .badge-won {{ background: #059669; color: white; }}
        .badge-lost {{ background: #ef4444; color: white; }}
        .badge-follow_up {{ background: #8b5cf6; color: white; }}
        .flex-between {{ display: flex; justify-content: space-between; align-items: center; }}
        .timestamp {{ font-size: 0.8rem; opacity: 0.8; }}
        canvas {{ max-height: 300px; margin-top: 15px; }}
        .lead-review-card {{
            background: var(--bg-nav);
            border-radius: 16px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .email-preview {{
            background: var(--bg-body);
            padding: 10px;
            border-radius: 8px;
            font-family: monospace;
            white-space: pre-wrap;
        }}
        .loading-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.85);
            z-index: 9999;
            display: none;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            backdrop-filter: blur(5px);
        }}
        .loading-text {{
            color: var(--text-primary);
            font-size: 1.4em;
            font-weight: bold;
        }}
    </style>
    <script>
        let campaignId = null;
        let pollInterval = null;
        let redirectTimeout = null;
        
        function startCampaign(cid) {{
            campaignId = cid;
            document.getElementById('loadingOverlay').style.display = 'flex';
            
            redirectTimeout = setTimeout(() => {{
                window.location.href = `/review/${{campaignId}}`;
            }}, 15000);
            
            pollInterval = setInterval(async () => {{
                try {{
                    const response = await fetch(`/debug/campaign/${{campaignId}}`);
                    const data = await response.json();
                    if (data.status === 'completed') {{
                        clearInterval(pollInterval);
                        clearTimeout(redirectTimeout);
                        window.location.href = `/review/${{campaignId}}`;
                    }}
                }} catch(e) {{ console.error(e); }}
            }}, 2000);
            
            let ws = new WebSocket(`ws://${{window.location.host}}/ws`);
            ws.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                if (data.type === 'campaign_complete') {{
                    clearInterval(pollInterval);
                    clearTimeout(redirectTimeout);
                    window.location.href = `/review/${{campaignId}}`;
                }}
            }};
        }}
        
        document.addEventListener('DOMContentLoaded', () => {{
            const campaignForm = document.querySelector('form[action="/campaign/run"]');
            if (campaignForm) {{
                campaignForm.addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    const formData = new FormData(campaignForm);
                    try {{
                        const response = await fetch('/campaign/run', {{
                            method: 'POST',
                            body: formData
                        }});
                        const data = await response.json();
                        if (data.campaign_id) {{
                            startCampaign(data.campaign_id);
                        }} else {{
                            alert('Failed to start campaign');
                        }}
                    }} catch (err) {{
                        console.error(err);
                        alert('Error starting campaign');
                    }}
                }});
            }}
        }});
        
        function setTheme(theme) {{
            document.body.classList.remove('theme-neutral', 'theme-dark', 'theme-forest', 'theme-om', 'theme-cool');
            if (theme === 'neutral') document.body.classList.add('theme-neutral');
            else if (theme === 'dark') document.body.classList.add('theme-dark');
            else if (theme === 'forest') document.body.classList.add('theme-forest');
            else if (theme === 'om') document.body.classList.add('theme-om');
            else if (theme === 'cool') document.body.classList.add('theme-cool');
            else document.body.classList.remove('theme-neutral', 'theme-dark', 'theme-forest', 'theme-om', 'theme-cool');
            localStorage.setItem('hive_theme', theme);
        }}
        function cycleTheme() {{
            const current = localStorage.getItem('hive_theme') || 'earthy';
            if (current === 'earthy') setTheme('neutral');
            else if (current === 'neutral') setTheme('dark');
            else if (current === 'dark') setTheme('forest');
            else if (current === 'forest') setTheme('om');
            else if (current === 'om') setTheme('cool');
            else setTheme('earthy');
        }}
        function refreshPage() {{ window.location.reload(); }}
        document.addEventListener('DOMContentLoaded', () => {{
            const saved = localStorage.getItem('hive_theme');
            if (saved === 'neutral') setTheme('neutral');
            else if (saved === 'dark') setTheme('dark');
            else if (saved === 'forest') setTheme('forest');
            else if (saved === 'om') setTheme('om');
            else if (saved === 'cool') setTheme('cool');
        }});
    </script>
</head>
<body>
<div class="container">
    <div class="nav">
        <div class="nav-links">
            <a href="/">📊 Dashboard</a>
            <a href="/leads">📋 Leads</a>
            <a href="/campaign">🚀 New Campaign</a>
            <a href="/analytics">📈 Analytics</a>
            <a href="/reports">📊 Reports</a>
            <a href="/import">📥 Import CSV</a>
        </div>
        <div>
            <button class="refresh-btn" onclick="refreshPage()">🔄 Refresh</button>
            <button class="theme-btn" onclick="cycleTheme()">🎨 Change Theme</button>
        </div>
    </div>
    <div id="loadingOverlay" class="loading-overlay">
        <div class="loading-text">⏳ Campaign running... Please wait</div>
    </div>
"""
def html_footer():
    return "</div></body></html>"

# ---------- Dashboard ----------
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    stats = manager.get_dashboard()
    total = stats.get('stats', {}).get('total', 0)
    avg_score = stats.get('stats', {}).get('avg_score', 0)
    emails_sent = stats.get('stats', {}).get('emails_sent', 0)
    follow_ups = stats.get('follow_ups_needed', 0)
    all_leads = manager.db.get_all_leads()
    recent = all_leads[-10:] if all_leads else []
    campaigns = campaign_results[-5:]

    html = html_header("Dashboard")
    html += f"""
    <div class="stats">
        <div class="stat"><div class="stat-number" id="stat-total">{total}</div><div>📊 Total Leads</div></div>
        <div class="stat"><div class="stat-number" id="stat-avg">{avg_score}</div><div>⭐ Avg Score</div></div>
        <div class="stat"><div class="stat-number" id="stat-emails">{emails_sent}</div><div>✉️ Emails Sent</div></div>
        <div class="stat"><div class="stat-number" id="stat-follow">{follow_ups}</div><div>⏰ Follow‑ups Due</div></div>
    </div>
    <div class="card">
        <div class="flex-between"><h2>📋 Recent Leads</h2><span class="timestamp">Updated: {datetime.now().strftime('%H:%M:%S')}</span></div>
        <div style="margin-bottom: 15px;"><a href="/export/csv" class="btn">📎 Export All Leads as CSV</a></div>
        <table>
            <thead><tr><th>Name</th><th>Score</th><th>Status</th><th>Created</th></tr></thead>
            <tbody>
    """
    for lead in recent:
        html += f"<tr onclick=\"location.href='/lead/{lead['id']}'\"><td>{lead['name']}</td><td>{lead['score']}/10</span></td><td><span class='badge badge-{lead['status']}'>{lead['status']}</span></td><td>{lead['created_at'][:10]}</td></tr>"
    html += "</tbody></table></div><div class='card'><h2>🚀 Recent Campaigns</h2><table><thead><tr><th>Industry</th><th>City</th><th>Leads</th><th>Status</th></tr></thead><tbody>"
    for c in campaigns:
        html += f"<tr onclick=\"location.href='/campaign/{c['id']}'\"><td>{c['industry']}</td><td>{c['city']}</td><td>{c['leads_found']}</td><td><span class='badge'>{c['status']}</span></td></tr>"
    html += "</tbody></table></div><div style='text-align:center;'><a href='/campaign' class='btn'>🚀 Start New Campaign</a></div>"
    html += html_footer()
    return HTMLResponse(content=html)

# ---------- CSV Export ----------
@app.get("/export/csv")
async def export_csv():
    all_leads = manager.db.get_all_leads()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Website", "Phone", "Rating", "Score", "Status", "Email Sent", "Created At", "Notes", "Category", "Role", "Keywords", "Industry", "Email"])
    for lead in all_leads:
        notes = "\n".join(lead.get("notes", []))
        writer.writerow([
            lead.get("name", ""),
            lead.get("website", ""),
            lead.get("phone", ""),
            lead.get("rating", ""),
            lead.get("score", ""),
            lead.get("status", ""),
            "Yes" if lead.get("email_sent") else "No",
            lead.get("created_at", ""),
            notes,
            lead.get("category", ""),
            lead.get("role", ""),
            lead.get("keywords", ""),
            lead.get("industry", ""),
            lead.get("email", "")
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=hive_sdr_leads.csv"}
    )

# ---------- Leads Page (with sorting, filters, pagination) ----------
@app.get("/leads", response_class=HTMLResponse)
async def leads_page(request: Request, sort_by: str = "created_at", order: str = "desc", filter_type: str = "", limit: int = 50, offset: int = 0):
    all_leads = manager.db.get_all_leads()
    if filter_type and filter_type in ["Company", "Person"]:
        all_leads = [l for l in all_leads if l.get("type") == filter_type]
    reverse = (order == "desc")
    if sort_by == "name":
        all_leads.sort(key=lambda l: l.get("name", ""), reverse=reverse)
    elif sort_by == "score":
        all_leads.sort(key=lambda l: l.get("score", 0), reverse=reverse)
    elif sort_by == "status":
        all_leads.sort(key=lambda l: l.get("status", ""), reverse=reverse)
    elif sort_by == "type":
        all_leads.sort(key=lambda l: l.get("type", "Company"), reverse=reverse)
    elif sort_by == "category":
        all_leads.sort(key=lambda l: l.get("category", ""), reverse=reverse)
    elif sort_by == "role":
        all_leads.sort(key=lambda l: l.get("role", ""), reverse=reverse)
    elif sort_by == "industry":
        all_leads.sort(key=lambda l: l.get("industry", ""), reverse=reverse)
    elif sort_by == "price":
        all_leads.sort(key=lambda l: calculate_lead_price(l), reverse=reverse)
    else:
        all_leads.sort(key=lambda l: l.get("created_at", ""), reverse=reverse)
    
    total = len(all_leads)
    paginated = all_leads[offset:offset+limit]
    html = html_header("All Leads")
    html += "<div class='card'><h2>📋 All Leads</h2>"
    html += f"<div><strong>Total: {total}</strong> leads | Showing {offset+1}-{min(offset+limit, total)}</div>"
    
    # Action buttons and filters
    html += "<div style='margin-bottom: 15px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;'>"
    html += "<a href='/export/csv' class='btn'>📎 Export All Leads as CSV</a>"
    html += "<button id='buyBtn' class='btn' style='background:#10b981;'>💰 Buy Selected Leads</button>"
    html += "<button id='matchBtn' class='btn' style='background:#8b5cf6;'>🤖 Auto-Match Persons to Companies</button>"
    html += "<select id='typeFilter' style='padding: 8px; border-radius: 8px;'>"
    html += "<option value=''>All Types</option>"
    html += "<option value='Company' " + ("selected" if filter_type == "Company" else "") + ">🏢 Company</option>"
    html += "<option value='Person' " + ("selected" if filter_type == "Person" else "") + ">👤 Person</option>"
    html += "</select>"
    html += "<input type='text' id='categoryFilter' placeholder='Filter by Category' style='padding: 8px; border-radius: 8px;'>"
    html += "</div>"
    
    # Rating and price filters
    html += "<div style='display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 20px;'>"
    html += "<select id='ratingFilter' style='padding: 8px; border-radius: 8px;'><option value=''>All Ratings</option><option value='1'>⭐ 1+ stars</option><option value='2'>⭐⭐ 2+ stars</option><option value='3'>⭐⭐⭐ 3+ stars</option><option value='4'>⭐⭐⭐⭐ 4+ stars</option><option value='5'>⭐⭐⭐⭐⭐ 5 stars</option></select>"
    html += "<input type='number' id='priceMin' placeholder='Min Price' step='10' style='width:100px; padding:8px; border-radius:8px;'>"
    html += "<input type='number' id='priceMax' placeholder='Max Price' step='10' style='width:100px; padding:8px; border-radius:8px;'>"
    html += "<button id='applyFilters' class='btn'>Apply Filters</button>"
    html += "<button id='clearFilters' class='btn'>Clear Filters</button>"
    html += "</div>"
    
    # Pagination top right
    html += "<div style='display: flex; justify-content: flex-end; margin-bottom: 20px;'>"
    if offset > 0:
        prev_url = f"?sort_by={sort_by}&order={order}&filter_type={filter_type}&limit={limit}&offset={max(0, offset-limit)}"
        html += f"<a href='{prev_url}' class='btn' style='margin-right:10px;'>◀ Previous</a>"
    if offset+limit < total:
        next_url = f"?sort_by={sort_by}&order={order}&filter_type={filter_type}&limit={limit}&offset={offset+limit}"
        html += f"<a href='{next_url}' class='btn'>Next ▶</a>"
    html += "</div>"
    
    # Table headers
    html += "<table class='table'><thead>"
    headers = ["Select", "Name", "Score", "Status", "Type", "Category", "Role", "Industry", "Price", "Created"]
    for header in headers:
        if header == "Select":
            html += "<th>Select</th>"
            continue
        col = header.lower()
        new_order = "asc" if order == "desc" else "desc"
        arrow = " ↑" if order == "asc" else " ↓" if sort_by == col else ""
        html += f"<th><a href='?sort_by={col}&order={new_order}&filter_type={filter_type}&limit={limit}&offset={offset}' style='color: var(--text-primary); text-decoration: none;'>{header}{arrow}</a></th>"
    html += "</thead><tbody>"
    
    for lead in paginated:
        price = calculate_lead_price(lead)
        type_icon = "🏢" if lead.get("type") == "Company" else "👤"
        html += f"<tr data-rating='{lead.get('rating', 0)}'>"
        html += f"<td><input type='checkbox' class='lead-checkbox' data-price='{price}' value='{lead['id']}'></td>"
        html += f"<td><a href='/lead/{lead['id']}'>{lead['name']}</a></td>"
        html += f"<td>{lead['score']}/10</span></td>"
        html += f"<td><span class='badge badge-{lead['status']}'>{lead['status']}</span></td>"
        html += f"<td>{type_icon} {lead.get('type', 'Company')}</td>"
        html += f"<td>{lead.get('category', '')}</td>"
        html += f"<td>{lead.get('role', '')}</td>"
        html += f"<td>{lead.get('industry', '')}</td>"
        html += f"<td class='price-cell'>${price}</td>"
        html += f"<td>{lead['created_at'][:10]}</td>"
        html += "<tr>"
    html += "</tbody>"
    html += "</table>"
    html += "<div id='totalPrice' style='margin-top: 15px; font-size: 1.2em; font-weight: bold;'></div>"
    
    # JavaScript for filters and buy button
    html += """
    <script>
        function filterTable() {
            const typeFilter = document.getElementById('typeFilter').value;
            const categoryFilter = document.getElementById('categoryFilter').value.toLowerCase();
            const ratingFilter = document.getElementById('ratingFilter').value;
            const priceMin = parseFloat(document.getElementById('priceMin').value);
            const priceMax = parseFloat(document.getElementById('priceMax').value);
            const rows = document.querySelectorAll('.table tbody tr');
            rows.forEach(row => {
                let show = true;
                if (typeFilter) {
                    const typeCell = row.cells[4];
                    if (typeCell && !typeCell.innerText.includes(typeFilter)) show = false;
                }
                if (categoryFilter) {
                    const categoryCell = row.cells[5];
                    if (categoryCell && !categoryCell.innerText.toLowerCase().includes(categoryFilter)) show = false;
                }
                if (ratingFilter) {
                    const rating = parseFloat(row.getAttribute('data-rating'));
                    if (!isNaN(rating) && rating < parseFloat(ratingFilter)) show = false;
                }
                if (!isNaN(priceMin) || !isNaN(priceMax)) {
                    const priceCell = row.cells[8];
                    if (priceCell) {
                        let price = parseFloat(priceCell.innerText.replace('$', ''));
                        if (!isNaN(priceMin) && price < priceMin) show = false;
                        if (!isNaN(priceMax) && price > priceMax) show = false;
                    }
                }
                row.style.display = show ? '' : 'none';
            });
        }
        function updateTotal() {
            let total = 0;
            document.querySelectorAll('.lead-checkbox:checked').forEach(cb => {
                total += parseInt(cb.dataset.price);
            });
            const totalDiv = document.getElementById('totalPrice');
            if (totalDiv) {
                totalDiv.innerText = total > 0 ? `Total: $${total}` : '';
            }
        }
        document.querySelectorAll('.lead-checkbox').forEach(cb => {
            cb.addEventListener('change', updateTotal);
        });
        document.getElementById('buyBtn').onclick = async () => {
            const checkboxes = document.querySelectorAll('.lead-checkbox:checked');
            const lead_ids = Array.from(checkboxes).map(cb => cb.value);
            if (lead_ids.length === 0) {
                alert('Select at least one lead.');
                return;
            }
            const response = await fetch('/api/create-checkout-session', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({lead_ids})
            });
            const data = await response.json();
            if (data.url) {
                window.location.href = data.url;
            } else {
                alert('Error creating checkout session: ' + (data.error || 'Unknown error'));
            }
        };
        document.getElementById('matchBtn').onclick = async () => {
            const response = await fetch('/api/match-all', {method: 'POST'});
            const data = await response.json();
            alert(`Matched ${data.matched} out of ${data.total_persons} persons.`);
            window.location.reload();
        };
        document.getElementById('applyFilters').onclick = filterTable;
        document.getElementById('clearFilters').onclick = () => {
            document.getElementById('typeFilter').value = '';
            document.getElementById('categoryFilter').value = '';
            document.getElementById('ratingFilter').value = '';
            document.getElementById('priceMin').value = '';
            document.getElementById('priceMax').value = '';
            filterTable();
        };
        document.getElementById('typeFilter').onchange = filterTable;
        document.getElementById('categoryFilter').oninput = filterTable;
        document.getElementById('ratingFilter').onchange = filterTable;
        updateTotal();
    </script>
    """
    html += "</div>" + html_footer()
    return HTMLResponse(content=html)

# ---------- Campaign Page (with Yelp dropdown) ----------
@app.get("/campaign", response_class=HTMLResponse)
async def campaign_page(request: Request):
    html = html_header("Start Campaign")
    html += """
    <div class="card">
        <h2>🚀 Launch New Campaign</h2>
        <form method="post" action="/campaign/run">
            <label>Industry (e.g., coffee shop, plumber):</label>
            <input type="text" name="industry" required>
            <label>City (e.g., Brooklyn, NY):</label>
            <input type="text" name="city" required>
            <label>Max Leads (1-20):</label>
            <input type="number" name="max_leads" value="5" min="1" max="20">
            <label>Minimum Rating (1 to 5 stars):</label>
            <select name="min_rating">
                <option value="1.0">⭐ 1.0 and above</option>
                <option value="2.0">⭐⭐ 2.0 and above</option>
                <option value="3.0" selected>⭐⭐⭐ 3.0 and above</option>
                <option value="4.0">⭐⭐⭐⭐ 4.0 and above</option>
                <option value="5.0">⭐⭐⭐⭐⭐ 5.0 only</option>
            </select>
            <label>Industry (for template personalisation):</label>
            <select name="campaign_industry">
                <option value="">Auto-detect (or leave blank)</option>
                <option value="gym">🏋️ Gym / Fitness</option>
                <option value="restaurant">🍽️ Restaurant</option>
                <option value="plumber">🔧 Plumber / Contractor</option>
                <option value="saas">💻 SaaS / Software</option>
                <option value="coffee shop">☕ Coffee Shop</option>
            </select>
            <label>Lead Source:</label>
            <select name="lead_source">
                <option value="google">🗺️ Google Maps</option>
                <option value="yelp">🍴 Yelp</option>
            </select>
            <button type="submit">▶ Start Campaign</button>
        </form>
    </div>
    """ + html_footer()
    return HTMLResponse(content=html)

# ---------- Campaign Run (with Yelp integration) ----------
@app.post("/campaign/run")
async def run_campaign(request: Request, industry: str = Form(...), city: str = Form(...), max_leads: int = Form(5), min_rating: float = Form(3.5), campaign_industry: str = Form(""), lead_source: str = Form("google")):
    campaign_id = str(uuid.uuid4())[:8]
    campaign = {
        "id": campaign_id,
        "industry": industry,
        "city": city,
        "max_leads": max_leads,
        "started_at": datetime.now().isoformat(),
        "status": "running",
        "leads": []
    }
    try:
        from lead_finder.agent import LeadFinderAgent
        from research_agent.agent import ResearchAgent
        from sdr_orchestrator.agent import SDROrchestrator
        from outreach_agent.email_agent import EmailAgent
        
        if lead_source == "yelp":
            from lead_finder.yelp_search import YelpLeadFinder
            yelp_key = os.environ.get("YELP_API_KEY")
            if not yelp_key:
                raise ValueError("YELP_API_KEY not found in .env")
            yf = YelpLeadFinder(yelp_key)
            raw_leads = yf.search_by_keyword(industry, city, max_leads * 2)
            class TempLead:
                def __init__(self, data):
                    self.name = data.get("name", "")
                    self.website = data.get("website", "")
                    self.phone = data.get("phone", "")
                    self.rating = data.get("rating", 0)
                    self.total_ratings = data.get("total_ratings", 0)
                    self.address = data.get("address", "")
            leads = [TempLead(l) for l in raw_leads if l.get("rating", 0) >= min_rating and l.get("website")]
        else:
            lf = LeadFinderAgent()
            leads = lf.find_leads_for_campaign(industry, city, max_leads, min_rating=min_rating)
        
        researcher = ResearchAgent()
        orch = SDROrchestrator()
        email_agent = EmailAgent()
        for lead in leads:
            research = researcher.research_lead(lead)
            out = orch.process_lead_workflow(lead, research)
            if not out.get('skipped'):
                email_prep = email_agent.prepare_outreach(lead, out)
                campaign["leads"].append({
                    "name": lead.name,
                    "website": lead.website,
                    "phone": lead.phone,
                    "rating": lead.rating,
                    "score": out.get('score', {}).get('score', 0),
                    "email_draft": email_prep.get('body', ''),
                    "research": research.get('ai_insights', {}),
                    "industry": campaign_industry
                })
        campaign["status"] = "completed"
        campaign["completed_at"] = datetime.now().isoformat()
    except Exception as e:
        campaign["status"] = "failed"
        campaign["error"] = str(e)
        import traceback
        traceback.print_exc()
    pending_campaigns[campaign_id] = campaign
    await manager_ws.broadcast({"type": "campaign_complete"})
    return {"campaign_id": campaign_id}

# ---------- Review Page ----------
@app.get("/review/{campaign_id}", response_class=HTMLResponse)
async def review_page(request: Request, campaign_id: str):
    campaign = pending_campaigns.get(campaign_id)
    if not campaign:
        return HTMLResponse("<h1>Campaign not found</h1>", status_code=404)
    if campaign["status"] != "completed":
        return HTMLResponse(f"<h1>Campaign still running. Status: {campaign['status']}</h1>", status_code=400)

    html = html_header("Review Leads")
    html += f"""
    <div class="card">
        <h2>📝 Review Leads from {campaign['industry']} in {campaign['city']}</h2>
        <p>Accept or reject each lead. You can edit the email draft before accepting.</p>
        <form id="reviewForm" method="post" action="/review/{campaign_id}/submit">
    """
    for idx, lead in enumerate(campaign["leads"]):
        html += f"""
        <div class="lead-review-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>{lead['name']}</h3>
                <div>
                    <label style="margin-right: 15px;">
                        <input type="checkbox" name="accept_{idx}" value="yes" checked> Accept
                    </label>
                    <label>
                        <input type="checkbox" name="reject_{idx}" value="yes"> Reject
                    </label>
                </div>
            </div>
            <p><strong>Website:</strong> {lead['website']} | <strong>Rating:</strong> {lead['rating']}/5 | <strong>Score:</strong> {lead['score']}/10</p>
            <p><strong>Research insights:</strong> {lead.get('research', {}).get('pain_points', ['N/A'])[0]}</p>
            <label><strong>Email Draft (editable):</strong></label>
            <textarea name="email_{idx}" rows="6" class="email-preview" style="width:100%">{lead['email_draft']}</textarea>
            <hr>
        </div>
        """
    html += """
            <div style="text-align: center;">
                <button type="submit" class="btn">💾 Save Accepted Leads</button>
            </div>
        </form>
    </div>
    """ + html_footer()
    return HTMLResponse(content=html)

@app.post("/review/{campaign_id}/submit")
async def review_submit(request: Request, campaign_id: str):
    campaign = pending_campaigns.get(campaign_id)
    if not campaign:
        return HTMLResponse("<h1>Campaign not found</h1>", status_code=404)
    form = await request.form()
    for idx, lead in enumerate(campaign["leads"]):
        accept = form.get(f"accept_{idx}") == "yes"
        reject = form.get(f"reject_{idx}") == "yes"
        if accept and not reject:
            edited_email = form.get(f"email_{idx}", lead["email_draft"])
            lead_id = manager.db.add_lead({
                "name": lead["name"],
                "website": lead["website"],
                "phone": lead["phone"],
                "rating": lead["rating"],
                "score": lead["score"],
                "industry": lead.get("industry", "")
            }, lead_type="Company")
            manager.db.add_note(lead_id, f"Accepted from campaign {campaign['industry']} in {campaign['city']}")
            manager.db.add_note(lead_id, f"Email draft: {edited_email}")
    del pending_campaigns[campaign_id]
    await broadcast_stats()
    return RedirectResponse(url="/", status_code=303)

# ---------- Import CSV ----------
@app.get("/import", response_class=HTMLResponse)
async def import_page(request: Request):
    html = html_header("Import Leads")
    html += """
    <div class="card">
        <h2>📥 Import Leads from CSV</h2>
        <p>Upload a CSV file with columns: <strong>Name, Website, Phone, Rating, Score, Type, Category, Role, Keywords, Industry, Email, Job Title</strong></p>
        <p><a href="/static/sample_import.csv" download>Download sample CSV template</a></p>
        <form method="post" action="/import/csv" enctype="multipart/form-data">
            <div class="form-group">
                <label>CSV File:</label>
                <input type="file" name="file" accept=".csv" required>
            </div>
            <button type="submit" class="btn">📤 Upload and Import</button>
        </form>
    </div>
    """ + html_footer()
    return HTMLResponse(content=html)

@app.post("/import/csv")
async def import_csv(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        return HTMLResponse("<h1>Error: Please upload a CSV file.</h1>", status_code=400)
    contents = await file.read()
    try:
        csv_data = csv.DictReader(io.StringIO(contents.decode('utf-8')))
        imported_count = 0
        errors = []
        for row_num, row in enumerate(csv_data, start=2):
            name = row.get("Name", "").strip()
            website = row.get("Website", "").strip()
            if not name or not website:
                errors.append(f"Row {row_num}: missing Name or Website")
                continue
            phone = row.get("Phone", "").strip() or None
            lead_type = row.get("Type", "Company").strip()
            if lead_type not in ["Company", "Person"]:
                lead_type = "Company"
            job_title = row.get("Job Title", "").strip()
            category = row.get("Category", "").strip()
            role = row.get("Role", "").strip()
            keywords = row.get("Keywords", "").strip()
            industry = row.get("Industry", "").strip()
            email = row.get("Email", "").strip()
            try:
                rating = float(row.get("Rating", 0)) if row.get("Rating") else None
            except:
                rating = None
            try:
                score = int(row.get("Score", 5)) if row.get("Score") else 5
            except:
                score = 5
            lead_id = manager.db.add_lead({
                "name": name,
                "website": website,
                "phone": phone,
                "rating": rating,
                "score": score,
                "category": category,
                "role": role,
                "keywords": keywords,
                "industry": industry,
                "email": email
            }, lead_type=lead_type)
            manager.db.add_note(lead_id, f"Imported from CSV on {datetime.now().isoformat()}")
            if job_title:
                manager.db.add_note(lead_id, f"Job Title: {job_title}")
            imported_count += 1
        await broadcast_stats()
        if errors:
            error_msg = "<br>".join(errors)
            return HTMLResponse(f"<h1>Import completed with warnings</h1><p>Imported {imported_count} leads.</p><ul><li>{error_msg}</li></ul>", status_code=207)
        else:
            return RedirectResponse(url="/leads", status_code=303)
    except Exception as e:
        return HTMLResponse(f"<h1>Error processing CSV: {e}</h1>", status_code=500)

# ---------- Analytics ----------
@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    stats = manager.get_dashboard()
    total = stats.get('stats', {}).get('total', 0)
    avg = stats.get('stats', {}).get('avg_score', 0)
    emails = stats.get('stats', {}).get('emails_sent', 0)
    by_status = stats.get('stats', {}).get('by_status', {})
    follow = stats.get('follow_ups_needed', 0)
    qualified = by_status.get('qualified', 0)
    conv_rate = round((qualified / total) * 100, 1) if total else 0
    labels = list(by_status.keys())
    counts = list(by_status.values())
    html = html_header("Analytics")
    html += f"""
    <div class="stats">
        <div class="stat"><div class="stat-number">{total}</div><div>📊 Total Leads</div></div>
        <div class="stat"><div class="stat-number">{avg}</div><div>⭐ Avg Score</div></div>
        <div class="stat"><div class="stat-number">{emails}</div><div>✉️ Emails Sent</div></div>
        <div class="stat"><div class="stat-number">{conv_rate}%</div><div>🎯 Qualified Rate</div></div>
    </div>
    <div class="card">
        <h2>📊 Lead Status Distribution</h2>
        <canvas id="statusChart" width="400" height="200"></canvas>
        <script>
            const ctx = document.getElementById('statusChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {labels},
                    datasets: [{{
                        label: 'Number of Leads',
                        data: {counts},
                        backgroundColor: '#C29666',
                        borderRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ position: 'top' }} }}
                }}
            }});
        </script>
    </div>
    <div class="card">
        <h2>💡 Recommendations</h2>
        <ul>
    """
    if follow > 0:
        html += f"<li>⚠️ You have {follow} leads waiting for follow-up.</li>"
    if avg < 6 and total > 0:
        html += "<li>📉 Average lead score is low. Consider adjusting targeting criteria.</li>"
    if emails == 0:
        html += "<li>📧 No emails sent yet. Start a campaign to generate leads!</li>"
    html += "</ul></div>" + html_footer()
    return HTMLResponse(content=html)

# ---------- Lead Detail (with email, industry, mirror, Hunter button) ----------
@app.get("/lead/{lead_id}", response_class=HTMLResponse)
async def lead_detail(request: Request, lead_id: str):
    lead = manager.db.get_lead(lead_id)
    if not lead:
        return HTMLResponse("<h1>Lead not found</h1>", status_code=404)
    draft = ""
    for note in lead.get("notes", []):
        if note.startswith("Email draft:"):
            draft = note.replace("Email draft:", "").strip()
            break
    email_sent = lead.get("email_sent", False)
    email_status = "Sent" if email_sent else "Not sent"
    email_count = lead.get("email_count", 0)
    email_number = email_count + 1 if not email_sent else email_count
    linked_company_id = lead.get("linked_company_id")
    linked_company_name = ""
    if linked_company_id:
        linked_company = manager.db.get_lead(linked_company_id)
        linked_company_name = linked_company["name"] if linked_company else "Unknown"
    html = html_header(f"Lead: {lead['name']}")
    html += f"""
    <div class='card'>
        <h2>{lead['name']}</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;">
            <div><strong>🌐 Website:</strong> {lead.get('website', 'N/A')}</div>
            <div><strong>📞 Phone:</strong> {lead.get('phone', 'N/A')}</div>
            <div><strong>⭐ Rating:</strong> {lead.get('rating', 'N/A')}/5</div>
            <div><strong>🎯 Score:</strong> {lead['score']}/10</div>
            <div><strong>📧 Email Status:</strong> {email_status} (Email #{email_number})</div>
            <div><strong>📊 Status:</strong> <span class='badge badge-{lead['status']}'>{lead['status']}</span></div>
            <div><strong>📅 Created:</strong> {lead['created_at'][:19]}</div>
            <div><strong>🔄 Updated:</strong> {lead['updated_at'][:19]}</div>
            <div><strong>🏷️ Category:</strong> {lead.get('category', '')}</div>
            <div><strong>👔 Role:</strong> {lead.get('role', '')}</div>
            <div><strong>🔑 Keywords:</strong> {lead.get('keywords', '')}</div>
            <div><strong>🏭 Industry:</strong> {lead.get('industry', '')}</div>
            <div><strong>✉️ Email:</strong> {lead.get('email', '')}</div>
    """
    if lead.get("type") == "Person":
        html += f"""
            <div><strong>🔗 Linked Company:</strong> {linked_company_name if linked_company_id else 'Not linked'}</div>
        </div>
        <hr>
        <h3>🏢 Link to Company</h3>
        <select id="companySelect">
            <option value="">-- Select a company --</option>
        </select>
        <button onclick="linkCompany()" class="btn">Link</button>
        <div id="linkStatus"></div>
        <script>
            async function loadCompanies() {{
                const resp = await fetch('/lead/{lead_id}/suggest-companies');
                const data = await resp.json();
                const select = document.getElementById('companySelect');
                data.suggestions.forEach(comp => {{
                    const option = document.createElement('option');
                    option.value = comp.id;
                    option.text = comp.name;
                    select.appendChild(option);
                }});
            }}
            async function linkCompany() {{
                const companyId = document.getElementById('companySelect').value;
                if (!companyId) return;
                const resp = await fetch('/lead/{lead_id}/link-company', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{company_id: companyId}})
                }});
                if (resp.ok) {{
                    document.getElementById('linkStatus').innerHTML = '<span style="color:green;">✅ Linked!</span>';
                    setTimeout(() => location.reload(), 1000);
                }} else {{
                    document.getElementById('linkStatus').innerHTML = '<span style="color:red;">❌ Error linking</span>';
                }}
            }}
            loadCompanies();
        </script>
    """
    else:
        html += "</div>"
    html += f"""
        <hr>
        <h3>📝 Notes</h3><ul>
    """
    for note in lead.get('notes', []):
        html += f"<li>{note}</li>"
    html += f"""
        </ul>
        <hr>
        <h3>📧 Email Draft (editable)</h3>
        <textarea id="emailDraft" rows="8" style="width:100%; font-family:monospace;">{draft}</textarea>
        <br><br>
        <button onclick="saveDraft()" class="btn">💾 Save Draft</button>
        <button onclick="sendEmail()" class="btn" style="background:#10b981;">✉️ Send Email</button>
        <button onclick="mirrorAndAnalyze()" class="btn" style="background:#8b5cf6;">🌐 Mirror & Analyze Website</button>
        <div id="mirrorStatus" style="margin-top:10px;"></div>
        <div id="emailStatus" style="margin-top:10px;"></div>
        <hr>
        <h3>🏷️ Update Categories</h3>
        <form method="post" action="/lead/{lead_id}/update-categories">
            <label>Category:</label>
            <input type="text" name="category" value="{lead.get('category', '')}">
            <label>Role:</label>
            <input type="text" name="role" value="{lead.get('role', '')}">
            <label>Keywords (comma separated):</label>
            <input type="text" name="keywords" value="{lead.get('keywords', '')}">
            <label>Industry:</label>
            <input type="text" name="industry" value="{lead.get('industry', '')}">
            <button type="submit">Save Categories</button>
        </form>
        <form method="post" action="/lead/{lead_id}/redetect-industry">
            <button type="submit" class="btn" style="background:#8b5cf6;">🔄 Re-detect Industry from Website</button>
        </form>
        <form method="post" action="/lead/{lead_id}/enrich-email">
            <button type="submit" class="btn" style="background:#10b981;">✉️ Enrich Email (Hunter.io)</button>
        </form>
        <hr>
        <h3>➕ Add Note</h3>
        <form method="post" action="/lead/{lead_id}/note">
            <textarea name="note" rows="3" style="width:100%"></textarea>
            <button type="submit">Add Note</button>
        </form>
        <hr>
        <h3>🔄 Update Status</h3>
        <form method="post" action="/lead/{lead_id}/status">
            <select name="status">
                <option value="new">New</option>
                <option value="contacted">Contacted</option>
                <option value="qualified">Qualified</option>
                <option value="negotiating">Negotiating</option>
                <option value="won">Won</option>
                <option value="lost">Lost</option>
                <option value="follow_up">Follow Up</option>
            </select>
            <button type="submit">Update Status</button>
        </form>
        <br><a href="/leads" class="btn">← Back to Leads</a>
    </div>
    <script>
        async function saveDraft() {{
            const draft = document.getElementById('emailDraft').value;
            const response = await fetch('/lead/{lead_id}/update-draft', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{draft: draft}})
            }});
            const data = await response.json();
            if (data.success) {{
                document.getElementById('emailStatus').innerHTML = '<span style="color:green;">✅ Draft saved</span>';
                setTimeout(() => {{ document.getElementById('emailStatus').innerHTML = ''; }}, 2000);
            }} else {{
                document.getElementById('emailStatus').innerHTML = '<span style="color:red;">❌ Error saving draft</span>';
            }}
        }}
        async function sendEmail() {{
            const draft = document.getElementById('emailDraft').value;
            const response = await fetch('/lead/{lead_id}/send-email', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{draft: draft}})
            }});
            const data = await response.json();
            if (data.success) {{
                document.getElementById('emailStatus').innerHTML = '<span style="color:green;">✅ Email sent! Status updated to "Contacted".</span>';
                setTimeout(() => {{ location.reload(); }}, 2000);
            }} else {{
                document.getElementById('emailStatus').innerHTML = '<span style="color:red;">❌ Failed to send email: ' + (data.error || 'Unknown error') + '</span>';
            }}
        }}
        async function mirrorAndAnalyze() {{
            document.getElementById('mirrorStatus').innerHTML = '<span style="color:#C29666;">⏳ Mirroring website and analyzing... This may take a minute.</span>';
            const response = await fetch('/lead/{lead_id}/mirror-analyze', {{method: 'POST'}});
            const data = await response.json();
            if (data.success) {{
                document.getElementById('mirrorStatus').innerHTML = '<span style="color:green;">✅ Analysis complete! Refresh to see insights in notes.</span>';
                setTimeout(() => location.reload(), 2000);
            }} else {{
                document.getElementById('mirrorStatus').innerHTML = '<span style="color:red;">❌ Failed: ' + (data.error || 'Unknown error') + '</span>';
            }}
        }}
    </script>
    """
    html += html_footer()
    return HTMLResponse(content=html)

# ---------- Additional Endpoints (update-draft, send-email, status, note, categories, link-company, suggest-companies, match-all, mirror-analyze, enrich-email, redetect-industry, etc.) ----------
@app.post("/lead/{lead_id}/update-draft")
async def update_draft(request: Request, lead_id: str):
    data = await request.json()
    draft = data.get("draft", "")
    lead = manager.db.get_lead(lead_id)
    if not lead:
        return {"error": "Lead not found"}, 404
    notes = lead.get("notes", [])
    new_notes = [n for n in notes if not n.startswith("Email draft:")]
    new_notes.append(f"Email draft: {draft}")
    lead["notes"] = new_notes
    lead["updated_at"] = datetime.now().isoformat()
    manager.db._save()
    return {"success": True}

@app.post("/lead/{lead_id}/send-email")
async def send_email_endpoint(request: Request, lead_id: str):
    data = await request.json()
    draft = data.get("draft", "")
    lead = manager.db.get_lead(lead_id)
    if not lead:
        return {"error": "Lead not found"}, 404
    lead["email_sent"] = True
    lead["email_count"] = lead.get("email_count", 0) + 1
    lead["status"] = "contacted"
    lead["updated_at"] = datetime.now().isoformat()
    notes = lead.get("notes", [])
    notes.append(f"Email #{lead['email_count']} sent at {datetime.now().isoformat()}: {draft[:100]}...")
    notes = [n for n in notes if not n.startswith("Email draft:")]
    notes.append(f"Email draft: {draft}")
    lead["notes"] = notes
    manager.db._save()
    await broadcast_stats()
    print(f"📧 MOCK SEND: To {lead.get('email', 'no email')} Subject: {draft.split(chr(10))[0]}")
    return {"success": True}

@app.post("/lead/{lead_id}/status")
async def update_lead_status(request: Request, lead_id: str, status: str = Form(...)):
    manager.update_lead_status(lead_id, status)
    await broadcast_stats()
    return RedirectResponse(url=f"/lead/{lead_id}", status_code=303)

@app.post("/lead/{lead_id}/note")
async def add_lead_note(request: Request, lead_id: str, note: str = Form(...)):
    manager.db.add_note(lead_id, note)
    await broadcast_stats()
    return RedirectResponse(url=f"/lead/{lead_id}", status_code=303)

@app.post("/lead/{lead_id}/update-categories")
async def update_categories(request: Request, lead_id: str, category: str = Form(""), role: str = Form(""), keywords: str = Form(""), industry: str = Form("")):
    lead = manager.db.get_lead(lead_id)
    if not lead:
        return HTMLResponse("Lead not found", status_code=404)
    lead["category"] = category
    lead["role"] = role
    lead["keywords"] = keywords
    lead["industry"] = industry
    lead["updated_at"] = datetime.now().isoformat()
    manager.db._save()
    await broadcast_stats()
    return RedirectResponse(url=f"/lead/{lead_id}", status_code=303)

@app.post("/lead/{lead_id}/redetect-industry")
async def redetect_industry(lead_id: str):
    lead = manager.db.get_lead(lead_id)
    if not lead:
        return {"error": "Lead not found"}, 404
    website = lead.get("website")
    if not website:
        return {"error": "No website"}, 400
    from utils.industry_detector import detect_industry_from_website
    industry = detect_industry_from_website(website, use_ai=False)
    lead["industry"] = industry
    manager.db.add_note(lead_id, f"🔄 Industry re-detected: {industry}")
    manager.db._save()
    return RedirectResponse(url=f"/lead/{lead_id}", status_code=303)

# ---------- Matching ----------
from matching_agent.agent import MatchingAgent
matching_agent = MatchingAgent()

@app.post("/api/match-all")
async def match_all():
    result = matching_agent.run_auto_matching()
    return result

@app.post("/lead/{lead_id}/link-company")
async def link_company(lead_id: str, request: Request):
    data = await request.json()
    company_id = data.get("company_id")
    lead = manager.db.get_lead(lead_id)
    if not lead:
        return {"error": "Lead not found"}, 404
    lead["linked_company_id"] = company_id
    lead["matched_by"] = "manual"
    manager.db._save()
    await broadcast_stats()
    return {"success": True}

@app.get("/lead/{lead_id}/suggest-companies")
async def suggest_companies(lead_id: str):
    lead = manager.db.get_lead(lead_id)
    if not lead or lead.get("type") != "Person":
        return {"error": "Invalid lead"}, 400
    all_leads = manager.db.get_all_leads()
    companies = [l for l in all_leads if l.get("type") == "Company"]
    person_name = lead.get("name", "").lower()
    suggestions = []
    for comp in companies:
        comp_name = comp["name"].lower()
        if comp_name in person_name:
            suggestions.append({"id": comp["id"], "name": comp["name"]})
    if not suggestions:
        suggestions = [{"id": c["id"], "name": c["name"]} for c in companies[:5]]
    return {"suggestions": suggestions}

# ---------- Website Mirroring ----------
from website_mirror.agent import WebsiteMirrorAgent
mirror_agent = WebsiteMirrorAgent()

@app.post("/lead/{lead_id}/mirror-analyze")
async def mirror_and_analyze(lead_id: str):
    lead = manager.db.get_lead(lead_id)
    if not lead:
        return {"error": "Lead not found"}, 404
    website = lead.get("website")
    if not website:
        return {"error": "No website URL"}, 400
    # Check cache
    for note in lead.get("notes", []):
        if note.startswith("🌐 Website Mirror Analysis:"):
            return {"success": True, "insights": note.replace("🌐 Website Mirror Analysis:", "").strip(), "cached": True}
    mirror_path = mirror_agent.mirror_site(website, exclude_paths=["*/blog/*", "*/wp-json/*"])
    if not mirror_path:
        return {"error": "Mirroring failed"}, 500
    site_text = mirror_agent.extract_text_from_mirror(mirror_path)
    try:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Analyze this company's website content and provide:
            1. Three pain points the company likely faces.
            2. Two opportunities where our service could help.
            3. One personalized opening line for outreach.
            Website text snippet: {site_text[:3000]}
            """
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            insights = response.text
        else:
            insights = "Mock insights: The company could improve customer retention, automate marketing, and streamline operations."
    except Exception as e:
        insights = f"AI analysis failed: {e}"
    manager.db.add_note(lead_id, f"🌐 Website Mirror Analysis:\n{insights}")
    import shutil
    shutil.rmtree(mirror_path)
    return {"success": True, "insights": insights}

# ---------- Hunter.io Email Enrichment ----------
@app.post("/lead/{lead_id}/enrich-email")
async def enrich_email(lead_id: str):
    lead = manager.db.get_lead(lead_id)
    if not lead:
        return {"error": "Lead not found"}, 404
    name = lead.get("name", "")
    website = lead.get("website", "")
    if not website:
        return {"error": "No website domain"}, 400
    domain = website.replace("https://", "").replace("http://", "").split("/")[0]
    parts = name.split()
    first = parts[0] if parts else ""
    last = " ".join(parts[1:]) if len(parts) > 1 else ""
    from utils.hunter import find_email
    email = find_email(domain, first, last)
    if email:
        lead["email"] = email
        manager.db.add_note(lead_id, f"✉️ Enriched email via Hunter.io: {email}")
        manager.db._save()
        return {"success": True, "email": email}
    else:
        return {"success": False, "message": "Email not found"}

# ---------- Stripe Checkout ----------
@app.post("/api/create-checkout-session")
async def create_checkout_session(request: Request):
    data = await request.json()
    lead_ids = data.get("lead_ids", [])
    line_items = []
    for lid in lead_ids:
        lead = manager.db.get_lead(lid)
        if lead:
            price = calculate_lead_price(lead)
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": lead["name"],
                        "description": f"Lead from HIVE-SDR (Score: {lead['score']}/10, Rating: {lead.get('rating', 'N/A')})"
                    },
                    "unit_amount": int(price * 100),
                },
                "quantity": 1,
            })
    if not line_items:
        return {"error": "No valid leads"}, 400
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=f"{BASE_URL}/sales/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{BASE_URL}/leads",
            metadata={"lead_ids": ",".join(lead_ids)}
        )
        return {"url": checkout_session.url}
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/sales/success")
async def sales_success(request: Request, session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        lead_ids = session.metadata.get("lead_ids", "").split(",")
        for lid in lead_ids:
            lead = manager.db.get_lead(lid)
            if lead:
                manager.db.add_note(lid, f"Sold via Stripe on {datetime.now().isoformat()}")
        return RedirectResponse(url="/export/csv", status_code=303)
    except Exception as e:
        return HTMLResponse(f"<h1>Payment verification failed: {e}</h1>", status_code=500)

# ---------- Cal.com Webhook and Booking ----------
CAL_COM_WEBHOOK_SECRET = os.environ.get("CAL_COM_WEBHOOK_SECRET", "")

@app.post("/webhook/cal-com")
async def cal_com_webhook(request: Request):
    try:
        body = await request.body()
        payload = json.loads(body)
        signature = request.headers.get("X-Cal-Signature-256")
        if CAL_COM_WEBHOOK_SECRET and signature:
            expected = hmac.new(
                CAL_COM_WEBHOOK_SECRET.encode(),
                msg=body,
                digestmod=hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                return {"error": "Invalid signature"}, 401
        event = payload.get("event", {})
        if event.get("type") == "booking.created":
            metadata = event.get("data", {}).get("metadata", {})
            lead_id = metadata.get("lead_id")
            if lead_id:
                lead = manager.db.get_lead(lead_id)
                if lead:
                    manager.update_lead_status(lead_id, "won")
                    manager.db.add_note(lead_id, f"✅ Call booked via Cal.com at {datetime.now().isoformat()}")
                    await broadcast_stats()
            attendee_email = event.get("data", {}).get("attendees", [{}])[0].get("email")
            if attendee_email and not lead_id:
                all_leads = manager.db.get_all_leads()
                for lead in all_leads:
                    if lead.get("email") == attendee_email:
                        manager.update_lead_status(lead["id"], "won")
                        manager.db.add_note(lead["id"], f"✅ Call booked via Cal.com at {datetime.now().isoformat()}")
                        await broadcast_stats()
                        break
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"error": str(e)}, 500

@app.get("/book/{lead_id}")
async def booking_page(request: Request, lead_id: str):
    lead = manager.db.get_lead(lead_id)
    if not lead:
        return HTMLResponse("<h1>Lead not found</h1>", status_code=404)
    if lead["status"] not in ["won", "lost"]:
        manager.update_lead_status(lead_id, "negotiating")
        manager.db.add_note(lead_id, f"📅 Booking page viewed at {datetime.now().isoformat()}")
        await broadcast_stats()
    cal_username = os.environ.get("CAL_USERNAME", "your-username")
    cal_event_slug = os.environ.get("CAL_EVENT_SLUG", "15min")
    cal_iframe_src = f"https://cal.com/{cal_username}/{cal_event_slug}?metadata[lead_id]={lead_id}&email={lead.get('email', '')}"
    html = html_header("Book a Call")
    html += f"""
    <div class="card">
        <h2>📅 Schedule a call with {lead['name']}</h2>
        <p>Select a time that works for you. We'll confirm instantly.</p>
        <iframe src="{cal_iframe_src}"
                width="100%"
                height="700px"
                frameborder="0"
                style="border-radius: 16px;">
        </iframe>
        <br>
        <a href="/lead/{lead_id}" class="btn">← Back to lead</a>
    </div>
    """ + html_footer()
    return HTMLResponse(content=html)

# ---------- Reports Page (Industry Intelligence) ----------
from collections import Counter
def extract_insights_from_notes(notes):
    pain_points = []
    opportunities = []
    for note in notes:
        if "🌐 Website Mirror Analysis:" in note or "pain point" in note.lower():
            lines = note.split('\n')
            for line in lines:
                if "pain" in line.lower() or "struggl" in line.lower():
                    pain_points.append(line.strip()[:100])
                elif "opportun" in line.lower() or "help" in line.lower():
                    opportunities.append(line.strip()[:100])
    return pain_points, opportunities

@app.get("/reports", response_class=HTMLResponse)
async def industry_report(request: Request):
    all_leads = manager.db.get_all_leads()
    industry_data = {}
    for lead in all_leads:
        industry = lead.get("industry", "Unknown")
        if not industry:
            industry = "Unknown"
        if industry not in industry_data:
            industry_data[industry] = {
                "count": 0,
                "ratings": [],
                "pain_points": [],
                "opportunities": []
            }
        industry_data[industry]["count"] += 1
        if lead.get("rating"):
            industry_data[industry]["ratings"].append(lead["rating"])
        notes = lead.get("notes", [])
        pain, opp = extract_insights_from_notes(notes)
        industry_data[industry]["pain_points"].extend(pain)
        industry_data[industry]["opportunities"].extend(opp)
    
    industries = list(industry_data.keys())
    lead_counts = [industry_data[i]["count"] for i in industries]
    avg_ratings = []
    for i in industries:
        ratings = industry_data[i]["ratings"]
        avg = sum(ratings) / len(ratings) if ratings else 0
        avg_ratings.append(round(avg, 1))
    
    all_pain = []
    all_opp = []
    for i in industries:
        all_pain.extend(industry_data[i]["pain_points"])
        all_opp.extend(industry_data[i]["opportunities"])
    top_pain = Counter(all_pain).most_common(5)
    top_opp = Counter(all_opp).most_common(5)
    
    html = html_header("Industry Intelligence Report")
    html += """
    <div class="card">
        <h2>📊 Industry Intelligence Report</h2>
        <p>Aggregated insights from your lead database.</p>
    </div>
    <div class="stats">
        <div class="stat"><div class="stat-number">""" + str(len(all_leads)) + """</div><div>Total Leads</div></div>
        <div class="stat"><div class="stat-number">""" + str(len(industries)) + """</div><div>Industries</div></div>
    </div>
    <div class="card">
        <h2>🏭 Leads per Industry</h2>
        <canvas id="industryChart" width="400" height="200"></canvas>
    </div>
    <div class="card">
        <h2>⭐ Average Rating per Industry</h2>
        <canvas id="ratingChart" width="400" height="200"></canvas>
    </div>
    <div class="card">
        <h2>💡 Top Pain Points</h2>
        <ul>
    """
    for pain, count in top_pain:
        html += f"<li><strong>{pain}</strong> (mentioned {count} times)</li>"
    html += """
        </ul>
    </div>
    <div class="card">
        <h2>🚀 Top Opportunities</h2>
        <ul>
    """
    for opp, count in top_opp:
        html += f"<li><strong>{opp}</strong> (mentioned {count} times)</li>"
    html += """
        </ul>
    </div>
    <div class="card">
        <h2>📈 Recommendations</h2>
        <ul>
    """
    if avg_ratings and max(avg_ratings) < 4.0:
        html += "<li>Overall ratings are low – consider offering reputation management services.</li>"
    if any(c > 20 for c in lead_counts):
        html += "<li>Some industries have a high volume of leads – focus your sales efforts there.</li>"
    if top_pain:
        html += f"<li>Top pain point: '{top_pain[0][0][:80]}...' – tailor your messaging to address this.</li>"
    html += """
        </ul>
    </div>
    <script>
        const ctx1 = document.getElementById('industryChart').getContext('2d');
        new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: """ + str(industries) + """,
                datasets: [{
                    label: 'Number of Leads',
                    data: """ + str(lead_counts) + """,
                    backgroundColor: '#C29666',
                    borderRadius: 8
                }]
            },
            options: { responsive: true }
        });
        const ctx2 = document.getElementById('ratingChart').getContext('2d');
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: """ + str(industries) + """,
                datasets: [{
                    label: 'Average Rating (1-5)',
                    data: """ + str(avg_ratings) + """,
                    backgroundColor: '#A6824A',
                    borderRadius: 8
                }]
            },
            options: { responsive: true, scales: { y: { min: 0, max: 5 } } }
        });
    </script>
    """ + html_footer()
    return HTMLResponse(content=html)

# ---------- Debug endpoints ----------
@app.get("/debug/pending")
async def debug_pending():
    return {"pending_campaigns": list(pending_campaigns.keys()), "count": len(pending_campaigns)}

@app.get("/debug/campaign/{campaign_id}")
async def debug_campaign(campaign_id: str):
    camp = pending_campaigns.get(campaign_id)
    if not camp:
        return {"error": "not found"}
    return {
        "status": camp.get("status"),
        "leads_count": len(camp.get("leads", [])),
        "error": camp.get("error"),
        "has_leads": bool(camp.get("leads"))
    }

@app.get("/debug/leads")
async def debug_leads():
    all_leads = manager.db.get_all_leads()
    return [{"id": l["id"], "name": l["name"], "status": l["status"]} for l in all_leads]

@app.get("/api/stats")
async def api_stats():
    return manager.get_dashboard()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/conversion-stats")
async def conversion_stats():
    all_leads = manager.db.get_all_leads()
    total = len(all_leads)
    booked = sum(1 for l in all_leads if l.get("status") == "won")
    conversion_rate = round((booked / total) * 100, 1) if total else 0
    return {
        "total_leads": total,
        "booked_calls": booked,
        "conversion_rate": conversion_rate,
        "last_updated": datetime.now().isoformat()
    }
