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
คอลัมน์ที่รองรับ: `ID, Date, Category, Title, Summary, Content, ImageURL, Author, Status`
- แสดงเฉพาะแถวที่ `Status` ว่าง หรือเป็น `Published` / `เผยแพร่` (ใส่ `Draft` หรือค่าอื่นเพื่อซ่อน)
- เรียงจากใหม่ไปเก่าตาม `Date` (รองรับ `2026-11-12`, `12/11/2569`, `11 พฤศจิกายน 2569`, `11 พ.ย. 2569`)
- `ImageURL` ต้องเป็นลิงก์ https ไปยังไฟล์รูปโดยตรง
- หน้าเว็บโหลดใหม่ทุก 60 วินาทีขณะเปิดอยู่ แต่ Google อาจแคชไฟล์ CSV ที่เผยแพร่ไว้ราว 5 นาที

## Deploy
- ปัจจุบัน deploy ด้วย Vercel CLI: `vercel deploy --prod --yes` (โปรเจ็กต์ `pataraya-pilot`)
- ธีมสี: `#0F2F4F` (navy) และ `#0284c7` (accent ของห้องข่าว)
