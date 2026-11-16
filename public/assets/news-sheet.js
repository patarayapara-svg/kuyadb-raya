/* ห้องข่าว: โหลดข่าวจาก Google Sheets (CSV เผยแพร่สาธารณะ) ฝั่งเบราว์เซอร์
   คอลัมน์ที่รองรับ: ID, Date, Category, Title, Summary, Content, ImageURL, Author, Status
   แสดงเฉพาะแถวที่ Status ว่าง หรือเป็น Published / เผยแพร่ เรียงจากใหม่ไปเก่า */
(function () {
  'use strict';
  var box = document.getElementById('sheet-news');
  if (!box) return;
  var CSV_URL = box.getAttribute('data-csv');
  var REFRESH_MS = 60000;
  var TH_MONTHS = ['มกราคม','กุมภาพันธ์','มีนาคม','เมษายน','พฤษภาคม','มิถุนายน','กรกฎาคม','สิงหาคม','กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม'];
  var TH_SHORT = ['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'];
  var lastText = null;

  // RFC 4180 CSV parser: รองรับเครื่องหมายคำพูด, จุลภาคและขึ้นบรรทัดใหม่ภายในช่อง, "" แทน "
  function parseCSV(text) {
    text = text.replace(/^\uFEFF/, '');
    var rows = [], row = [], field = '', i = 0, q = false, c;
    while (i < text.length) {
      c = text[i];
      if (q) {
        if (c === '"') {
          if (text[i + 1] === '"') { field += '"'; i += 2; continue; }
          q = false; i++; continue;
        }
        field += c; i++; continue;
      }
      if (c === '"') { q = true; i++; continue; }
      if (c === ',') { row.push(field); field = ''; i++; continue; }
      if (c === '\r') { i++; continue; }
      if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; i++; continue; }
      field += c; i++;
    }
    if (field !== '' || row.length) { row.push(field); rows.push(row); }
    return rows.filter(function (r) { return r.some(function (v) { return v.trim() !== ''; }); });
  }

  function norm(h) { return String(h || '').trim().toLowerCase().replace(/[\s_\-]+/g, ''); }
  var ALIASES = {
    id: ['id', 'ลำดับ'], date: ['date', 'วันที่', 'publishdate', 'published'], category: ['category', 'หมวด', 'หมวดหมู่', 'ประเภท'],
    title: ['title', 'หัวข้อ', 'ชื่อข่าว'], summary: ['summary', 'สรุป', 'เกริ่น'], content: ['content', 'เนื้อหา', 'รายละเอียด', 'body'],
    image: ['imageurl', 'image', 'ภาพ', 'รูป', 'รูปภาพ'], author: ['author', 'ผู้เขียน'], status: ['status', 'สถานะ'],
    link: ['link', 'url', 'ลิงก์']
  };
  function toObjects(rows) {
    var head = rows[0].map(norm), map = {};
    Object.keys(ALIASES).forEach(function (k) {
      for (var j = 0; j < head.length; j++) if (ALIASES[k].indexOf(head[j]) !== -1) { map[k] = j; break; }
    });
    return rows.slice(1).map(function (r, idx) {
      var o = { _row: idx };
      Object.keys(map).forEach(function (k) { o[k] = (r[map[k]] || '').trim(); });
      return o;
    });
  }

  // แปลงวันที่: 2026-11-12, 12/11/2026, 12/11/2569, 11 พฤศจิกายน 2569, 11 พ.ย. 2569
  function parseDate(s) {
    if (!s) return null;
    s = s.trim().replace(/[๐-๙]/g, function (d) { return String(d.charCodeAt(0) - 0x0E50); });
    var m, y, mo, d;
    if ((m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/))) { y = +m[1]; mo = +m[2]; d = +m[3]; }
    else if ((m = s.match(/^(\d{1,2})[\/.](\d{1,2})[\/.](\d{4})/))) { d = +m[1]; mo = +m[2]; y = +m[3]; }
    else {
      m = s.match(/^(\d{1,2})\s*([^\s\d]+)\s*(\d{4})/);
      if (!m) { var t = Date.parse(s); return isNaN(t) ? null : new Date(t); }
      d = +m[1]; y = +m[3];
      var name = m[2].replace(/\s/g, '');
      mo = TH_MONTHS.indexOf(name) + 1 || TH_SHORT.indexOf(name) + 1 || TH_SHORT.map(function (x) { return x.replace(/\./g, ''); }).indexOf(name.replace(/\./g, '')) + 1;
      if (!mo) { var t2 = Date.parse(s); return isNaN(t2) ? null : new Date(t2); }
    }
    if (y > 2400) y -= 543;
    var dt = new Date(y, mo - 1, d);
    return isNaN(dt.getTime()) ? null : dt;
  }
  function thaiDate(dt) { return dt.getDate() + ' ' + TH_SHORT[dt.getMonth()] + ' ' + (dt.getFullYear() + 543); }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function safeUrl(u) {
    try { var x = new URL(u, location.href); return x.protocol === 'https:' ? x.href : null; } catch (e) { return null; }
  }
  function isVisible(o) {
    var s = norm(o.status);
    return !s || s === 'published' || s === 'publish' || s === 'เผยแพร่' || s === 'แสดง' || s === 'live';
  }

  function card(o, featured) {
    var a = el('article', 'sn-card' + (featured ? ' sn-card--featured' : ''));
    var img = o.image && safeUrl(o.image);
    if (img) {
      var fig = el('div', 'sn-media');
      var im = el('img');
      im.src = img; im.alt = o.title || ''; im.loading = featured ? 'eager' : 'lazy'; im.decoding = 'async';
      im.referrerPolicy = 'no-referrer';
      im.onerror = function () { fig.remove(); a.classList.add('sn-card--noimg'); };
      fig.appendChild(im); a.appendChild(fig);
    } else a.classList.add('sn-card--noimg');
    var body = el('div', 'sn-body');
    var meta = el('p', 'sn-meta');
    if (o.category) meta.appendChild(el('span', 'sn-cat', o.category));
    if (o._date) { var t = el('time', 'sn-date', thaiDate(o._date)); t.dateTime = o._date.toISOString().slice(0, 10); meta.appendChild(t); }
    else if (o.date) meta.appendChild(el('span', 'sn-date', o.date));
    if (meta.childNodes.length) body.appendChild(meta);
    body.appendChild(el(featured ? 'h2' : 'h3', 'sn-title', o.title || '(ไม่มีหัวข้อ)'));
    if (o.summary) body.appendChild(el('p', 'sn-summary', o.summary));
    if (o.content && o.content !== o.summary) {
      var det = el('details', 'sn-more');
      det.appendChild(el('summary', null, 'อ่านต่อ'));
      o.content.split(/\n+/).forEach(function (p) { if (p.trim()) det.appendChild(el('p', null, p.trim())); });
      body.appendChild(det);
    }
    var link = o.link && safeUrl(o.link);
    if (link) { var l = el('a', 'sn-link', 'ดูรายละเอียด'); l.href = link; l.rel = 'noopener'; if (new URL(link).origin !== location.origin) l.target = '_blank'; body.appendChild(l); }
    a.appendChild(body);
    return a;
  }

  function status(msg, isError) {
    box.setAttribute('aria-busy', 'false');
    box.textContent = '';
    var p = el('div', 'sn-status' + (isError ? ' sn-status--error' : ''));
    p.appendChild(el('p', null, msg));
    if (isError) {
      var b = el('button', 'sn-retry', 'ลองใหม่');
      b.type = 'button'; b.onclick = function () { load(true); };
      p.appendChild(b);
    }
    box.appendChild(p);
  }

  function render(text) {
    var rows = parseCSV(text);
    if (rows.length < 2) { status('ยังไม่มีข่าวในขณะนี้'); return; }
    var items = toObjects(rows).filter(function (o) { return (o.title || o.summary) && isVisible(o); });
    items.forEach(function (o) { o._date = parseDate(o.date); o._id = parseFloat(o.id); });
    items.sort(function (a, b) {
      var da = a._date ? a._date.getTime() : -Infinity, db = b._date ? b._date.getTime() : -Infinity;
      if (db !== da) return db - da;
      if (!isNaN(a._id) && !isNaN(b._id) && a._id !== b._id) return b._id - a._id;
      return b._row - a._row;
    });
    if (!items.length) { status('ยังไม่มีข่าวในขณะนี้'); return; }
    box.setAttribute('aria-busy', 'false');
    box.textContent = '';
    box.appendChild(card(items[0], true));
    if (items.length > 1) {
      var grid = el('div', 'sn-grid');
      items.slice(1).forEach(function (o) { grid.appendChild(card(o, false)); });
      box.appendChild(grid);
    }
  }

  function load(manual) {
    if (manual || lastText === null) { box.setAttribute('aria-busy', 'true'); }
    if (manual) status('กำลังโหลดข่าวล่าสุด…');
    var url = CSV_URL + (CSV_URL.indexOf('?') === -1 ? '?' : '&') + '_t=' + Date.now();
    fetch(url, { cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
      .then(function (t) {
        if (/^\s*</.test(t)) throw new Error('not csv');
        if (t === lastText) return;
        lastText = t; render(t);
      })
      .catch(function () {
        if (lastText === null) status('โหลดข่าวล่าสุดไม่สำเร็จ กรุณาตรวจการเชื่อมต่อแล้วลองใหม่', true);
      });
  }

  load(false);
  setInterval(function () { if (!document.hidden) load(false); }, REFRESH_MS);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) load(false); });
})();
