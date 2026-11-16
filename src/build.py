import os, shutil, re, glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = ROOT + '/src'
import sys
sys.path.insert(0, SRC)
from articles import ARTICLES as LIB_ARTICLES
OUT = ROOT + '/public'
EMAIL = 'patarayapara@gmail.com'
CTA = 'นัดเยี่ยมชม / สอบถามการสมัคร'
SITE = 'https://pataraya-pilot.vercel.app'

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT + '/assets')
shutil.copytree(ROOT + '/assets/img', OUT + '/assets/img')
shutil.copytree(ROOT + '/assets/fonts', OUT + '/assets/fonts')
os.remove(OUT + '/assets/fonts/fonts.css')
fonts_css = open(ROOT + '/assets/fonts/fonts.css').read()
css = open(SRC + '/style.css').read() + open(SRC + '/system.css').read()
open(OUT + '/assets/style.css', 'w').write(fonts_css + css)
shutil.copy(SRC + '/site.js', OUT + '/assets/site.js')
shutil.copy(ROOT + '/assets/og.jpg', OUT + '/assets/og.jpg')
if os.path.isdir(ROOT + '/assets/downloads'):
    if os.path.exists(OUT + '/downloads'):
        shutil.rmtree(OUT + '/downloads')
    shutil.copytree(ROOT + '/assets/downloads', OUT + '/downloads')
os.makedirs(OUT + '/assets/vendor', exist_ok=True)
shutil.copy(ROOT + '/assets/vendor/supabase.js', OUT + '/assets/vendor/supabase.js')
shutil.copy(SRC + '/sb-public.js', OUT + '/assets/sb-public.js')
shutil.copy(SRC + '/write.js', OUT + '/assets/write.js')
shutil.copy(SRC + '/news-sheet.js', OUT + '/assets/news-sheet.js')

import hashlib
ASSET_V = hashlib.md5((fonts_css + css + open(SRC + '/site.js').read() + open(SRC + '/write.js').read() + open(SRC + '/news-sheet.js').read()).encode()).hexdigest()[:8]
WRITE_JS = f'<script type="module" src="/assets/write.js?v={ASSET_V}"></script>'
NEWS_CSV = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQe0ljXjRA5jN_mgYpv4F8oiPKAwnwxJO0qEYRfRwW-5mdRoLCLpiNt0zSU9Gnw51vwfGas24Ov9Cu0/pub?gid=1444979164&single=true&output=csv'
NEWS_JS = f'<script src="/assets/news-sheet.js?v={ASSET_V}" defer></script>'
def pic(name, alt, sizes='100vw', eager=False, cls=''):
    ws = sorted(int(re.search(r'-(\d+)\.webp$', f).group(1)) for f in glob.glob(f'{ROOT}/assets/img/{name}-*.webp'))
    big = ws[-1]
    im = Image.open(f'{ROOT}/assets/img/{name}-{big}.webp')
    w, h = im.size
    srcset = ', '.join(f'/assets/img/{name}-{x}.webp {x}w' for x in ws)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="/assets/img/{name}-{ws[min(1,len(ws)-1)]}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{alt}" {load}>')

def logo_img(name, alt):
    return f'<img src="/assets/img/{name}.webp" width="150" height="150" alt="{alt}" loading="lazy" decoding="async">'

NAV = [('/', 'หน้าแรก', 'home'), ('/about/', 'เราเชื่ออะไร', 'about'),
       ('/programs/', 'หลักสูตร/โรงเรียน', 'programs'), ('/raya-hub/', 'Raya Hub', 'hub'),
       ('/contact/', 'ติดต่อ/สมัคร', 'contact')]

NB = '<span class="nb">%s</span>'
def softwrap(html):
    pairs = [
      ('วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์', 'วิทยาลัย<wbr>เทคโนโลยี<wbr>' + NB % 'พณิชยการ' + '<wbr>' + NB % 'มูฮำมาดีย์'),
      ('มูลนิธิเพื่อการศึกษามูฮำมาดียะห์', 'มูลนิธิ<wbr>เพื่อการศึกษา<wbr>' + NB % 'มูฮำมาดียะห์'),
      ('โรงเรียนอิสลามวิทยามูลนิธิ', 'โรงเรียน<wbr>อิสลามวิทยา<wbr>มูลนิธิ'),
    ]
    def fix(m):
        t = m.group(1)
        for a, b in pairs:
            t = t.replace(a, b)
        return '>' + t + '<'
    return re.sub(r'>([^<]+)<', fix, html)


GROUPS = [
  ('หน้าแรก', 'ห้องโถง', '/', [('/', 'ห้องโถง', 'หน้าแรก', 'home')]),
  ('เกี่ยวกับเรา', 'รับแขก · ประชุม · เกียรติยศ', None, [
     ('/about/', 'ห้องรับแขก', 'เราเชื่ออะไร และประวัติ', 'about'),
     ('/network/', 'ห้องประชุม', 'บุคลากรและเครือข่าย', 'network'),
     ('/honors/', 'ห้องเกียรติยศ', 'ความภาคภูมิใจของบ้าน', 'honors')]),
  ('ห้องเรียน', 'หลักสูตร/โรงเรียน', None, [
     ('/programs/', 'ภาพรวมห้องเรียน', 'หลักสูตรและโรงเรียนทั้งหมด', 'programs'),
     ('/programs/#iwfs', 'IWFS', 'โรงเรียนอิสลามวิทยามูลนิธิ', 'programs-iwfs'),
     ('/programs/#mutec', 'MUTEC', 'วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์', 'programs-mutec'),
     ('/programs/#muef', 'MUEF', 'มูลนิธิเพื่อการศึกษามูฮำมาดียะห์', 'programs-muef')]),
  ('นวัตกรรมและความรู้', 'แลป · สมุด · ข่าว', None, [
     ('/raya-hub/', 'ห้องแลป', 'นวัตกรรมและแพลตฟอร์ม', 'hub'),
     ('/library/', 'ห้องสมุด', 'งานเขียนและบทเรียน', 'library'),
     ('/news/', 'ห้องข่าว', 'ข่าวและกิจกรรม', 'news')]),
  ('ติดต่อ/สมัคร', 'นั่งเล่น · หน้าประตู', None, [
     ('/faq/', 'ห้องนั่งเล่น', 'FAQ ผู้ปกครอง', 'faq'),
     ('/contact/', 'หน้าประตู', 'ติดต่อ อีเมล LINE ที่ตั้ง', 'contact')]),
]
NAV = [(h, r, t, k) for g in GROUPS for (h, r, t, k) in g[3] if '#' not in h]

def build_nav(key):
    out = []
    for n, (label, sub, href, items) in enumerate(GROUPS):
        active = any(k == key for _, _, _, k in items)
        cur = ' aria-current="page"' if active else ''
        if href:
            out.append(f'<li class="top-item"><a class="top" href="{href}"{cur}><b>{label}</b><small>{sub}</small></a></li>')
            continue
        lis = ''.join(f'<li><a href="{h}"{" aria-current=\"page\"" if k == key else ""}>{ARCH}<span><b>{r}</b><small>{t}</small></span></a></li>' for h, r, t, k in items)
        out.append(f'<li class="top-item has-sub{" is-active" if active else ""}"><button class="top" type="button" aria-expanded="false" aria-controls="sub-{n}"><b>{label}</b><small>{sub}</small><i class="chev" aria-hidden="true"></i></button>'
                   f'<ul class="sub" id="sub-{n}">{lis}</ul></li>')
    return ''.join(out)

def subbar(key):
    for label, sub, href, items in GROUPS:
        if href or not any(k == key for *_, k in items): continue
        lis = ''.join(f'<li><a href="{h}"{" aria-current=\"page\"" if k == key else ""}>{r}</a></li>' for h, r, t, k in items if '#' not in h)
        return f'<nav class="subbar" aria-label="ห้องในหมวด{label}"><div class="wrap"><span class="sb-label">{label}</span><ul>{lis}</ul></div></nav>'
    return ''

ARCH = '<svg class="arch" width="28" height="34" viewBox="0 0 28 34" aria-hidden="true" focusable="false"><use href="#arch"/></svg>'
SPRITE = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="arch" viewBox="0 0 28 34">'
          '<path d="M3 33V15C3 8 8 3 14 1c6 2 11 7 11 14v18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/>'
          '<path d="M9 33V17c0-4 2.2-7 5-8.4 2.8 1.4 5 4.4 5 8.4v16" fill="none" stroke="currentColor" stroke-width="1.8" opacity=".55"/></symbol></svg>')


ICONS = {
 'fb': '<path d="M14 8.5V6.8c0-.8.2-1.3 1.4-1.3H17V2.6c-.3 0-1.2-.1-2.3-.1-2.3 0-3.8 1.4-3.8 3.9v2.1H8.3v3.3h2.6V22H14v-10.2h2.6l.4-3.3z"/>',
 'yt': '<path d="M22 8.2a3 3 0 0 0-2.1-2.1C18 5.6 12 5.6 12 5.6s-6 0-7.9.5A3 3 0 0 0 2 8.2 31 31 0 0 0 1.6 12 31 31 0 0 0 2 15.8a3 3 0 0 0 2.1 2.1c1.9.5 7.9.5 7.9.5s6 0 7.9-.5a3 3 0 0 0 2.1-2.1c.3-1.2.4-2.5.4-3.8s-.1-2.6-.4-3.8zM10 15.1V8.9l5.2 3.1z"/>',
 'tt': '<path d="M16.6 2h-3.3v13.4a2.8 2.8 0 1 1-2-2.7V9.3a6.1 6.1 0 1 0 5.3 6V8.6a7.6 7.6 0 0 0 4.4 1.4V6.7a4.4 4.4 0 0 1-4.4-4.4z"/>',
 'web': '<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm6.9 6h-3a15.7 15.7 0 0 0-1.4-3.6A8 8 0 0 1 18.9 8zM12 4c.8 1.1 1.5 2.4 1.9 4h-3.8c.4-1.6 1.1-2.9 1.9-4zM4.3 14a8.2 8.2 0 0 1 0-4h3.4a16.5 16.5 0 0 0 0 4zm.8 2h3a15.7 15.7 0 0 0 1.4 3.6A8 8 0 0 1 5.1 16zm3-8h-3a8 8 0 0 1 4.4-3.6A15.7 15.7 0 0 0 8.1 8zM12 20c-.8-1.1-1.5-2.4-1.9-4h3.8c-.4 1.6-1.1 2.9-1.9 4zm2.3-6H9.7a14.7 14.7 0 0 1 0-4h4.6a14.7 14.7 0 0 1 0 4zm.2 5.6c.6-1.1 1.1-2.3 1.4-3.6h3a8 8 0 0 1-4.4 3.6zm1.8-5.6a16.5 16.5 0 0 0 0-4h3.4a8.2 8.2 0 0 1 0 4z"/>',
}
def icon(k): return f'<svg class="ico" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false" fill="currentColor">{ICONS[k]}</svg>'
SOCIAL = [
 ('เครือข่ายการศึกษาปาตารายอ', [
   ('fb', 'Facebook', 'เครือข่ายการศึกษาปาตารายอ', 'https://www.facebook.com/kuyadailamee'),
   ('yt', 'YouTube', '@patarayahub', 'https://www.youtube.com/@patarayahub'),
   ('tt', 'TikTok', '@anak.pataraya', 'https://www.tiktok.com/@anak.pataraya')]),
 ('โรงเรียนอิสลามวิทยามูลนิธิ (IWFS)', [
   ('fb', 'Facebook', 'โรงเรียนอิสลามวิทยามูลนิธิ เพจหลัก', 'https://www.facebook.com/iwf.ac.th'),
   ('tt', 'TikTok', '@iwfs60', 'https://www.tiktok.com/@iwfs60')]),
 ('วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC)', [
   ('web', 'เว็บไซต์', 'www.mutec.ac.th', 'https://www.mutec.ac.th/'),
   ('fb', 'Facebook', 'วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์', 'https://www.facebook.com/mutec.ac.th')]),
]
SHORT = {'เครือข่ายการศึกษาปาตารายอ':'เครือข่าย','โรงเรียนอิสลามวิทยามูลนิธิ (IWFS)':'IWFS','วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC)':'MUTEC'}
def social_footer():
    items=''.join(f'<li><a class="soc" href="{u}" rel="noopener" target="_blank" aria-label="{n} {SHORT[g]} (เปิดในแท็บใหม่)" title="{n} {SHORT[g]}">{icon(k)}</a></li>' for g,l in SOCIAL for k,n,h,u in l)
    return f'<ul class="soc-row" aria-label="ช่องทางออนไลน์">{items}</ul>'
def social_section():
    cols=''
    for g,l in SOCIAL:
        lis=''.join(f'<li><a class="soc-link" href="{u}" rel="noopener" target="_blank">{icon(k)}<span><b>{n}</b><small>{h}</small></span><span class="sr">(เปิดในแท็บใหม่)</span></a></li>' for k,n,h,u in l)
        cols+=f'<div class="card soc-card"><h3>{g}</h3><ul>{lis}</ul></div>'
    return f'<section class="section" id="social"><div class="wrap"><div class="section-head"><p class="eyebrow">ช่องทางออนไลน์</p><h2>ติดตามเราได้ที่</h2><p>ช่องทางทางการของเครือข่ายและแต่ละสถาบัน</p></div><div class="grid3">{cols}</div></div></section>'

