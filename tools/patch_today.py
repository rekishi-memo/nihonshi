# 一度きりのパッチ（2026-11-09）：「今日のぶん」（全範囲・間隔をあけた復習）、「最頻出／頻出」だけの絞りこみ、
# 授業の「次へ」がセットをまたいで続く、の3つを app/source.html に入れる。2回目は何もしない。
#   python3 patch_today.py ../app/source.html
import sys
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
if 'id="todayBtn"' in s: sys.exit('already patched')
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:60])
    s=s.replace(a,b)

# ---------- CSS ----------
rep("  .navbtns{display:flex;gap:9px;margin-top:9px;}",
"""  .navbtns{display:flex;gap:9px;margin-top:9px;}
  .today-btn{display:flex;align-items:center;justify-content:space-between;gap:10px;width:100%;margin:0 0 12px;padding:13px 15px;border:none;border-radius:13px;cursor:pointer;
    font-family:var(--gothic);font-size:15px;font-weight:700;color:#1a140a;background:linear-gradient(180deg,var(--gold-bright),var(--gold));text-align:left;}
  .today-btn small{font-size:11.5px;font-weight:500;opacity:.8;white-space:nowrap;}
  .today-btn:active{filter:brightness(.92);}
  .today-bar{display:none;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px;padding:9px 12px;border:1px solid var(--line);border-radius:11px;font-family:var(--gothic);font-size:12.5px;color:var(--gold);}
  .today-bar button{font-family:var(--gothic);font-size:11.5px;color:var(--ivory-dim);background:transparent;border:1px solid var(--line);border-radius:8px;padding:6px 9px;cursor:pointer;}
  .is-today .today-bar{display:flex;}
  .is-today .modes,.is-today .row2{display:none;}
  .rate .kx{color:var(--gold);font-weight:700;}""")

# ---------- HTML ----------
rep("""  <nav class="sectabs" id="secTabs" role="tablist"></nav>""",
"""  <button class="today-btn" id="todayBtn"><span>今日のぶん</span><small id="todayCnt"></small></button>
  <nav class="sectabs" id="secTabs" role="tablist"></nav>""")
rep("""        <button data-mode="important" aria-pressed="false">重要 ★4+</button>""",
"""        <button data-mode="top" aria-pressed="false">最頻出</button>
        <button data-mode="freq" aria-pressed="false">頻出</button>""")
rep("""      <div class="modes" role="group">""",
"""      <div class="today-bar" id="todayBar"><span>今日のぶん（全範囲から）</span><button id="todayExit">ふつうの一問一答へ</button></div>
      <div class="modes" role="group">""")

