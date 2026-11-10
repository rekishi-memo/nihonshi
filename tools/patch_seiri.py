# 一度きりのパッチ（2026-11-10）：「整理する」のカードの見た目、授業のあいだを飛ぶボタン（.jump）、「もとの授業にもどる」ボタン。
#   python3 patch_seiri.py ../app/source.html
import sys
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
if 'id="backBtn"' in s: sys.exit('already patched')
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)
rep("  .navbtns{display:flex;gap:9px;margin-top:9px;}","""  .navbtns{display:flex;gap:9px;margin-top:9px;}
  /* ---- 整理する：付箋のようなカード（明るい紙に、黒と赤の字） ---- */
  #lBody .mm{background:#d7ebf5;color:#1b2230;border-radius:5px;padding:14px 13px 13px;margin:18px 0;box-shadow:3px 4px 0 rgba(0,0,0,.4);font-family:var(--gothic);font-size:13.5px;line-height:1.7;scroll-margin-top:70px;}
  #lBody .mm.g{background:#dcefd0;} #lBody .mm.y{background:#f5edc0;}
  #lBody .mm h4{font-size:15.5px;font-weight:800;margin:0 0 10px;padding-bottom:6px;border-bottom:2px solid #1b2230;color:#1b2230;letter-spacing:.02em;}
  #lBody .mm .k{color:#c0281f;font-weight:700;}
  #lBody .mm p{margin:7px 0;color:#1b2230;font-size:13px;line-height:1.7;}
  #lBody .mm .sm{font-size:11.5px;color:#3d4960;}
  #lBody .mm .pp{border-left:3px solid #c0281f;padding-left:8px;}
  #lBody .mm .lb{display:inline-block;background:#1b2230;color:#fff;border-radius:4px;padding:0 7px;font-size:11.5px;font-weight:700;margin-right:7px;}
  #lBody .mm .lbp{margin-top:11px;}
  #lBody .mm .vch{display:flex;flex-direction:column;align-items:stretch;gap:2px;margin:7px 0;}
  #lBody .mm .hch{display:flex;flex-wrap:wrap;align-items:center;gap:4px 5px;margin:7px 0;}
  #lBody .mm .bx{border:1.5px solid #1b2230;border-radius:7px;padding:4px 9px;background:rgba(255,255,255,.5);font-size:13px;line-height:1.55;}
  #lBody .mm .ar{color:#c0281f;font-size:11.5px;font-weight:700;padding:0 4px;}
  #lBody .mm .vch .ar{padding:1px 12px;}
  #lBody .mm .rt{font-weight:700;margin-top:9px;}
  #lBody .mm .tr{margin:4px 0 8px 7px;border-left:2px solid #c0281f;}
  #lBody .mm .tr>div{position:relative;padding:3px 0 3px 24px;font-size:13px;line-height:1.6;}
  #lBody .mm .tr>div:before{content:"→";position:absolute;left:3px;top:3px;color:#c0281f;font-weight:700;}
  #lBody .mm .tw{overflow-x:auto;margin:7px 0;}
  #lBody .mm table{width:100%;border-collapse:collapse;font-size:12.5px;line-height:1.5;}
  #lBody .mm th,#lBody .mm td{border:1px solid rgba(27,34,48,.6);padding:4px 6px;vertical-align:top;text-align:left;color:#1b2230;}
  #lBody .mm th{background:rgba(27,34,48,.12);font-weight:700;white-space:nowrap;}
  #lBody .mm td:first-child{font-weight:700;}
  #lBody .mm.hl-jump{outline:3px solid var(--gold-bright);outline-offset:3px;background-image:none;animation:none;}
  #lBody .mm .mm-go{margin-top:10px;text-align:right;}
  #lBody .mm .jump{border-color:#1b2230;color:#1b2230;background:rgba(255,255,255,.55);}
  .seiri-intro{font-size:12.5px;color:var(--ash);}
  .jump{display:inline-block;margin:8px 6px 0 0;font-family:var(--gothic);font-size:12px;font-weight:600;line-height:1.4;text-align:left;color:var(--gold-bright);background:transparent;border:1px solid var(--line);border-radius:9px;padding:7px 10px;cursor:pointer;}
  .jump:active{filter:brightness(.85);}
  .recall .jump{display:block;border-color:#7fb0d8;color:#a9cdea;}
  .seiri-link{margin:18px 0 6px;padding:11px 13px;border:1px dashed var(--gold);border-radius:12px;}
  .seiri-link .bx-tag{background:var(--gold);color:#1a140a;}
  #backBtn{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(14px + env(safe-area-inset-bottom));z-index:60;font-family:var(--gothic);font-size:13px;font-weight:700;color:#1a140a;
    background:linear-gradient(180deg,var(--gold-bright),var(--gold));border:none;border-radius:22px;padding:10px 18px;box-shadow:0 4px 14px rgba(0,0,0,.5);cursor:pointer;white-space:nowrap;}""")
rep("""  <nav class="sectabs" id="secTabs" role="tablist"></nav>""","""  <nav class="sectabs" id="secTabs" role="tablist"></nav>
  <button id="backBtn" class="hidden">← もとの授業にもどる</button>""")
rep("""tmp.querySelectorAll("details,.point,.yodan,.recall,.flow,""","""tmp.querySelectorAll("details,.point,.yodan,.recall,.flow,.seiri-link,.mm,.jump,.seiri-intro,""")
rep("""document.getElementById("todayExit").addEventListener""","""/* ---- 授業のあいだを飛ぶ（「ここで思い出そう」→ その授業、授業 →「整理する」のカード）と、もどる ---- */
let backStack=[];
function showBack(){ document.getElementById("backBtn").classList.toggle("hidden",!backStack.length); }
document.addEventListener("click",async e=>{ const b=e.target.closest(".jump"); if(!b) return;
  const pid=b.dataset.p, src=b.dataset.s, mark=b.dataset.m||"", p=packsById[pid]; if(!p) return;
  const idx=p.lessons.findIndex(l=>(l.src||(pid+"-"+l.no))===src); if(idx<0) return;
  backStack.push({p:activeId,i:lIdx,y:window.scrollY}); if(backStack.length>12) backStack.shift();
  if(pid!==activeId) await goPack(pid,idx); else showLesson(idx);
  if(activeSec!=="lesson") switchSec("lesson"); showBack();
  setTimeout(()=>{ const body=document.getElementById("lBody"); let el=null;
    if(mark){ el=body.querySelector('[data-card="'+mark+'"]'); if(el) el.classList.add("hl-jump"); else el=highlightInBody(body,mark); }
    if(el) el.scrollIntoView({behavior:"smooth",block:el.classList.contains("mm")?"start":"center"}); else toLessonTop(); },140);
});
document.getElementById("backBtn").addEventListener("click",async()=>{ const s0=backStack.pop(); if(!s0){showBack();return;}
  if(s0.p!==activeId) await goPack(s0.p,s0.i); else showLesson(s0.i);
  if(activeSec!=="lesson") switchSec("lesson"); showBack(); setTimeout(()=>window.scrollTo(0,s0.y),60); });
document.getElementById("todayExit").addEventListener""")
rep("""document.getElementById("packSel").addEventListener("change",async e=>{exitToday();""","""document.getElementById("packSel").addEventListener("change",async e=>{backStack=[];showBack();exitToday();""")
open(f,'w',encoding='utf-8').write(s); print('patched')
