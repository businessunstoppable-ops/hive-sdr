import requests
import os

def find_email(domain: str, first_name: str = None, last_name: str = None) -> str:
    api_key = os.getenv("HUNTER_API_KEY")
    if not api_key:
        return ""
    url = "https://api.hunter.io/v2/email-finder"
    params = {
        "domain": domain,
        "api_key": api_key
    }
    if first_name and last_name:
        params["first_name"] = first_name
        params["last_name"] = last_name
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("email", "")
    except Exception as e:
        print(f"Hunter.io error: {e}")
    return ""
