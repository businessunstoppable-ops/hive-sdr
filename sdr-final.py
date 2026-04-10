from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import json
from datetime import datetime
from typing import List

from lead_finder.agent import LeadFinderAgent
from research_agent.agent import ResearchAgent
from sdr_orchestrator.agent import SDROrchestrator
from lead_finder.google_maps_search import Lead

app = FastAPI(title="HIVE-SDR Final")

# In-memory database
leads_db = {}
next_lead_id = 1

# ---------- Bee Animation Overlay ----------
BEE_OVERLAY = """
<div id="beehiveOverlay" class="beehive-overlay" style="display: none;">
    <div class="hive"></div>
    <div class="lead-count" id="leadCount">Loading... 0</div>
    <button id="cancelBtn" class="btn-cancel" style="margin-top: 20px;">Cancel</button>
</div>

<style>
.beehive-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.85);
  backdrop-filter: blur(5px);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  pointer-events: auto;
}
.hive {
  width: 200px; height: 180px;
  background: radial-gradient(circle at 30% 30%, #F7D44A, #D98C2B);
  border-radius: 50% 50% 45% 45%;
  position: relative;
  box-shadow: 0 0 30px rgba(247,212,74,0.5);
  animation: pulse 1.5s infinite;
}
.hive::before {
  content: "🍯";
  position: absolute;
  font-size: 80px;
  top: 30px; left: 50%;
  transform: translateX(-50%);
}
.bee {
  position: absolute; width: 30px; height: 30px;
  background: #F5C542; border-radius: 50%;
  box-shadow: 0 0 5px #000;
  opacity: 0;
}
.bee::before, .bee::after {
  content: ""; position: absolute;
  background: #2B1A0F; width: 6px; height: 20px; top: 5px; border-radius: 2px;
}
.bee::before { left: 5px; transform: rotate(-20deg); }
.bee::after { right: 5px; transform: rotate(20deg); }
.wing {
  position: absolute;
  background: rgba(255,255,200,0.6);
  width: 20px; height: 15px;
  border-radius: 50%;
  top: -8px; left: 5px;
  animation: flap 0.2s infinite alternate;
}
@keyframes fly {
  0% { left: -50px; top: 20%; opacity: 1; transform: scale(0.8); }
  100% { left: 120%; top: 80%; opacity: 0; transform: scale(1.2); }
}
@keyframes flap { 0% { transform: scaleY(1); } 100% { transform: scaleY(0.5); } }
@keyframes pulse { 0% { transform: scale(1); opacity: 0.8; } 100% { transform: scale(1.05); opacity: 1; } }
.lead-count {
  margin-top: 30px; font-size: 24px;
  background: rgba(0,0,0,0.6); padding: 10px 20px;
  border-radius: 40px; color: #F7D44A;
}
.btn-cancel {
  background: #743014; color: #E8D1A7; border: 1px solid #9D9167;
  padding: 8px 20px; border-radius: 8px; cursor: pointer; font-size: 16px;
}
.btn-cancel:hover { background: #9D9167; color: #2B1A0F; }
</style>

<script>
let beeInterval;
let leadCounter = 0;
let currentAbortController = null;

function startBeeAnimation() {
  const overlay = document.getElementById('beehiveOverlay');
  if (overlay) overlay.style.display = 'flex';
  leadCounter = 0;
  const countEl = document.getElementById('leadCount');
  if (countEl) countEl.innerText = 'Loading... 0';
  if (beeInterval) clearInterval(beeInterval);
  beeInterval = setInterval(() => {
    const bee = document.createElement('div'); bee.className = 'bee';
    const wing = document.createElement('div'); wing.className = 'wing';
    bee.appendChild(wing);
    const startY = Math.random() * window.innerHeight;
    bee.style.left = '-50px'; bee.style.top = startY + 'px';
    const duration = 3 + Math.random() * 2;
    bee.style.animation = `fly ${duration}s linear forwards`;
    document.body.appendChild(bee);
    bee.addEventListener('animationend', () => {
      bee.remove();
      leadCounter++;
      const countEl2 = document.getElementById('leadCount');
      if (countEl2) countEl2.innerText = `Loading... ${leadCounter}`;
    });
  }, 1500);
}

function stopBeeAnimation() {
  if (beeInterval) clearInterval(beeInterval);
  const overlay = document.getElementById('beehiveOverlay');
  if (overlay) overlay.style.display = 'none';
  document.querySelectorAll('.bee').forEach(b => b.remove());
  if (currentAbortController) { currentAbortController.abort(); currentAbortController = null; }
}

document.addEventListener('DOMContentLoaded', () => {
  const cancelBtn = document.getElementById('cancelBtn');
  if (cancelBtn) {
    cancelBtn.onclick = () => {
      stopBeeAnimation();
      alert('Operation cancelled.');
    };
  }
});
</script>
"""

