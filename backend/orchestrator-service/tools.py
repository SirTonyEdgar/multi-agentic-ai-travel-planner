import os
import httpx
import difflib
from langchain.tools import tool

def _resolve_url(env_value: str) -> str:
    """Terima bare hostname (dari Render) atau full URL (docker-compose lokal)."""
    if env_value.startswith("http://") or env_value.startswith("https://"):
        return env_value
    return f"https://{env_value}"

INTEGRATION_URL = _resolve_url(os.getenv("INTEGRATION_URL", "http://integration-service:8000"))

# ============================================================
# FUZZY MATCHING HELPER
# ============================================================

def fuzzy_filter(nama_query: str, items: list, key: str, threshold: float = 0.45) -> list:
    """
    Filter daftar item berdasarkan kemiripan nama dengan nama_query.
    Mengembalikan item yang cocok diurutkan dari skor tertinggi.
    Mendukung typo, urutan kata berbeda, dan pencocokan sebagian.
    """
    q = nama_query.lower().strip()
    scored = []

    for item in items:
        name = item.get(key, "").lower().strip()

        if q in name or name in q:
            scored.append((1.0, item))
            continue

        q_words = set(q.split())
        n_words = set(name.split())
        if q_words and n_words:
            overlap = len(q_words & n_words) / max(len(q_words), len(n_words))
        else:
            overlap = 0.0

        seq_sim = difflib.SequenceMatcher(None, q, name).ratio()

        score = max(overlap, seq_sim)
        if score >= threshold:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored]


# ============================================================
# TOOLS
# ============================================================

@tool
def cari_penerbangan(query_rute: str) -> str:
    """
    Gunakan alat ini untuk mencari tiket pesawat berdasarkan rute.
    PENTING: Input WAJIB format "ASAL,TUJUAN" menggunakan kode bandara IATA.
    Contoh Input: "CGK,DPS" (Jakarta ke Bali) atau "SUB,DPS" (Surabaya ke Bali).

    Kode bandara yang tersedia:
    - CGK = Jakarta (Soekarno-Hatta)
    - SUB = Surabaya (Juanda)
    - DPS = Bali (Ngurah Rai)
    - LOP = Lombok (Praya)
    """
    try:
        if "," not in query_rute:
            return (
                "Error: Format input salah. "
                "Gunakan format 'ASAL,TUJUAN' (contoh: CGK,DPS)."
            )

        asal, tujuan = query_rute.split(",", 1)
        asal = asal.strip().upper()
        tujuan = tujuan.strip().upper()

        print(f"[TOOL] cari_penerbangan: {asal} → {tujuan}")

        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{INTEGRATION_URL}/flights",
                params={"origin": asal, "destination": tujuan}
            )

        if response.status_code == 200:
            data = response.json()
            flights = data.get("flights", [])
            if not flights:
                return f"Tidak ada penerbangan untuk rute {asal} → {tujuan}."

            result = f"Penerbangan {asal} → {tujuan} ({data['total_results']} tersedia):\n"
            for f in flights:
                result += (
                    f"- [{f['id']}] {f['airline']} {f['flight_number']} | "
                    f"Berangkat: {f['departure']} | Tiba: {f['arrival']} | "
                    f"Harga: Rp {f['price']:,} | Kursi: {f['seats_available']}\n"
                )
            return result

        elif response.status_code == 404:
            detail = response.json().get("detail", "")
            return f"DATA TIDAK DITEMUKAN: {detail}"

        return f"Error dari Mock API: HTTP {response.status_code}"

    except httpx.RequestError as e:
        return (
            f"Koneksi ke Mock API gagal: {str(e)}. "
            f"Pastikan Mock API berjalan di port 8002."
        )

