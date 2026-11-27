from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from ingest import get_collection, ingest_file, KNOWLEDGE_DIR, SUPPORTED
from rag import answer, ollama_status

load_dotenv()
st.set_page_config(page_title="Local Technical AI", page_icon="🛠️", layout="wide")

st.title("🛠️ Local Technical AI")
st.caption("ผู้ช่วยด้าน Network • MikroTik • Server • Cybersecurity • Python")

KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

with st.sidebar:
    st.header("สถานะระบบ")
    online, detail = ollama_status()
    if online:
        st.success("เชื่อมต่อ Ollama แล้ว")
        st.caption(detail)
    else:
        st.error("เชื่อมต่อ Ollama ไม่ได้")
        st.caption(detail)

    st.divider()
    st.subheader("ฐานความรู้")
    collection = get_collection()
    st.metric("จำนวน chunks", collection.count())

    uploaded = st.file_uploader(
        "เพิ่มเอกสาร PDF / TXT / MD",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )
    if st.button("นำเข้าเอกสารที่เลือก", use_container_width=True):
        if not uploaded:
            st.warning("กรุณาเลือกไฟล์ก่อน")
        else:
            progress = st.progress(0)
            status = st.empty()
            for index, file in enumerate(uploaded):
                target = KNOWLEDGE_DIR / Path(file.name).name
                target.write_bytes(file.getvalue())
                try:
                    count = ingest_file(target, collection)
                    status.success(f"{file.name}: นำเข้า {count} chunks แล้ว")
                except Exception as exc:
                    status.error(f"{file.name}: {exc}")
                progress.progress((index + 1) / len(uploaded))
            st.rerun()

    st.divider()
    if st.button("ล้างประวัติแชต", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("เอกสารอ้างอิง"):
                for source in message["sources"]:
                    st.markdown(
                        f"- **{source['source']}** หน้า {source['page']} "
                        f"(ระยะห่าง: {source['distance']:.3f})"
                    )

question = st.chat_input("ถามปัญหาด้าน Network, Server, MikroTik หรือ Python...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("กำลังค้นฐานความรู้และสร้างคำตอบ..."):
            try:
                history = st.session_state.messages[:-1]
                response, sources = answer(question, history=history)
                st.markdown(response)
                if sources:
                    with st.expander("เอกสารอ้างอิง"):
                        for source in sources:
                            st.markdown(
                                f"- **{source['source']}** หน้า {source['page']} "
                                f"(ระยะห่าง: {source['distance']:.3f})"
                            )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources,
                })
            except Exception as exc:
                error = f"เกิดข้อผิดพลาด: {exc}"
                st.error(error)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error,
                })
