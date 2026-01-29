import requests
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GOOGLE_API_KEY")

print(f"Testing Key: {KEY[:5]}...{KEY[-5:]}")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={KEY}"
payload = {
    "contents": [{
        "parts": [{"text": "Hello"}]
    }]
}

response = requests.post(url, json=payload)
print(f"Status: {response.status_code}")
print(response.text)