@tool
def cari_hotel(query: str) -> str:
    """
    Gunakan alat ini untuk mencari hotel berdasarkan lokasi, harga, atau nama hotel.

    Format yang didukung:
    - "LOKASI"                        → semua hotel di kota
    - "LOKASI,MAX_HARGA"              → hotel di kota dengan harga maksimal
    - "LOKASI,nama=NAMA_HOTEL"        → cari hotel berdasarkan nama (mendukung typo)

    Contoh:
    - "Bali"
    - "Bali,500000"
    - "Bali,nama=Kuta Central Park Hotel"
    - "Bali,nama=Hotel Kuta Central"   ← urutan kata berbeda tetap bisa ditemukan

    Lokasi yang tersedia: Bali, Lombok, Yogyakarta.
    """
    try:
        lokasi = query.strip()
        max_price = None
        nama_hotel = None

        if "," in query:
            parts = query.split(",", 1)
            lokasi = parts[0].strip()
            sisa = parts[1].strip()

            if sisa.lower().startswith("nama="):
                nama_hotel = sisa[5:].strip()
            else:
                try:
                    max_price = int(sisa)
                except ValueError:
                    # Mungkin user ketik nama tanpa prefix "nama="
                    nama_hotel = sisa

        print(f"[TOOL] cari_hotel: lokasi={lokasi}, max_price={max_price}, nama={nama_hotel}")

        params = {"location": lokasi}
        if max_price:
            params["max_price"] = max_price

        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{INTEGRATION_URL}/hotels", params=params)

        if response.status_code == 200:
            data = response.json()
            hotels = data.get("hotels", [])
            if not hotels:
                return f"Tidak ada hotel tersedia di {lokasi}."

            # Fuzzy filter by name if requested
            if nama_hotel:
                matched = fuzzy_filter(nama_hotel, hotels, key="name")
                if matched:
                    hotels = matched
                    prefix = f"Hasil pencarian hotel '{nama_hotel}' di {lokasi}:\n"
                else:
                    # Fallback: tampilkan semua hotel di kota itu
                    prefix = (
                        f"Hotel dengan nama '{nama_hotel}' tidak ditemukan di {lokasi}. "
                        f"Berikut semua hotel yang tersedia di {lokasi}:\n"
                    )
            else:
                prefix = f"Hotel di {lokasi} ({data['total_results']} tersedia):\n"

            result = prefix
            for h in hotels:
                result += (
                    f"- [{h['id']}] {h['name']} | Area: {h['area']} | "
                    f"Rating: {h['rating']} | "
                    f"Harga: Rp {h['price_per_night']:,}/malam | "
                    f"Kamar tersedia: {h['rooms_available']} | "
                    f"Fasilitas: {', '.join(h['facilities'])}\n"
                )
            return result

        elif response.status_code == 404:
            detail = response.json().get("detail", "")
            return f"DATA TIDAK DITEMUKAN: {detail}"

        return f"Error dari Mock API: HTTP {response.status_code}"

    except httpx.RequestError as e:
        return (
            f"Koneksi ke Mock API gagal: {str(e)}. "
            f"Pastikan Mock API berjalan di port 8002."
        )

@tool
def cari_aktivitas(query: str) -> str:
    """
    Gunakan alat ini untuk mencari aktivitas wisata, tempat makan, atau tempat ibadah.

    Format yang didukung:
    - "LOKASI"                        → semua aktivitas di kota
    - "LOKASI,KATEGORI"               → filter by kategori (wisata/kuliner/ibadah)
    - "LOKASI,nama=NAMA_AKTIVITAS"    → cari aktivitas berdasarkan nama (mendukung typo)

    Kategori yang tersedia: wisata, kuliner, ibadah
    Contoh:
    - "Bali"
    - "Bali,wisata"
    - "Bali,nama=Tanah Lot"
    - "Yogyakarta,nama=Candi Borobudur"

    Lokasi yang tersedia: Bali, Lombok, Yogyakarta.
    """
    try:
        lokasi = query.strip()
        kategori = None
        nama_aktivitas = None

        if "," in query:
            parts = query.split(",", 1)
            lokasi = parts[0].strip()
            sisa = parts[1].strip()

            if sisa.lower().startswith("nama="):
                nama_aktivitas = sisa[5:].strip()
            else:
                kategori = sisa

        print(f"[TOOL] cari_aktivitas: lokasi={lokasi}, kategori={kategori}, nama={nama_aktivitas}")

        params = {"location": lokasi}
        if kategori:
            params["category"] = kategori

        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{INTEGRATION_URL}/activities", params=params)

        if response.status_code == 200:
            data = response.json()
            activities = data.get("activities", [])
            if not activities:
                return f"Tidak ada aktivitas tersedia di {lokasi}."

            if nama_aktivitas:
                matched = fuzzy_filter(nama_aktivitas, activities, key="name")
                if matched:
                    activities = matched
                    prefix = f"Hasil pencarian aktivitas '{nama_aktivitas}' di {lokasi}:\n"
                else:
                    prefix = (
                        f"Aktivitas '{nama_aktivitas}' tidak ditemukan di {lokasi}. "
                        f"Berikut semua aktivitas yang tersedia:\n"
                    )
            else:
                label = f" (kategori: {kategori})" if kategori else ""
                prefix = f"Aktivitas di {lokasi}{label} ({data['total_results']} tersedia):\n"

            result = prefix
            for a in activities:
                harga = (
                    f"Rp {a['entry_fee']:,}" if a["entry_fee"] > 0
                    else f"Gratis (est. makan Rp {a.get('average_meal_price', 0):,})"
                    if a.get("average_meal_price") else "Gratis"
                )
                result += (
                    f"- [{a['id']}] {a['name']} | Kategori: {a['category']} | "
                    f"Harga: {harga} | Buka: {a['open_hours']} | "
                    f"Rating: {a['rating']} | Durasi: ~{a['duration_recommended_hours']} jam\n"
                )
            return result

        elif response.status_code == 404:
            detail = response.json().get("detail", "")
            return f"DATA TIDAK DITEMUKAN: {detail}"

        return f"Error dari Mock API: HTTP {response.status_code}"

    except httpx.RequestError as e:
        return (
            f"Koneksi ke Mock API gagal: {str(e)}. "
            f"Pastikan Mock API berjalan di port 8002."
        )