def page(path, key, title, desc, body, hero='', index=True, scripts=''):
    nav = build_nav(key)
    canon = SITE + (path if path != '/' else '/')
    if path == '/_404/':
        canon = SITE + '/'
    robots = 'index,follow' if index else 'noindex,nofollow'
    hero_preload = ''
    if path == '/':
        hero_preload = ('<link rel="preload" as="image" href="/assets/img/b-hero-480.webp" imagesrcset="/assets/img/b-hero-480.webp 480w, /assets/img/b-hero-960.webp 960w, /assets/img/b-hero-1600.webp 1600w" imagesizes="(min-width:900px) 55vw, 100vw" fetchpriority="high">\n')
    html = f'''<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#0F2F4F">
<meta property="og:type" content="website">
<meta property="og:site_name" content="เครือข่ายการศึกษาปาตารายอ">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="th_TH">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta name="format-detection" content="telephone=no">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/IBMPlexSansThai-400-thai.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/Anuphan-600-thai.woff2" as="font" type="font/woff2" crossorigin>
{hero_preload}<link rel="stylesheet" href="/assets/style.css?v={ASSET_V}">
<script src="/assets/site.js?v={ASSET_V}" defer></script>
{scripts}
</head>
<body>
{SPRITE}
<a class="skip" href="#main">ข้ามไปที่เนื้อหา</a>
<div class="chrome">
<div class="topbar"><div class="wrap">
<p class="where">ตำบลจะแหน อำเภอสะบ้าย้อย จังหวัดสงขลา</p>
<div class="right">
<div class="lang" role="group" aria-label="ภาษา"><span lang="th" aria-current="true">ไทย</span><span lang="ms" aria-disabled="true" title="ภาษามลายู กำลังจัดทำ">MS</span><span lang="en" aria-disabled="true" title="English: coming soon">EN</span></div>
<a href="mailto:{EMAIL}">{EMAIL}</a>
</div></div></div>
<header class="site-header">
<div class="wrap head-top">
<a class="brand" href="/"><img src="/assets/img/mark-light.svg" width="52" height="44" alt=""><span><b>เครือข่ายการศึกษาปาตารายอ</b><span>Pataraya Education Network</span></span></a>
<a class="btn header-cta" href="/contact/#visit">{CTA}</a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="main-nav"><span class="bars" aria-hidden="true"></span>เมนู</button>
</div>
<nav class="main-nav" id="main-nav" aria-label="เมนูหลัก"><div class="wrap">
<ul class="menu">{nav}</ul>
<a class="btn nav-cta" href="/contact/#visit">{CTA}</a>
</div></nav>
</header>
</div>
<main id="main">
{hero}
{subbar(key)}
{body}
</main>
<footer class="site-footer"><div class="wrap">
<div class="cols">
<div>
<a class="brand" href="/"><img src="/assets/img/mark-dark.svg" width="52" height="44" alt=""><span><b>เครือข่ายการศึกษาปาตารายอ</b><span>Pataraya Education Network</span></span></a>
<p style="margin-top:1rem">โรงเรียนอิสลามวิทยามูลนิธิ (IWFS)<br>วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC)<br>มูลนิธิเพื่อการศึกษามูฮำมาดียะห์ (MUEF)</p>
</div>
<div>
<h2>เดินดูบ้าน</h2>
<ul>
{''.join(f'<li><a href="{h}">{r}</a> <span class="room">{t}</span></li>' for h, r, t, k in NAV)}
</ul>
</div>
<div>
<h2>ติดต่อ</h2>
<p>อีเมล <a href="mailto:{EMAIL}">{EMAIL}</a><br>LINE: <a href="/contact/#line">ดู QR และลิงก์</a><br>ตำบลจะแหน อำเภอสะบ้าย้อย<br>จังหวัดสงขลา 90210</p>
{social_footer()}
</div>
</div>
<p class="legal">ภาพบุคคลในเว็บนี้ใช้โดยได้รับความยินยอมจากเจ้าของภาพ ติดต่อทางอีเมลและ LINE · <a href="/write/">ส่งงานเขียน</a> · <a href="/privacy/">ความเป็นส่วนตัว</a></p>
</div></footer>
</body>
</html>
'''
    d = OUT + path
    os.makedirs(d, exist_ok=True)
    open(d + 'index.html', 'w').write(softwrap(html))

def sub_hero(room, eyebrow, h1, lead):
    return (f'<section class="hero-sub"><div class="wrap on-navy"><p class="eyebrow">{ARCH}<span>{room}</span> · {eyebrow}</p>'
            f'<h1>{h1}</h1><p>{lead}</p></div></section>')

CTA_BTN = f'<a class="btn btn--lg" href="/contact/#visit">{CTA}</a>'

def mb_label(path):
    return f'{os.path.getsize(path)/1_000_000:.1f} เมกะไบต์'

DL_FIVE = '/downloads/thod-rahat-rongrian-5-miti-a5.pdf'
DL_PROMPTS = '/downloads/30-prompts-notebooklm-pataraya-somboon.pdf'
FIVE_FILE = ROOT + '/assets/downloads/thod-rahat-rongrian-5-miti-a5.pdf'
PROMPTS_FILE = ROOT + '/assets/downloads/30-prompts-notebooklm-pataraya-somboon.pdf'
FIVE_SIZE = mb_label(FIVE_FILE)
PROMPTS_SIZE = mb_label(PROMPTS_FILE)

def pocket_card(href, cover, title, meta, lead):
    return (
        f'<article class="card book-card"><a href="{href}">'
        f'{cover}<span class="tag tag--blue">คู่มือฉบับพกพา</span>'
        f'<h3>{title}</h3><p class="small muted">{meta}</p><p>{lead}</p>'
        f'<span class="more">ดูรายละเอียดและดาวน์โหลด</span></a></article>'
    )

POCKET_FIVE_TITLE = 'ถอดรหัสโรงเรียน 5 มิติ สร้างสวนดอกไม้ ไม่ไล่ตามผึ้ง'
POCKET_PROMPTS_TITLE = '30 Prompts Gemini Notebook'
COVER_FIVE = pic('pb-five', 'ปกพ็อกเก็ตบุ๊ค ถอดรหัสโรงเรียน 5 มิติ สร้างสวนดอกไม้ ไม่ไล่ตามผึ้ง', '(min-width:700px) 28rem, 70vw')
COVER_PROMPTS = pic('pb-prompts', 'ปกคู่มือ 30 Prompts Gemini Notebook ของเครือข่ายการศึกษาปาตารายอ มีป้าย NotebookLM', '(min-width:700px) 28rem, 70vw')
POCKET_CARDS = (
    '<div class="grid2 book-grid">'
    + pocket_card('/library/five-dimensions/', COVER_FIVE, POCKET_FIVE_TITLE,
                  f'PDF ขนาด A5 · 128 หน้า · {FIVE_SIZE}',
                  'สังเคราะห์จากบทสนทนากับผู้บริหาร 5 วงการ ได้แก่ สร้างบ้าน ร้านอาหาร ฟุตบอล E-sport และ Smart Farmer')
    + pocket_card('/library/30-prompts-notebook/', COVER_PROMPTS, POCKET_PROMPTS_TITLE,
                  f'PDF สัดส่วน A5 · 72 หน้า · {PROMPTS_SIZE}',
                  'คู่มือสำหรับครู อาจารย์ นักเรียน นักศึกษา และนักวิจัย ในกลุ่มอาชีพการศึกษาและวิชาการ รวบรวม 30 พร้อมต์สำหรับใช้กับ Gemini Notebook (NotebookLM) รวมถึงพร้อมต์เสริมสำหรับผู้เริ่มเรียนรู้ การทำสไลด์ และอินโฟกราฟิก')
    + '</div>'
)


def qr(name, alt):
    return f'<img src="/assets/img/{name}.png" width="240" height="240" alt="{alt}" loading="lazy" decoding="async">'

# ---------------- HOME ----------------
hero = f'''<section class="hero"><div class="wrap on-navy"><div class="grid">
<div class="txt">
<p class="eyebrow">{ARCH}<span>ห้องโถง</span> · สะบ้าย้อย จังหวัดสงขลา</p>
<h1>เปิดบ้านปาตารายอ</h1>
<p class="tagline">ท่ามกลางความขาดแคลน เราเลือกลงมือทำ</p>
<p class="lede">เว็บไซต์นี้คือบ้านของเครือข่ายการศึกษาปาตารายอ (PEN) เครือข่ายของโรงเรียนอิสลามวิทยามูลนิธิ (IWFS) วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC) และมูลนิธิเพื่อการศึกษามูฮำมาดียะห์ (MUEF) ในอำเภอสะบ้าย้อย จังหวัดสงขลา เชิญเดินดูทีละห้อง</p>
<div class="ctas">{CTA_BTN}<a href="/contact/#line">หรือทัก LINE / ส่งอีเมล</a></div>
</div>
<div class="pic">{pic('b-hero','อาคารเรียนหลังคาแดงสามชั้น ซุ้มหน้าต่างโค้งลายฉลุ มีต้นปาล์มด้านหน้าและท้องฟ้าสีฟ้า','(min-width:900px) 55vw, 100vw',eager=True)}</div>
</div></div></section>'''

def room_card(href, room, label, text):
    return f'<a class="room-card" href="{href}">{ARCH}<span class="rn">{room}</span><span class="rl">{label}</span><span class="rt">{text}</span></a>'

home = f'''
<section class="section"><div class="wrap">
<div class="section-head"><p class="eyebrow">เดินดูบ้าน</p><h2>ในบ้านนี้มีอะไรบ้าง</h2>
<p class="lede">แต่ละห้องคือหนึ่งหน้าของเว็บไซต์ เริ่มจากห้องไหนก็ได้</p></div>
<div class="rooms">
{room_card('/about/','ห้องรับแขก','เราเชื่ออะไร และประวัติ','ที่มาของชื่อปาตารายอ และสิ่งที่เราให้ความสำคัญ')}
{room_card('/network/','ห้องประชุม','บุคลากรและเครือข่าย','ประธาน หน่วยงานสมาชิก และพันธมิตร')}
{room_card('/honors/','ห้องเกียรติยศ','ความภาคภูมิใจของบ้าน','งานและก้าวสำคัญของคน สถาบัน และเครือข่าย')}
{room_card('/programs/','ห้องเรียน','หลักสูตร/โรงเรียน','IWFS, MUTEC, MUEF พร้อมทุนและค่าใช้จ่าย')}
{room_card('/raya-hub/','ห้องแลป','นวัตกรรมและแพลตฟอร์ม','Raya Hub และระบบที่เครือข่ายกำลังทดลอง')}
{room_card('/library/','ห้องสมุด','งานเขียนและบทเรียน','งานเขียน ผลงานทางวิชาการ และคู่มือฉบับพกพาให้ดาวน์โหลด')}
{room_card('/news/','ห้องข่าว','ข่าวและกิจกรรม','งานเปิดบ้านและกิจกรรมของเครือข่าย')}
{room_card('/faq/','ห้องนั่งเล่น','FAQ ผู้ปกครอง','คำถามที่ผู้ปกครองถามบ่อย')}
{room_card('/contact/','หน้าประตู','ติดต่อ/สมัคร','อีเมล LINE และที่ตั้ง')}
</div></div></section>

<section class="section section--cream" id="pocket-books"><div class="wrap">
<div class="section-head"><p class="eyebrow">ห้องสมุด</p><h2>คู่มือฉบับพกพา</h2>
<p>ดาวน์โหลดเป็นไฟล์ PDF</p></div>
{POCKET_CARDS}
<p style="margin-top:1.4rem"><a class="more" href="/library/">ไปห้องสมุด</a></p>
</div></section>

<section class="section section--mist"><div class="wrap">
<div class="section-head"><p class="eyebrow">สามเสาหลัก</p><h2>สิ่งที่เราให้ความสำคัญ</h2>
<p class="lede">สามเรื่องที่บ้านนี้ยึดเป็นหลักในการทำงาน</p></div>
<div class="grid3">
<article class="card"><span class="num" aria-hidden="true">1</span><h3>ห้องเรียนที่มีหัวใจ</h3>
<p>ดูแลนักเรียนให้ถึงตัว MUTEC มีทุนการศึกษาตามเกรดเฉลี่ย และมีหอพักสำหรับนักศึกษาหญิงที่เดินทางไป-กลับไม่ได้</p>
<p><a class="more" href="/about/#heart">อ่านต่อ</a></p></article>
<article class="card"><span class="num" aria-hidden="true">2</span><h3>สถาปัตยกรรมข้ามศาสตร์</h3>
<p>โครงสร้างเดียวทั้งเครือข่าย ให้ทั้งสามหน่วยงานทำงานบนกรอบเดียวกัน ไม่ใช่ต่างคนต่างทำ</p>
<p><a class="more" href="/about/#cross">อ่านต่อ</a></p></article>
<article class="card"><span class="num" aria-hidden="true">3</span><h3>สร้างเกมที่แฟร์</h3>
<p>เกมที่แฟร์ในที่นี้คือสนามที่เท่าเทียม หนึ่งงานมีหนึ่งเจ้าของ ข้อมูลมีแหล่งความจริงเดียว และตรวจสอบได้</p>
<p><a class="more" href="/about/#fair">อ่านต่อ</a></p></article>
</div></div></section>

<section class="section" id="latest"><div class="wrap">
<div class="section-head"><p class="eyebrow">ห้องข่าว</p><h2>ข่าวล่าสุด</h2></div>
<div class="news-latest">
<a class="card lab-card news-card" href="/news/iwfs-cs-pattani-hearing/">{pic('news-cs-pattani-2','นางซีนาวาตีย์ เบ็ญบาเห็ม ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิ นั่งร่วมกับสูไฮลา มะเด็ง ผู้ติดตาม ที่โต๊ะประชุม','(min-width:900px) 40vw, 100vw')}<span class="tag tag--blue">ล่าสุด · 11 พ.ย. 2569 · IWFS</span><h3>ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิเข้าร่วมการประชุมรับฟังความคิดเห็นด้านการศึกษาจังหวัดชายแดนภาคใต้</h3><span class="more">อ่านต่อ</span></a>
<a class="card lab-card news-card" href="/news/wami-iwfs-musolla/">{pic('wami-group','ภาพหมู่ตัวแทนจาก WAMI Thailand และผู้ต้อนรับที่ IWFS','(min-width:900px) 40vw, 100vw')}<span class="tag tag--blue">5 พ.ย. 2569 · IWFS</span><h3>ตัวแทนจาก WAMI Thailand มาเยือน IWFS <span class="nb">เพื่อสนับสนุน</span><wbr><span class="nb">มูซอลลา</span></h3><span class="more">อ่านต่อ</span></a>
</div>
<p style="margin-top:1rem"><a class="more" href="/news/">ดูข่าวทั้งหมดในห้องข่าว</a></p>
</div></section>

<section class="section" id="event"><div class="wrap">
<div class="section-head"><p class="eyebrow">ห้องข่าว</p><h2>เปิดบ้านปาตารายอ 63 ปี</h2></div>
<figure class="band">{pic('banner','ป้ายงาน Pataraya Synergy 2026 เปิดบ้านปาตารายอ 63 ปี วาระครบรอบประวัติศาสตร์ 24-26 September 2026','(min-width:1200px) 1160px, 100vw')}<figcaption>ป้ายงาน Pataraya Synergy 2026</figcaption></figure>
<div class="grid2" style="margin-top:1.2rem;align-items:start">
<div><p>งาน <strong>Pataraya Synergy 2026 เปิดบ้านปาตารายอ</strong> จัดในวาระครบรอบ 63 ปี ระหว่างวันที่ 24 ถึง 26 กันยายน 2569 ตามที่ระบุบนป้ายงาน งานนี้ผ่านมาแล้ว</p></div>
<div><p>อ่านข่าวกิจกรรมล่าสุดได้ที่ <a href="/news/">ห้องข่าว</a></p></div>
</div></div></section>

<section class="section section--cream"><div class="wrap">
<div class="grid2" style="align-items:start">
<div>
<p class="eyebrow">ที่มา</p><h2>จาก Pondok Pantai Raya สู่เครือข่าย</h2>
<ol class="timeline">
<li><strong>พ.ศ. 2501 Pondok Pantai Raya</strong>ปอเนาะยุคบุกเบิกที่ตำบลจะแหน อำเภอสะบ้าย้อย คนเรียกสั้นๆ ว่าปาตารายอ</li>
<li><strong>เป็นโรงเรียนราษฎร์</strong>ชื่อโรงเรียนอิสลามวิทยา ต่อมาเป็นโรงเรียนอิสลามวิทยามูลนิธิ ภายใต้การอุปถัมภ์ของ MUEF</li>
<li><strong>พ.ศ. 2559 ก่อตั้ง MUTEC</strong>แยกจากแผนกอาชีวะของโรงเรียน เป็นวิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์</li>
<li class="now"><strong>24-26 กันยายน 2569</strong>งานเปิดบ้านปาตารายอ ครบรอบ 63 ปี</li>
</ol>
<p class="small muted">ปี 2501 เป็นปีที่เก่าที่สุดที่ปรากฏในบันทึกของเครือข่าย <a href="/about/#history">อ่านประวัติ</a></p>
</div>
<div>
<p class="eyebrow">เยี่ยมชมและสอบถาม</p><h2>พร้อมต้อนรับผู้ปกครอง</h2>
<p>นัดเยี่ยมชมหรือสอบถามการสมัครได้ทาง <a href="mailto:{EMAIL}">{EMAIL}</a> หรือทาง <a href="/contact/#line">LINE ของแต่ละสถาบัน</a></p>
<p><a class="more" href="/contact/">ไปหน้าติดต่อ</a></p>
</div></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><p class="eyebrow">ภาพจากเครือข่าย</p><h2>อาคารเรียนและนักเรียนของเรา</h2></div>
<div class="gallery">
<figure class="photo">{pic('assembly','นักเรียนเข้าแถวหน้าอาคารเรียนหลังคาเขียว','(min-width:700px) 50vw, 100vw')}<figcaption>นักเรียนเข้าแถวหน้าอาคารเรียน</figcaption></figure>
<figure class="photo">{pic('graduates','ภาพหมู่ผู้สำเร็จการศึกษาในชุดครุย ยืนหน้าอาคารเรียนซุ้มโค้ง','(min-width:700px) 50vw, 100vw')}<figcaption>ภาพหมู่ผู้สำเร็จการศึกษาหน้าอาคารเรียน</figcaption></figure>
</div></div></section>

<section class="section section--navy"><div class="wrap on-navy" style="text-align:center">
<h2>อยากรู้จักเรามากขึ้น</h2>
<p style="max-width:40rem;margin-inline:auto">สอบถามเรื่องการสมัคร หรือขอนัดเวลาเข้าเยี่ยมชมได้ที่ <a href="mailto:{EMAIL}">{EMAIL}</a> หรือทักทาง <a href="/contact/#line">LINE</a></p>
<p style="margin-top:1.4rem">{CTA_BTN}</p>
</div></section>
'''
page('/', 'home', 'เปิดบ้านปาตารายอ | เครือข่ายการศึกษาปาตารายอ (Pataraya Education Network)',
     'เว็บไซต์คือบ้านของเครือข่ายการศึกษาปาตารายอ โรงเรียนอิสลามวิทยามูลนิธิ (IWFS) วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC) และมูลนิธิเพื่อการศึกษามูฮำมาดียะห์ (MUEF) อำเภอสะบ้าย้อย จังหวัดสงขลา',
     home, hero)

