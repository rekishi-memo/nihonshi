# 一度きりのパッチ（2026-11-10）：整理カードを「白っぽい灰色の地に黒と赤字」にし、
# 「整理する」のセットの一問一答タブを赤シート（赤い語をかくして、タップでめくる）にする。
#   python3 patch_aka.py ../app/source.html
import sys,re
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
if 'id="akaWrap"' in s: sys.exit('already patched')
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:70]); s=s.replace(a,b)
a=s.index("  /* ---- 整理する：カード"); b=s.index("  .seiri-intro{")
css='''  /* ---- 整理する：カード（白っぽい灰色の地に、黒と赤の字）。#akaBody は赤シート用 ---- */
  :is(#lBody,#akaBody) .mm{background:#eceef1;color:#1b2230;border-radius:10px;padding:15px 14px 14px;margin:18px 0;font-family:var(--gothic);font-size:13.5px;line-height:1.7;scroll-margin-top:70px;}
  :is(#lBody,#akaBody) .mm h4{font-size:15.5px;font-weight:800;margin:0 0 10px;padding-bottom:7px;border-bottom:2px solid #1b2230;color:#1b2230;letter-spacing:.02em;}
  :is(#lBody,#akaBody) .mm .k{color:#c62a20;font-weight:700;}
  :is(#lBody,#akaBody) .mm p{margin:7px 0;color:#1b2230;font-size:13px;line-height:1.7;}
  :is(#lBody,#akaBody) .mm .sm{font-size:11.5px;color:#4a5568;}
  :is(#lBody,#akaBody) .mm .pp{border-left:3px solid #c62a20;padding-left:9px;}
  :is(#lBody,#akaBody) .mm .lb{display:inline-block;background:#1b2230;color:#fff;border-radius:4px;padding:0 7px;font-size:11.5px;font-weight:700;margin-right:7px;}
  :is(#lBody,#akaBody) .mm .lbp{margin-top:12px;}
  :is(#lBody,#akaBody) .mm .vch{display:flex;flex-direction:column;align-items:stretch;gap:2px;margin:7px 0;}
  :is(#lBody,#akaBody) .mm .hch{display:flex;flex-wrap:wrap;align-items:center;gap:4px 5px;margin:7px 0;}
  :is(#lBody,#akaBody) .mm .bx{border:1.5px solid #1b2230;border-radius:8px;padding:5px 10px;background:#fff;font-size:13px;line-height:1.55;}
  :is(#lBody,#akaBody) .mm .ar{color:#c62a20;font-size:11.5px;font-weight:700;padding:0 4px;}
  :is(#lBody,#akaBody) .mm .vch .ar{padding:1px 12px;}
  :is(#lBody,#akaBody) .mm .rt{font-weight:700;margin-top:10px;color:#1b2230;}
  :is(#lBody,#akaBody) .mm .tr{margin:4px 0 8px 7px;border-left:2px solid #c62a20;}
  :is(#lBody,#akaBody) .mm .tr>div{position:relative;padding:3px 0 3px 24px;font-size:13px;line-height:1.6;}
  :is(#lBody,#akaBody) .mm .tr>div:before{content:"→";position:absolute;left:4px;top:3px;color:#c62a20;font-weight:700;}
  :is(#lBody,#akaBody) .mm .tw{overflow-x:auto;margin:7px 0;}
  :is(#lBody,#akaBody) .mm table{width:100%;border-collapse:collapse;font-size:12.5px;line-height:1.5;background:#fff;}
  :is(#lBody,#akaBody) .mm th,:is(#lBody,#akaBody) .mm td{border:1px solid #8a93a3;padding:5px 7px;vertical-align:top;text-align:left;color:#1b2230;}
  :is(#lBody,#akaBody) .mm th{background:#d9dde3;font-weight:700;white-space:nowrap;}
  :is(#lBody,#akaBody) .mm td:first-child{font-weight:700;min-width:4.3em;}
  #lBody .mm.hl-jump{outline:3px solid var(--gold-bright);outline-offset:3px;background-image:none;animation:none;}
  #lBody .mm .mm-go{margin-top:10px;text-align:right;}
  #lBody .mm .jump{border-color:#1b2230;color:#1b2230;background:#fff;}
  /* 赤シート：赤い語をぬりつぶし、タップでめくる */
  #akaBody .mm .k{color:transparent;background:#c62a20;border-radius:3px;cursor:pointer;-webkit-user-select:none;user-select:none;}
  #akaBody .mm .k.open{color:#c62a20;background:transparent;}
  .aka-bar{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:10px;padding:9px 12px;border:1px solid var(--line);border-radius:11px;font-family:var(--gothic);font-size:12.5px;color:var(--gold);}
  .aka-bar span{flex:1;min-width:9em;}
  .aka-bar button{font-family:var(--gothic);font-size:11.5px;color:var(--ivory-dim);background:transparent;border:1px solid var(--line);border-radius:8px;padding:6px 9px;cursor:pointer;}
'''
s=s[:a]+css+s[b:]
rep("""    <div id="quizWrap">""","""    <div id="akaWrap" class="hidden">
      <div class="aka-bar"><span id="akaCnt">赤シート</span><button id="akaHide">全部かくす</button><button id="akaShow">全部めくる</button></div>
      <div class="lesson-nav" id="akaNav"></div>
      <div id="akaBody"></div>
    </div>
    <div id="quizWrap">""")
