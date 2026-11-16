import { createClient } from '/assets/vendor/supabase.js';
import { SB_URL, SB_ANON, SB_BUCKET, ADMIN_EMAIL } from '/assets/sb-public.js';

const sb = createClient(SB_URL, SB_ANON, {
  auth: { persistSession: true, detectSessionInUrl: true, autoRefreshToken: true }
});

const CAT = { writing: 'งานเขียนและบทความ', academic: 'ผลงานทางวิชาการ', lesson: 'บทเรียน' };
const AFF = [
  ['IWFS', 'โรงเรียนอิสลามวิทยามูลนิธิ (IWFS)'],
  ['MUTEC', 'วิทยาลัยเทคโนโลยีพณิชยการมูฮำมาดีย์ (MUTEC)'],
  ['มศม.', 'มูลนิธิเพื่อการศึกษามูฮำมาดียะห์ (มศม.)'],
  ['เครือข่าย', 'เครือข่ายการศึกษาปาตารายอ'],
  ['อื่น', 'อื่น']
];
const ST = { draft: 'ฉบับร่าง', pending: 'รอพิจารณา', approved: 'เผยแพร่แล้ว', rejected: 'ยังไม่ผ่าน' };

const $ = (s, r=document) => r.querySelector(s);
const el = (html) => { const t=document.createElement('div'); t.innerHTML=html.trim(); return t.firstElementChild; };
const esc = (s) => String(s??'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function md(src){
  let t = esc(src || '');
  t = t.replace(/```([\s\S]*?)```/g, (_,c)=>'<pre><code>'+c+'</code></pre>');
  t = t.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  t = t.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  t = t.replace(/^# (.+)$/gm, '<h2>$1</h2>');
  t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/\*(.+?)\*/g, '<em>$1</em>');
  t = t.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" rel="noopener" target="_blank">$1</a>');
  t = t.replace(/^(?:- |\* )(.+)$/gm, '<li>$1</li>');
  t = t.replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>');
  t = t.replace(/(<h[23]>.*<\/h[23]>)|(<pre>[\s\S]*?<\/pre>)|(<ul>[\s\S]*?<\/ul>)|(.+?)(?=<h[23]>|<pre>|<ul>|$)/g, (m,h,p,u,para) => h||p||u||(para && para.trim() ? '<p>'+para.trim().replace(/\n\n+/g,'</p><p>').replace(/\n/g,'<br>')+'</p>' : ''));
  return t;
}

function slugify(title){
  const a = (title||'').toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,40);
  const r = Math.random().toString(36).slice(2,8);
  return ((a || 'w') + '-' + r).slice(0,80);
}

function msg(box, text, ok){
  if(!box) return;
  box.className = 'msg ' + (ok ? 'msg--ok' : 'msg--err');
  box.hidden = !text;
  box.textContent = text || '';
}

function coverUrl(path){
  if(!path) return '';
  return SB_URL + '/storage/v1/object/public/' + SB_BUCKET + '/' + path;
}

async function session(){
  const { data } = await sb.auth.getSession();
  return data.session || null;
}

async function getProfile(){
  const s = await session();
  if(!s) return { session:null, profile:null };
  const { data, error } = await sb.from('profiles').select('id,email,display_name,affiliation,title,is_admin').eq('id', s.user.id).maybeSingle();
  if(error) console.warn(error);
  return { session:s, profile:data };
}

function profileForm(p, notice){
  const opts = AFF.map(([v,l]) => `<option value="${esc(v)}"${p&&p.affiliation===v?' selected':''}>${esc(l)}</option>`).join('');
  return `<form id="profile-form" class="write-panel">
    ${notice?`<p class="msg">${esc(notice)}</p>`:''}
    <div id="p-msg" hidden></div>
    <div class="field"><label for="display_name">ชื่อที่แสดง</label>
      <input id="display_name" name="display_name" required maxlength="80" value="${esc(p&&p.display_name||'')}"></div>
    <div class="field"><label for="affiliation">สังกัด</label>
      <select id="affiliation" name="affiliation" required>
        <option value="">เลือกสังกัด</option>${opts}
      </select></div>
    <div class="field"><label for="title">ตำแหน่งหรือบทบาท</label>
      <input id="title" name="title" maxlength="80" value="${esc(p&&p.title||'')}" placeholder="เช่น ครู หัวหน้างาน หรือนักเรียน"></div>
    <div class="form-actions"><button class="btn" type="submit">บันทึกประวัติ</button></div>
  </form>`;
}

