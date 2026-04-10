"""Preview endpoint for discovering leads before running campaign"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from lead_finder.agent import LeadFinderAgent

router = APIRouter()

@router.post("/preview", response_class=HTMLResponse)
async def preview_leads(
    request: Request,
    industry: str = Form(...),
    city: str = Form(...),
    max_leads: int = Form(10)
):
    """Preview discovered leads without running the full campaign"""
    
    lead_finder = LeadFinderAgent()
    leads = lead_finder.find_leads_for_campaign(industry, city, max_leads)
    
    # Generate HTML for the preview table
    rows_html = ""
    for i, lead in enumerate(leads):
        rows_html += f"""
        <tr>
            <td><input type="checkbox" name="select_{i}" value="{i}" checked class="lead-checkbox"></td>
            <td><strong>{lead.name}</strong></td>
            <td>{lead.rating if lead.rating else 'N/A'}/5</td>
            <td>{lead.total_ratings if lead.total_ratings else 0}</td>
            <td><a href="{lead.website}" target="_blank" style="color:#9D9167;">{lead.website[:40] if lead.website else 'N/A'}</a></td>
            <td>{lead.address[:50] if lead.address else 'N/A'}</td>
         </>
        """
    
    # Build leads data as JSON
    leads_data = []
    for lead in leads:
        leads_data.append({
            'name': lead.name,
            'website': lead.website,
            'phone': lead.phone,
            'rating': lead.rating,
            'total_ratings': lead.total_ratings,
            'address': lead.address
        })
    
    import json
    leads_json = json.dumps(leads_data)
    
    return HTMLResponse(content=f"""
    <div class="preview-container">
        <div class="card">
            <div class="flex-between">
                <h2>🔍 Discovered Businesses ({len(leads)} found)</h2>
                <div>
                    <button type="button" class="btn btn-secondary" onclick="selectAll()">Select All</button>
                    <button type="button" class="btn btn-secondary" onclick="deselectAll()">Deselect All</button>
                </div>
            </div>
            
            <div style="overflow-x: auto; margin-top: 20px;">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Select</th>
                            <th>Business Name</th>
                            <th>Rating</th>
                            <th>Reviews</th>
                            <th>Website</th>
                            <th>Address</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            
            <div class="mt-20" style="display: flex; gap: 10px; justify-content: space-between;">
                <div>
                    <span id="selectedCount">Selected: {len(leads)}</span> of {len(leads)} businesses
                </div>
                <div>
                    <button type="button" class="btn" onclick="runCampaignWithSelected()">Run Campaign on Selected</button>
                    <button type="button" class="btn btn-secondary" onclick="closePreview()">Cancel</button>
                </div>
            </div>
        </div>
    </div>
    
    <input type="hidden" id="leadsData" value='{leads_json}'>
    <input type="hidden" id="industry" value="{industry}">
    <input type="hidden" id="city" value="{city}">
    
    <script>
        const leadsData = JSON.parse(document.getElementById('leadsData').value);
        const checkboxes = document.querySelectorAll('.lead-checkbox');
        const selectedCountSpan = document.getElementById('selectedCount');
        
        function updateSelectedCount() {{
            const checked = document.querySelectorAll('.lead-checkbox:checked').length;
            selectedCountSpan.textContent = `Selected: ${{checked}}`;
        }}
        
        function selectAll() {{
            checkboxes.forEach(cb => cb.checked = true);
            updateSelectedCount();
        }}
        
        function deselectAll() {{
            checkboxes.forEach(cb => cb.checked = false);
            updateSelectedCount();
        }}
        
        checkboxes.forEach(cb => cb.addEventListener('change', updateSelectedCount));
        
        function closePreview() {{
            const container = document.getElementById('previewContainer');
            if (container) {{
                container.innerHTML = '';
                container.style.display = 'none';
            }}
        }}
        
        async function runCampaignWithSelected() {{
            const selectedIndices = [];
            checkboxes.forEach((cb, idx) => {{
                if (cb.checked) selectedIndices.push(parseInt(cb.value));
            }});
            
            if (selectedIndices.length === 0) {{
                alert('Please select at least one business to run the campaign.');
                return;
            }}
            
            const selectedLeads = selectedIndices.map(i => leadsData[i]);
            
            // Show loading
            const previewContainer = document.getElementById('previewContainer');
            if (previewContainer) {{
                previewContainer.innerHTML = '<div class="card"><h2>⏳ Running campaign...</h2><p>Processing ' + selectedIndices.length + ' leads...</p></div>';
            }}
            
            // Submit the form with selected leads
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/campaign/run_selected';
            
            const leadsInput = document.createElement('input');
            leadsInput.type = 'hidden';
            leadsInput.name = 'selected_leads';
            leadsInput.value = JSON.stringify(selectedLeads);
            form.appendChild(leadsInput);
            
            const industryInput = document.createElement('input');
            industryInput.type = 'hidden';
            industryInput.name = 'industry';
            industryInput.value = document.getElementById('industry').value;
            form.appendChild(industryInput);
            
            const cityInput = document.createElement('input');
            cityInput.type = 'hidden';
            cityInput.name = 'city';
            cityInput.value = document.getElementById('city').value;
            form.appendChild(cityInput);
            
            document.body.appendChild(form);
            form.submit();
        }}
        
        updateSelectedCount();
    </script>
    """)
