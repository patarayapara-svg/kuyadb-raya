/* ห้องข่าว: โหลดข่าวจาก Google Sheets (CSV เผยแพร่สาธารณะ)
   คอลัมน์: ID, Date, Category, Title, Summary, Content, ImageURL, Author, Status, GalleryURLs, ReadMoreURL
   แสดงเฉพาะ Status=Published (หรือ เผยแพร่) เรียง ID มากไปน้อย
   ผสานกับข่าวสถิตใน #static-news และตัดรายการซ้ำ */
(function () {
  'use strict';
  var box = document.getElementById('sheet-news');
  if (!box) return;
  var CSV_URL = box.getAttribute('data-csv');
  var staticRoot = document.getElementById('static-news');
  var REFRESH_MS = 60000;
  var TH_MONTHS = ['มกราคม','กุมภาพันธ์','มีนาคม','เมษายน','พฤษภาคม','มิถุนายน','กรกฎาคม','สิงหาคม','กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม'];
  var TH_SHORT = ['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'];
  var lastText = null;
  var lastItems = [];
  var modalEl = null;
  var lastFocus = null;

  function parseCSV(text) {
    text = String(text || '').replace(/^\uFEFF/, '');
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
    return rows.filter(function (r) { return r.some(function (v) { return String(v).trim() !== ''; }); });
  }

  function norm(h) { return String(h || '').trim().toLowerCase().replace(/[\s_\-]+/g, ''); }
  var ALIASES = {
    id: ['id', 'ลำดับ'], date: ['date', 'วันที่', 'publishdate', 'published'],
    category: ['category', 'หมวด', 'หมวดหมู่', 'ประเภท'],
    title: ['title', 'หัวข้อ', 'ชื่อข่าว'], summary: ['summary', 'สรุป', 'เกริ่น'],
    content: ['content', 'เนื้อหา', 'รายละเอียด', 'body'],
    image: ['imageurl', 'image', 'ภาพ', 'รูป', 'รูปภาพ'],
    author: ['author', 'ผู้เขียน'], status: ['status', 'สถานะ'],
    gallery: ['galleryurls', 'gallery', 'galleryurl', 'ภาพเพิ่มเติม', 'แกลเลอรี', 'แกลเลอรี่'],
    readmore: ['readmoreurl', 'readmore', 'link', 'url', 'ลิงก์', 'อ่านต่อ']
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

  function parseDate(s) {
    if (!s) return null;
    s = String(s).trim().replace(/[๐-๙]/g, function (d) { return String(d.charCodeAt(0) - 0x0E50); });
    var m, y, mo, d;
    if ((m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/))) { y = +m[1]; mo = +m[2]; d = +m[3]; }
    else if ((m = s.match(/^(\d{1,2})[\/.](\d{1,2})[\/.](\d{4})/))) { d = +m[1]; mo = +m[2]; y = +m[3]; }
    else {
      m = s.match(/^(\d{1,2})\s*([^\s\d]+)\s*(\d{4})/);
      if (!m) { var t = Date.parse(s); return isNaN(t) ? null : new Date(t); }
      d = +m[1]; y = +m[3];
      var name = m[2].replace(/\s/g, '');
      mo = TH_MONTHS.indexOf(name) + 1 || TH_SHORT.indexOf(name) + 1 ||
        TH_SHORT.map(function (x) { return x.replace(/\./g, ''); }).indexOf(name.replace(/\./g, '')) + 1;
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
  function extractDriveId(u) {
    try {
      var x = new URL(u, location.href);
      var host = x.hostname;
      if (host !== 'drive.google.com' && host !== 'docs.google.com' && !/\.googleusercontent\.com$/.test(host)) return null;
      var m = x.pathname.match(/\/(?:file|document|uc|open|thumbnail)\/d\/([a-zA-Z0-9_-]+)/) ||
              x.pathname.match(/\/d\/([a-zA-Z0-9_-]{20,})/) ||
              x.pathname.match(/\/d\/([a-zA-Z0-9_-]+)/);
      if (m) return m[1];
      var id = x.searchParams.get('id');
      return id || null;
    } catch (e) { return null; }
  }
  function safeUrl(u, asImage) {
    if (!u) return null;
    u = String(u).trim();
    if (!u || /^(javascript|data|vbscript):/i.test(u)) return null;
    var driveId = extractDriveId(u);
    if (driveId) {
      return asImage
        ? 'https://drive.google.com/thumbnail?id=' + encodeURIComponent(driveId) + '&sz=w1600'
        : 'https://drive.google.com/file/d/' + encodeURIComponent(driveId) + '/view';
    }
    try {
      if (u.charAt(0) === '/' && u.charAt(1) !== '/') {
        return new URL(u, location.origin).href;
      }
      var x = new URL(u, location.href);
      if (x.protocol === 'https:' || (x.protocol === 'http:' && x.origin === location.origin)) return x.href;
      return null;
    } catch (e) { return null; }
  }
  function isPublished(o) {
    var s = norm(o.status);
    return s === 'published' || s === 'publish' || s === 'เผยแพร่';
  }
  function pathOf(u) {
    try { return new URL(u, location.href).pathname.replace(/\/+$/, '') || '/'; } catch (e) { return ''; }
  }
  function splitGallery(s) {
    if (!s) return [];
    return String(s).split('|').map(function (x) { return x.trim(); }).filter(Boolean);
  }

  function readStatic() {
    if (!staticRoot) return [];
    return Array.prototype.map.call(staticRoot.querySelectorAll('a.news-card, article.news-card'), function (node) {
      var href = node.getAttribute('href') || '';
      var titleEl = node.querySelector('h3, h2');
      var img = node.querySelector('img');
      var tag = node.querySelector('.tag');
      return {
        source: 'static',
        node: node,
        id: (node.getAttribute('data-sheet-id') || '').trim(),
        _id: parseFloat(node.getAttribute('data-sheet-id')),
        title: (node.getAttribute('data-title') || (titleEl && titleEl.textContent) || '').trim(),
        date: node.getAttribute('data-date') || '',
        _date: parseDate(node.getAttribute('data-date') || ''),
        category: node.getAttribute('data-category') || '',
        href: href,
        image: img ? img.getAttribute('src') : '',
        tagText: tag ? tag.textContent : '',
        _row: 0
      };
    });
  }

  function isDupe(csv, stat) {
    if (csv.id && stat.id && String(csv.id) === String(stat.id)) return true;
    if (csv.readmore && stat.href && pathOf(csv.readmore) === pathOf(stat.href)) return true;
    var sameDate = csv._date && stat._date && csv._date.getTime() === stat._date.getTime();
    if (sameDate && csv.title && stat.title) {
      var a = norm(csv.title), b = norm(stat.title);
      if (a === b || a.indexOf(b) !== -1 || b.indexOf(a) !== -1) return true;
    }
    return false;
  }

  function tagText(o) {
    var bits = [];
    if (o._date) bits.push(thaiDate(o._date));
    else if (o.date) bits.push(o.date);
    if (o.category) bits.push(o.category);
    return bits.join(' · ');
  }

  function cardFromCsv(o) {
    var art = el('article', 'card lab-card news-card');
    art.setAttribute('data-open', o.id || '');
    art.setAttribute('tabindex', '0');
    art.setAttribute('role', 'button');
    art.setAttribute('aria-haspopup', 'dialog');
    var imgUrl = safeUrl(o.image, true);
    if (imgUrl) {
      var im = el('img');
      im.src = imgUrl; im.alt = o.title || ''; im.loading = 'lazy'; im.decoding = 'async';
      im.referrerPolicy = 'no-referrer';
      im.width = 1600; im.height = 900;
      im.onerror = function () { im.remove(); };
      art.appendChild(im);
    }
    var tag = tagText(o);
    if (tag) art.appendChild(el('span', 'tag tag--blue', tag));
    art.appendChild(el('h3', null, o.title || '(ไม่มีหัวข้อ)'));
    if (o.summary) art.appendChild(el('p', null, o.summary));
    art.appendChild(el('span', 'more', 'อ่านต่อ'));
    function open() { openModal(o); }
    art.addEventListener('click', open);
    art.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
    });
    return art;
  }

  function closeModal() {
    if (!modalEl) return;
    modalEl.remove();
    modalEl = null;
    document.body.classList.remove('news-modal-open');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
    lastFocus = null;
    if (location.hash.indexOf('#news-') === 0) {
      history.replaceState(null, '', location.pathname + location.search);
    }
  }

  function openModal(o, fromHash) {
    closeModal();
    lastFocus = document.activeElement;
    var back = el('div', 'news-modal-back');
    back.setAttribute('role', 'presentation');
    var dlg = el('div', 'news-modal');
    dlg.setAttribute('role', 'dialog');
    dlg.setAttribute('aria-modal', 'true');
    var titleId = 'news-modal-title';
    dlg.setAttribute('aria-labelledby', titleId);
    var close = el('button', 'news-modal-close', '×');
    close.type = 'button'; close.setAttribute('aria-label', 'ปิด');
    close.addEventListener('click', closeModal);
    dlg.appendChild(close);
    var tag = tagText(o);
    if (tag) dlg.appendChild(el('span', 'tag tag--blue', tag));
    var h = el('h2', null, o.title || '');
    h.id = titleId;
    dlg.appendChild(h);
    if (o.author) dlg.appendChild(el('p', 'small muted', o.author));
    var imgs = [];
    var cover = safeUrl(o.image, true);
    if (cover) imgs.push(cover);
    splitGallery(o.gallery).forEach(function (g) {
      var u = safeUrl(g, true);
      if (u && imgs.indexOf(u) === -1) imgs.push(u);
    });
    if (imgs.length) {
      var gal = el('div', 'news-gallery');
      imgs.forEach(function (src, i) {
        var im = el('img');
        im.src = src; im.alt = (o.title || '') + (i ? ' ภาพที่ ' + (i + 1) : '');
        im.loading = i ? 'lazy' : 'eager'; im.decoding = 'async';
        im.referrerPolicy = 'no-referrer';
        im.onerror = function () { im.remove(); };
        gal.appendChild(im);
      });
      dlg.appendChild(gal);
    }
    var body = o.content || o.summary || '';
    String(body).split(/\n+/).forEach(function (p) {
      if (p.trim()) dlg.appendChild(el('p', null, p.trim()));
    });
    var actions = el('p', 'form-actions');
    var more = o.readmore && safeUrl(o.readmore, false);
    if (more) {
      var a = el('a', 'btn', 'อ่านเพิ่มเติม');
      a.href = more; a.rel = 'noopener';
      try { if (new URL(more).origin !== location.origin) a.target = '_blank'; } catch (e) {}
      actions.appendChild(a);
    }
    var shareUrl = more && pathOf(more) && more.indexOf(location.origin) === 0 ? more :
      (location.origin + location.pathname + (o.id ? '#news-' + encodeURIComponent(o.id) : ''));
    var fb = el('a', 'btn btn--line', 'แชร์ไป Facebook');
    fb.href = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(shareUrl);
    fb.target = '_blank'; fb.rel = 'noopener noreferrer';
    var line = el('a', 'btn btn--line', 'แชร์ไป LINE');
    line.href = 'https://social-plugins.line.me/lineit/share?url=' + encodeURIComponent(shareUrl);
    line.target = '_blank'; line.rel = 'noopener noreferrer';
    actions.appendChild(fb); actions.appendChild(line);
    dlg.appendChild(actions);
    back.appendChild(dlg);
    back.addEventListener('click', function (e) { if (e.target === back) closeModal(); });
    document.body.appendChild(back);
    document.body.classList.add('news-modal-open');
    modalEl = back;
    close.focus();
    if (o.id && !fromHash) history.replaceState(null, '', location.pathname + location.search + '#news-' + encodeURIComponent(o.id));
  }

  function onKey(e) {
    if (!modalEl) return;
    if (e.key === 'Escape') { e.preventDefault(); closeModal(); return; }
    if (e.key !== 'Tab') return;
    var f = modalEl.querySelectorAll('a,button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])');
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
  document.addEventListener('keydown', onKey);

  function status(msg, isError) {
    box.setAttribute('aria-busy', 'false');
    box.textContent = '';
    var p = el('div', 'sn-status' + (isError ? ' sn-status--error' : ''));
    p.appendChild(el('p', null, msg));
    if (isError) {
      var b = el('button', 'btn btn--line', 'ลองใหม่');
      b.type = 'button'; b.onclick = function () { load(true); };
      p.appendChild(b);
    }
    box.appendChild(p);
  }

  function render(csvItems) {
    var stat = readStatic();
    var merged = [];
    csvItems.forEach(function (c) {
      if (stat.some(function (s) { return isDupe(c, s); })) return;
      merged.push(c);
    });
    stat.forEach(function (s) { merged.push(s); });
    merged.sort(function (a, b) {
      var ia = isNaN(a._id) ? -Infinity : a._id;
      var ib = isNaN(b._id) ? -Infinity : b._id;
      if (ib !== ia) return ib - ia;
      var da = a._date ? a._date.getTime() : -Infinity;
      var db = b._date ? b._date.getTime() : -Infinity;
      if (db !== da) return db - da;
      return (b._row || 0) - (a._row || 0);
    });
    lastItems = merged;
    box.setAttribute('aria-busy', 'false');
    box.textContent = '';
    box.classList.add('news-feed');
    if (!merged.length) { status('ยังไม่มีข่าวในขณะนี้'); if (staticRoot) staticRoot.hidden = false; return; }
    merged.forEach(function (o) {
      if (o.source === 'static' && o.node) {
        var clone = o.node.cloneNode(true);
        clone.removeAttribute('hidden');
        box.appendChild(clone);
      } else {
        box.appendChild(cardFromCsv(o));
      }
    });
    if (staticRoot) staticRoot.hidden = true;
    openFromHash();
  }

  function openFromHash() {
    var m = (location.hash || '').match(/^#news-(.+)$/);
    if (!m) return;
    var id = decodeURIComponent(m[1]);
    var found = lastItems.filter(function (o) { return String(o.id) === id && o.source !== 'static'; })[0];
    if (found) openModal(found, true);
  }
  window.addEventListener('hashchange', openFromHash);

  function csvItemsFromText(text) {
    var rows = parseCSV(text);
    if (rows.length < 2) return [];
    var items = toObjects(rows).filter(function (o) { return (o.title || o.summary) && isPublished(o); });
    items.forEach(function (o) { o._date = parseDate(o.date); o._id = parseFloat(o.id); o.source = 'csv'; });
    items.sort(function (a, b) {
      var ia = isNaN(a._id) ? -Infinity : a._id;
      var ib = isNaN(b._id) ? -Infinity : b._id;
      if (ib !== ia) return ib - ia;
      return (b._row || 0) - (a._row || 0);
    });
    return items;
  }

  function load(manual) {
    if (manual || lastText === null) box.setAttribute('aria-busy', 'true');
    if (manual) status('กำลังโหลดข่าวล่าสุด…');
    var url = CSV_URL + (CSV_URL.indexOf('?') === -1 ? '?' : '&') + '_t=' + Date.now();
    fetch(url, { cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
      .then(function (t) {
        if (/^\s*</.test(t)) throw new Error('not csv');
        if (t === lastText && !manual) return;
        lastText = t;
        render(csvItemsFromText(t));
      })
      .catch(function () {
        if (lastText === null) {
          render([]);
          if (staticRoot) staticRoot.hidden = false;
          var note = el('p', 'small muted', 'โหลดข่าวจากตารางไม่สำเร็จ แสดงเฉพาะข่าวที่อยู่บนเว็บไว้ก่อน');
          box.insertBefore(note, box.firstChild);
        }
      });
  }

  load(false);
  setInterval(function () { if (!document.hidden) load(false); }, REFRESH_MS);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) load(false); });
})();