function loginForm(){
  return `<div class="write-panel">
    <h2>เข้าสู่ระบบเพื่อส่งงานเขียน</h2>
    <p>ใส่ที่อยู่อีเมล เราจะส่งลิงก์เข้าสู่ระบบให้ ท่านต้องมีบัญชีก่อนจึงจะส่งต้นฉบับได้</p>
    <div id="auth-msg" hidden></div>
    <form id="login-form">
      <div class="field"><label for="email">อีเมล</label>
        <input id="email" name="email" type="email" required autocomplete="email"></div>
      <div class="form-actions"><button class="btn" type="submit">ส่งลิงก์เข้าสู่ระบบ</button></div>
    </form>
  </div>`;
}

function accountBar(profile){
  const admin = profile && profile.is_admin ? `<a href="/admin/review/">พิจารณาผลงาน</a>` : '';
  return `<p class="toolbar small">เข้าสู่ระบบแล้วในชื่อ ${esc(profile.display_name||profile.email)}
    · <a href="/write/">เขียนใหม่</a> · <a href="/write/my/">งานของฉัน</a> ${admin? '· '+admin : ''}
    · <button type="button" class="btn btn--line" id="sign-out" style="min-height:36px;padding:.3rem .9rem;font-size:.875rem">ออกจากระบบ</button></p>`;
}

async function saveProfile(form){
  const { session:s } = await getProfile();
  if(!s) return { error:'ยังไม่ได้เข้าสู่ระบบ' };
  const display_name = form.display_name.value.trim();
  const affiliation = form.affiliation.value;
  const title = form.title.value.trim();
  if(!display_name || !affiliation) return { error:'กรุณากรอกชื่อที่แสดงและสังกัด' };
  const { error } = await sb.from('profiles').update({ display_name, affiliation, title }).eq('id', s.user.id);
  return { error: error && error.message };
}

function bindProfile(root){
  const form = $('#profile-form', root);
  if(!form) return;
  form.addEventListener('submit', async ev => {
    ev.preventDefault();
    const r = await saveProfile(form);
    msg($('#p-msg', root), r.error || 'บันทึกแล้ว', !r.error);
  });
}

function bindSignOut(root){
  const b = $('#sign-out', root);
  if(!b) return;
  b.addEventListener('click', async () => {
    await sb.auth.signOut();
    location.href = '/write/';
  });
}

async function pageWrite(root){
  const { session:s, profile } = await getProfile();
  if(!s){ root.innerHTML = loginForm(); bindLogin(root); return; }
  if(!profile || !profile.display_name || !profile.affiliation){
    root.innerHTML = accountBar(profile||{email:s.user.email}) + profileForm(profile, 'กรุณากรอกประวัติสั้นๆ ก่อนส่งงานเขียน');
    bindProfile(root); bindSignOut(root); return;
  }
  const params = new URLSearchParams(location.search);
  const id = params.get('id');
  let row = null;
  if(id){
    const { data, error } = await sb.from('submissions').select('*').eq('id', id).maybeSingle();
    if(error){ root.innerHTML = `<p class="msg msg--err">${esc(error.message)}</p>`; return; }
    row = data;
  }
  root.innerHTML = accountBar(profile) + editorHtml(row, profile);
  bindSignOut(root);
  bindEditor(root, row, profile);
}

