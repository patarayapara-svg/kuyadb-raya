import sys,asyncio
from playwright.sync_api import sync_playwright
B=sys.argv[1]; OUT=sys.argv[2]
with sync_playwright() as p:
    br=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    def pg(w,h,mob=False):
        c=br.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=mob,has_touch=mob); return c.new_page()
    def full(page,path,name):
        page.goto(B+path,wait_until='networkidle')
        page.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
        page.wait_for_timeout(700); page.screenshot(path=f'{OUT}/{name}.png',full_page=True)
    d=pg(1440,900)
    for path,name in [('/','home-desktop'),('/about/','about-desktop'),('/honors/','honors-desktop'),('/library/','library-desktop'),('/raya-hub/','lab-desktop'),('/contact/','contact-desktop'),('/news/','news-desktop')]:
        full(d,path,name)
    d.goto(B+'/',wait_until='networkidle'); d.hover('.has-sub:nth-child(2)>.top'); d.wait_for_timeout(400); d.screenshot(path=f'{OUT}/menu-desktop-dropdown.png')
    d.mouse.move(5,800); d.wait_for_timeout(400); d.focus('.has-sub:nth-child(4)>.top'); d.keyboard.press('Enter'); d.wait_for_timeout(400); d.screenshot(path=f'{OUT}/menu-desktop-keyboard.png')
    t=pg(820,1180,True); full(t,'/','home-tablet')
    m=pg(390,844,True)
    for path,name in [('/','home-mobile'),('/about/','about-mobile'),('/honors/','honors-mobile'),('/library/','library-mobile'),('/contact/','contact-mobile')]:
        full(m,path,name)
    m.goto(B+'/about/',wait_until='networkidle'); m.tap('.nav-toggle'); m.wait_for_timeout(300); m.screenshot(path=f'{OUT}/menu-mobile-open.png')
    m.tap('.has-sub:nth-child(4)>.top'); m.wait_for_timeout(300); m.screenshot(path=f'{OUT}/menu-mobile-accordion.png')
    br.close()
