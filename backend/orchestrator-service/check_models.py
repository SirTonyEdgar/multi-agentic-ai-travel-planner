import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("[ERROR] API Key tidak ditemukan di environment variables (.env).")
    sys.exit(1)

genai.configure(api_key=api_key)

print("Fetching available Google AI models...")
print("-" * 45)
print("AVAILABLE TEXT GENERATION MODELS:")
print("-" * 45)

try:
    found = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            found = True
    
    if not found:
        print("[WARN] Tidak ada model text-generation yang ditemukan.")
        
except Exception as e:
    print(f"[ERROR] Terjadi kesalahan saat mengambil daftar model: {str(e)}")