# ---------------- ABOUT ----------------
about_hero = sub_hero('ห้องรับแขก', 'เราเชื่ออะไร และประวัติ', 'เราเชื่อในการดูแลคน ในโครงสร้างเดียว และในกติกาที่แฟร์',
                      'เชิญนั่งก่อน เครือข่ายเริ่มจากปอเนาะ ทำงานมาด้วยทุนน้อยและขาดแคลนหลายด้าน หน้านี้เล่าว่าเราให้ความสำคัญกับอะไร')
about = f'''
<section class="section" id="history"><div class="wrap">
<div class="grid2" style="align-items:start">
<div><p class="eyebrow">ประวัติ</p><h2>ชื่อปาตารายอมาจากไหน</h2>
<p>ก่อนจะเป็นเครือข่าย ที่นี่คือปอเนาะยุคบุกเบิก ก่อตั้งโดย <strong>ฮัจยีมูฮัมหมัดดาฆัง เบ็ญบาเห็ม</strong> บิดาของประธานมูลนิธิเพื่อการศึกษามูฮำมาดียะห์ ผู้คนรู้จักและเรียกกันมานานว่า <strong lang="ms">Pondok Pantai Raya</strong> เรียกสั้นๆ ต่อกันมาจนเป็น <strong>ปาตารายอ</strong></p>
<p>เพราะเป็นชื่อที่ผู้คนเรียกกันเอง วันเวลาที่แน่ชัดจึงไม่มีใครจดไว้ เราใช้ปีที่เก่าที่สุดที่ปรากฏในบันทึกของเครือข่าย คือ พ.ศ. 2501 เป็นจุดเริ่มต้น</p>
<p>จากปอเนาะที่เป็นทั้งสุเหร่าและที่สอนศาสนา ค่อยๆ เติบโตเป็นโรงเรียน มีมูลนิธิดูแล และมีวิทยาลัย ชื่อปาตารายอยังเป็นชื่อที่รวมทุกหน่วยงานไว้ในบ้านเดียวกัน</p></div>
<div><ol class="timeline">
<li><strong>พ.ศ. 2501</strong>Pondok Pantai Raya ปอเนาะยุคบุกเบิก ที่ตำบลจะแหน อำเภอสะบ้าย้อย ตามบันทึกที่เก่าที่สุด</li>
<li><strong>เป็นโรงเรียนราษฎร์</strong>ชื่อโรงเรียนอิสลามวิทยา ต่อมาเป็นโรงเรียนอิสลามวิทยามูลนิธิ ภายใต้การอุปถัมภ์ของ MUEF</li>
<li><strong>พ.ศ. 2559 ก่อตั้ง MUTEC</strong>แยกจากแผนกอาชีวะของโรงเรียน</li>
<li class="now"><strong>24-26 กันยายน 2569</strong>งานเปิดบ้านปาตารายอ ครบรอบ 63 ปี</li>
</ol>
</div>
</div></div></section>

<section class="section section--cream" id="words"><div class="wrap">
<div class="section-head"><p class="eyebrow">ถ้อยคำของบ้าน</p><h2>ปรัชญาของแต่ละสถาบัน</h2><p>สามสถาบันในบ้านเดียวกัน แต่ละแห่งมีปรัชญาของตัวเอง</p></div>
<div class="grid3">
<div class="card"><p class="eyebrow">ปรัชญา MUTEC</p><h3>สร้างนักคิด ผลิตนักปฏิบัติ</h3><p class="small muted">วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์</p></div>
<div class="card"><p class="eyebrow">ปรัชญา IWFS</p><h3>การศึกษาดี มีวินัย เน้นคุณธรรม</h3><p class="small muted">โรงเรียนอิสลามวิทยามูลนิธิ</p></div>
<div class="card"><p class="eyebrow">ปรัชญามูลนิธิ</p><h3>การศึกษาคือทางนำแห่งชีวิต</h3><p class="small muted">มูลนิธิเพื่อการศึกษามูฮำมาดียะห์</p></div>
</div>
</div></section>

<section class="section" id="heart"><div class="wrap">
<div class="grid2" style="align-items:center">
<div><p class="eyebrow">เสาที่ 1</p><h2>ห้องเรียนที่มีหัวใจ</h2>
<p>ในความหมายของเรา หัวใจคือการดูแล ดังนี้</p>
<ul>
<li>MUTEC มีทุนการศึกษาตามเกรดเฉลี่ย รายละเอียดอยู่ในหน้า <a href="/programs/#mutec">หลักสูตร/โรงเรียน</a></li>
<li>MUTEC มีหอพักสำหรับนักศึกษาหญิงที่เดินทางไป-กลับไม่ได้ สอบถามรายละเอียดได้ทางอีเมลหรือ LINE</li>
</ul>
</div>
<figure class="photo">{pic('b-front','อาคารเรียนหลังคาแดงด้านหน้า มีบันไดทางขึ้นตรงกลางและภูเขาเป็นฉากหลัง','(min-width:900px) 45vw, 100vw')}<figcaption>อาคารเรียนของเครือข่าย</figcaption></figure>
</div></div></section>

<section class="section section--cream" id="buildings"><div class="wrap">
<div class="section-head"><p class="eyebrow">รอบบ้าน</p><h2>อาคารในบ้านปาตารายอ</h2><p>ภาพอาคารจริงของเครือข่าย</p></div>
<div class="gallery">
<figure class="photo">{pic('b-aerial','ภาพมุมสูงของอาคารเรียนหลังคาแดงท่ามกลางชุมชนและสวนยาง มีภูเขาไกลๆ','(min-width:700px) 50vw, 100vw')}<figcaption>มุมสูงของอาคารเรียนและชุมชนรอบๆ</figcaption></figure>
<figure class="photo">{pic('b-wide','อาคารเรียนหลังคาแดงสามชั้น ซุ้มหน้าต่างโค้ง มองจากมุมเฉียง','(min-width:700px) 50vw, 100vw')}<figcaption>อาคารเรียนหลังคาแดง</figcaption></figure>
<figure class="photo">{pic('b-side','อาคารยาวสองชั้นทางเดินซุ้มโค้ง มองจากมุมสูง','(min-width:700px) 50vw, 100vw')}<figcaption>อาคารสองชั้นทางเดินซุ้มโค้ง</figcaption></figure>
<figure class="photo">{pic('b-gate','ประตูรั้วสีเขียวหน้าอาคาร มีธงชาติไทยและธงสีเหลือง','(min-width:700px) 50vw, 100vw')}<figcaption>ประตูรั้วหน้าอาคาร</figcaption></figure>
<figure class="photo">{pic('b-green','อาคารเรียนสามชั้นหลังคาสีเขียว ระเบียงยาว','(min-width:700px) 50vw, 100vw')}<figcaption>อาคารเรียนหลังคาสีเขียว</figcaption></figure>
<figure class="photo">{pic('b-tower','อาคารสองชั้นหลังคาสีม่วงเข้ม มีมุขทรงหอคอย','(min-width:700px) 50vw, 100vw')}<figcaption>อาคารมุขทรงหอคอย</figcaption></figure>
<figure class="photo">{pic('c-angles','อาคารเรียนหลังคาแดงสามชั้น ซุ้มหน้าต่างโค้งลายฉลุ มีบันไดทางขึ้นด้านหน้า','(min-width:700px) 50vw, 100vw')}<figcaption>อาคารเรียนหลังคาแดง มุมบันไดหน้าอาคาร</figcaption></figure>
<figure class="photo">{pic('b-long','อาคารยาวสองชั้นหลังคาสีเทา มีลานจอดรถด้านหน้าและป่าเขียวด้านหลัง','(min-width:700px) 50vw, 100vw')}<figcaption>อาคารยาวสองชั้น</figcaption></figure>
</div>
<h3 style="margin-top:2rem">แบบอาคารในอนาคต</h3>
<div class="gallery">
<figure class="photo">{pic('wami-plan','ภาพแบบมัสยิดทรงโดมสีทองมีหออะซานสองข้าง เป็นแบบอาคารที่วางแผนไว้ ยังไม่ได้สร้าง','(min-width:700px) 50vw, 100vw')}<figcaption>ภาพแบบอาคารที่วางแผนไว้ในอนาคต ยังไม่ใช่อาคารที่มีอยู่จริง</figcaption></figure>
</div></div></section>

<section class="section section--mist" id="cross"><div class="wrap">
<div class="section-head"><p class="eyebrow">เสาที่ 2</p><h2>สถาปัตยกรรมข้ามศาสตร์</h2>
<p>หมายถึงโครงสร้างเดียวทั้งเครือข่าย ไม่ใช่ต่างหน่วยงานต่างทำ ทั้งโรงเรียน วิทยาลัย และมูลนิธิควรเดินบนกรอบเดียวกัน แม้จะสอนคนละระดับและคนละวิชาชีพ</p>
</div>
</div></section>

<section class="section" id="fair"><div class="wrap">
<div class="section-head"><p class="eyebrow">เสาที่ 3</p><h2>สร้างเกมที่แฟร์</h2>
<p>เกมที่แฟร์ในที่นี้คือสนามที่เท่าเทียม เราแปลเป็นกติกาที่ตรวจสอบได้ ไม่ใช่คำขวัญ</p></div>
<div class="grid3">
<div class="card"><h3>หนึ่งงาน หนึ่งเจ้าของ</h3><p>ทุกงานมีคนรับผิดชอบคนเดียวที่ถามได้</p></div>
<div class="card"><h3>แหล่งความจริงเดียว</h3><p>ข้อมูลชุดเดียวกันไม่ควรมีหลายฉบับที่ไม่ตรงกัน</p></div>
<div class="card"><h3>ตรวจสอบได้</h3><p>ข้อมูลที่เราบอกต้องมีที่มา</p></div>
</div>
<p style="margin-top:1.2rem">ที่ผ่านมาข้อมูลกระจายอยู่คนละหน่วยงาน ทำให้ตรวจสอบยาก เราจึงอยากรวมไว้ที่เดียว เครื่องมือที่ใช้ทดลองเรื่องนี้คือ <a href="/raya-hub/">Raya Hub</a></p>
</div></section>

<section class="section section--cream"><div class="wrap">
<div class="quote">
<div class="ph">{pic('chair','ภาพถ่ายหน้าตรงของประธานเครือข่ายการศึกษาปาตารายอ','220px')}</div>
<blockquote>
<p>ข้อมูลที่ถูกต้อง โปร่งใส และตรวจสอบได้ คืออะมานะฮ์ของเรา Raya Hub จะช่วยให้คุณครูใช้เวลากับเอกสารน้อยลง และมีเวลาให้ลูกศิษย์มากขึ้น</p>
<footer><b>คูยา ดัยลามี</b><br>ประธานเครือข่ายการศึกษาปาตารายอ</footer>
</blockquote>
</div></div></section>

<section class="section"><div class="wrap">
<div class="grid2" style="align-items:center">
<div><p class="eyebrow">ความหมายของเรา</p><h2>เราทำงานท่ามกลางความขาดแคลน</h2>
<p>เรามีทุนน้อยและขาดแคลนหลายด้านมาโดยตลอด จึงเลือกบอกข้อจำกัดไว้ข้างหน้า แล้วลงมือทำทีละเรื่อง</p></div>
<div>
<div class="note"><p><strong>ความหมายของโลโก้</strong></p>
<p>หนังสือคือความรู้ ดาวคือมูลนิธิ (MUEF) เส้นปลายจุดสองเส้นคือสถาบันทั้งสอง (IWFS และ MUTEC) เส้นที่โค้งขึ้นคือการเติบโต</p></div>
<p style="max-width:220px"><img src="/assets/img/mark-light.svg" width="212" height="180" alt="เครื่องหมายของเครือข่าย เป็นหนังสือเปิดมีสามเส้นโค้งขึ้น เส้นบนสุดปลายเป็นดาว อีกสองเส้นปลายเป็นจุด" loading="lazy"></p>
</div></div></div></section>

'''
page('/about/', 'about', 'เราเชื่ออะไร และประวัติ (ห้องรับแขก) | เครือข่ายการศึกษาปาตารายอ',
     'ประวัติ Pondok Pantai Raya ปรัชญาของสามสถาบัน และเสาหลักของเครือข่ายการศึกษาปาตารายอ',
     about, about_hero)

# ---------------- PROGRAMS ----------------
prog_hero = sub_hero('ห้องเรียน', 'หลักสูตร/โรงเรียน', 'โรงเรียน วิทยาลัย และมูลนิธิในเครือข่าย',
                     'สามหน่วยงานตั้งอยู่ที่ตำบลจะแหน อำเภอสะบ้าย้อย จังหวัดสงขลา เนื้อหาด้านล่างมาจากหลักสูตรและแผนแนะแนวของแต่ละแห่ง หากต้องการรายละเอียดเพิ่มเติม สอบถามทางอีเมลหรือ LINE ได้')
