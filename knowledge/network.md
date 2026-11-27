# Network Fundamentals — คู่มือความรู้พื้นฐานเครือข่าย

## 1. แบบจำลองเครือข่าย
- LAN คือเครือข่ายภายในพื้นที่จำกัด เช่น บ้านหรือสำนักงาน
- WAN เชื่อมต่อเครือข่ายที่อยู่ห่างกัน เช่น การเชื่อมต่อผ่านผู้ให้บริการอินเทอร์เน็ต
- OSI มี 7 ชั้น: Physical, Data Link, Network, Transport, Session, Presentation, Application
- TCP/IP มักอธิบายเป็น Link, Internet, Transport และ Application

## 2. IP Address และ Subnet
IPv4 มี 32 บิต เช่น `192.168.1.10`
- Network address ระบุเครือข่าย
- Host address ระบุอุปกรณ์ในเครือข่าย
- Default gateway เป็นทางออกไปยังเครือข่ายอื่น
- Subnet mask หรือ prefix เช่น `/24` กำหนดขอบเขต network
- อุปกรณ์ใน subnet เดียวกันสื่อสารกันได้โดยตรงผ่าน Layer 2 เมื่อไม่มีการแยก VLAN

ตัวอย่าง `192.168.10.25/24`
- Network: `192.168.10.0/24`
- ช่วง host ทั่วไป: `192.168.10.1` ถึง `192.168.10.254`
- Broadcast: `192.168.10.255`

## 3. TCP และ UDP
- TCP เป็น connection-oriented มีการยืนยันการรับส่งและจัดลำดับข้อมูล เหมาะกับเว็บทั่วไป, SSH, ฐานข้อมูล
- UDP ไม่มีการรับประกันการส่งถึง เหมาะกับ DNS query ทั่วไป, VoIP, streaming และงานที่ต้องการ latency ต่ำ
- TCP handshake: SYN → SYN-ACK → ACK

## 4. DNS
DNS แปลงชื่อโดเมนเป็น IP address
- `A`: ชื่อไป IPv4
- `AAAA`: ชื่อไป IPv6
- `CNAME`: alias
- `MX`: mail exchanger
- `TXT`: ข้อความ เช่น SPF/verification
คำสั่งตรวจสอบ:
```powershell
nslookup example.com
ipconfig /displaydns
ipconfig /flushdns
```
การ flush cache ควรทำเมื่อสงสัย cache DNS ในเครื่อง ไม่ใช่แก้ปัญหา DNS server ต้นทาง

## 5. DHCP
DHCP แจก IP configuration อัตโนมัติ โดยกระบวนการ DORA:
1. Discover
2. Offer
3. Request
4. Acknowledge

ข้อมูลที่มักได้รับ: IP, subnet mask, gateway, DNS server, lease time
คำสั่ง Windows:
```powershell
ipconfig /all
ipconfig /release
ipconfig /renew
```
อย่า release/renew เครื่องที่เชื่อมต่อระยะไกลโดยไม่มีช่องทางสำรอง

## 6. VLAN และ Switching
- VLAN แบ่ง broadcast domain บน switch
- Access port ใช้กับอุปกรณ์ปลายทาง VLAN เดียว
- Trunk port ส่งหลาย VLAN โดยใช้ tagging เช่น IEEE 802.1Q
- การสื่อสารข้าม VLAN ต้องผ่าน Layer 3 routing
- ตรวจสอบ VLAN ID, port membership, trunk allowed VLAN และ native VLAN ให้ตรงกันทั้งสองฝั่ง

## 7. Routing
Router ส่ง packet ระหว่าง network โดยดู routing table
- Connected route: เครือข่ายที่ interface เชื่อมต่อโดยตรง
- Static route: ผู้ดูแลกำหนดเอง
- Default route: เส้นทางเมื่อไม่มี route ที่เฉพาะเจาะจงกว่า
- NAT แปลง IP address มักใช้ให้ private IP ออกอินเทอร์เน็ต

## 8. Firewall
Firewall กรอง traffic ตามเงื่อนไข เช่น source/destination IP, protocol, port, interface และ state
แนวทาง:
- ใช้หลัก least privilege
- อนุญาตเฉพาะ traffic ที่จำเป็น
- ตรวจสอบลำดับ rule และ default policy
- สำรอง config ก่อนแก้ไข
- หลีกเลี่ยงการเปิด management port สู่อินเทอร์เน็ตโดยตรง

## 9. ลำดับตรวจสอบเมื่ออินเทอร์เน็ตใช้ไม่ได้
1. ตรวจสาย, ไฟ, link light และ Wi-Fi association
2. `ipconfig /all` ตรวจ IP, mask, gateway, DNS
3. `ping 127.0.0.1` ตรวจ TCP/IP stack ในเครื่อง
4. `ping <default-gateway>` ตรวจการเชื่อมต่อถึง gateway
5. `ping 1.1.1.1` ทดสอบออก IP ภายนอก (อาจถูกบล็อก ICMP)
6. `nslookup example.com` ตรวจ DNS
7. `tracert 1.1.1.1` ดูเส้นทาง (บาง hop ไม่ตอบ ICMP ได้)
8. ตรวจ switch port, VLAN, DHCP, router route, NAT และ firewall ตามหลักฐาน

## 10. Windows network commands
```powershell
ipconfig /all
ping 192.168.1.1
tracert 1.1.1.1
pathping 1.1.1.1
nslookup example.com
arp -a
route print
netstat -ano
Test-NetConnection example.com -Port 443
```
คำสั่งเหล่านี้เป็นการตรวจสอบเป็นหลัก แต่ `ipconfig /release`, `/renew`, `/flushdns` เปลี่ยนสถานะหรือ cache บางส่วน
