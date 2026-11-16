document.documentElement.classList.add('js');
(function(){
  var d=document,b=d.querySelector('.nav-toggle'),n=d.getElementById('main-nav'),h=d.querySelector('.site-header');
  var tops=[].slice.call(d.querySelectorAll('.has-sub>.top'));
  var mq=window.matchMedia('(max-width:1099px)');
  function closeSubs(except){tops.forEach(function(t){if(t!==except)t.setAttribute('aria-expanded','false');});}
  function setMenu(o){if(!n)return;n.classList.toggle('open',o);b&&b.setAttribute('aria-expanded',o?'true':'false');if(!o)closeSubs();}
  b&&b.addEventListener('click',function(){setMenu(!n.classList.contains('open'));});
  tops.forEach(function(t){
    t.addEventListener('click',function(){var o=t.getAttribute('aria-expanded')!=='true';closeSubs(t);t.setAttribute('aria-expanded',o?'true':'false');});
    var li=t.parentNode,timer;
    li.addEventListener('mouseenter',function(){if(mq.matches)return;clearTimeout(timer);closeSubs(t);t.setAttribute('aria-expanded','true');});
    li.addEventListener('mouseleave',function(){if(mq.matches)return;timer=setTimeout(function(){t.setAttribute('aria-expanded','false');},180);});
    li.addEventListener('focusout',function(e){if(!mq.matches&&!li.contains(e.relatedTarget))t.setAttribute('aria-expanded','false');});
  });
  d.addEventListener('keydown',function(e){
    if(e.key!=='Escape')return;
    var open=tops.filter(function(t){return t.getAttribute('aria-expanded')==='true';})[0];
    if(open){open.setAttribute('aria-expanded','false');open.focus();}
    else if(n&&n.classList.contains('open')){setMenu(false);b.focus();}
  });
  d.addEventListener('click',function(e){if(h&&!h.contains(e.target)){closeSubs();if(mq.matches)setMenu(false);}});
  if(mq.matches){var cur=d.querySelector('.has-sub.is-active>.top');}
  var chrome=d.querySelector('.chrome');
  var onS=function(){var on=window.scrollY>8;h&&h.classList.toggle('scrolled',on);chrome&&chrome.classList.toggle('scrolled',on);};onS();window.addEventListener('scroll',onS,{passive:true});
  var sb=d.querySelector('.subbar .wrap');
  if(sb){
    var cue=function(){var max=sb.scrollWidth-sb.clientWidth; if(max<=4){sb.className=sb.className.replace(/is-start|is-end|is-middle/g,'').trim();return;} var x=sb.scrollLeft; sb.classList.remove('is-start','is-end','is-middle'); if(x<8) sb.classList.add('is-start'); else if(x>max-8) sb.classList.add('is-end'); else sb.classList.add('is-middle');};
    sb.addEventListener('scroll',cue,{passive:true}); cue();
  }
  if('IntersectionObserver' in window&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    var els=[].slice.call(d.querySelectorAll('main .section .section-head, main .card, main .room-card, main .honor, main .shelf, main .photo, main .qrcard, main .timeline li'));
    var vh=window.innerHeight;
    els=els.filter(function(el){return el.getBoundingClientRect().top>vh;});
    if(els.length){
      d.documentElement.classList.add('rv-on');
      var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});},{rootMargin:'0px 0px -8% 0px'});
      els.forEach(function(el){el.classList.add('rv');io.observe(el);});
    }
  }
})();
