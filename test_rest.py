import httpx
import json

key = "AIzaSyDKxE8SebK1uBv3mU4nNCC2_h0BY_Zb88I"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={key}"

payload = {
    "contents": [{
        "parts": [{"text": "Write a short test sentence."}]
    }]
}

print("Testing REST API connectivity...")
try:
    response = httpx.post(url, json=payload, timeout=30.0)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Response Content:")
        print(response.json())
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection Failed: {e}")
