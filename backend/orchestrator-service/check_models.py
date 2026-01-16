import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: API Key tidak ditemukan di .env")
    exit()

# 2. Konfigurasi Google AI
genai.configure(api_key=api_key)

print("Sedang menghubungi server Google...")
print("====================================")
print("DAFTAR MODEL YANG TERSEDIA UNTUK ANDA:")
print("====================================")

try:
    # 3. Minta daftar model
    found = False
    for m in genai.list_models():
        # Hanya tampilkan model yang bisa generate text (bukan image/embedding)
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            found = True
    
    if not found:
        print("⚠ Tidak ada model text-generation yang ditemukan.")
        
except Exception as e:
    print(f"❌ Terjadi kesalahan koneksi: {e}")