function editorHtml(row, profile){
  const locked = row && !['draft','rejected'].includes(row.status) && !(profile&&profile.is_admin);
  const cat = Object.entries(CAT).map(([v,l])=>`<option value="${v}"${row&&row.category===v?' selected':''}>${l}</option>`).join('');
  const cover = row && row.cover_path ? `<img class="cover-preview" alt="" src="${esc(coverUrl(row.cover_path))}">` : '';
  return `<div class="write-panel">
    <h2>${row ? 'แก้ไขต้นฉบับ' : 'เขียนต้นฉบับใหม่'}</h2>
    ${row?`<p><span class="status-pill status-${esc(row.status)}">${ST[row.status]||row.status}</span>
      ${row.review_note? ' · หมายเหตุจากผู้พิจารณา: '+esc(row.review_note):''}</p>`:''}
    ${locked?'<p class="msg">ต้นฉบับนี้อยู่ระหว่างพิจารณาหรือเผยแพร่แล้ว แก้ไขไม่ได้จนกว่าผู้พิจารณาจะส่งคืน</p>':''}
    <div id="ed-msg" hidden></div>
    <form id="ed-form">
      <div class="field"><label for="title">ชื่อเรื่อง</label>
        <input id="title" name="title" required maxlength="200" value="${esc(row&&row.title||'')}" ${locked?'disabled':''}></div>
      <div class="field"><label for="category">หมวด</label>
        <select id="category" name="category" required ${locked?'disabled':''}>${cat}</select></div>
      <div class="field"><label for="body">เนื้อหา (ใช้มาร์กดาวน์ได้ เช่น ## หัวข้อ, **ตัวหนา**, รายการขึ้นต้นด้วย - )</label>
        <textarea id="body" name="body" required ${locked?'disabled':''}>${esc(row&&row.body||'')}</textarea></div>
      <div class="field"><label for="cover">ภาพปก (ไม่บังคับ, ไฟล์ JPEG PNG หรือ WEBP ไม่เกิน 2 เมกะไบต์)</label>
        <input id="cover" name="cover" type="file" accept="image/jpeg,image/png,image/webp" ${locked?'disabled':''}>
        <div id="cover-slot">${cover}</div></div>
      ${locked?'':`<div class="form-actions">
        <button class="btn btn--line" type="submit" data-act="draft">บันทึกฉบับร่าง</button>
        <button class="btn" type="submit" data-act="pending">ส่งให้พิจารณา</button>
      </div>`}
    </form>
  </div>`;
}

function bindLogin(root){
  const form = $('#login-form', root);
  const box = $('#auth-msg', root);
  form.addEventListener('submit', async ev => {
    ev.preventDefault();
    const email = form.email.value.trim();
    const redirectTo = location.origin + '/write/';
    const { error } = await sb.auth.signInWithOtp({ email, options: { emailRedirectTo: redirectTo } });
    msg(box, error ? error.message : 'ส่งลิงก์แล้ว กรุณาเปิดอีเมลแล้วกดลิงก์เพื่อเข้าสู่ระบบ', !error);
  });
}

function bindEditor(root, row, profile){
  const form = $('#ed-form', root);
  if(!form) return;
  let act = 'draft';
  form.querySelectorAll('[data-act]').forEach(b => b.addEventListener('click', () => { act = b.getAttribute('data-act'); }));
  form.addEventListener('submit', async ev => {
    ev.preventDefault();
    const box = $('#ed-msg', root);
    const title = form.title.value.trim();
    const category = form.category.value;
    const body = form.body.value.trim();
    if(!title || !body){ msg(box, 'กรุณากรอกชื่อเรื่องและเนื้อหา', false); return; }
    let cover_path = row && row.cover_path || null;
    const file = form.cover.files && form.cover.files[0];
    if(file){
      if(file.size > 2*1024*1024){ msg(box, 'ไฟล์ภาพใหญ่เกิน 2 เมกะไบต์', false); return; }
      const ext = (file.type==='image/png'?'png':file.type==='image/webp'?'webp':'jpg');
      const path = profile.id + '/' + crypto.randomUUID() + '.' + ext;
      const { error: upErr } = await sb.storage.from(SB_BUCKET).upload(path, file, { upsert:false, contentType:file.type });
      if(upErr){ msg(box, 'อัปโหลดภาพไม่สำเร็จ: '+upErr.message, false); return; }
      cover_path = path;
    }
    const payload = { title, category, body, cover_path, status: act==='pending'?'pending':'draft' };
    let error, data;
    if(row){
      ({ error } = await sb.from('submissions').update(payload).eq('id', row.id));
    } else {
      payload.slug = slugify(title);
      ({ data, error } = await sb.from('submissions').insert(payload).select('id').maybeSingle());
    }
    if(error){ msg(box, error.message, false); return; }
    msg(box, act==='pending' ? 'ส่งให้พิจารณาแล้ว ผู้ดูแลจะตรวจก่อนเผยแพร่บนห้องสมุด' : 'บันทึกฉบับร่างแล้ว', true);
    const newId = row ? row.id : (data && data.id);
    if(newId && !row) history.replaceState(null,'', '/write/?id='+newId);
  });
}