programs = f'''
<section class="section"><div class="wrap">

<div class="inst" id="iwfs"><div class="logo">{logo_img('logo-iwfs','ตราโรงเรียนอิสลามวิทยามูลนิธิ')}</div>
<div><h2>IWFS โรงเรียนอิสลามวิทยามูลนิธิ</h2>
<dl class="facts">
<dt>ที่ตั้ง</dt><dd>หมู่ 3 ตำบลจะแหน อำเภอสะบ้าย้อย จังหวัดสงขลา</dd>
<dt>ระดับที่เปิดสอน</dt><dd>ปฐมวัย (อนุบาล 1 ถึง 3) ประถมศึกษา และมัธยมศึกษาปีที่ 1 ถึง 6 ตามแผนแนะแนวของโรงเรียน</dd>
<dt>รูปแบบการเรียน</dt><dd>ทวิศึกษา คือเรียนหลักสูตรแกนกลางของกระทรวงศึกษาธิการควบคู่กับหลักสูตรอิสลามศึกษา</dd>
<dt>แผนการเรียน ม.ปลาย</dt><dd>วิทยาศาสตร์-คณิตศาสตร์ และศิลป์ทั่วไป</dd>
<dt>ปฐมวัย</dt><dd>อิสลามศึกษาควบคู่กับการปลูกฝังจริยธรรม มีโครงการห้องเรียนจินตคณิต และกิจกรรม เล่น เรียน รู้</dd>
</dl>
<p>วิสัยทัศน์ในหลักสูตรอิสลามศึกษา: โรงเรียนอิสลามวิทยามูลนิธิ เป็นสถานศึกษาที่พัฒนาการบริหารจัดการ การศึกษาคู่คุณธรรม ก้าวทันเทคโนโลยี ภายใต้การมีส่วนร่วม</p>
<h3>อิสลามศึกษา 4 ระดับ</h3>
<div class="tablewrap"><table>
<thead><tr><th scope="col">ระดับ</th><th scope="col">ชั้นปี</th></tr></thead>
<tbody>
<tr><td>ตอนต้น (อิบตีดาอีย์)</td><td>ปีที่ 1 ถึง 3</td></tr>
<tr><td>ตอนกลาง (มุตาวัศซิต)</td><td>ปีที่ 4 ถึง 6</td></tr>
<tr><td>ตอนปลาย (ซานาวีย์)</td><td>ปีที่ 7 ถึง 9</td></tr>
<tr><td>เตรียมกุลยะห์ เตรียมสู่มหาวิทยาลัยศาสนา</td><td>ปีที่ 10</td></tr>
</tbody></table></div>
</div></div>

<div class="inst" id="mutec"><div class="logo">{logo_img('logo-mutec','ตราวิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์')}</div>
<div><h2>MUTEC วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์</h2>
<dl class="facts">
<dt>ที่ตั้ง</dt><dd>ตำบลจะแหน อำเภอสะบ้าย้อย จังหวัดสงขลา 90210</dd>
<dt>ก่อตั้ง</dt><dd>พ.ศ. 2559 โดยแยกจากแผนกอาชีวะของโรงเรียน อยู่ในการกำกับของสำนักงานคณะกรรมการการอาชีวศึกษา</dd>
<dt>ระดับที่เปิดรับ</dt><dd>ประกาศนียบัตรวิชาชีพ (ปวช.) หลักสูตร 3 ปี สองสาขา สำหรับผู้จบ ม.3 หรือเทียบเท่า</dd>
<dt>ปรัชญา</dt><dd>สร้างนักคิด ผลิตนักปฏิบัติ</dd>
</dl>
</div></div>
</div></section>

<section class="section section--mist"><div class="wrap">
<div class="section-head"><p class="eyebrow">สองสาขาของ MUTEC</p><h2>เลือกสาขาที่ตรงกับงานที่อยากทำ</h2></div>
<div class="two-prog">
<article class="prog"><h3>ภาษาต่างประเทศธุรกิจบริการ (FLS)</h3><p class="en">Foreign Language for Business Studies</p>
<ul>
<li>ฝึกใช้ภาษาต่างประเทศสื่อสารในงานธุรกิจและงานอาชีพ</li>
<li>เรียนรู้ความต่างทางวัฒนธรรม เพื่อทำงานกับคนหลายชาติ</li>
<li>เตรียมตัวสู่งานธุรกิจระหว่างประเทศ การท่องเที่ยว และบริการ</li>
</ul>
<p><strong>ภาษาที่เรียน</strong> มลายู อาหรับ อังกฤษเพื่อธุรกิจ และจีนกลางพื้นฐาน</p>
<p><strong>ฝึกปฏิบัติ</strong> ฝึกงานในสถานประกอบการ เช่น ธุรกิจท่องเที่ยว โรงแรม และการตลาด ทำโครงงาน และมีค่ายภาษา</p>
<p><strong>เหมาะกับ</strong> ผู้ที่สนใจต่อยอดทักษะภาษาต่างประเทศ และอยากทำงานด้านตลาดโลก การบริการลูกค้า หรือโครงการแลกเปลี่ยนวัฒนธรรม</p>
<p><strong>ค่านิยม F-L-S</strong> Flexibility ความยืดหยุ่น · Linguistic Excellence ความเป็นเลิศทางภาษา · Service Mindset จิตบริการ</p></article>
<article class="prog prog--b"><h3>เทคโนโลยีธุรกิจดิจิทัล (DBT)</h3><p class="en">Digital Business Technology</p>
<ul>
<li>เน้นทักษะดิจิทัลให้ตรงกับความต้องการของตลาดแรงงาน</li>
<li>ส่งเสริมความคิดสร้างสรรค์ ทั้งการทำเนื้อหาและการออกแบบสื่อดิจิทัล</li>
<li>เชื่อมการเรียนกับงานจริง นักศึกษาได้ฝึกในโครงการจริง</li>
</ul>
<p><strong>วิชาหลักตามแผนแนะแนว</strong> การพัฒนาเว็บไซต์และออกแบบกราฟิก การตลาดดิจิทัลและมัลติมีเดีย การเขียนโปรแกรมพื้นฐานและระบบเครือข่าย การบริหารจัดการข้อมูล และการฝึกใช้เครื่องมือดิจิทัลเพื่อประกอบอาชีพ</p>
<p><strong>ฝึกปฏิบัติ</strong> โครงงานเชิงปฏิบัติ แคมเปญการตลาดออนไลน์ และฝึกงานในบริษัทที่เกี่ยวข้องกับเทคโนโลยีดิจิทัล</p>
<p><strong>เหมาะกับ</strong> ผู้ที่สนใจงานธุรกิจดิจิทัล การตลาดออนไลน์ และการออกแบบสื่อ</p>
<p class="small muted">หลักสูตรปี 2567 ปรับและพัฒนาเพิ่มเติมจากสาขาคอมพิวเตอร์ธุรกิจ</p>
<p><strong>ค่านิยม D-B-T</strong> Digital Mindset ทัศนคติดิจิทัล · Business Readiness ความพร้อมด้านธุรกิจ · Technology Application การประยุกต์ใช้เทคโนโลยี</p></article>
</div></div></section>

<section class="section" id="classes"><div class="wrap">
<div class="section-head"><p class="eyebrow">ห้องเรียนโครงการของ IWFS</p><h2>ห้องเรียนพิเศษ ม.ต้น และ ม.ปลาย</h2>
<p>ข้อมูลในส่วนนี้มาจากแผนแนะแนวการรับสมัครของโรงเรียน เงื่อนไขและจำนวนที่รับของปีการศึกษาปัจจุบัน กรุณาสอบถามทางอีเมลหรือ LINE</p></div>
<div class="grid3">
<article class="card"><span class="tag tag--blue">ม.ต้น</span><h3>QCP</h3><p class="muted small">Quality Classroom Program ห้องเรียนความเป็นเลิศทางวิทยาศาสตร์และเทคโนโลยี</p>
<p>เรียนวิทยาศาสตร์เชิงลึก เคมี ฟิสิกส์ ชีววิทยา และเทคโนโลยี ใช้ห้องแล็บทดลอง มีโครงงานและค่ายวิทยาศาสตร์</p>
<p><strong>การสมัคร</strong> จบประถมศึกษา มีผลการเรียนดี สอบข้อเขียนวิทยาศาสตร์ คณิตศาสตร์ และการคิดวิเคราะห์ แล้วสัมภาษณ์ ต้องรักษาเกรดวิชากลุ่มวิทย์และคณิตไม่ต่ำกว่า 2.5</p></article>
<article class="card"><span class="tag tag--blue">ม.ปลาย</span><h3>UP</h3><p class="muted small">University Preparation Program ห้องเรียนเตรียมความพร้อมสู่มหาวิทยาลัย</p>
<p>เตรียมเรียนต่อสายวิทยาศาสตร์และเทคโนโลยี ติวเข้มก่อนสอบ มีฝึกทำข้อสอบจำลอง ฝึกปฏิบัติในห้องแล็บ และมีครูที่ปรึกษาแนะแนวการศึกษาต่อและทุน</p>
<p><strong>การสมัคร</strong> สำเร็จมัธยมศึกษาตอนต้น มีผลการเรียนดี สนใจคณิตศาสตร์ วิทยาศาสตร์ และภาษาอังกฤษ สมัครออนไลน์หรือที่โรงเรียน สอบข้อเขียน แล้วสัมภาษณ์ ต้องรักษาเกรดวิชาหลักไม่ต่ำกว่า 2.75</p></article>
<article class="card"><span class="tag tag--blue">ม.ต้น ชาย</span><h3>ห้องเรียนนักกีฬา</h3><p class="muted small">Pataraya Academy Football Club</p>
<p>สำหรับนักเรียนชาย ม.1 ถึง ม.3 ที่มีความสามารถด้านกีฬา ฝึกฟุตบอลกับโค้ช เรียนวิชาสามัญตามหลักสูตรในรูปแบบ Active Learning ที่ยืดหยุ่นสำหรับนักกีฬา และมีโปรแกรมดูแลสุขภาพ</p>
<p class="small muted">เกณฑ์การคัดเลือกและจำนวนที่รับ กรุณาสอบถามทางอีเมลหรือ LINE</p></article>
</div></div></section>

<section class="section section--mist"><div class="wrap">
<div class="section-head"><p class="eyebrow">ทุนและค่าใช้จ่าย</p><h2>เราไม่เขียนว่า เรียนฟรี เฉยๆ</h2>
<p>ทุกทุนมีเงื่อนไข และบางรายการอาจมีค่าใช้จ่ายแยกต่างหาก เช่น ชุดนักเรียน อาหาร และหอพัก เงื่อนไขของปีการศึกษาปัจจุบันสอบถามทางอีเมลหรือ LINE ได้ทุกครั้ง</p></div>
<div class="grid2">
<div><h3>MUTEC ทุนตามเกรดเฉลี่ย</h3>
<div class="tablewrap"><table>
<thead><tr><th scope="col">ทุน</th><th scope="col">เงื่อนไขเกรดเฉลี่ย</th></tr></thead>
<tbody>
<tr><td>ทุนเรียนฟรี 100%</td><td>2.50 ขึ้นไป</td></tr>
<tr><td>ทุนส่วนลด 50%</td><td>2.30 ขึ้นไป</td></tr>
<tr><td>ทุนมินิ</td><td>2.00 ขึ้นไป</td></tr>
</tbody></table></div></div>
<div><h3>IWFS</h3>
<p>โรงเรียนได้รับเงินอุดหนุนจากรัฐสำหรับระดับ ม.1 ถึง ม.6 จึงไม่เก็บค่าธรรมเนียมการเรียนตามข้อมูลที่เรามี ค่าใช้จ่ายอื่นและรายละเอียดของปีการศึกษาปัจจุบัน กรุณาสอบถามโรงเรียน</p></div>
</div>
<p><strong>การรับสมัคร</strong> ขั้นตอนและเอกสารกำลังเตรียมประกาศในเว็บนี้ ระหว่างนี้ส่งอีเมล <a href="mailto:{EMAIL}">{EMAIL}</a> ทัก <a href="/contact/#line">LINE</a> หรือ <a href="/contact/#visit">ดูวิธีนัดเยี่ยมชม / สอบถามการสมัคร</a></p>
</div></section>

<section class="section section--cream" id="muef"><div class="wrap">
<div class="inst" style="padding-top:0"><div class="logo">{logo_img('logo-muef','ตรามูลนิธิเพื่อการศึกษามูฮำมาดียะห์')}</div>
<div><h2>MUEF มูลนิธิเพื่อการศึกษามูฮำมาดียะห์</h2>
<p>มูลนิธิคือดาวในโลโก้ของเครือข่าย เป็นองค์กรที่อุปถัมภ์โรงเรียน ตามใบอนุญาตจัดตั้งที่ได้รับจากสำนักงานคณะกรรมการวัฒนธรรมแห่งชาติ มูลนิธิมีวัตถุประสงค์ดังนี้</p>
<ol>
<li>ส่งเสริมการศึกษาด้านศาสนาอิสลาม สามัญ และวิชาชีพแก่เยาวชนมุสลิม</li>
<li>สร้างสถาบันและศูนย์การศึกษา และอบรมจริยธรรมอิสลาม</li>
<li>พัฒนาคุณภาพชีวิตของเยาวชนและชุมชนไทยที่นับถืออิสลาม ให้เป็นพลเมืองดีของชาติ</li>
<li>ร่วมเผยแพร่และบำเพ็ญประโยชน์แก่สังคมตามแนวทางอิสลาม</li>
<li>ร่วมมือกับองค์กรรัฐบาลและเอกชนทำสาธารณประโยชน์ที่สอดคล้องกับหลักศาสนา</li>
<li>สงเคราะห์เด็กกำพร้าและยากจนให้ได้รับการศึกษา</li>
</ol>
</div></div>
<div class="gallery" style="margin-top:1rem">
<figure class="photo">{pic('muef-wide','อาคารมูฮำมาดีย์ มุมกว้าง มีป้ายมูลนิธิและลานหน้าอาคาร','(min-width:700px) 50vw, 100vw')}<figcaption>อาคารมูฮำมาดีย์ มุมกว้างจากลานหน้าอาคาร</figcaption></figure>
<figure class="photo">{pic('muef-stairs','ป้ายอาคารมูฮำมาดีย์และบันไดหน้าอาคาร','(min-width:700px) 50vw, 100vw')}<figcaption>ป้ายอาคารและบันไดหน้าอาคาร</figcaption></figure>
</div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><p class="eyebrow">ภาพอาคาร</p><h2>พื้นที่เรียนของเครือข่าย</h2></div>
<div class="gallery three">
<figure class="photo">{pic('c-arch','อาคารเรียนสองชั้นผนังลายฉลุสีส้มอิฐ ทางเดินซุ้มโค้ง มีลานกว้างด้านหน้า','(min-width:1000px) 33vw, (min-width:700px) 50vw, 100vw')}<figcaption>อาคารเรียน ซุ้มโค้งลายฉลุสีส้ม</figcaption></figure>
<figure class="photo">{pic('c-long','อาคารเรียนยาวสองชั้นสีครีม มีลานจอดรถด้านหน้าและท้องฟ้าสีฟ้า','(min-width:1000px) 33vw, (min-width:700px) 50vw, 100vw')}<figcaption>ลานหน้าอาคาร ซุ้มโค้ง</figcaption></figure>
<figure class="photo">{pic('upper-room','ห้องโล่งชั้นบนพื้นกระเบื้อง ถ่ายสองมุม','(min-width:1000px) 33vw, (min-width:700px) 50vw, 100vw')}<figcaption>ห้องโล่งชั้นบน พื้นกระเบื้อง</figcaption></figure>
</div></div></section>
'''
page('/programs/', 'programs', 'หลักสูตร/โรงเรียน (ห้องเรียน) | เครือข่ายการศึกษาปาตารายอ',
     'IWFS โรงเรียนอิสลามวิทยามูลนิธิ MUTEC วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ สองสาขา ปวช. และมูลนิธิ MUEF พร้อมทุนและวิธีสอบถามการสมัคร',
     programs, prog_hero)

