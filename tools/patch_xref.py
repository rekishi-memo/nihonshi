#!/usr/bin/env python3
"""授業本文の「（授業06）」「（近代②）」「近代④ 授業03」「テーマ史：貨幣史」を、タップでその授業に飛べるボタンにする（1回だけ当てるパッチ）。
   本文のデータは変えず、授業を表示するときに画面の上で置きかえる（linkRefs）。
   セットだけが書いてあるとき（近代②）は、その文に出てくる語がいちばん多く出る授業をえらび、その語を光らせる。
   「▶」で始まる段落は「くわしくはこの授業へ」の案内として枠をつける。
   使い方: python3 patch_xref.py ../app/source.html"""
import sys
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
if 'function linkRefs(' in s: print('already'); sys.exit()
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)

CSS='''  .xref{font:inherit;color:var(--gold-bright);background:none;border:0;border-bottom:1px dashed var(--gold-bright);padding:0 1px;margin:0;cursor:pointer;-webkit-tap-highlight-color:rgba(255,220,130,.25);}
  .xref::after{content:"\\2197";font-size:.72em;margin-left:1px;}
  #lBody p.xhint{font-size:11.5px;line-height:1.6;opacity:.85;border-left:2px solid var(--gold-bright);padding:1px 0 1px 9px;margin-bottom:14px;}
  #lBody p.more{border:1px solid var(--line);border-radius:10px;padding:9px 12px;font-size:13.5px;line-height:1.75;}
'''
rep('  .recall .jump{', CSS+'  .recall .jump{')

JS='''/* ---- 本文の（授業06）（近代②）を、タップでその授業に飛べるようにする ---- */
const _plainCache=new Map();
function lessonPlain(pid,i){ const k=pid+"|"+i; let t=_plainCache.get(k);
  if(t==null){ const l=packsById[pid].lessons[i]; t=(l.title||"")+" "+(l.html||"").replace(/<rt>.*?<\\/rt>/g,"").replace(/<[^>]+>/g,""); _plainCache.set(k,t); } return t; }
function packByLabel(lb){ return packOrder.find(id=>packsById[id].title.indexOf(lb)===0)||null; }
function xrefTarget(pid,no,ctx){ const p=packsById[pid]; if(!p||!p.lessons.length) return null;
  if(no){ const i=p.lessons.findIndex(l=>String(l.no)===no); return i<0?null:{i:i,m:""}; }
  const ws=(ctx.match(/[一-龥々ァ-ヶー]{3,}/g)||[]).slice(-7); let best=0,bs=0,bm="";
  p.lessons.forEach((l,i)=>{ const t=lessonPlain(pid,i); let sc=0,m="";
    ws.forEach((w,k)=>{ if(t.indexOf(w)>=0){ sc+=1+k*0.15+w.length*0.05; m=w; } }); if(sc>bs){bs=sc;best=i;bm=m;} });
  return {i:best,m:bm}; }
function linkRefs(body){
  const XRE=/(古代|中世|近世|近代|現代)([①-⑩])((?:・[①-⑩])*)(?:[・ 　の]*授業(\\d{2}))?|テーマ史[：〈]([^（）〉・、。]+)〉?|授業(\\d{2})((?:・\\d{2})*)/g;
  const w=document.createTreeWalker(body,NodeFilter.SHOW_TEXT,null), nodes=[]; let n, cnt=0;
  while(n=w.nextNode()){ if(n.parentNode.closest("button,rt,h4,.mm,svg")) continue; XRE.lastIndex=0; if(XRE.test(n.nodeValue)) nodes.push(n); }
  nodes.forEach(node=>{ const s=node.nodeValue, frag=document.createDocumentFragment(); let last=0,m,pre="";
    try{ const blk=node.parentNode.closest("p,li,div")||body, rg=document.createRange(); rg.setStart(blk,0); rg.setEnd(node,0); pre=rg.toString().slice(-70); }catch(e){}
    const tx=t=>frag.appendChild(document.createTextNode(t));
    const mk=(txt,pid,no,ctx)=>{ const t=pid?xrefTarget(pid,no,ctx):null; if(!t){tx(txt);return;}
      const b=document.createElement("button"), L=packsById[pid].lessons[t.i]; b.type="button"; b.className="xref"; b.textContent=txt;
      b.dataset.p=pid; b.dataset.i=t.i; b.dataset.m=t.m||""; b.setAttribute("aria-label",txt+"「"+(L.title||"")+"」へ飛ぶ"); frag.appendChild(b); cnt++; };
    XRE.lastIndex=0;
    while(m=XRE.exec(s)){ tx(s.slice(last,m.index)); const ctx=pre+s.slice(0,m.index);
      if(m[1]){ const pid=packByLabel(m[1]+m[2]);
        if(m[4]) mk(m[0],pid,m[4],ctx);
        else { mk(m[1]+m[2],pid,null,ctx); (m[3]||"").split("・").filter(Boolean).forEach(c=>{ tx("・"); mk(c,packByLabel(m[1]+c),null,ctx); }); } }
      else if(m[5]) mk(m[0],packByLabel("テーマ史："+m[5]),null,ctx);
      else { mk("授業"+m[6],activeId,m[6],ctx); (m[7]||"").split("・").filter(Boolean).forEach(c=>{ tx("・"); mk(c,activeId,c,ctx); }); }
      last=m.index+m[0].length; }
    tx(s.slice(last)); node.parentNode.replaceChild(frag,node); });
  body.querySelectorAll("p").forEach(p=>{ if(/^\\s*▶/.test(p.textContent)) p.classList.add("more"); });
  if(cnt){ const h=document.createElement("p"); h.className="xhint"; h.textContent="金色の点線の「授業06」「近代②」などは、タップするとその授業に飛べる。もどるときは「← もとの授業にもどる」を押す。"; body.insertBefore(h,body.firstChild); }
  return cnt; }
document.addEventListener("click",async e=>{ const b=e.target.closest(".xref"); if(!b) return; e.preventDefault();
  const pid=b.dataset.p, idx=+b.dataset.i, mark=b.dataset.m||""; if(!packsById[pid]) return;
  backStack.push({p:activeId,i:lIdx,y:window.scrollY}); if(backStack.length>12) backStack.shift();
  if(pid!==activeId) await goPack(pid,idx); else showLesson(idx);
  if(activeSec!=="lesson") switchSec("lesson"); showBack();
  setTimeout(()=>{ const body=document.getElementById("lBody"); const el=mark?highlightInBody(body,mark):null;
    if(el) el.scrollIntoView({behavior:"smooth",block:"center"}); else toLessonTop(); },140); });
'''
rep('/* ---- 授業のあいだを飛ぶ（「ここで思い出そう」→ その授業、授業 →「整理する」のカード）と、もどる ---- */', JS+'/* ---- 授業のあいだを飛ぶ（「ここで思い出そう」→ その授業、授業 →「整理する」のカード）と、もどる ---- */')
rep('''document.getElementById("lBody").innerHTML=l.html||""; applyRanks(document.getElementById("lBody"),p);''',
    '''document.getElementById("lBody").innerHTML=l.html||""; applyRanks(document.getElementById("lBody"),p); linkRefs(document.getElementById("lBody"));''')
open(f,'w',encoding='utf-8').write(s); print('patched')