async function pageMine(root){
  const { session:s, profile } = await getProfile();
  if(!s){ location.href='/write/'; return; }
  const { data, error } = await sb.from('submissions').select('id,title,category,status,updated_at,review_note').eq('author_id', s.user.id).order('updated_at',{ascending:false});
  if(error){ root.innerHTML = `<p class="msg msg--err">${esc(error.message)}</p>`; return; }
  const items = (data||[]).map(r => `<li><article class="card sub-item">
    <span class="status-pill status-${esc(r.status)}">${ST[r.status]||r.status}</span>
    <h3 style="margin:0">${esc(r.title)}</h3>
    <p class="small muted" style="margin:0">${CAT[r.category]||r.category}${r.review_note?' · '+esc(r.review_note):''}</p>
    ${['draft','rejected'].includes(r.status)?`<p style="margin:0"><a class="more" href="/write/?id=${esc(r.id)}">แก้ไข</a></p>`:
      r.status==='approved'?`<p style="margin:0">เผยแพร่แล้ว</p>`:`<p style="margin:0">รอพิจารณา แก้ไขไม่ได้ในตอนนี้</p>`}
  </article></li>`).join('') || '<li><p>ยังไม่มีต้นฉบับ <a href="/write/">เริ่มเขียน</a></p></li>';
  root.innerHTML = accountBar(profile) + `<div class="write-panel"><h2>งานของฉัน</h2><ul class="sub-list">${items}</ul></div>`;
  bindSignOut(root);
}

async function pageReview(root){
  const { session:s, profile } = await getProfile();
  if(!s){ location.href='/write/'; return; }
  if(!profile || !profile.is_admin){
    root.innerHTML = `<p class="msg msg--err">หน้านี้สำหรับผู้พิจารณาเท่านั้น</p>`;
    return;
  }
  const { data, error } = await sb.from('submissions').select('*').order('updated_at',{ascending:false});
  if(error){ root.innerHTML = `<p class="msg msg--err">${esc(error.message)}</p>`; return; }
  const pending = (data||[]).filter(r=>r.status==='pending');
  const others = (data||[]).filter(r=>r.status!=='pending');
  const card = (r) => `<li><article class="card sub-item" data-id="${esc(r.id)}">
    <span class="status-pill status-${esc(r.status)}">${ST[r.status]||r.status}</span>
    <h3 style="margin:0">${esc(r.title)}</h3>
    <p class="small muted" style="margin:0">${esc(r.author_name||'')} ${esc(r.author_affiliation||'')} · ${CAT[r.category]||r.category}</p>
    ${r.cover_path?`<img class="cover-preview" alt="" src="${esc(coverUrl(r.cover_path))}">`:''}
    <div class="md">${md(r.body)}</div>
    <form class="review-form">
      <div class="field"><label>หมายเหตุถึงผู้เขียน (ถ้ามี)</label>
        <input name="review_note" value="${esc(r.review_note||'')}"></div>
      <div class="form-actions">
        ${r.status!=='approved'?`<button class="btn" type="submit" data-act="approved">เผยแพร่</button>`:''}
        ${r.status!=='rejected'?`<button class="btn btn--line" type="submit" data-act="rejected">ยังไม่ผ่าน</button>`:''}
        ${r.status==='approved'?`<button class="btn btn--line" type="submit" data-act="rejected">ถอนออกจากห้องสมุด</button>`:''}
      </div>
    </form>
  </article></li>`;
  root.innerHTML = accountBar(profile) + `<div class="write-panel">
    <h2>พิจารณาผลงาน</h2>
    <p>ต้นฉบับที่รอตรวจจะขึ้นก่อน อนุมัติแล้วจะปรากฏในห้องสมุด</p>
    <div id="rv-msg" hidden></div>
    <h3>รอพิจารณา (${pending.length})</h3>
    <ul class="sub-list">${pending.map(card).join('')||'<li><p>ไม่มีต้นฉบับรอตรวจ</p></li>'}</ul>
    <h3>ทั้งหมด</h3>
    <ul class="sub-list">${others.map(card).join('')||'<li><p>ยังไม่มีรายการอื่น</p></li>'}</ul>
  </div>`;
  bindSignOut(root);
  root.querySelectorAll('.review-form').forEach(form => {
    let act='approved';
    form.querySelectorAll('[data-act]').forEach(b => b.addEventListener('click', ()=>{ act=b.getAttribute('data-act'); }));
    form.addEventListener('submit', async ev => {
      ev.preventDefault();
      const id = form.closest('[data-id]').getAttribute('data-id');
      const review_note = form.review_note.value.trim();
      const { error } = await sb.from('submissions').update({ status: act, review_note }).eq('id', id);
      msg($('#rv-msg', root), error?error.message:'บันทึกแล้ว', !error);
      if(!error) pageReview(root);
    });
  });
}