# ---------------- RAYA HUB ----------------
hub_hero = sub_hero('ห้องแลป', 'นวัตกรรมและแพลตฟอร์ม', 'ห้องแลปของบ้าน',
                    'ที่รวมนวัตกรรมและแพลตฟอร์มของเครือข่ายและสถาบัน ทุกอย่างในห้องนี้ยังเป็นงานทดลอง เราบอกสถานะไว้ตามจริง')
hub = f'''
<section class="section section--mist"><div class="wrap">
<div class="section-head"><p class="eyebrow">บนโต๊ะทดลอง</p><h2>แพลตฟอร์มในห้องแลป</h2></div>
<div class="grid2">
<a class="card lab-card" href="#hub"><span class="tag">กำลังทดลองใช้</span><h3>Raya Hub</h3><p>ระบบกลางของเครือข่าย ให้งานมีเจ้าของคนเดียว ข้อมูลอยู่ที่เดียว และตรวจสอบได้</p><span class="more">ดูรายละเอียด</span></a>
<a class="card lab-card" href="#test"><span class="tag">เปิดลงทะเบียนทดสอบ</span><h3>SCHOOL MIS : RAYA HUB V2</h3><p>ลงทะเบียนเพื่อร่วมทดสอบระบบ SCHOOL MIS ของ Raya Hub V2 | Rayademy</p><span class="more">ดู QR และลิงก์</span></a>
</div>

</div></section>

<section class="section" id="hub"><div class="wrap">
<div class="status" role="note" aria-label="สถานะของ Raya Hub">
<span class="tag">กำลังทดลองใช้</span>
</div>
<div class="section-head" style="margin-top:1rem"><h2>Raya Hub คืออะไร</h2>
<p>เป็นระบบกลางที่เครือข่ายกำลังทดลองใช้ เพื่อให้งานมีเจ้าของคนเดียว ข้อมูลอยู่ที่เดียว และตรวจสอบได้</p></div>
<h3>สามส่วนของระบบ</h3>
<div class="nodes">
<div class="node"><h3>MIS</h3></div>
<div class="node"><h3>Care</h3></div>
<div class="node"><h3>Rayademy</h3><p class="small muted">ยังไม่เปิดตัว</p></div>
</div>
<p class="small muted" style="margin-top:.8rem">ชื่อส่วนงานข้างต้นเป็นชื่อเรียกชั่วคราว ยังไม่ใช่ชื่อทางการ</p>
</div></section>

<section class="section section--cream" id="test"><div class="wrap">
<div class="grid2" style="align-items:center">
<div><p class="eyebrow">ลงทะเบียนทดสอบ</p><h2>ลงทะเบียนทดสอบระบบ</h2>
<p>มีแบบฟอร์มลงทะเบียนทดสอบระบบ SCHOOL MIS : RAYA HUB V2 | RAYADEMY สำหรับผู้ที่จะร่วมทดสอบ สแกน QR หรือกดลิงก์ด้านล่าง</p>
<p><a href="https://www.canvaqr.com/RGVkpsud4R" rel="noopener">ลงทะเบียนทดสอบระบบ</a></p>
<p class="small muted">การลงทะเบียนทดสอบใช้แบบฟอร์มภายนอกเว็บไซต์นี้ ข้อมูลที่กรอกจะไปอยู่กับแบบฟอร์มนั้น</p></div>
<figure>{qr('qr-raya-test','QR code ลงทะเบียนทดสอบระบบ SCHOOL MIS Raya Hub V2 Rayademy ตรงกลางเป็นตัวอักษร R บนพื้นสีน้ำเงิน')}<figcaption>QR ลงทะเบียนทดสอบระบบ SCHOOL MIS : RAYA HUB V2 | RAYADEMY</figcaption></figure>
</div></div></section>

<section class="section section--mist"><div class="wrap">
<div class="section-head"><p class="eyebrow">สถานะฟีเจอร์</p><h2>ทำไปแล้วเท่าไร</h2>
<p>ฟีเจอร์ของต้นแบบทั้งหมด 36 รายการ แบ่งตามสถานะดังนี้ ตัวเลขนี้ยังต้องตรวจซ้ำก่อนเปิดตัวจริง</p></div>
<div class="bar" role="img" aria-label="ใช้แล้ว 12 รายการ ใช้บางส่วน 5 รายการ อยู่ในแผนเวอร์ชัน 2 จำนวน 14 รายการ เป็นข้อเสนอ 5 รายการ">
<span class="seg seg-12">12</span><span class="seg seg-5">5</span><span class="seg seg-14">14</span><span class="seg seg-5b">5</span></div>
<ul class="legend">
<li><i style="background:#0F2F4F"></i>ใช้แล้ว 12</li>
<li><i style="background:#184F86"></i>ใช้บางส่วน 5</li>
<li><i style="background:#6EACE2"></i>อยู่ในแผนเวอร์ชัน 2 จำนวน 14</li>
<li><i style="background:#EFE6D4"></i>เป็นข้อเสนอ 5</li>
</ul>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><p class="eyebrow">แนวคิดเบื้องหลัง</p><h2>แนวคิดที่เราใช้</h2>
<p>แนวคิดเบื้องหลัง Raya Hub อยู่ในห้องรับแขก</p></div>
<div class="grid3">
<div class="card"><h3>หนึ่งงาน หนึ่งเจ้าของ</h3><p><a class="more" href="/about/#fair">อ่านต่อ</a></p></div>
<div class="card"><h3>แหล่งความจริงเดียว</h3><p><a class="more" href="/about/#fair">อ่านต่อ</a></p></div>
<div class="card"><h3>โครงสร้างเดียวทั้งเครือข่าย</h3><p><a class="more" href="/about/#cross">อ่านต่อ</a></p></div>
</div></div></section>

<section class="section section--cream"><div class="wrap">
<div class="quote">
<div class="ph">{pic('chair','ภาพถ่ายหน้าตรงของประธานเครือข่ายการศึกษาปาตารายอ','220px')}</div>
<blockquote>
<p>ข้อมูลที่ถูกต้อง โปร่งใส และตรวจสอบได้ คืออะมานะฮ์ของเรา Raya Hub จะช่วยให้คุณครูใช้เวลากับเอกสารน้อยลง และมีเวลาให้ลูกศิษย์มากขึ้น</p>
<footer><b>คูยา ดัยลามี</b><br>ประธานเครือข่ายการศึกษาปาตารายอ</footer>
</blockquote></div>
<p style="margin-top:2rem">ต้นแบบนี้ยังไม่ใช่ผลงานของเครือข่าย อ่านต่อว่ามีอะไรที่เรายังทำไม่ได้ <a class="more" href="/about/#limits">สิ่งที่เรายังทำไม่ได้</a></p>
</div></section>
'''
page('/raya-hub/', 'hub', 'ห้องแลป: Raya Hub และแพลตฟอร์ม | เครือข่ายการศึกษาปาตารายอ',
     'Raya Hub ระบบกลางที่เครือข่ายการศึกษาปาตารายอกำลังทดลองใช้ มีลิงก์ลงทะเบียนทดสอบระบบ', hub, hub_hero)

# ---------------- NETWORK ----------------
net_hero = sub_hero('ห้องประชุม', 'บุคลากรและเครือข่าย', 'คนที่นั่งอยู่ในห้องประชุม',
                    'ผู้นำและหน่วยงานสมาชิกของเครือข่ายการศึกษาปาตารายอ')
network = f'''
<section class="section"><div class="wrap">
<div class="quote">
<div class="ph">{pic('chair2','ภาพถ่ายครึ่งตัวของประธานเครือข่ายการศึกษาปาตารายอ ในสูทสีกรมท่า','220px')}</div>
<div>
<p class="eyebrow">ประธานเครือข่าย</p>
<h2>คูยา ดัยลามี</h2>
<p>ประธานเครือข่ายการศึกษาปาตารายอ ชื่อที่แสดงและภาพนี้ใช้โดยได้รับความยินยอมจากเจ้าตัว ข้อความของประธานอยู่ที่ <a href="/about/">ห้องรับแขก</a></p>
</div></div></div></section>

<section class="section section--mist"><div class="wrap">
<div class="section-head"><p class="eyebrow">หน่วยงานสมาชิก</p><h2>สามหน่วยงานในบ้านเดียวกัน</h2></div>
<div class="grid3">
<article class="card"><div class="mlogo">{logo_img('logo-iwfs','ตราโรงเรียนอิสลามวิทยามูลนิธิ')}</div><h3>IWFS</h3><p>โรงเรียนอิสลามวิทยามูลนิธิ จัดการเรียนแบบทวิศึกษา เรียนหลักสูตรแกนกลางควบคู่กับอิสลามศึกษา</p><p><a class="more" href="/programs/#iwfs">ดูหลักสูตร</a></p></article>
<article class="card"><div class="mlogo">{logo_img('logo-mutec','ตราวิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์')}</div><h3>MUTEC</h3><p>วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ เปิดรับ ปวช. สองสาขา ก่อตั้ง พ.ศ. 2559</p><p><a class="more" href="/programs/#mutec">ดูหลักสูตร</a></p></article>
<article class="card"><div class="mlogo">{logo_img('logo-muef','ตรามูลนิธิเพื่อการศึกษามูฮำมาดียะห์')}</div><h3>MUEF</h3><p>มูลนิธิเพื่อการศึกษามูฮำมาดียะห์ ดาวในโลโก้ของเครือข่าย เป็นองค์กรที่อุปถัมภ์โรงเรียน</p><p><a class="more" href="/programs/#muef">ดูวัตถุประสงค์</a></p></article>
</div></div></section>


<section class="section section--cream"><div class="wrap">
<div class="grid2" style="align-items:center">
<figure class="photo">{pic('ribbon','พิธีตัดริบบิ้นที่มูลนิธิเพื่อการศึกษามูฮำมาดียะห์ มีธงอาเซียนและธงหลายประเทศประดับด้านบน นักเรียนหญิงนั่งด้านหน้า','(min-width:900px) 45vw, 100vw')}<figcaption>พิธีตัดริบบิ้นที่มูลนิธิเพื่อการศึกษามูฮำมาดียะห์ มีธงอาเซียนประดับ</figcaption></figure>
<div><p class="eyebrow">ร่วมประชุมกับเรา</p><h2>ถ้าอยากร่วมงาน</h2>
<p>เครือข่ายยินดีพูดคุยกับผู้ที่พร้อมสนับสนุนทุนการศึกษา ที่ฝึกงานสำหรับนักเรียนอาชีวะ และครูพี่เลี้ยง ส่งอีเมลหรือทัก LINE ได้ที่หน้าติดต่อ</p>
<p><a class="more" href="/contact/">ดูช่องทางติดต่อ</a></p></div>
</div></div></section>
'''
page('/network/', 'network', 'บุคลากรและเครือข่าย (ห้องประชุม) | เครือข่ายการศึกษาปาตารายอ',
     'ประธานเครือข่ายและหน่วยงานสมาชิก IWFS MUTEC และ MUEF ของเครือข่ายการศึกษาปาตารายอ', network, net_hero)

# ---------------- CONTACT ----------------
con_hero = sub_hero('หน้าประตู', 'ติดต่อ/สมัคร', 'ติดต่อเราทางอีเมลหรือ LINE',
                    'ส่งอีเมลหรือทัก LINE ของสถาบันที่สนใจ นัดเยี่ยมชมหรือสอบถามการสมัครได้ที่นี่')
contact = f'''
<section class="section" id="visit"><div class="wrap">
<div class="grid2" style="align-items:start">
<div>
<p class="eyebrow">{CTA}</p>
<h2>ส่งอีเมลหรือทัก LINE</h2>
<p><a class="contact-email" href="mailto:{EMAIL}">{EMAIL}</a></p>
<p class="small muted">อีเมลนี้เป็นช่องทางติดต่อของเครือข่าย และเป็นช่องทางขอข้อมูลส่วนบุคคลตามหน้าความเป็นส่วนตัว</p>
<ol class="steps">
<li><strong>ส่งอีเมลหรือทัก LINE</strong> บอกว่าสนใจ IWFS หรือ MUTEC และระดับชั้นหรือสาขาที่สนใจ</li>
<li><strong>ถามเรื่องที่อยากรู้</strong> เช่น ทุน ค่าใช้จ่าย หอพัก หรือขอนัดเวลาเข้าเยี่ยมชมสถานที่</li>
<li><strong>ขั้นตอนและเอกสารรับสมัคร</strong> สอบถามได้ทางอีเมลหรือ LINE</li>
</ol>
<p class="small muted">กรุณานัดหมายก่อนเดินทาง</p>
</div>
<div class="card">
<h3>ที่ตั้ง</h3>
<p>ตำบลจะแหน อำเภอสะบ้าย้อย จังหวัดสงขลา 90210</p>
<h3 style="margin-top:1.2rem">ช่องทางอื่น</h3>
<p>ติดต่อได้ทางอีเมลและ LINE บัญชีทางการ (OA) ของ IWFS และ MUTEC ด้านล่าง เว็บนี้ไม่มีแบบฟอร์มส่งข้อความในหน้าสาธารณะ</p>
<h3 style="margin-top:1.2rem">เรื่องที่รับ</h3>
<ul><li>รับสมัครและสอบถามข้อมูล</li><li>พันธมิตรและผู้สนับสนุน</li><li>สื่อมวลชน</li></ul>
<p class="small muted">ตอนนี้ทุกเรื่องใช้ช่องทางเดียวกัน</p>
</div></div></div></section>

{social_section()}
<section class="section section--mist" id="line"><div class="wrap">
<div class="section-head"><p class="eyebrow">LINE</p><h2>เพิ่มเพื่อนทาง LINE</h2>
<p>สแกน QR ด้วยแอป LINE หรือกดลิงก์ของสถาบันที่คุณสนใจ</p></div>
<div class="grid2">
<figure class="qrcard">{qr('qr-line-2','QR code เพิ่มเพื่อน LINE ของโรงเรียนอิสลามวิทยามูลนิธิ (IWFS)')}<figcaption><strong>LINE IWFS</strong><br>โรงเรียนอิสลามวิทยามูลนิธิ<br><a href="https://lin.ee/rOxmwQH" rel="noopener">lin.ee/rOxmwQH</a></figcaption></figure>
<figure class="qrcard">{qr('qr-line-1','QR code เพิ่มเพื่อน LINE ของวิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC)')}<figcaption><strong>LINE MUTEC</strong><br>วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์<br><a href="https://lin.ee/wnmWkIc" rel="noopener">lin.ee/wnmWkIc</a></figcaption></figure>
</div></div></section>

<section class="section"><div class="wrap">
<div class="section-head"><p class="eyebrow">ร่วมสร้างเกมที่แฟร์</p><h2>เราขาดอะไร</h2>
<p>เครือข่ายยินดีพูดคุยกับผู้ที่พร้อมสนับสนุนทุนการศึกษา ที่ฝึกงานสำหรับนักเรียนอาชีวะ และครูพี่เลี้ยง</p></div>
<p><a class="btn btn--line" href="/faq/">คำถามที่ผู้ปกครองถามบ่อย</a></p>
</div></section>
'''
page('/contact/', 'contact', 'ติดต่อ/สมัคร (หน้าประตู) | เครือข่ายการศึกษาปาตารายอ',
     f'ติดต่อเครือข่ายการศึกษาปาตารายอทางอีเมล {EMAIL} หรือ LINE นัดเยี่ยมชมหรือสอบถามการสมัคร', contact, con_hero)

