import os
import time
import chromadb
from chromadb.config import Settings

CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = "travel_conversations"
MAX_WINDOW = 5  # sliding window 5 interaksi terakhir
TTL_SECONDS = 86400  # 24 jam

def get_chroma_client():
    return chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        settings=Settings(anonymized_telemetry=False)
    )

def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def save_conversation(session_id: str, query: str, response: str):
    """Simpan satu pasang query-response ke ChromaDB."""
    try:
        collection = get_collection()
        timestamp = int(time.time())
        doc_id = f"{session_id}_{timestamp}"

        collection.add(
            documents=[f"User: {query}\nAI: {response}"],
            metadatas=[{
                "session_id": session_id,
                "timestamp": timestamp,
                "query": query[:200],
            }],
            ids=[doc_id]
        )
    except Exception as e:
        print(f"[MEMORY] Gagal simpan percakapan: {e}")

def get_relevant_context(session_id: str, query: str) -> str:
    """
    Ambil konteks relevan dari ChromaDB untuk session tertentu.
    Gabungkan sliding window (5 terbaru) + semantic search.
    """
    try:
        collection = get_collection()

        # Ambil 5 interaksi terakhir dari session ini (sliding window)
        all_results = collection.get(
            where={"session_id": session_id},
            include=["documents", "metadatas"]
        )

        if not all_results["documents"]:
            return ""

        # Urutkan berdasarkan timestamp, ambil 5 terbaru
        paired = list(zip(
            all_results["documents"],
            all_results["metadatas"]
        ))
        paired.sort(key=lambda x: x[1].get("timestamp", 0), reverse=True)
        recent = paired[:MAX_WINDOW]

        # Hapus yang sudah expired (TTL 24 jam)
        now = int(time.time())
        recent = [
            (doc, meta) for doc, meta in recent
            if now - meta.get("timestamp", 0) < TTL_SECONDS
        ]

        if not recent:
            return ""

        # Susun konteks dari yang paling lama ke paling baru
        recent.reverse()
        context_lines = [doc for doc, _ in recent]
        context = "\n---\n".join(context_lines)

        return f"Konteks percakapan sebelumnya:\n{context}\n"

    except Exception as e:
        print(f"[MEMORY] Gagal ambil konteks: {e}")
        return ""

def cleanup_old_sessions():
    """Hapus dokumen yang sudah melewati TTL 24 jam."""
    try:
        collection = get_collection()
        all_results = collection.get(include=["metadatas"])

        now = int(time.time())
        ids_to_delete = []

        for i, meta in enumerate(all_results["metadatas"]):
            if now - meta.get("timestamp", 0) > TTL_SECONDS:
                ids_to_delete.append(all_results["ids"][i])

        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            print(f"[MEMORY] Hapus {len(ids_to_delete)} dokumen expired")

    except Exception as e:
        print(f"[MEMORY] Gagal cleanup: {e}")