Local Technical AI
ระบบผู้ช่วยด้านไอทีที่ทำงานในเครื่องผ่าน Ollama + Qwen3 + BGE-M3 + ChromaDB + Streamlit
1. ตรวจสอบโมเดลในเครื่อง
เปิด PowerShell ในโฟลเดอร์โปรเจกต์:
```powershell
ollama list
```
ควรเห็น `qwen3:1.7b` และ `bge-m3:latest` (ถ้าแสดงชื่อ embedding เป็น `bge-m3:latest` ก็ใช้ชื่อนี้ใน `.env` ได้)
2. สร้างและเปิด virtual environment
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
หาก PowerShell บล็อกสคริปต์ ให้เปิดเฉพาะหน้าต่างนี้ด้วย:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
3. ติดตั้งไลบรารี
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
4. ตั้งค่าโมเดล
โปรแกรมตั้งค่าเริ่มต้นไว้แล้ว:
Chat: `qwen3:1.7b`
Embedding: `bge-m3`
หากชื่อโมเดลใน `ollama list` ต่างออกไป ให้แก้ค่าที่หัวไฟล์ `.env` โดยคัดลอกจาก `.env.example` แล้วเปลี่ยนชื่อให้ตรง:
```powershell
Copy-Item .env.example .env
```
5. นำเข้าเอกสารใน knowledge
รองรับ PDF, TXT และ Markdown (`.md`) รวมถึงโฟลเดอร์ย่อย
```powershell
python ingest.py
```
PDF ที่เป็นภาพสแกนล้วนจะไม่มีข้อความให้ดึง ต้องทำ OCR ก่อน
6. เปิดหน้าแชต
ตรวจว่า Ollama ทำงานอยู่ แล้วรัน:
```powershell
streamlit run app.py
```
เบราว์เซอร์จะเปิดหน้าเว็บในเครื่อง โดยปกติคือ `http://localhost:8501`
7. เพิ่มเอกสารภายหลัง
ทำได้ 2 วิธี:
วางไฟล์ `.pdf`, `.txt`, `.md` ใน `knowledge` แล้วรัน `python ingest.py`
ใช้แถบด้านข้างในหน้าเว็บเพื่ออัปโหลดเอกสาร
8. โครงสร้าง
```text
Local_Technical_AI/
├── knowledge/       # เอกสารความรู้
├── skills/          # คู่มือขั้นตอนเฉพาะงาน
├── vector_db/       # ฐานข้อมูลเวกเตอร์ (สร้างอัตโนมัติ)
├── app.py           # หน้าแชต
├── ingest.py        # อ่านเอกสารและทำดัชนี
├── rag.py           # ค้นเอกสารและสร้างคำตอบ
└── requirements.txt
```
ข้อจำกัดและความปลอดภัย
ระบบนี้เป็น RAG ไม่ใช่การ fine-tune โมเดล
คำตอบอาจผิดได้ ต้องตรวจสอบก่อนนำไปใช้กับระบบจริง
เวอร์ชันนี้ยังไม่สั่งงานเครื่องหรือแก้ config อัตโนมัติ
อย่าใส่รหัสผ่าน, API keys, private keys หรือข้อมูลลับลงใน knowledge
คำสั่งที่เปลี่ยนแปลงระบบควรตรวจสอบและสำรองข้อมูลก่อนเสมอ
