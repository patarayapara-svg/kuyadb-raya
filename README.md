# kuyadb-raya — เว็บไซต์เครือข่ายการศึกษาปาตารายอ (Pataraya)

ซอร์สโค้ดของเว็บ https://pataraya-pilot.vercel.app (โปรเจ็กต์ Vercel `pataraya-pilot`)

## โครงสร้าง
- `public/` — **ไฟล์เว็บที่เผยแพร่จริง** (Vercel ใช้ `outputDirectory: public` ใน `vercel.json` ไม่ต้องมีขั้นตอน build)
  - `public/index.html` หน้าแรก, `public/news/index.html` ห้องข่าว, `public/write/` ระบบส่งงานเขียน ฯลฯ
  - `public/assets/` CSS, JS, ฟอนต์, รูปภาพ
- `src/` — ตัวสร้างหน้าเว็บ (`python3 src/build.py` เขียนทับ `public/` ทั้งหมด)
  - เนื้อหาและเมนูอยู่ใน `src/build.py`, สไตล์ใน `src/style.css` และ `src/system.css`
  - ห้องข่าวโหลดข่าวจาก Google Sheets ผ่าน `src/news-sheet.js` (ที่อยู่ CSV อยู่ในตัวแปร `NEWS_CSV` ใน `src/build.py`)
- `vercel.json` — ส่วนหัวความปลอดภัย (CSP), redirect, rewrite
- `news/index.html` ที่ระดับบนสุดของ repo เป็นร่างเดิม (12 พ.ย. 2569) **ไม่ถูกเผยแพร่** หน้าจริงคือ `public/news/index.html`

## ไฟล์ไบนารี (รูปภาพ ฟอนต์ PDF)
ไฟล์ไบนารี 108 ไฟล์ (ประมาณ 35 MB) ระบุไว้ใน `scripts/binary-assets.sha256`
หากยังไม่มีใน repo ให้รัน

    bash scripts/fetch-binary-assets.sh

สคริปต์จะดาวน์โหลดจากเว็บจริง ตรวจ SHA-256 ทุกไฟล์ แล้วคัดลอกไว้ใน `assets/` ให้ `src/build.py` ใช้ต่อได้
**ต้อง commit ไฟล์ไบนารีให้ครบก่อนผูก repo นี้กับ Vercel** มิฉะนั้นการ deploy อัตโนมัติจะได้เว็บที่ไม่มีรูปและฟอนต์

## ห้องข่าวจาก Google Sheets
คอลัมน์ 11 ช่อง: `ID, Date, Category, Title, Summary, Content, ImageURL, Author, Status, GalleryURLs, ReadMoreURL`
- แสดงเฉพาะแถวที่ `Status` เป็น `Published` หรือ `เผยแพร่` (ว่าง, Draft หรือค่าอื่นจะไม่แสดง)
- เรียงจาก `ID` มากไปน้อย (ให้ข่าวใหม่ใช้เลข ID มากกว่าข่าวเก่า)
- `ImageURL` และ `GalleryURLs` ต้องเป็นไฟล์ที่เปิดดูได้โดยไม่ต้องล็อกอิน: ลิงก์ https ตรงถึงรูป, เส้นทางบนเว็บเช่น `/assets/img/...`, หรือลิงก์แชร์ Google Drive ที่ตั้งเป็น "Anyone with the link can view" (เว็บจะแปลงเป็น `https://drive.google.com/thumbnail?id=FILEID&sz=w1600` เอง)
- `GalleryURLs` คั่นหลายรูปด้วยเครื่องหมาย `|`
- `ReadMoreURL` ถ้ามี จะแสดงปุ่มอ่านเพิ่มเติมในกล่องข่าว
- ข่าวที่มีหน้าสถิตบนเว็บอยู่แล้วจะไม่ถูกแสดงซ้ำจากตาราง
- คลิกการ์ดข่าวจากตารางเปิดกล่องอ่านเนื้อหาเต็ม (ข้อความถูกใส่แบบปลอดภัย ไม่รัน HTML จากช่อง Content) พร้อมปุ่มแชร์ Facebook และ LINE
- หน้าเว็บโหลดใหม่ทุก 60 วินาทีขณะเปิดอยู่ แต่ Google อาจแคชไฟล์ CSV ที่เผยแพร่ไว้ราว 5 นาที

## Deploy
- ปัจจุบัน deploy ด้วย Vercel CLI: `vercel deploy --prod --yes` (โปรเจ็กต์ `pataraya-pilot`)
- ธีมสี: `#0F2F4F` (navy) และ `#0284c7` (accent ของห้องข่าว)