async function fillLibraryFeed(){
  const host = document.getElementById('community-list');
  if(!host) return;
  const { data, error } = await sb.from('submissions').select('id,title,slug,category,author_name,author_affiliation,cover_path,published_at').eq('status','approved').order('published_at',{ascending:false});
  if(error || !data || !data.length) return;
  host.hidden = false;
  host.innerHTML = `<div class="section-head"><p class="eyebrow">จากบุคลากรในเครือข่าย</p><h2>งานเขียนที่เผยแพร่จากผู้ร่วมส่ง</h2></div>
    <div class="article-list">${data.map(r => `<article class="card article-card">
      ${r.cover_path?`<img src="${esc(coverUrl(r.cover_path))}" alt="" width="800" height="450" loading="lazy">`:''}
      <span class="tag tag--blue">${esc(CAT[r.category]||r.category)}</span>
      <h3>${esc(r.title)}</h3>
      <p class="small muted">เขียนโดย ${esc(r.author_name||'')}${r.author_affiliation?' · '+esc(r.author_affiliation):''}</p>
      <a class="more" href="/library/w/${esc(r.slug)}/">อ่านต่อ</a>
    </article>`).join('')}</div>`;
}

async function pageRead(root){
  const parts = location.pathname.replace(/\/+$/,'').split('/');
  const slug = parts[parts.length-1];
  if(!slug || slug==='w'){ root.innerHTML = '<p>ไม่พบบทความ</p>'; return; }
  const { data, error } = await sb.from('submissions').select('id,title,slug,body,cover_path,category,author_name,author_affiliation,author_title,published_at').eq('slug', slug).eq('status','approved').maybeSingle();
  if(error || !data){ root.innerHTML = '<p>ไม่พบบทความนี้ หรือยังไม่ได้รับการเผยแพร่</p>'; return; }
  document.title = data.title + ' | ห้องสมุด เครือข่ายการศึกษาปาตารายอ';
  const desc = document.querySelector('meta[name="description"]');
  if(desc) desc.setAttribute('content', data.title);
  root.innerHTML = `<article class="article">
    <p><a href="/library/">กลับไปห้องสมุด</a></p>
    <span class="tag tag--blue">${esc(CAT[data.category]||data.category)}</span>
    <h1>${esc(data.title)}</h1>
    <p class="byline"><span>เขียนโดย ${esc(data.author_name||'')}</span>
      ${data.author_title||data.author_affiliation?`<span>${esc([data.author_title,data.author_affiliation].filter(Boolean).join(' · '))}</span>`:''}</p>
    ${data.cover_path?`<figure class="band"><img src="${esc(coverUrl(data.cover_path))}" alt=""></figure>`:''}
    <div class="md">${md(data.body)}</div>
  </article>`;
}

function bindLoginCheck(){
  const root = document.getElementById('write-app');
  const mode = root && root.getAttribute('data-mode');
  if(mode==='write') return pageWrite(root);
  if(mode==='mine') return pageMine(root);
  if(mode==='review') return pageReview(root);
  if(mode==='read') return pageRead(root);
}

document.addEventListener('DOMContentLoaded', () => {
  bindLoginCheck();
  fillLibraryFeed();
});
