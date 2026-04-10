# Add this to your working_app.py - Campaign page with autocomplete

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
            font-size: 16px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #9D9167;
        }
        .autocomplete-container {
            position: relative;
            width: 100%;
        }
        .autocomplete-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #3A2A1A;
            border: 1px solid #9D9167;
            border-radius: 8px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .autocomplete-item {
            padding: 12px 15px;
            cursor: pointer;
            border-bottom: 1px solid #5C3A1E;
            transition: all 0.2s ease;
        }
        .autocomplete-item:hover {
            background: #5C3A1E;
        }
        .autocomplete-item .main {
            font-weight: bold;
            color: #E8D1A7;
        }
        .autocomplete-item .sub {
            font-size: 12px;
            color: #C4B89A;
            margin-top: 3px;
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
                    <div class="autocomplete-container">
                        <input type="text" name="city" id="city" placeholder="Start typing a city name..." autocomplete="off" required>
                        <div id="autocompleteDropdown" class="autocomplete-dropdown" style="display: none;"></div>
                    </div>
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
        const cityInput = document.getElementById('city');
        const dropdown = document.getElementById('autocompleteDropdown');
        
        let debounceTimer;
        
        cityInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = this.value.trim();
            
            if (query.length < 2) {
                dropdown.style.display = 'none';
                return;
            }
            
            debounceTimer = setTimeout(async () => {
                try {
                    const response = await fetch(`/api/locations/autocomplete?input=${encodeURIComponent(query)}`);
                    const suggestions = await response.json();
                    
                    if (suggestions.length === 0) {
                        dropdown.style.display = 'none';
                        return;
                    }
                    
                    dropdown.innerHTML = '';
                    suggestions.forEach(suggestion => {
                        const item = document.createElement('div');
                        item.className = 'autocomplete-item';
                        item.innerHTML = \`
                            <div class="main">\${escapeHtml(suggestion.name)}</div>
                            <div class="sub">\${escapeHtml(suggestion.description || suggestion.name)}</div>
                        \`;
                        item.onclick = () => {
                            cityInput.value = suggestion.name;
                            dropdown.style.display = 'none';
                        };
                        dropdown.appendChild(item);
                    });
                    
                    dropdown.style.display = 'block';
                } catch (error) {
                    console.error('Autocomplete error:', error);
                    dropdown.style.display = 'none';
                }
            }, 300);
        });
        
        document.addEventListener('click', function(e) {
            if (!cityInput.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
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
                previewContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
            
            const cityInputField = document.createElement('input');
            cityInputField.type = 'hidden';
            cityInputField.name = 'city';
            cityInputField.value = city;
            form.appendChild(cityInputField);
            
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
