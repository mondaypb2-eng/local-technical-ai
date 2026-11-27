from __future__ import annotations

import os
from typing import Any

import chromadb
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen3:1.7b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
CHROMA_DIR = os.getenv("CHROMA_DIR", "vector_db")
COLLECTION_NAME = "technical_knowledge"

SYSTEM_PROMPT = """คุณคือ Local Technical AI ผู้ช่วยด้านไอทีและงานระบบ
ตอบเป็นภาษาไทยที่ชัดเจน เป็นขั้นตอน และอธิบายเหตุผลของคำสั่ง
ใช้ข้อมูลจาก CONTEXT เป็นหลัก หากบริบทไม่พอให้บอกตรง ๆ ว่าข้อมูลไม่เพียงพอ
ห้ามแต่งผลตรวจสอบหรืออ้างว่าได้รันคำสั่งจริง
ก่อนเสนอคำสั่งที่เปลี่ยนแปลงระบบ เครือข่าย บัญชี หรือข้อมูล ให้เตือนผลกระทบและให้ผู้ใช้ตรวจสอบก่อน
หากเป็นคำสั่งลบข้อมูล ปิดระบบ หรือเปลี่ยน firewall ให้เน้นความเสี่ยงและเสนอวิธีสำรอง/ย้อนกลับ
แยกข้อเท็จจริงจากข้อสันนิษฐาน และขอข้อมูลเพิ่มเมื่อจำเป็น
"""


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def embed_query(text: str) -> list[float]:
    response = requests.post(
        f"{BASE_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
        timeout=180,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("embeddings"):
        raise RuntimeError("ไม่ได้รับ embedding จาก Ollama")
    return data["embeddings"][0]


def retrieve(query: str, n_results: int = 5) -> list[dict[str, Any]]:
    collection = get_collection()
    if collection.count() == 0:
        return []

    vector = embed_query(query)
    result = collection.query(
        query_embeddings=[vector],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    items = []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for doc, meta, distance in zip(docs, metas, distances):
        items.append({
            "text": doc,
            "source": meta.get("source", "ไม่ทราบไฟล์"),
            "page": meta.get("page", 1),
            "distance": distance,
        })
    return items


def answer(question: str, history: list[dict] | None = None, n_results: int = 5):
    sources = retrieve(question, n_results=n_results)
    if sources:
        context = "\n\n".join(
            f"[แหล่งข้อมูล {i+1}: {s['source']} หน้า {s['page']}]\n{s['text']}"
            for i, s in enumerate(sources)
        )
    else:
        context = "ไม่พบเอกสารที่เกี่ยวข้องในฐานความรู้"

    user_prompt = f"""คำถาม:
{question}

CONTEXT จากฐานความรู้:
{context}

แนวทางตอบ:
- ถ้า CONTEXT มีคำตอบ ให้สังเคราะห์โดยอ้างชื่อไฟล์และหน้า
- ถ้า CONTEXT ไม่พอ ให้ระบุส่วนที่ยังไม่ทราบ อย่าสร้างข้อมูลเอกสารขึ้นเอง
- สามารถให้ความรู้ทั่วไปประกอบได้ แต่ต้องแยกให้ชัดว่าเป็นความรู้ทั่วไป
"""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        # ใช้เฉพาะบทสนทนาล่าสุดจำนวนจำกัด ไม่ส่ง system prompt ซ้ำ
        for item in history[-8:]:
            if item.get("role") in {"user", "assistant"} and item.get("content"):
                messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": user_prompt})

    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"model": CHAT_MODEL, "messages": messages, "stream": False},
        timeout=300,
    )
    response.raise_for_status()
    payload = response.json()
    text = payload.get("message", {}).get("content", "").strip()
    if not text:
        raise RuntimeError(f"ไม่ได้รับคำตอบจาก Ollama: {payload}")
    return text, sources


def ollama_status() -> tuple[bool, str]:
    try:
        response = requests.get(f"{BASE_URL}/api/tags", timeout=5)
        response.raise_for_status()
        names = [m.get("name", "") for m in response.json().get("models", [])]
        return True, ", ".join(names) if names else "เชื่อมต่อได้ แต่ยังไม่พบโมเดล"
    except Exception as exc:
        return False, str(exc)