# ---------- Campaign Page ----------
CAMPAIGN_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<title>HIVE-SDR - New Campaign</title>
<style>
body {{ background: #2B1A0F; color: #E8D1A7; font-family: sans-serif; padding: 20px; }}
.container {{ max-width: 800px; margin: 0 auto; }}
.card {{ background: rgba(0,0,0,0.3); border-radius: 15px; padding: 20px; margin-bottom: 20px; }}
.btn {{ background: #743014; color: #E8D1A7; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }}
.btn-primary {{ background: #9D9167; color: #2B1A0F; }}
input, select {{ width: 100%; padding: 10px; margin-bottom: 10px; background: #3A2A1A; border: 1px solid #84592B; color: #E8D1A7; border-radius: 8px; }}
</style>
</head>
<body>
<div class="container">
<div class="card">
<h2>🚀 New Campaign</h2>
<form id="campaignForm">
<div><label>Industry:</label><input type="text" id="industry" placeholder="e.g., gym" required></div>
<div><label>City:</label><input type="text" id="city" placeholder="e.g., Amsterdam" required></div>
<div><label>Max Leads:</label><input type="number" id="max_leads" value="10"></div>
<button type="submit" class="btn btn-primary">🔍 Preview Leads</button>
</form>
</div>
<div id="previewContainer"></div>
<div id="loading" style="display:none;">Loading...</div>
</div>
{BEE_OVERLAY}
<script>
const form = document.getElementById('campaignForm');
form.onsubmit = async (e) => {
    e.preventDefault();
    const industry = document.getElementById('industry').value;
    const city = document.getElementById('city').value;
    const maxLeads = document.getElementById('max_leads').value;
    if (!industry || !city) { alert("Please fill both fields"); return; }

    startBeeAnimation();
    currentAbortController = new AbortController();
    const signal = currentAbortController.signal;

    const formData = new FormData();
    formData.append('industry', industry);
    formData.append('city', city);
    formData.append('max_leads', maxLeads);

    try {
        const resp = await fetch('/preview', { method:'POST', body: formData, signal });
        const html = await resp.text();
        stopBeeAnimation();
        document.getElementById('previewContainer').innerHTML = html;
    } catch(err) {
        stopBeeAnimation();
        alert('Error: ' + err.message);
    }
};
</script>
</body>
</html>
"""

# ---------- Routes ----------

@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/campaign")

@app.get("/campaign", response_class=HTMLResponse)
async def campaign():
    return CAMPAIGN_HTML

@app.post("/preview", response_class=HTMLResponse)
async def preview(industry: str = Form(...), city: str = Form(...), max_leads: int = Form(10)):
    finder = LeadFinderAgent()
    leads = finder.find_leads_for_campaign(industry, city, max_leads)
    rows = ""
    for i, lead in enumerate(leads):
        rows += f"""
        <tr>
            <td><input type='checkbox' name='selected_leads' value='{i}'></td>
            <td><strong>{lead.name}</strong></td>
            <td>{lead.rating}/5</td>
            <td>{lead.total_ratings}</td>
            <td><a href='{lead.website}' target='_blank'>{lead.website[:40]}</a></td>
            <td>{lead.address[:50]}</td>
        </tr>
        """
    leads_json = json.dumps([{
        "name": l.name, "website": l.website, "phone": l.phone,
        "rating": l.rating, "total_ratings": l.total_ratings, "address": l.address
    } for l in leads])
    return f"""
    <div class="card">
    <h3>Discovered Businesses ({len(leads)})</h3>
    <form method="post" action="/review" id="reviewForm">
    <table style="width:100%; border-collapse:collapse;">
    <thead><tr><th>Select</th><th>Name</th><th>Rating</th><th>Reviews</th><th>Website</th><th>Address</th></tr></thead>
    <tbody>{rows}</tbody>
    </table>
    <input type="hidden" name="leads_data" value='{leads_json}'>
    <input type="hidden" name="industry" value="{industry}">
    <input type="hidden" name="city" value="{city}">
    <div style="margin-top:20px;">
    <button type="button" onclick="selectAll()">Select All</button>
    <button type="button" onclick="deselectAll()">Deselect All</button>
    <button type="submit" class="btn btn-primary">Run on Selected</button>
    </div>
    </form>
    </div>
    <script>
    const checkboxes = document.querySelectorAll('input[name="selected_leads"]');
    function selectAll() {{ checkboxes.forEach(cb => cb.checked = true); }}
    function deselectAll() {{ checkboxes.forEach(cb => cb.checked = false); }}
    </script>
    """

# ---------- Review Page (Accept/Reject workflow) ----------
@app.post("/review", response_class=HTMLResponse)
async def review(selected_leads: List[int] = Form(...), leads_data: str = Form(...), industry: str = Form(...), city: str = Form(...)):
    selected_indices = selected_leads
    leads_data_list = json.loads(leads_data)
    selected = [leads_data_list[i] for i in selected_indices]

    leads_json = json.dumps(selected)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Review Leads</title>
    <style>
    body {{ background: #2B1A0F; color: #E8D1A7; font-family: sans-serif; padding: 20px; }}
    .container {{ max-width: 1000px; margin: 0 auto; }}
    .card {{ background: rgba(0,0,0,0.3); border-radius: 15px; padding: 20px; margin-bottom: 20px; }}
    .lead-card {{ background: rgba(0,0,0,0.2); border-radius: 12px; padding: 15px; margin-bottom: 15px; }}
    .btn {{ background: #743014; color: #E8D1A7; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; }}
    .btn-primary {{ background: #9D9167; color: #2B1A0F; }}
    hr {{ border-color: #84592B; }}
    </style>
    </head>
    <body>
    <div class="container">
    <div class="card">
    <h2>🐝 Review Selected Leads</h2>
    <p>Accept or reject each lead before processing.</p>
    <div id="leadsContainer"></div>
    <div style="margin-top:20px;">
    <button class="btn btn-primary" onclick="processSelected()">💾 Process Selected Leads</button>
    <a href="/campaign" class="btn">Cancel</a>
    </div>
    </div>
    {BEE_OVERLAY}
    <script>
    const leadsData = {leads_json};
    const container = document.getElementById('leadsContainer');
    let decisions = {{}};
    function renderCards() {{
        container.innerHTML = '';
        leadsData.forEach((lead, idx) => {{
            const card = document.createElement('div'); card.className='lead-card';
            card.innerHTML = `
            <div style="display:flex; justify-content:space-between;">
                <h3>${{lead.name}}</h3>
                <div>
                <label><input type="radio" name="decision_${{idx}}" value="accept" checked> Accept</label>
                <label><input type="radio" name="decision_${{idx}}" value="reject"> Reject</label>
                </div>
            </div>
            <p><strong>Rating:</strong> ${{lead.rating}}/5 (${{lead.total_ratings}} reviews)</p>
            <p><strong>Website:</strong> <a href="${{lead.website}}" target="_blank">${{lead.website}}</a></p>
            <hr>
            `;
            const radios = card.querySelectorAll(`input[name="decision_${{idx}}"]`);
            radios.forEach(r => r.addEventListener('change', e => {{ decisions[idx]=e.target.value; }}));
            decisions[idx]='accept';
            container.appendChild(card);
        }});
    }}
    async function processSelected() {{
        const toProcess = [];
        leadsData.forEach((lead, idx) => {{ if (decisions[idx]==='accept') toProcess.push(lead); }});
        if (toProcess.length===0) {{ alert('No leads accepted.'); return; }}
        startBeeAnimation();
        currentAbortController = new AbortController();
        try {{
            const resp = await fetch('/review_data', {{
                method:'POST',
                headers:{{'Content-Type':'application/json'}},
                body: JSON.stringify({{
                    leads: toProcess,
                    industry: '{industry}',
                    city: '{city}'
                }})
            }});
            const html = await resp.text();
            stopBeeAnimation();
            document.body.innerHTML = html;
        }} catch(err) {{
            stopBeeAnimation();
            alert('Error: '+err.message);
        }}
    }}
    renderCards();
    </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# ---------- Review Data Processing ----------
@app.post("/review_data", response_class=HTMLResponse)
async def review_data(request: Request):
    data = await request.json()
    leads_to_process = data.get('leads', [])
    industry = data.get('industry', '')
    city = data.get('city', '')

    researcher = ResearchAgent()
    orchestrator = SDROrchestrator()
    leads_data_out = []

    for item in leads_to_process:
        lead = Lead(
            name=item['name'], place_id='rev', address=item.get('address',''),
            phone=item.get('phone'), website=item.get('website'),
            rating=item.get('rating'), total_ratings=item.get('total_ratings'),
            business_status='OPERATIONAL', lat=0, lng=0
        )
        research = researcher.research_lead(lead)
        result = orchestrator.process_lead_workflow(lead, research, industry)
        if not result.get('skipped'):
            leads_data_out.append({
                'name': lead.name,
                'website': lead.website,
                'phone': lead.phone,
                'rating': lead.rating,
                'total_ratings': lead.total_ratings,
                'score': result.get('score', {}).get('score',0),
                'email_draft': result.get('email_draft','No draft')
            })

    leads_json = json.dumps(leads_data_out)
    # Render similar review page but now with processed data
    # For brevity, you can reuse the same HTML as in previous render (or expand to include email drafts)
    html = f"<h1>Processed {len(leads_data_out)} leads</h1>"
    return HTMLResponse(content=html)

# ---------- Run server ----------
if