# ---------------- FAQ ----------------
faq_hero = sub_hero('ห้องนั่งเล่น', 'FAQ ผู้ปกครอง', 'นั่งคุยกัน ตอบตรง ตอบครบในที่เดียว',
                    f'ถ้าคำถามของคุณยังไม่มีคำตอบ ส่งอีเมล {EMAIL} หรือทักทาง LINE ได้เลย')
faq = f'''
<section class="section"><div class="wrap" style="max-width:52rem">
<details open><summary>ค่าใช้จ่ายเท่าไร</summary><div class="ans">
<p><strong>IWFS</strong> โรงเรียนได้รับเงินอุดหนุนจากรัฐสำหรับระดับ ม.1 ถึง ม.6 จึงไม่เก็บค่าธรรมเนียมการเรียนตามข้อมูลที่เรามี</p>
<p><strong>MUTEC</strong> มีทุนตามเกรดเฉลี่ย ทุนเรียนฟรี 100% สำหรับเกรดเฉลี่ย 2.50 ขึ้นไป ทุนส่วนลด 50% สำหรับเกรดเฉลี่ย 2.30 ขึ้นไป และทุนมินิสำหรับเกรดเฉลี่ย 2.00 ขึ้นไป</p>
<p>เราไม่เขียนว่าเรียนฟรีเฉยๆ ค่าใช้จ่ายอื่น เช่น ชุดนักเรียน อาหาร และหอพัก สอบถามเงื่อนไขของปีการศึกษาปัจจุบันได้ที่ <a href="mailto:{EMAIL}">{EMAIL}</a> หรือทาง LINE</p></div></details>
<details><summary>มีชั้นอนุบาลและประถมไหม</summary><div class="ans">
<p>แผนแนะแนวของ IWFS มีหลักสูตรปฐมวัยสำหรับเด็กอนุบาล 1 ถึง 3 และระบุระดับประถมศึกษาไว้ด้วย รายละเอียดช่วงชั้นที่เปิดรับในปีการศึกษาปัจจุบัน กรุณาสอบถามทางอีเมลหรือ LINE</p></div></details>
<details><summary>จบ ม.3 แล้วสมัคร MUTEC ได้ไหม</summary><div class="ans">
<p>ได้ MUTEC เปิดรับผู้จบมัธยมศึกษาตอนต้น (ม.3) หรือเทียบเท่า เข้าเรียน ปวช. หลักสูตร 3 ปี สองสาขา คือ ภาษาต่างประเทศธุรกิจบริการ และเทคโนโลยีธุรกิจดิจิทัล ดูรายละเอียดที่ <a href="/programs/#mutec">ห้องเรียน</a></p></div></details>
<details><summary>ห้องเรียน QCP, UP และห้องเรียนนักกีฬา คืออะไร สมัครอย่างไร</summary><div class="ans">
<p>เป็นห้องเรียนโครงการของ IWFS ตามแผนแนะแนว QCP สำหรับ ม.ต้น เน้นวิทยาศาสตร์และเทคโนโลยี UP สำหรับ ม.ปลาย เตรียมสอบเข้ามหาวิทยาลัย และห้องเรียนนักกีฬาสำหรับนักเรียนชาย ม.ต้น ตามแผน QCP และ UP สมัครผ่านฝ่ายแนะแนวหรือออนไลน์ สอบข้อเขียน แล้วสัมภาษณ์ ดูรายละเอียดที่ <a href="/programs/#classes">ห้องเรียนโครงการ</a> และสอบถามเงื่อนไขของปีปัจจุบันทางอีเมลหรือ LINE</p></div></details>
<details><summary>มีหอพักไหม</summary><div class="ans">
<p>MUTEC มีหอพักสำหรับนักศึกษาหญิงที่เดินทางไป-กลับไม่ได้ เรื่องหอพักชาย เวลาดูแล กฎของหอพัก และหอพักของ IWFS กรุณาสอบถามทางอีเมลหรือ LINE</p></div></details>
<details><summary>เรียนวิชาศาสนาด้วยไหม</summary><div class="ans">
<p>IWFS เรียนวิชาสามัญตามหลักสูตรแกนกลางควบคู่กับอิสลามศึกษา 4 ระดับ คือ ตอนต้น ตอนกลาง ตอนปลาย และเตรียมกุลยะห์ MUTEC เน้นจริยธรรมควบคู่กับวิชาชีพ รายละเอียดวิชาศาสนาของ MUTEC กรุณาสอบถามวิทยาลัย</p></div></details>
<details><summary>เครือข่ายนี้ประกอบด้วยใครบ้าง</summary><div class="ans">
<p>โรงเรียนอิสลามวิทยามูลนิธิ (IWFS) วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC) และมูลนิธิเพื่อการศึกษามูฮำมาดียะห์ (MUEF) ดูรายละเอียดที่หน้า <a href="/network/">ห้องประชุม</a></p></div></details>
<details><summary>สมัครเรียนอย่างไร</summary><div class="ans">
<p>ขั้นตอนและเอกสารรับสมัครกำลังเตรียมประกาศในเว็บนี้ ตอนนี้ส่งอีเมล {EMAIL} หรือทัก LINE เพื่อสอบถามการสมัครหรือนัดเวลาเข้าเยี่ยมชม</p></div></details>
<details><summary>ติดต่อทาง LINE หรืออีเมลได้ไหม</summary><div class="ans">
<p>ได้ ดู QR และลิงก์ที่หน้า <a href="/contact/#line">ติดต่อ/สมัคร</a></p></div></details>
<details><summary>สอนด้วยภาษาอะไร</summary><div class="ans"><p>กรุณาสอบถามทางอีเมลหรือ LINE</p></div></details>
<details><summary>มีรถรับส่งไหม</summary><div class="ans"><p>กรุณาสอบถามทางอีเมลหรือ LINE</p></div></details>
<details><summary>จัดเปิดบ้านเมื่อไร</summary><div class="ans"><p>เครือข่ายจัดงาน Pataraya Synergy 2026 เปิดบ้านปาตารายอ ครบรอบ 63 ปี ไปแล้วเมื่อวันที่ 24 ถึง 26 กันยายน 2569 ครั้งต่อไปยังไม่ประกาศวัน เมื่อกำหนดแล้วจะแจ้งที่ <a href="/news/">ห้องข่าว</a></p></div></details>
<details><summary>Raya Hub คืออะไร ผู้ปกครองต้องใช้ไหม</summary><div class="ans">
<p>Raya Hub เป็นระบบกลางที่เครือข่ายกำลังทดลองใช้ ตอนนี้ผู้ปกครองยังไม่ต้องใช้ ดูรายละเอียดได้ที่ <a href="/raya-hub/">ห้องแลป</a></p></div></details>
<p style="margin-top:2rem">{CTA_BTN}</p>
</div></section>
'''
page('/faq/', 'faq', 'FAQ ผู้ปกครอง (ห้องนั่งเล่น) | เครือข่ายการศึกษาปาตารายอ',
     'คำตอบเรื่องค่าใช้จ่าย หอพัก วิชาศาสนา ห้องเรียนโครงการ และการสมัคร ของ IWFS และ MUTEC สำหรับผู้ปกครอง', faq, faq_hero)

# ---------------- NEWS ----------------
news_hero = sub_hero('ห้องข่าว', 'ข่าวและกิจกรรม', 'ห้องข่าว',
                     'ข่าว กิจกรรม และบทความของเครือข่ายจะลงที่นี่ เราลงเฉพาะรายการที่มีข้อมูลและภาพที่ได้รับอนุญาตครบ')
news = f'''
<section class="section"><div class="wrap" style="max-width:60rem">
<h2 style="font-size:1.35rem">ข่าวล่าสุด</h2>
<div id="sheet-news" class="sheet-news news-feed" data-csv="{NEWS_CSV.replace('&','&amp;')}" aria-live="polite" aria-busy="true"><div class="sn-status"><p>กำลังโหลดข่าวล่าสุด…</p></div></div>
<noscript><p>เปิด JavaScript เพื่อดูข่าวจากตาราง หากปิดสคริปต์ ข่าวที่อยู่ในหน้านี้ยังอ่านได้ด้านล่าง</p></noscript>
<div id="static-news" class="news-latest">
<a class="card lab-card news-card" href="/news/iwfs-cs-pattani-hearing/" data-sheet-id="2" data-date="2026-11-11" data-category="IWFS" data-title="ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิเข้าร่วมการประชุมรับฟังความคิดเห็นด้านการศึกษาจังหวัดชายแดนภาคใต้">{pic('news-cs-pattani-2','นางซีนาวาตีย์ เบ็ญบาเห็ม ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิ นั่งร่วมกับสูไฮลา มะเด็ง ผู้ติดตาม ที่โต๊ะประชุม','(min-width:900px) 40vw, 100vw')}<span class="tag tag--blue">11 พ.ย. 2569 · IWFS</span><h3>ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิเข้าร่วมการประชุมรับฟังความคิดเห็นด้านการศึกษาจังหวัดชายแดนภาคใต้</h3><span class="more">อ่านต่อ</span></a>
<a class="card lab-card news-card" href="/news/wami-iwfs-musolla/" data-sheet-id="1" data-date="2026-11-05" data-category="IWFS" data-title="ตัวแทนจาก WAMI Thailand มาเยือน IWFS เพื่อสนับสนุนมูซอลลา">{pic('wami-group','ภาพหมู่ตัวแทนจาก WAMI Thailand และผู้ต้อนรับที่ IWFS','(min-width:900px) 40vw, 100vw')}<span class="tag tag--blue">5 พ.ย. 2569 · IWFS</span><h3>ตัวแทนจาก WAMI Thailand มาเยือน IWFS <span class="nb">เพื่อสนับสนุน</span><wbr><span class="nb">มูซอลลา</span></h3><span class="more">อ่านต่อ</span></a>
</div>
<h2 class="news-archive-h">ข่าวและกิจกรรมที่ผ่านมา</h2>
<article style="margin-top:2.5rem">
<span class="tag tag--blue">กิจกรรมที่ผ่านมาแล้ว</span>
<h2>Pataraya Synergy 2026 เปิดบ้านปาตารายอ</h2>
<figure class="band">{pic('banner','ป้ายงาน Pataraya Synergy 2026 เปิดบ้านปาตารายอ 63 ปี วาระครบรอบประวัติศาสตร์ 24-26 September 2026','(min-width:1000px) 960px, 100vw')}<figcaption>ป้ายงาน Pataraya Synergy 2026</figcaption></figure>
<dl class="facts" style="margin-top:1.2rem">
<dt>ชื่องาน</dt><dd>Pataraya Synergy 2026 เปิดบ้านปาตารายอ</dd>
<dt>วาระ</dt><dd>ครบรอบ 63 ปี วาระครบรอบประวัติศาสตร์ ตามที่ระบุบนป้ายงาน</dd>
<dt>วันที่</dt><dd>24 ถึง 26 กันยายน 2569 (24-26 September 2026)</dd>
</dl>

</article>
<div class="news" style="margin-top:2rem">
<article><span class="tag tag--blue">บทความ</span><h2 style="font-size:1.35rem">งานเขียนและบทความวิชาการ</h2>
<p>อ่านงานเขียนและผลงานทางวิชาการได้ที่ <a href="/library/">ห้องสมุด</a></p></article>
<article><span class="tag tag--blue">กิจกรรม</span><h2 style="font-size:1.35rem">งานเปิดบ้านครั้งต่อไป</h2>
<p>ยังไม่ประกาศวันและสถานที่</p></article>
</div>
<p style="margin-top:2rem">ต้องการข่าวสารก่อนหน้านั้น ส่งอีเมล <a href="mailto:{EMAIL}">{EMAIL}</a> หรือทักทาง <a href="/contact/#line">LINE</a></p>
</div></section>
'''
page('/news/', 'news', 'ห้องข่าว: ข่าวและกิจกรรม | เครือข่ายการศึกษาปาตารายอ',
     'ติดตามข่าวสาร ความเคลื่อนไหว และกิจกรรมล่าสุดจากเครือข่ายการศึกษาปาตารายอ: โรงเรียนอิสลามวิทยามูลนิธิ (IWFS), วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC) และมูลนิธิเพื่อการศึกษามูฮำมาดียะห์', news, news_hero, scripts=NEWS_JS)


# ---------------- LIBRARY ----------------
def shelf(sid, title, text, kinds, items):
    head = (
        f'<section class="shelf" id="{sid}" aria-labelledby="{sid}-h"><div class="shelf-head"><h3 id="{sid}-h">{title}</h3><span class="count">{len(items)} รายการ</span></div>'
        f'<p>{text}</p>'
    )
    if not items:
        return head + (
            f'<div class="empty" role="note">{ARCH}<p><strong>ชั้นนี้ยังว่าง</strong><br>รายการแรกจะขึ้นที่นี่เมื่อเจ้าของผลงานยินยอมให้เผยแพร่</p>'
            f'<ul class="kinds">{"".join(f"<li>{k}</li>" for k in kinds)}</ul></div></section>'
        )
    cards = "".join(
        f'<a class="card lab-card article-card" href="/library/{a["slug"]}/"><span class="tag tag--blue">บทความ</span><h3>{a["title"]}</h3><p>{a["lead"]}</p><p class="small muted">เขียนโดย คูยา ดัยลามี</p><span class="more">อ่านต่อ</span></a>'
        for a in items
    )
    return head + f'<div class="article-list">{cards}</div></section>'

lib_hero = sub_hero('ห้องสมุด', 'งานเขียนและบทเรียน', 'ห้องสมุดของบ้าน',
                    'งานเขียน ผลงานทางวิชาการ และคู่มือฉบับพกพาของเครือข่าย ให้ดาวน์โหลดได้')
