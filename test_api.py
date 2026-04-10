import os
import requests
from dotenv import load_dotenv

# Load .env from current directory
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key: {api_key[:20] if api_key else 'NOT FOUND'}...")

if not api_key:
    print("ERROR: No API key found in .env")
    exit()

url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={api_key}"
payload = {"contents": [{"parts": [{"text": "Say OK"}]}]}

print(f"Sending request...")
response = requests.post(url, json=payload, timeout=10)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("SUCCESS! API is working")
else:
    print(f"Error: {response.text}")