@tool
def cari_transport(query: str) -> str:
    """
    Gunakan alat ini untuk mencari transportasi lokal di destinasi wisata.

    Format yang didukung:
    - "LOKASI"                        → semua transportasi di kota
    - "LOKASI,JENIS"                  → filter by jenis transportasi
    - "LOKASI,nama=NAMA_PROVIDER"     → cari berdasarkan nama provider (mendukung typo)

    Jenis yang tersedia: Shuttle Bandara, Rental Mobil, Rental Motor, Taksi
    Contoh:
    - "Bali"
    - "Bali,Shuttle Bandara"
    - "Bali,nama=Bali Shuttle Express"

    Lokasi yang tersedia: Bali, Lombok, Yogyakarta.
    """
    try:
        lokasi = query.strip()
        jenis = None
        nama_provider = None

        if "," in query:
            parts = query.split(",", 1)
            lokasi = parts[0].strip()
            sisa = parts[1].strip()

            if sisa.lower().startswith("nama="):
                nama_provider = sisa[5:].strip()
            else:
                jenis = sisa

        print(f"[TOOL] cari_transport: lokasi={lokasi}, jenis={jenis}, nama={nama_provider}")

        params = {"location": lokasi}
        if jenis:
            params["type"] = jenis

        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{INTEGRATION_URL}/transport", params=params)

        if response.status_code == 200:
            data = response.json()
            transports = data.get("transports", [])
            if not transports:
                return f"Tidak ada transportasi tersedia di {lokasi}."

            if nama_provider:
                matched = fuzzy_filter(nama_provider, transports, key="provider")
                if matched:
                    transports = matched
                    prefix = f"Hasil pencarian transportasi '{nama_provider}' di {lokasi}:\n"
                else:
                    prefix = (
                        f"Provider '{nama_provider}' tidak ditemukan di {lokasi}. "
                        f"Berikut semua transportasi yang tersedia:\n"
                    )
            else:
                label = f" (jenis: {jenis})" if jenis else ""
                prefix = f"Transportasi di {lokasi}{label} ({data['total_results']} tersedia):\n"

            result = prefix
            for t in transports:
                harga = f"Rp {t['price']:,}"
                if t.get("notes"):
                    harga += f" ({t['notes']})"
                result += (
                    f"- [{t['id']}] {t['type']} | {t['provider']} | "
                    f"Rute: {t['origin']} → {t['destination']} | "
                    f"Harga: {harga} | Jam: {t['open_hours']}\n"
                )
            return result

        elif response.status_code == 404:
            detail = response.json().get("detail", "")
            return f"DATA TIDAK DITEMUKAN: {detail}"

        return f"Error dari Mock API: HTTP {response.status_code}"

    except httpx.RequestError as e:
        return (
            f"Koneksi ke Mock API gagal: {str(e)}. "
            f"Pastikan Mock API berjalan di port 8002."
        )