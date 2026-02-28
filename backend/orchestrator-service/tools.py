import requests
from langchain.tools import tool

BASE_URL = "http://127.0.0.1:8000"

@tool
def cari_hotel(lokasi: str) -> str:
    """
    Gunakan alat ini untuk mencari hotel.
    Input: Nama lokasi (misal: "Bali", "Jakarta").
    """
    try:
        print(f"[TOOL] Executing cari_hotel for location: {lokasi}")
        response = requests.get(f"{BASE_URL}/hotels", params={"location": lokasi})
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                return "Maaf, tidak ditemukan hotel di lokasi tersebut."
            return str(data)
            
        return f"Error mengambil data hotel: {response.status_code}"
        
    except Exception as e:
        return f"Terjadi kesalahan koneksi pada layanan hotel: {str(e)}"

@tool
def cari_penerbangan(query_rute: str) -> str:
    """
    Gunakan alat ini untuk mencari tiket pesawat.
    PENTING: Input harus format "ASAL,TUJUAN" (pisahkan dengan koma).
    Contoh Input: "CGK,DPS" atau "SUB,JKT".
    """
    try:
        if "," not in query_rute:
            return "Error: Format input salah. Harap gunakan format 'ASAL,TUJUAN' (contoh: CGK,DPS)."
        
        asal, tujuan = query_rute.split(",")
        asal = asal.strip()
        tujuan = tujuan.strip()
        
        print(f"[TOOL] Executing cari_penerbangan from {asal} to {tujuan}")

        params = {"origin": asal, "destination": tujuan}
        response = requests.get(f"{BASE_URL}/flights", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                return "Maaf, tidak ada penerbangan untuk rute tersebut."
            return str(data)
            
        return f"Error mengambil data penerbangan: {response.status_code}"
        
    except Exception as e:
        return f"Terjadi kesalahan koneksi pada layanan penerbangan: {str(e)}"