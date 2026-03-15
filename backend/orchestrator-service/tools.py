import httpx
from langchain.tools import tool

MOCK_API_URL = "http://127.0.0.1:8002"


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
                f"{MOCK_API_URL}/flights",
                params={"origin": asal, "destination": tujuan}
            )

        if response.status_code == 200:
            data = response.json()
            flights = data.get("flights", [])
            if not flights:
                return f"Tidak ada penerbangan untuk rute {asal} → {tujuan}."

            # Format output agar mudah dibaca AI
            result = f"Penerbangan {asal} → {tujuan} ({data['total_results']} tersedia):\n"
            for f in flights:
                result += (
                    f"- [{f['id']}] {f['airline']} {f['flight_number']} | "
                    f"Berangkat: {f['departure']} | Tiba: {f['arrival']} | "
                    f"Harga: Rp {f['price']:,} | Kursi: {f['seats_available']}\n"
                )
            return result

        elif response.status_code == 404:
            # Sinyal eksplisit: AI TIDAK BOLEH mengarang data
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
    Gunakan alat ini untuk mencari hotel berdasarkan lokasi.
    Input bisa berupa nama kota saja, atau nama kota + harga maksimal.
    Format: "LOKASI" atau "LOKASI,MAX_HARGA"
    Contoh: "Bali" atau "Bali,500000"

    Lokasi yang tersedia: Bali, Lombok, Yogyakarta.
    """
    try:
        lokasi = query.strip()
        max_price = None

        if "," in query:
            parts = query.split(",", 1)
            lokasi = parts[0].strip()
            try:
                max_price = int(parts[1].strip())
            except ValueError:
                pass

        print(f"[TOOL] cari_hotel: lokasi={lokasi}, max_price={max_price}")

        params = {"location": lokasi}
        if max_price:
            params["max_price"] = max_price

        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{MOCK_API_URL}/hotels", params=params)

        if response.status_code == 200:
            data = response.json()
            hotels = data.get("hotels", [])
            if not hotels:
                return f"Tidak ada hotel tersedia di {lokasi}."

            result = f"Hotel di {lokasi} ({data['total_results']} tersedia):\n"
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
    Format: "LOKASI" atau "LOKASI,KATEGORI"
    Kategori yang tersedia: wisata, kuliner, ibadah
    Contoh: "Bali" atau "Bali,wisata" atau "Yogyakarta,kuliner"

    Lokasi yang tersedia: Bali, Lombok, Yogyakarta.
    """
    try:
        lokasi = query.strip()
        kategori = None

        if "," in query:
            parts = query.split(",", 1)
            lokasi = parts[0].strip()
            kategori = parts[1].strip()

        print(f"[TOOL] cari_aktivitas: lokasi={lokasi}, kategori={kategori}")

        params = {"location": lokasi}
        if kategori:
            params["category"] = kategori

        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{MOCK_API_URL}/activities", params=params)

        if response.status_code == 200:
            data = response.json()
            activities = data.get("activities", [])
            if not activities:
                return f"Tidak ada aktivitas tersedia di {lokasi}."

            label = f" (kategori: {kategori})" if kategori else ""
            result = f"Aktivitas di {lokasi}{label} ({data['total_results']} tersedia):\n"
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