# ---------- JS: 記録（セットを指定できるように） ----------
rep("""function rec(id){ const pp=prog[activeId]||{}; return pp[id]||{c:0,w:0,last:null}; }
async function setRec(id,r){ if(!prog[activeId])prog[activeId]={}; prog[activeId][id]=r; await sSet(PROG_KEY,prog); }""",
"""function rec(id,pid){ const pp=prog[pid||activeId]||{}; return pp[id]||{c:0,w:0,last:null}; }
async function setRec(id,r,pid){ pid=pid||activeId; if(!prog[pid])prog[pid]={}; prog[pid][id]=r; await sSet(PROG_KEY,prog); }
/* ---- 今日のぶん：全範囲から、忘れかけの復習＋新しい問題（過去問でよく出る順） ----
   記録 r に d（次に出す日）と iv（間隔・日）を足す。○で間隔が 1→3→7→14→30→60 日とのび、×で翌日にもどる。
   その日の新しい問題は prog._today に覚えておく（開き直しても増えない）。 */
const SRS=[1,3,7,14,30,60], NEW_PER_DAY=20, DUE_MAX=80;
let today=false;
function DAY(){ const d=new Date(); return Math.floor((d.getTime()-d.getTimezoneOffset()*60000)/864e5); }
function qScore(q){ return Math.min(q.x||0,3)*10+(q.f||0); }
function todayItems(more){
  const day=DAY(); let st=prog._today; if(!st||st.day!==day) st={day:day,nw:[]};
  const due=[], fresh=[], inNw=new Set(st.nw.map(x=>x[0]+"|"+x[1]));
  packOrder.forEach(pid=>{ const p=packsById[pid], pp=prog[pid]||{};
    p.quiz.forEach(q=>{ const r=pp[q.id];
      if(r&&(r.c+r.w)>0){ const weak=r.last==="×"||r.w>r.c;
        if(!inNw.has(pid+"|"+q.id)&&((r.d!=null&&r.d<=day)||(r.d==null&&weak))) due.push({p:pid,id:q.id,d:r.d==null?-1:r.d}); }
      else if(pid.indexOf("theme_")!==0&&!inNw.has(pid+"|"+q.id)) fresh.push({p:pid,id:q.id,s:qScore(q)});
    }); });
  due.sort((a,b)=>a.d-b.d); const dueCut=shuffle(due.slice(0,DUE_MAX));
  if(!st.nw.length||more){ shuffle(fresh); fresh.sort((a,b)=>b.s-a.s); fresh.slice(0,NEW_PER_DAY).forEach(x=>st.nw.push([x.p,x.id])); }
  prog._today=st;
  const nw=st.nw.filter(x=>{const r=(prog[x[0]]||{})[x[1]]; return packsById[x[0]]&&!(r&&(r.c+r.w)>0);}).map(x=>({p:x[0],id:x[1]}));
  return {due:dueCut,dueAll:due.length,nw:nw};
}
function todayCount(){ const t=todayItems(false); const el=document.getElementById("todayCnt");
  el.textContent=(t.dueAll+t.nw.length)?`復習 ${t.dueAll}・新しい ${t.nw.length}`:"今日は終わり ✓"; }
async function startToday(more){
  const t=todayItems(more); await sSet(PROG_KEY,prog);
  today=true; queue=t.due.concat(t.nw); pos=0; revealed=false; run={correct:0,total:0};
  document.getElementById("quizWrap").classList.add("is-today");
  switchSec("quiz"); todayCount();
  if(!queue.length){showDone(true);return;} showCard();
}
function exitToday(){ today=false; document.getElementById("quizWrap").classList.remove("is-today"); }
function qItem(i){ const it=queue[i]; if(today){ const p=packsById[it.p]; return {p:p,q:p.quiz.find(d=>d.id===it.id)}; }
  return {p:cur(),q:cur().quiz.find(d=>d.id===it)}; }
/* セットを切りかえる（授業の「次へ」・一問一答から授業へ）。li は開く授業（"last"＝最後） */
async function goPack(id,li){ activeId=id; await sSet(ACT_KEY,id); document.getElementById("packSel").value=id;
  unitFilter=""; curTag=""; const n=packsById[id].lessons.length; lIdx=(li==="last")?Math.max(0,n-1):(li||0); renderActivePack(); }
function nextPackId(dir){ let i=packOrder.indexOf(activeId)+dir; while(i>=0&&i<packOrder.length){ if(packsById[packOrder[i]].lessons.length) return packOrder[i]; i+=dir; } return null; }""")

# ---------- JS: 授業の「次へ」をセットをまたいで続ける ----------
rep("""  document.getElementById("lPrev").disabled=lIdx===0;
  document.getElementById("lNext").disabled=lIdx===p.lessons.length-1;""",
"""  const bp=document.getElementById("lPrev"), bn=document.getElementById("lNext"), pv=nextPackId(-1), nx=nextPackId(1);
  if(lIdx>0){bp.disabled=false;bp.textContent="← 前の授業";} else if(pv){bp.disabled=false;bp.textContent="← 前："+packsById[pv].title.replace(/（.*$/,"");} else {bp.disabled=true;bp.textContent="← 前の授業";}
  if(lIdx<p.lessons.length-1){bn.disabled=false;bn.textContent="次の授業 →";} else if(nx){bn.disabled=false;bn.textContent="次："+packsById[nx].title.replace(/（.*$/,"")+"へ →";} else {bn.disabled=true;bn.textContent="次の授業 →";}""")
rep("""document.getElementById("lPrev").addEventListener("click",()=>{showLesson(lIdx-1);toLessonTop();});
document.getElementById("lNext").addEventListener("click",()=>{showLesson(lIdx+1);toLessonTop();});""",
"""document.getElementById("lPrev").addEventListener("click",async()=>{ if(lIdx>0) showLesson(lIdx-1); else { const pv=nextPackId(-1); if(!pv) return; await goPack(pv,"last"); } toLessonTop(); });
document.getElementById("lNext").addEventListener("click",async()=>{ if(lIdx<cur().lessons.length-1) showLesson(lIdx+1); else { const nx=nextPackId(1); if(!nx) return; await goPack(nx,0); } toLessonTop(); });
document.getElementById("todayBtn").addEventListener("click",()=>startToday(false));
document.getElementById("todayExit").addEventListener("click",()=>{exitToday();startRun();});""")

