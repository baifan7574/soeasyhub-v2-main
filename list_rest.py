import httpx
import json

key = "AIzaSyDKxE8SebK1uBv3mU4nNCC2_h0BY_Zb88I"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

print("Listing models via REST...")
try:
    response = httpx.get(url, timeout=30.0)
    if response.status_code == 200:
        models = response.json().get('models', [])
        for m in models:
            print(m.get('name'))
    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Failed: {e}")