_w = [a for a in LIB_ARTICLES if a['shelf'] == 'writing']
_ac = [a for a in LIB_ARTICLES if a['shelf'] == 'academic']
library = (
    '<section class="section section--mist"><div class="wrap">'
    '<div class="section-head"><p class="eyebrow">คู่มือฉบับพกพา</p><h2>ดาวน์โหลดได้ที่นี่</h2>'
    '<p>สองเล่มที่เปิดให้ดาวน์โหลดเป็นไฟล์ PDF</p></div>'
    + POCKET_CARDS +
    '</div></section>'
    '<section class="section"><div class="wrap">'
    '<div class="section-head"><p class="eyebrow">ชั้นหนังสือ</p><h2>งานเขียนและผลงานทางวิชาการ</h2>'
    '<p>บทความของคูยา ดัยลามี ประธานเครือข่ายการศึกษาปาตารายอ</p></div>'
    '<div class="shelves shelves--fill">'
    + shelf('writing','งานเขียนและบทความ','บทความ ข้อเขียน และบันทึกของครูและบุคลากร',['บทความ','บันทึกการสอน','ข้อเขียน'],_w)
    + shelf('academic','ผลงานทางวิชาการ','งานวิจัย รายงาน และผลงานทางวิชาการของบุคลากร',['งานวิจัย','รายงาน','เอกสารประกอบการสอน'],_ac)
   
    + '</div></div></section>'
    '<section class="section section--cream"><div class="wrap">'
    '<div class="grid2" style="align-items:center">'
    '<div id="community-list" hidden></div>'
    + '<div class="grid2" style="align-items:center;margin-top:2.5rem">'
    + '<div><p class="eyebrow">ส่งผลงานเข้าห้องสมุด</p><h2>ครูและบุคลากรที่อยากเผยแพร่ผลงาน</h2>'
    + '<p>บุคลากรในเครือข่ายเข้าสู่ระบบด้วยอีเมล แล้วส่งต้นฉบับให้ผู้พิจารณาตรวจก่อนเผยแพร่บนหน้านี้</p>'
    + '<p><a class="btn" href="/write/">เข้าสู่ระบบเพื่อส่งงานเขียน</a></p></div>'
    + '<div class="note"><p>แนวคิดเบื้องหลังระบบของเครือข่ายอยู่ที่ <a href="/about/#fair">ห้องรับแขก</a> ส่วนนวัตกรรมและแพลตฟอร์มอยู่ที่ <a href="/raya-hub/">ห้องแลป</a></p></div>'
    + '</div></div></section>'
)
page('/library/', 'library', 'ห้องสมุด: งานเขียนและบทเรียน | เครือข่ายการศึกษาปาตารายอ',
     'ห้องสมุดของเครือข่ายการศึกษาปาตารายอ งานเขียน ผลงานทางวิชาการ และคู่มือฉบับพกพาให้ดาวน์โหลด', library, lib_hero, scripts=WRITE_JS)


# ---------------- POCKET BOOKS ----------------
five_hero = sub_hero('ห้องสมุด', 'คู่มือฉบับพกพา', POCKET_FIVE_TITLE,
                     'พ็อกเก็ตบุ๊คฉบับสมบูรณ์ ดาวน์โหลดเป็นไฟล์ PDF ขนาด A5')
five_page = (
    '<section class="section"><div class="wrap book-page">'
    '<div class="grid2 book-detail">'
    f'<figure class="book-cover">{COVER_FIVE}<figcaption>ปกเล่ม ถอดรหัสโรงเรียน 5 มิติ</figcaption></figure>'
    '<div>'
    '<p class="tag tag--blue">คู่มือฉบับพกพา · ฉบับสมบูรณ์</p>'
    f'<h2>{POCKET_FIVE_TITLE}</h2>'
    '<dl class="facts">'
    '<dt>ผู้เขียน</dt><dd>ดัยลามี (คูยา) เบ็ญบาเห็ม</dd>'
    '<dt>จัดทำโดย</dt><dd>เครือข่ายการศึกษาปาตารายอ (Pataraya)</dd>'
    '<dt>รูปแบบ</dt><dd>ไฟล์ PDF ขนาด A5</dd>'
    '<dt>จำนวนหน้า</dt><dd>128 หน้า</dd>'
    f'<dt>ขนาดไฟล์</dt><dd>{FIVE_SIZE}</dd>'
    '</dl>'
    '<p>เล่มนี้ออกแบบเป็นพ็อกเก็ตบุ๊คฉบับสมบูรณ์ สังเคราะห์จากบทสนทนากับผู้บริหาร 5 วงการ ได้แก่ สร้างบ้าน ร้านอาหาร ฟุตบอล E-sport และ Smart Farmer เนื้อหาจัดเป็นห้าแฉก คือ รากฐานและโครงสร้างที่มั่นคง กลยุทธ์และปรัชญาที่ชัดเจน การวัดผล พัฒนา และสร้างชื่อเสียง การบริหารความเสี่ยงและความเข้มแข็ง และการมีส่วนร่วมและระบบนิเวศที่เกื้อกูล</p>'
    f'<p class="form-actions"><a class="btn" href="{DL_FIVE}" download="thod-rahat-rongrian-5-miti-a5.pdf">ดาวน์โหลด PDF</a>'
    f'<a class="btn btn--line" href="{DL_FIVE}" target="_blank" rel="noopener">เปิดอ่านในเบราว์เซอร์</a></p>'
    '<p><a class="more" href="/library/">กลับไปห้องสมุด</a></p>'
    '</div></div></div></section>'
)
page('/library/five-dimensions/', 'library',
     POCKET_FIVE_TITLE + ' | ห้องสมุด เครือข่ายการศึกษาปาตารายอ',
     'พ็อกเก็ตบุ๊คฉบับสมบูรณ์ ถอดรหัสโรงเรียน 5 มิติ สร้างสวนดอกไม้ ไม่ไล่ตามผึ้ง โดย ดัยลามี (คูยา) เบ็ญบาเห็ม ดาวน์โหลดไฟล์ PDF ขนาด A5 จำนวน 128 หน้า',
     five_page, five_hero)

prompts_hero = sub_hero('ห้องสมุด', 'คู่มือฉบับพกพา', POCKET_PROMPTS_TITLE,
                        'คู่มือฉบับพกพา ให้ดาวน์โหลดเป็นไฟล์ PDF สัดส่วน A5')
prompts_page = (
    '<section class="section"><div class="wrap book-page">'
    '<div class="grid2 book-detail">'
    f'<figure class="book-cover">{COVER_PROMPTS}<figcaption>ปกคู่มือ 30 Prompts Gemini Notebook</figcaption></figure>'
    '<div>'
    '<p class="tag tag--blue">คู่มือฉบับพกพา</p>'
    f'<h2>{POCKET_PROMPTS_TITLE}</h2>'
    '<p class="muted">NotebookLM · สำหรับครู อาจารย์ นักเรียน นักศึกษา และนักวิจัย</p>'
    '<dl class="facts">'
    '<dt>จัดทำโดย</dt><dd>เครือข่ายการศึกษาปาตารายอ (Pataraya)</dd>'
    '<dt>รูปแบบ</dt><dd>ไฟล์ PDF สัดส่วน A5</dd>'
    '<dt>จำนวนหน้า</dt><dd>72 หน้า</dd>'
    f'<dt>ขนาดไฟล์</dt><dd>{PROMPTS_SIZE}</dd>'
    '</dl>'
    '<p>คู่มือฉบับพกพานี้จัดทำโดยเครือข่ายการศึกษาปาตารายอ สำหรับครู อาจารย์ นักเรียน นักศึกษา และนักวิจัย ในกลุ่มอาชีพการศึกษาและวิชาการ (Education &amp; Academia) รวบรวม 30 พร้อมต์สำหรับใช้กับ Gemini Notebook (NotebookLM) รวมถึงพร้อมต์เสริมสำหรับผู้เริ่มเรียนรู้ การทำสไลด์ และอินโฟกราฟิก เนื้อหาเรียบเรียงจากเอกสาร 30 Prompts NotebookLM กลุ่มอาชีพการศึกษาและวิชาการ มีสารจากประธานเครือข่าย เมนู 6 หมวด กรณีศึกษา Pitch Deck และ Prompt สไลด์ การสร้าง Infographic ในแท็บ Studio และภาคผนวก 5 สไตล์สไลด์</p>'
    f'<p class="form-actions"><a class="btn" href="{DL_PROMPTS}" download="30-prompts-notebooklm-pataraya-somboon.pdf">ดาวน์โหลด PDF</a>'
    f'<a class="btn btn--line" href="{DL_PROMPTS}" target="_blank" rel="noopener">เปิดอ่านในเบราว์เซอร์</a></p>'
    '<p><a class="more" href="/library/">กลับไปห้องสมุด</a></p>'
    '</div></div></div></section>'
)
page('/library/30-prompts-notebook/', 'library',
     POCKET_PROMPTS_TITLE + ' | ห้องสมุด เครือข่ายการศึกษาปาตารายอ',
     'คู่มือฉบับพกพา 30 Prompts Gemini Notebook (NotebookLM) สำหรับครู อาจารย์ นักเรียน นักศึกษา และนักวิจัย ดาวน์โหลดไฟล์ PDF สัดส่วน A5 จำนวน 72 หน้า',
     prompts_page, prompts_hero)

# ---------------- LIBRARY ARTICLES ----------------
_DEFEAT_PIC = pic(
    'infographic-defeat',
    'ภาพสรุปบทความ พ่ายแพ้อย่างเป็นระบบ สามบทเรียนจากเวียดนาม อัฟกานิสถาน และแอลจีเรีย และคำถามว่าระบบให้รางวัลกับอะไร',
    '(min-width:900px) 720px, 100vw',
    eager=True,
)
for _art in LIB_ARTICLES:
    _body = _art['body'].replace('PIC_DEFEAT', _DEFEAT_PIC)
    _hero = sub_hero('ห้องสมุด', 'บทความ', _art['title'], _art['lead'])
    page(
        '/library/' + _art['slug'] + '/',
        'library',
        _art['title'] + ' | ห้องสมุด เครือข่ายการศึกษาปาตารายอ',
        _art['desc'],
        '<section class="section"><div class="wrap article">' + _body + '<p style="margin-top:2rem"><a class="more" href="/library/">กลับไปห้องสมุด</a></p></div></section>',
        _hero,
    )

# ---------------- HONORS ----------------
hon_hero = sub_hero('ห้องเกียรติยศ', 'ความภาคภูมิใจของบ้าน', 'ห้องเกียรติยศ',
                    'งานที่คน สถาบัน และเครือข่ายทำแล้วภูมิใจ ก้าวสำคัญ และกิจกรรมที่ส่งผลกว้าง')
def honor(img, tag, title, text, link=''):
    return f'<article class="honor">{img}<div class="hb"><span class="tag tag--blue">{tag}</span><h3>{title}</h3><p>{text}</p>{link}</div></article>'
def honor_wait(title, text):
    return f'<article class="honor honor--wait" aria-label="รอเนื้อหา: {title}"><div class="hb"><span class="tag tag--wait">รอเนื้อหา</span><h3>{title}</h3><p>{text}</p></div></article>'
honors = f'''
<section class="section"><div class="wrap">
<div class="section-head"><p class="eyebrow">บนผนังห้อง</p><h2>เรื่องจากบ้านของเรา</h2></div>
<div class="honors">
{honor(pic('banner','ป้ายงาน Pataraya Synergy 2026 เปิดบ้านปาตารายอ 63 ปี','(min-width:900px) 50vw, 100vw'),'เครือข่าย · 2569','Pataraya Synergy 2026 เปิดบ้านปาตารายอ','งานเปิดบ้านในวาระครบรอบ 63 ปี วันที่ 24 ถึง 26 กันยายน 2569','<a class="more" href="/news/">อ่านในห้องข่าว</a>')}
{honor(pic('ribbon','พิธีตัดริบบิ้นที่มูลนิธิเพื่อการศึกษามูฮำมาดียะห์ มีธงอาเซียนประดับ','(min-width:900px) 50vw, 100vw'),'มูลนิธิ','พิธีตัดริบบิ้นที่มูลนิธิเพื่อการศึกษามูฮำมาดียะห์','พิธีตัดริบบิ้นที่มีธงอาเซียนประดับ')}
{honor('','สถาบัน · 2559','ก่อตั้งวิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC)','วิทยาลัยแยกจากแผนกอาชีวะของโรงเรียน เปิดสอน ปวช. สองสาขา','<a class="more" href="/programs/#mutec">ดูหลักสูตร</a>')}
</div></div></section>
'''
page('/honors/', 'honors', 'ห้องเกียรติยศ | เครือข่ายการศึกษาปาตารายอ',
     'ความภาคภูมิใจ ก้าวสำคัญ และกิจกรรมของคน สถาบัน และเครือข่ายการศึกษาปาตารายอ', honors, hon_hero)


# ---------------- NEWS POST: IWFS CS PATTANI ----------------
iwfs_hear_hero = sub_hero('ห้องข่าว', 'กิจกรรม', 'ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิเข้าร่วมการประชุมรับฟังความคิดเห็นด้านการศึกษาจังหวัดชายแดนภาคใต้', 'วันที่ 11 พฤศจิกายน 2569 ณ โรงแรม ซี.เอส. ปัตตานี จังหวัดปัตตานี')
iwfs_hear = f'''
<article class="article">
<p><a href="/news/">กลับไปห้องข่าว</a></p>
<span class="tag tag--blue">11 พ.ย. 2569 · IWFS</span>
<h2>ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิเข้าร่วมการประชุมรับฟังความคิดเห็นด้านการศึกษาจังหวัดชายแดนภาคใต้</h2>
<figure class="photo">{pic('news-cs-pattani-2','นางซีนาวาตีย์ เบ็ญบาเห็ม ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิ นั่งร่วมกับสูไฮลา มะเด็ง ผู้ติดตาม ที่โต๊ะประชุม','(min-width:700px) 50vw, 100vw')}<figcaption>ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิและผู้ติดตาม ที่โต๊ะประชุม โรงแรม ซี.เอส. ปัตตานี</figcaption></figure>
<figure class="photo">{pic('news-cs-pattani-1','โต๊ะประธานและผู้เข้าร่วมการประชุมรับฟังความคิดเห็นด้านการศึกษา ในห้องประชุมโรงแรม ซี.เอส. ปัตตานี','(min-width:700px) 50vw, 100vw')}<figcaption>โต๊ะประธานการประชุมรับฟังความคิดเห็นด้านการศึกษา</figcaption></figure>
<figure class="photo">{pic('news-cs-pattani-3','ภาพรวมห้องประชุม ผู้เข้าร่วมนั่งเป็นแถวหันไปทางโต๊ะประธานและจอภาพ','(min-width:700px) 50vw, 100vw')}<figcaption>ภาพรวมห้องประชุม โรงแรม ซี.เอส. ปัตตานี</figcaption></figure>
<dl class="facts">
<dt>วันที่</dt><dd>11 พฤศจิกายน 2569</dd>
<dt>ผู้เข้าร่วม</dt><dd>นางซีนาวาตีย์ เบ็ญบาเห็ม ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิ พร้อมด้วยสูไฮลา มะเด็ง ผู้ติดตาม</dd>
<dt>สถานที่</dt><dd>โรงแรม ซี.เอส. ปัตตานี จังหวัดปัตตานี</dd>
<dt>ผู้จัด</dt><dd>ศูนย์ขับเคลื่อนการศึกษาในจังหวัดชายแดนภาคใต้ (ศค.จชต.) ร่วมกับสำนักงานสภาความมั่นคงแห่งชาติ (สมช.)</dd>
<dt>ฐานะ</dt><dd>ตัวแทนผู้บริหารโรงเรียนเอกชนในระบบจากพื้นที่นำร่อง 14 อำเภอ</dd>
</dl>
<p>วันที่ 11 พฤศจิกายน 2569 นางซีนาวาตีย์ เบ็ญบาเห็ม ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิ พร้อมด้วยสูไฮลา มะเด็ง ผู้ติดตาม เข้าร่วมการประชุมรับฟังความคิดเห็นต่อแนวทางการขับเคลื่อนงานการศึกษาในระดับพื้นที่จังหวัดชายแดนภาคใต้ ณ โรงแรม ซี.เอส. ปัตตานี จังหวัดปัตตานี ในฐานะตัวแทนผู้บริหารโรงเรียนเอกชนในระบบจากพื้นที่นำร่อง 14 อำเภอ</p>
<p>การประชุมจัดโดยศูนย์ขับเคลื่อนการศึกษาในจังหวัดชายแดนภาคใต้ (ศค.จชต.) ร่วมกับสำนักงานสภาความมั่นคงแห่งชาติ (สมช.) เพื่อเปิดเวทีแลกเปลี่ยนความคิดเห็น สะท้อนปัญหาและอุปสรรค ตลอดจนเสนอแนะแนวทางพัฒนาการศึกษาให้สอดคล้องกับบริบทของพื้นที่</p>
<p>การเข้าร่วมครั้งนี้เป็นการสะท้อนมุมมองของสถานศึกษาเอกชนในระบบ และมีส่วนร่วมในการกำหนดทิศทางการพัฒนาการศึกษาในจังหวัดชายแดนภาคใต้</p>
</article>
'''
page('/news/iwfs-cs-pattani-hearing/', 'news',
     'ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิเข้าร่วมการประชุมรับฟังความคิดเห็นด้านการศึกษาจังหวัดชายแดนภาคใต้ | ห้องข่าว เครือข่ายการศึกษาปาตารายอ',
     'วันที่ 11 พฤศจิกายน 2569 นางซีนาวาตีย์ เบ็ญบาเห็ม ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิ พร้อมด้วยสูไฮลา มะเด็ง ผู้ติดตาม เข้าร่วมการประชุมรับฟังความคิดเห็นด้านการศึกษา ณ โรงแรม ซี.เอส. ปัตตานี',
     iwfs_hear, iwfs_hear_hero)

