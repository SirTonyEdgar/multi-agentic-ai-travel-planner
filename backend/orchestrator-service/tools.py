import requests
from langchain.tools import tool

# Alamat Integration Service (Mock API)
BASE_URL = "http://127.0.0.1:8000"

@tool
def cari_hotel(lokasi: str):
    """
    Gunakan alat ini untuk mencari hotel.
    Input: Nama lokasi (misal: "Bali", "Jakarta").
    """
    try:
        # AI akan menembak endpoint /hotels
        print(f"[TOOL] Mencari hotel di: {lokasi}") # Debugging
        response = requests.get(f"{BASE_URL}/hotels", params={"location": lokasi})
        if response.status_code == 200:
            data = response.json()
            if not data:
                return "Maaf, tidak ditemukan hotel di lokasi tersebut."
            return str(data)
        else:
            return f"Error mengambil data hotel: {response.status_code}"
    except Exception as e:
        return f"Terjadi kesalahan koneksi: {e}"

@tool
def cari_penerbangan(query_rute: str):
    """
    Gunakan alat ini untuk mencari tiket pesawat.
    PENTING: Input harus format "ASAL,TUJUAN" (pisahkan dengan koma).
    Contoh Input: "CGK,DPS" atau "SUB,JKT".
    """
    try:
        # Kita pecah string "CGK,DPS" menjadi dua variabel di sini
        # Ini lebih aman daripada menyuruh AI memecahnya
        if "," not in query_rute:
            return "Error: Format input salah. Harusnya 'ASAL,TUJUAN' (contoh: CGK,DPS)"
        
        asal, tujuan = query_rute.split(",")
        asal = asal.strip()
        tujuan = tujuan.strip()
        
        print(f"[TOOL] Mencari flight dari {asal} ke {tujuan}") # Debugging

        params = {"origin": asal, "destination": tujuan}
        response = requests.get(f"{BASE_URL}/flights", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                return "Maaf, tidak ada penerbangan untuk rute tersebut."
            return str(data)
        else:
            return f"Error mengambil data penerbangan: {response.status_code}"
    except Exception as e:
        return f"Terjadi kesalahan koneksi: {e}"