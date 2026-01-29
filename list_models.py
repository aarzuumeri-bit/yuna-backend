import requests
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={KEY}"

response = requests.get(url)
print(f"Status: {response.status_code}")
print(response.text)
