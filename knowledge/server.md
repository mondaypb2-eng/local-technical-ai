# Server Administration — พื้นฐานดูแลระบบเซิร์ฟเวอร์

## 1. Server คืออะไร
Server คือระบบที่ให้บริการแก่ client ผ่านเครือข่าย เช่น Web, DNS, DHCP, File, Database, Authentication และ Application service

## 2. การตรวจสอบเบื้องต้น
ตรวจตามลำดับ:
1. ไฟเลี้ยง, สถานะเครื่อง, ไฟแจ้งเตือน, พัดลมและอุณหภูมิ
2. สาย LAN, link, switch port และ IP
3. CPU, RAM, Disk space และ I/O
4. สถานะ service/process
5. Log ของระบบและแอปพลิเคชัน
6. Firewall, port listening, DNS และ routing
7. Dependency เช่น database, storage หรือ upstream service

## 3. Windows Server
PowerShell commands:
```powershell
hostname
ipconfig /all
Get-Service
Get-Process
Get-Volume
Get-EventLog -LogName System -Newest 30
Get-NetTCPConnection -State Listen
Test-NetConnection 127.0.0.1 -Port 3389
```
บางคำสั่งต้องใช้สิทธิ์ Administrator และ `Get-EventLog` อาจถูกแทนด้วย `Get-WinEvent` ในระบบใหม่

## 4. Linux Server
```bash
hostnamectl
ip addr
ip route
systemctl --failed
systemctl status <service>
journalctl -u <service> -n 100 --no-pager
df -h
free -h
top
ss -tulpn
```
ตรวจ permission และ service account ก่อนแก้ไฟล์หรือ restart service

## 5. ตรวจสอบ Port และ Service
- `LISTEN` หมายถึง process กำลังรอรับ connection
- ตรวจว่า service bind ที่ IP/port ที่ถูกต้อง
- ตรวจ firewall ทั้งฝั่ง client, server และ network firewall
- ทดสอบจาก client ด้วย `Test-NetConnection host -Port 443` หรือ `nc -vz host 443`
- Port เปิดไม่ได้ไม่ได้แปลว่า service เสียเสมอ อาจเป็น routing หรือ firewall

## 6. Database เบื้องต้น
ตรวจ:
- Service/database process ทำงานหรือไม่
- Disk เต็มหรือไม่
- Network/port และ credentials ถูกต้องหรือไม่
- Connection limit, lock, slow query และ error log
- Backup ล่าสุดและความสามารถในการ restore

ห้ามแก้ไขหรือลบ database files โดยตรงเพื่อแก้ปัญหาโดยไม่มีแผนสำรอง

## 7. Active Directory เบื้องต้น
AD DS ใช้จัดการ identity, domain join, authentication, group และ Group Policy
จุดตรวจ:
- DNS client ต้องชี้ DNS ภายในที่รู้จัก AD domain
- ตรวจเวลาเครื่องให้สอดคล้องกับ domain controller
- ตรวจการเชื่อมต่อ DC และ service สำคัญ
- ตรวจ event logs, replication และ account lockout
คำสั่งที่พบได้:
```powershell
whoami
nltest /dsgetdc:<domain>
gpresult /r
```

## 8. Incident handling
1. ระบุผลกระทบและขอบเขตผู้ใช้
2. เก็บเวลา, error message, log และการเปลี่ยนแปลงล่าสุด
3. แยกสาเหตุเป็น hardware, network, OS, service, application, dependency
4. ทดสอบสมมติฐานทีละข้อ
5. เปลี่ยนแปลงเท่าที่จำเป็นและมี rollback
6. ตรวจสอบผลหลังแก้ไข
7. บันทึกสาเหตุและแนวทางป้องกัน