# renderQuizSection を作り直す
i=s.index("function renderQuizSection(){"); j=s.index("function startRun(){")
new='''function quizVis(v){ document.getElementById("quizWrap").classList.toggle("hidden",!v); document.querySelector("#sec-quiz .stats").style.display=v?"flex":"none"; document.querySelector("#sec-quiz .bar").style.display=v?"block":"none"; }
function renderQuizSection(){
  const p=cur(), emp=document.getElementById("quizEmpty"), aw=document.getElementById("akaWrap");
  aw.classList.add("hidden"); emp.classList.add("hidden");
  if(today){ quizVis(true); buildUnitOptions(); if(queue.length&&pos<queue.length) showCard(); else showDone(!queue.length); return; }
  if(p.id==="seiri"){ quizVis(false); renderAka(); return; }   /* 「整理する」は一問一答のかわりに赤シート */
  if(!p.quiz.length){ quizVis(false); emp.classList.remove("hidden"); emp.innerHTML="このセットの<b>一問一答</b>はまだ準備中。"; return; }
  quizVis(true); buildUnitOptions(); startRun();
}
/* ---- 赤シート（整理カードの赤い語をかくす。タップでめくる） ---- */
let akaIdx=0;
function akaCount(){ const all=document.querySelectorAll("#akaBody .k").length, op=document.querySelectorAll("#akaBody .k.open").length;
  document.getElementById("akaCnt").textContent=`赤シート：赤い所をタップでめくる（${op} / ${all}）`; }
function renderAka(){
  const p=cur(), nav=document.getElementById("akaNav"), body=document.getElementById("akaBody");
  document.getElementById("akaWrap").classList.remove("hidden");
  if(akaIdx>=p.lessons.length) akaIdx=0;
  nav.innerHTML=""; p.lessons.forEach((l,i)=>{ const b=document.createElement("button"); b.className="chip"; b.setAttribute("aria-current",i===akaIdx?"true":"false");
    b.innerHTML=`<span class="cno">${l.no||(i+1)}</span>${l.navTitle||l.title}`; b.addEventListener("click",()=>{akaIdx=i;renderAka();}); nav.appendChild(b); });
  const tmp=document.createElement("div"); tmp.innerHTML=p.lessons[akaIdx].html||"";
  tmp.querySelectorAll(".jump,.mm-go,.seiri-intro,.flow,.seiri-link").forEach(x=>x.remove());
  body.innerHTML=tmp.innerHTML; akaCount();
}
document.addEventListener("click",e=>{ const k=e.target.closest("#akaBody .k"); if(!k) return; k.classList.toggle("open"); akaCount(); });
'''
s=s[:i]+new+s[j:]
rep("""document.getElementById("todayExit").addEventListener("click",()=>{ if(today){todayOff=true;startRun();} else {todayOff=false;startToday(todayCount()===0);} });""",
"""document.getElementById("todayExit").addEventListener("click",()=>{ if(today){todayOff=true;exitToday();renderQuizSection();} else {todayOff=false;startToday(todayCount()===0);} });
document.getElementById("akaHide").addEventListener("click",()=>{document.querySelectorAll("#akaBody .k").forEach(k=>k.classList.remove("open"));akaCount();});
document.getElementById("akaShow").addEventListener("click",()=>{document.querySelectorAll("#akaBody .k").forEach(k=>k.classList.add("open"));akaCount();});""")
rep("""  if(k==="quiz"&&!today&&!todayOff&&todayCount()>0) startToday(false);""","""  if(k==="quiz"&&!today&&!todayOff&&activeId!=="seiri"&&todayCount()>0) startToday(false);""")
rep("""  today=true; queue=t.due.concat(t.nw); pos=0; revealed=false; run={correct:0,total:0};""","""  today=true; queue=t.due.concat(t.nw); pos=0; revealed=false; run={correct:0,total:0};
  document.getElementById("akaWrap").classList.add("hidden"); document.getElementById("quizEmpty").classList.add("hidden"); quizVis(true);""")
open(f,'w',encoding='utf-8').write(s); print('patched')
