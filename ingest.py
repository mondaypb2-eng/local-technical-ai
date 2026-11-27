from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Iterable

import chromadb
import fitz
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
KNOWLEDGE_DIR = Path(os.getenv("KNOWLEDGE_DIR", "knowledge"))
CHROMA_DIR = os.getenv("CHROMA_DIR", "vector_db")
COLLECTION_NAME = "technical_knowledge"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 180
SUPPORTED = {".pdf", ".txt", ".md"}


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def embed_text(text: str) -> list[float]:
    response = requests.post(
        f"{BASE_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
        timeout=180,
    )
    response.raise_for_status()
    data = response.json()
    embeddings = data.get("embeddings")
    if not embeddings or not embeddings[0]:
        raise RuntimeError(f"Ollama ไม่ส่ง embedding กลับมา: {data}")
    return embeddings[0]


def split_text(text: str) -> list[str]:
    text = text.replace("\x00", "").strip()
    if not text:
        return []

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + CHUNK_SIZE, length)
        if end < length:
            # พยายามตัดที่บรรทัดหรือช่องว่างเพื่อไม่ตัดกลางประโยค
            boundary = max(text.rfind("\n", start, end), text.rfind(" ", start, end))
            if boundary > start + int(CHUNK_SIZE * 0.55):
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break
        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks


def read_file(path: Path) -> Iterable[tuple[int, str]]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        with fitz.open(path) as pdf:
            for page_no, page in enumerate(pdf, start=1):
                yield page_no, page.get_text("text")
    else:
        yield 1, path.read_text(encoding="utf-8-sig", errors="replace")


def ingest_file(path: Path, collection) -> int:
    total = 0
    # ลบชิ้นข้อมูลเก่าของไฟล์เดียวกันก่อน เพื่อไม่ให้ข้อมูลซ้ำเมื่อสั่งนำเข้าใหม่
    collection.delete(where={"source_path": str(path.resolve())})

    for page_no, text in read_file(path):
        for chunk_no, chunk in enumerate(split_text(text)):
            digest = hashlib.sha256(
                f"{path.resolve()}|{page_no}|{chunk_no}|{chunk}".encode("utf-8")
            ).hexdigest()
            vector = embed_text(chunk)
            collection.upsert(
                ids=[digest],
                documents=[chunk],
                embeddings=[vector],
                metadatas=[{
                    "source": path.name,
                    "source_path": str(path.resolve()),
                    "page": page_no,
                    "chunk": chunk_no,
                }],
            )
            total += 1
    return total


def main():
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    paths = sorted(
        p for p in KNOWLEDGE_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED
    )
    if not paths:
        print(f"ไม่พบไฟล์ PDF/TXT/MD ใน {KNOWLEDGE_DIR.resolve()}")
        return

    collection = get_collection()
    grand_total = 0

    for path in paths:
        try:
            count = ingest_file(path, collection)
            grand_total += count
            print(f"สำเร็จ: {path} ({count} chunks)")
        except Exception as exc:
            print(f"ผิดพลาด: {path} -> {exc}")

    print(f"\nเสร็จสิ้น: เพิ่ม/ปรับปรุง {grand_total} chunks")
    print(f"จำนวน chunks ทั้งหมดในฐานข้อมูล: {collection.count()}")


if __name__ == "__main__":
    main()
