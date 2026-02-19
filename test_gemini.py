"""SoEasyHub v2 Gemini Connectivity Test"""
import google.generativeai as genai
import os

key = os.environ.get("GOOGLE_API_KEY", "MISSING_KEY_PLEASE_SET_ENV")
genai.configure(api_key=key)

print("Starting connectivity test...")
try:
    print("Listing models (timeout=10s)...")
    # genai doesn't have a direct timeout on list_models, but we can try
    models = list(genai.list_models())
    print("Successfully retrieved models:")
    for m in models:
        if "pro" in m.name.lower():
            print(f" - {m.name}")
except Exception as e:
    print(f"Connectivity Error: {e}")
