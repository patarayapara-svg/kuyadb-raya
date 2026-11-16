import sys
from playwright.sync_api import sync_playwright
B=sys.argv[1]; OUT=sys.argv[2]
UA='Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0 Mobile Safari/537.36'
with sync_playwright() as p:
    br=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for w,h in [(360,800),(412,915)]:
        pg=br.new_context(viewport={'width':w,'height':h},device_scale_factor=2.625,is_mobile=True,has_touch=True,user_agent=UA).new_page()
        for path,name in [('/','home'),('/about/','about'),('/honors/','honors'),('/programs/','programs'),('/contact/','contact')]:
            pg.goto(B+path,wait_until='networkidle')
            r=pg.evaluate("""()=>{const W=document.documentElement.clientWidth;let wide=[];document.querySelectorAll('main *').forEach(e=>{const b=e.getBoundingClientRect();if(b.width>0&&(b.right>W+1))wide.push(e.tagName+'.'+e.className)});
            const cols=[...document.querySelectorAll('.grid2,.grid3,.rooms,.honors,.gallery,.hero .grid,.shelves')].map(g=>getComputedStyle(g).gridTemplateColumns.split(' ').length);
            return {W,sw:document.documentElement.scrollWidth,maxcols:Math.max(0,...cols),wide:[...new Set(wide)].slice(0,5)}}""")
            print(w,path,r)
            if w==360 and name in('home','about','honors'):
                pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))"); pg.wait_for_timeout(500)
                pg.screenshot(path=f'{OUT}/android-{name}.png',full_page=True)
    br.close()