# ---------------- NEWS POST: WAMI ----------------
POSTS = [('/news/iwfs-cs-pattani-hearing/', 'ผู้อำนวยการโรงเรียนอิสลามวิทยามูลนิธิเข้าร่วมการประชุมรับฟังความคิดเห็นด้านการศึกษาจังหวัดชายแดนภาคใต้', 'news-cs-pattani-2'),
         ('/news/wami-iwfs-musolla/', 'ตัวแทนจาก WAMI Thailand มาเยือน IWFS เพื่อสนับสนุนมูซอลลา', 'b-hero')]
wami_hero = sub_hero('ห้องข่าว', 'กิจกรรม', 'ตัวแทนจาก WAMI Thailand มาเยือน IWFS <span class="nb">เพื่อสนับสนุน</span><wbr><span class="nb">มูซอลลา</span>', 'วันที่ 5 พฤศจิกายน 2569 ที่โรงเรียนอิสลามวิทยามูลนิธิ (IWFS)')
wami = f'''
<section class="section"><div class="wrap" style="max-width:60rem">
<p><a href="/news/">กลับไปห้องข่าว</a></p>
<span class="tag tag--blue">กิจกรรม · IWFS · 5 พ.ย. 2569</span>
<h2>ตัวแทนจาก WAMI Thailand มาเยือน IWFS <span class="nb">เพื่อสนับสนุน</span><wbr><span class="nb">มูซอลลา</span></h2>
<p>เมื่อวันที่ 5 พฤศจิกายน 2569 ตัวแทนจาก WAMI Thailand มาเยือนโรงเรียนอิสลามวิทยามูลนิธิ (IWFS) <span class="nb">เพื่อสนับสนุน</span><wbr><span class="nb">มูซอลลา</span>ของโรงเรียน นายอับดุลกอเดร์ เบ็ญบาเห็ม ประธานมูลนิธิเพื่อการศึกษามูฮำมาดียะห์ ให้การต้อนรับ ร่วมกับผู้บริหารสถาบันในเครือข่ายการศึกษาปาตารายอ</p>
<dl class="facts" style="margin-top:1rem">
<dt>วันที่</dt><dd>5 พฤศจิกายน 2569</dd>
<dt>สถานที่</dt><dd>โรงเรียนอิสลามวิทยามูลนิธิ (IWFS)</dd>
<dt>ผู้มาเยือน</dt><dd>ตัวแทนจาก WAMI Thailand</dd>
<dt>ผู้ต้อนรับ</dt><dd>นายอับดุลกอเดร์ เบ็ญบาเห็ม ประธานมูลนิธิเพื่อการศึกษามูฮำมาดียะห์ และผู้บริหารสถาบันในเครือข่าย</dd>
</dl>
<div class="gallery" style="margin-top:1.5rem">
<figure class="photo">{pic('wami-group','ภาพหมู่ตัวแทนจาก WAMI Thailand และผู้ต้อนรับ ยืนเรียงห้าคนหน้าอาคาร','(min-width:700px) 50vw, 100vw')}<figcaption>ภาพหมู่ตัวแทนและผู้ต้อนรับ</figcaption></figure>
<figure class="photo">{pic('wami-site','กลุ่มผู้ชายยืนพูดคุยกันที่ลานข้างอาคารเรียน ใต้โครงหลังคาเหล็ก','(min-width:700px) 50vw, 100vw')}<figcaption>ดูพื้นที่ภายในโรงเรียน</figcaption></figure>
<figure class="photo">{pic('wami-roof','ผู้ชายสามคนยืนคุยกันใต้โครงหลังคาเหล็กที่ยังไม่มุงหลังคา','(min-width:700px) 50vw, 100vw')}<figcaption>ใต้โครงหลังคาเหล็กในโรงเรียน</figcaption></figure>
<figure class="photo">{pic('wami-talk','ผู้ชายสามคนยืนคุยกันหน้าอาคาร คนหนึ่งสวมหมวกสีส้ม อีกคนสวมชุดโต๊ปสีขาว','(min-width:700px) 50vw, 100vw')}<figcaption>พูดคุยระหว่างการเยี่ยมชม</figcaption></figure>
</div>
<figure class="band" style="margin-top:1.5rem">{pic('wami-plan','ภาพแบบมัสยิดทรงโดมสีทองมีหออะซานสองข้าง เป็นแบบอาคารที่วางแผนไว้ ยังไม่ได้สร้าง','(min-width:1000px) 960px, 100vw')}<figcaption>แบบอาคารที่วางแผนไว้ในอนาคต ยังไม่ใช่อาคารที่มีอยู่จริง</figcaption></figure>
</div></section>
'''
page('/news/wami-iwfs-musolla/', 'news', 'ตัวแทนจาก WAMI Thailand มาเยือน IWFS เพื่อสนับสนุนมูซอลลา | ห้องข่าว เครือข่ายการศึกษาปาตารายอ',
     'ตัวแทนจาก WAMI Thailand มาเยือนโรงเรียนอิสลามวิทยามูลนิธิ (IWFS) เพื่อสนับสนุนมูซอลลา', wami, wami_hero)


# ---------------- PRIVACY ----------------
priv_hero = ('<section class="hero-sub"><div class="wrap on-navy">'
             '<h1>ความเป็นส่วนตัว</h1>'
             '<p>วิธีที่เว็บไซต์นี้จัดการข้อมูลของท่าน</p>'
             '</div></section>')
privacy = (
'<section class="section"><div class="wrap" style="max-width:42rem">'
'<p>เครือข่ายการศึกษาปาตารายอ ดูแลเว็บไซต์นี้เพื่อให้ผู้ปกครอง นักเรียน และผู้สนใจ รู้จักโรงเรียนอิสลามวิทยามูลนิธิ (IWFS) วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC) และมูลนิธิเพื่อการศึกษามูฮำมาดียะห์ (MUEF)</p>'
'<p>หน้าสาธารณะของเว็บไซต์นี้ไม่มีแบบฟอร์มส่งข้อความ และไม่เก็บข้อมูลการเข้าชมไว้ในระบบของเครือข่าย เราไม่ใช้คุกกี้เพื่อติดตามพฤติกรรมข้ามเว็บ และไม่ขายข้อมูลผู้เข้าชม</p>'
'<p>การติดต่อทำได้ทางอีเมลของเครือข่ายและ LINE บัญชีทางการของแต่ละสถาบัน หากท่านส่งข้อความมา ข้อมูลที่ท่านบอก เช่น ชื่อ ที่อยู่อีเมล ระดับชั้นที่สนใจ หรือวันที่จะเยี่ยมชม จะใช้เพื่อตอบคำถาม นัดหมาย และงานรับสมัครเท่านั้น</p>'
'<p>หน้า<a href="/raya-hub/">ห้องแลป</a>มีลิงก์และคิวอาร์ไปแบบฟอร์มภายนอก สำหรับผู้ที่ร่วมทดสอบระบบ Raya Hub ข้อมูลที่กรอกในแบบฟอร์มนั้นอยู่ในระบบของผู้ให้บริการแบบฟอร์ม ไม่ได้อยู่บนเว็บไซต์นี้ ท่านควรอ่านประกาศของแบบฟอร์มนั้นก่อนกรอก</p>'
'<p>ผู้ที่ต้องการส่งงานเขียนเข้าห้องสมุดต้องเข้าสู่ระบบด้วยลิงก์ทางอีเมล เราเก็บอีเมล ชื่อที่แสดง สังกัด ตำแหน่งหรือบทบาท ต้นฉบับ และภาพปกที่ท่านส่ง ใช้เพื่อยืนยันตัวตน พิจารณาผลงาน และเผยแพร่เฉพาะงานที่ได้รับอนุมัติบนหน้าห้องสมุด ผู้ดูแลระบบใช้ที่อยู่อีเมลของเครือข่ายเป็นผู้พิจารณา ข้อมูลนี้เก็บในระบบฐานข้อมูลที่เครือข่ายใช้สำหรับงานเขียน หากต้องการแก้ไขหรือลบบัญชีหรือต้นฉบับ ส่งคำขอทางอีเมลด้านล่าง</p>''<p>ภาพบุคคลที่ปรากฏบนเว็บนี้ใช้โดยได้รับความยินยอมจากเจ้าของภาพ</p>'
f'<p>หากต้องการสอบถามเรื่องข้อมูลส่วนบุคคล ส่งอีเมล <a href="mailto:{EMAIL}">{EMAIL}</a> หรือทัก LINE ตามช่องทางในหน้า <a href="/contact/">ติดต่อ</a></p>'
f'<p class="small muted">หน้านี้ใช้กับเว็บไซต์ที่อยู่ {SITE} ปรับปรุงเมื่อ 11 พฤศจิกายน 2569</p>'
'</div></section>'
)
page('/privacy/', 'privacy', 'ความเป็นส่วนตัว | เครือข่ายการศึกษาปาตารายอ',
     'วิธีที่เว็บไซต์เครือข่ายการศึกษาปาตารายอ จัดการข้อมูลของท่าน รวมถึงข้อมูลของผู้ที่ส่งงานเขียนเข้าห้องสมุด',
     privacy, priv_hero)


# ---------------- WRITE / ADMIN ----------------
write_hero = sub_hero('ห้องสมุด', 'ส่งงานเขียน', 'ส่งงานเขียนเข้าห้องสมุด',
                      'เข้าสู่ระบบด้วยอีเมล แล้วส่งต้นฉบับให้ผู้พิจารณาตรวจก่อนเผยแพร่')
write_body = '<section class="section"><div class="wrap"><div id="write-app" class="write-app" data-mode="write"><p>กำลังเปิดหน้าเขียน</p></div></div></section>'
page('/write/', 'library', 'ส่งงานเขียน | ห้องสมุด เครือข่ายการศึกษาปาตารายอ',
     'เข้าสู่ระบบด้วยอีเมลเพื่อส่งงานเขียนเข้าห้องสมุดของเครือข่ายการศึกษาปาตารายอ',
     write_body, write_hero, index=False, scripts=WRITE_JS)

mine_hero = sub_hero('ห้องสมุด', 'งานของฉัน', 'งานเขียนของฉัน',
                     'ดูสถานะฉบับร่าง งานที่รอพิจารณา และงานที่เผยแพร่แล้ว')
mine_body = '<section class="section"><div class="wrap"><div id="write-app" class="write-app" data-mode="mine"><p>กำลังเปิดรายการ</p></div></div></section>'
page('/write/my/', 'library', 'งานของฉัน | ห้องสมุด เครือข่ายการศึกษาปาตารายอ',
     'รายการต้นฉบับของท่านในห้องสมุดเครือข่ายการศึกษาปาตารายอ',
     mine_body, mine_hero, index=False, scripts=WRITE_JS)

admin_hero = sub_hero('ห้องสมุด', 'ผู้พิจารณา', 'พิจารณาผลงาน',
                      'หน้านี้สำหรับผู้พิจารณาของเครือข่ายเท่านั้น')
admin_body = '<section class="section"><div class="wrap"><div id="write-app" class="write-app" data-mode="review"><p>กำลังเปิดคิวพิจารณา</p></div></div></section>'
page('/admin/review/', 'library', 'พิจารณาผลงาน | เครือข่ายการศึกษาปาตารายอ',
     'หน้าพิจารณาต้นฉบับก่อนเผยแพร่ในห้องสมุด',
     admin_body, admin_hero, index=False, scripts=WRITE_JS)

read_body = '<section class="section"><div class="wrap"><div id="write-app" class="write-app" data-mode="read"><p>กำลังเปิดบทความ</p></div></div></section>'
page('/library/w/', 'library', 'งานเขียนจากผู้ร่วมส่ง | ห้องสมุด เครือข่ายการศึกษาปาตารายอ',
     'งานเขียนที่ได้รับอนุมัติให้เผยแพร่ในห้องสมุดเครือข่ายการศึกษาปาตารายอ',
     read_body, '', index=True, scripts=WRITE_JS)

# ---------------- 404 ----------------
nf = ('<section class="section page-404"><div class="wrap">''<p class="eyebrow">ห้องที่หาไม่เจอ</p>''<h1>ไม่พบหน้านี้</h1>''<p>หน้าที่คุณหาอาจย้ายไปแล้ว ลองกลับไปหน้าแรก หรือส่งอีเมล ' + EMAIL + ' เพื่อสอบถาม</p>''<p class="ctas">' + CTA_BTN + '<a class="btn btn--line" href="/">กลับหน้าแรก</a></p>''</div></section>')
page('/_404/', 'none', 'ไม่พบหน้านี้ | เครือข่ายการศึกษาปาตารายอ', 'ไม่พบหน้านี้', nf, index=False)
os.rename(OUT + '/_404/index.html', OUT + '/404.html'); os.rmdir(OUT + '/_404')

open(OUT + '/robots.txt', 'w').write(
    'User-agent: *\nAllow: /\n\nSitemap: ' + SITE + '/sitemap.xml\n'
)

urls = []
for dirpath, _, files in os.walk(OUT):
    if 'index.html' not in files:
        continue
    rel = dirpath[len(OUT):].replace(chr(92), '/') or '/'
    if not rel.endswith('/'):
        rel += '/'
    if rel.startswith('/write/') or rel.startswith('/admin/') or rel == '/library/w/':
        continue
    urls.append(SITE + rel)
urls = sorted(set(urls), key=lambda u: (u != SITE + '/', u))
header1 = '<?xml version="1.0" encoding="UTF-8"?>'
header2 = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
sm = [header1, header2]
for u in urls:
    sm.append('  <url><loc>' + u + '</loc><lastmod>2026-11-11</lastmod></url>')
sm.append('</urlset>\n')
open(OUT + '/sitemap.xml', 'w').write('\n'.join(sm))
print('built', len(urls), 'pages')
