import requests

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("TEST_GEMINI_API_KEY", "")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

prompt = "Halo, apakah API berjalan?"
payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}
headers = {"Content-Type": "application/json"}

print("Mengirim request ke Gemini API...")
try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    response.raise_for_status()
    print("Sukses!")
except Exception as e:
    print(f"Exception: {e}")