# ---------- JS: 絞りこみ ----------
rep("""  if(mode==="important")l=l.filter(d=>d.i>=4); if(mode==="weak")l=l.filter(d=>isWeak(d.id)); return l; }""",
"""  if(mode==="top")l=l.filter(d=>(d.x||0)>=2); if(mode==="freq")l=l.filter(d=>d.x===1); if(mode==="weak")l=l.filter(d=>isWeak(d.id)); return l; }""")

# ---------- JS: 一問一答の本体 ----------
rep("""  buildUnitOptions(); startRun();
}""","""  buildUnitOptions(); if(today){ if(queue.length&&pos<queue.length) showCard(); else showDone(!queue.length); return; } startRun();
}""")
rep("""function startRun(){ let l=filtered().map(d=>d.id);""","""function startRun(){ exitToday(); let l=filtered().map(d=>d.id);""")
rep("""  const q=cur().quiz.find(d=>d.id===queue[pos]);
  document.getElementById("cUnit").textContent=q.unit||"";""",
"""  const it=qItem(pos), q=it.q;
  document.getElementById("cUnit").textContent=today?(it.p.title.replace(/（.*$/,"")+"｜"+(q.unit||"")):(q.unit||"");""")
rep("""<span class="rate"><em>頻度</em><span class="stars">${starHtml(q.f)}</span></span>`;""",
"""<span class="rate"><em>頻度</em><span class="stars">${starHtml(q.f)}</span></span>`+(q.x?`<span class="rate"><em>過去問</em><span class="kx">${q.x>=2?"最頻出":"頻出"}（${q.x}回）</span></span>`:"");""")
rep("""  const tl=findLessonForAnswer(q), tb=document.getElementById("toLessonBtn");
  if(tl){ tb.classList.remove("hidden"); tb.onclick=()=>quizToLesson(tl.idx,tl.mark); }""",
"""  const tl=findLessonForAnswer(q,it.p), tb=document.getElementById("toLessonBtn");
  if(tl){ tb.classList.remove("hidden"); tb.onclick=async()=>{ if(it.p.id!==activeId) await goPack(it.p.id,tl.idx); quizToLesson(tl.idx,tl.mark); }; }""")
rep("""function findLessonForAnswer(q){
  const p=cur(); const mark""","""function findLessonForAnswer(q,pk){
  const p=pk||cur(); const mark""")
rep("""async function judge(ok){ if(!revealed)return; const id=queue[pos],r=rec(id);
  if(ok){r.c++;r.last="○";run.correct++;stamp();}else{r.w++;r.last="×";} await setRec(id,r); run.total++;""",
"""async function judge(ok){ if(!revealed)return; const it=qItem(pos), id=it.q.id, r=Object.assign({},rec(id,it.p.id));
  if(ok){r.c++;r.last="○";run.correct++;stamp(); const k=SRS.indexOf(r.iv); r.iv=SRS[Math.min(k+1,SRS.length-1)]; r.d=DAY()+r.iv; }
  else{r.w++;r.last="×"; r.iv=0; r.d=DAY()+1; if(today&&!queue[pos].again) queue.push({p:it.p.id,id:id,again:1}); }
  await setRec(id,r,it.p.id); run.total++;""")
rep("""  else{dp.querySelector("h2").textContent="このまわり、おわり";const rate""",
"""  else{dp.querySelector("h2").textContent=today?"今日のぶん、おわり":"このまわり、おわり";const rate""")
rep("""  updateStats();
}
function updateStats(){""","""  if(today){ document.getElementById("againWeak").style.display="none"; if(empty){dp.querySelector("h2").textContent="今日のぶんは終わり";document.getElementById("doneSub").textContent="復習するものも、今日の新しい問題も残っていない。";} todayCount(); }
  document.getElementById("againAll").textContent=today?"新しい問題をあと20問":"もう一周";
  updateStats();
}
function updateStats(){""")
rep("""document.getElementById("againAll").addEventListener("click",startRun);""",
"""document.getElementById("againAll").addEventListener("click",()=>{ if(today) startToday(true); else startRun(); });""")
rep("""document.getElementById("packSel").addEventListener("change",async e=>{activeId=e.target.value;""",
"""document.getElementById("packSel").addEventListener("change",async e=>{exitToday();activeId=e.target.value;""")
rep("""  renderActivePack();
  switchSec(activeSec);
})();""","""  renderActivePack();
  switchSec(activeSec); todayCount();
})();""")
open(f,'w',encoding='utf-8').write(s)
print('patched')
