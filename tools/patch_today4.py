# 今日のぶんを「1日100問・固定」にする（2026-11-12 ユーザーの指示）。
#   「今日の分はランダムに100問もってきて。開くたびに問題増えるのやめて。
#     しっかり記録残していき、復習も大事だけど、ある程度ランダムにも持ってこないと。」
#   python3 patch_today4.py ../app/source.html ../app/source.html
# しくみ：その日はじめて開いたときに 100問を決めて prog._today.list に残す（[セットid, 問題id, 0=まだ/1=○/2=×]）。
#   復習（間隔がきた問題・まちがえたままの問題）を最大 REV_MAX 問、残りは全範囲からランダム。
#   開き直しても、まだの問題から続きが出るだけで、問題は増えない。まちがえた問題をその場で列の最後に足すのもやめた
#   （まちがえた問題は翌日の復習に入る）。ふやすのは「あと20問（ランダム）」を押したときだけ。
import sys
src,out=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:80]); s=s.replace(a,b)

i=s.index('/* ---- 今日のぶん：全範囲から')
j=s.index('function exitToday()')
s=s[:i]+r'''/* ---- 今日のぶん：1日100問を朝に決めて記録する（復習＋全範囲からランダム） ----
   記録 r に d（次に出す日）と iv（間隔・日）を足す。○で間隔が 1→3→7→14→30→60 日とのび、×で翌日にもどる。
   その日の100問は prog._today.list に [セット, 問題id, 0=まだ/1=○/2=×] で残す。開き直しても増えない。 */
const SRS=[1,3,7,14,30,60], DAY_N=100, REV_MAX=40, MORE_N=20;
let today=false, todayOff=false; /* todayOff＝「ふつうの一問一答へ」を押したあと（開き直すまで自動では出さない） */
function DAY(){ const d=new Date(); return Math.floor((d.getTime()-d.getTimezoneOffset()*60000)/864e5); }
function todaySt(){ const day=DAY(); let st=prog._today;
  if(!st||st.day!==day){ const h=(st&&st.hist)||[]; if(st&&st.n) h.push([st.day,st.n,st.ok||0]); st={day:day,n:0,ok:0,hist:h.slice(-90)}; prog._today=st; }
  if(st.n==null){st.n=0;st.ok=0;} if(!st.hist)st.hist=[]; return st; }
function dayLabel(d){ const t=new Date(d*864e5); return (t.getUTCMonth()+1)+"/"+t.getUTCDate(); }
function qOK(pid,id){ const p=packsById[pid]; return !!(p&&p.quiz.some(q=>q.id===id)); }
/* 全範囲の問題（テーマ史・整理は除く）。taken にあるものは除く */
function todayPool(taken){ const due=[], rest=[], day=DAY();
  packOrder.forEach(pid=>{ if(pid.indexOf("theme_")===0||pid==="seiri") return; const p=packsById[pid], pp=prog[pid]||{};
    p.quiz.forEach(q=>{ const k=pid+"|"+q.id; if(taken.has(k)) return; const r=pp[q.id];
      const seen=r&&(r.c+r.w)>0, weak=seen&&(r.last==="×"||r.w>r.c);
      if(seen&&((r.d!=null&&r.d<=day)||(r.d==null&&weak))) due.push({p:pid,id:q.id,d:r.d==null?-1:r.d});
      else rest.push({p:pid,id:q.id}); }); });
  return {due,rest}; }
function todayAdd(st,nRev,nAll){ const taken=new Set((st.list||[]).map(x=>x[0]+"|"+x[1])); const {due,rest}=todayPool(taken);
  due.sort((a,b)=>a.d-b.d); const rv=due.slice(0,nRev); shuffle(rest);
  const pick=rv.concat(rest.slice(0,Math.max(0,nAll-rv.length))); shuffle(pick);
  st.list=(st.list||[]).concat(pick.map(x=>[x.p,x.id,0])); }
function todayItems(more){ const st=todaySt();
  if(!st.list){ todayAdd(st,REV_MAX,DAY_N); }
  else if(more){ todayAdd(st,0,MORE_N); }
  st.list=st.list.filter(x=>qOK(x[0],x[1])); prog._today=st;
  const left=[]; st.list.forEach((x,i)=>{ if(!x[2]) left.push({p:x[0],id:x[1],i:i}); });
  return {left:left,total:st.list.length,done:st.list.length-left.length}; }
function todayCount(){ const t=todayItems(false), st=todaySt();
  document.getElementById("todayCnt").textContent=today?`今日のぶん：${t.done} / ${t.total}問`:(t.left.length?`今日のぶん：${t.done} / ${t.total}問すみ（のこり ${t.left.length}）`:`今日のぶんは終わり ✓（${t.total}問）`);
  document.getElementById("todayExit").textContent=today?"ふつうの一問一答へ":(t.left.length?"今日のぶんへ →":"あと20問やる →"); return t.left.length; }
function startToday(more){
  const t=todayItems(more); sSet(PROG_KEY,prog);
  today=true; queue=t.left; pos=0; revealed=false; run={correct:0,total:0};
  document.getElementById("akaWrap").classList.add("hidden"); document.getElementById("quizEmpty").classList.add("hidden"); quizVis(true);
  document.getElementById("quizWrap").classList.add("is-today");
  switchSec("quiz"); todayCount();
  if(!queue.length){showDone(true);return;} showCard();
}
'''+s[j:]

rep('document.getElementById("cNo").textContent=today?`今日 ${todaySt().n+1}問目・のこり ${queue.length-pos}`:`${pos+1} / ${queue.length}`;',
    'document.getElementById("cNo").textContent=today?(()=>{const L=todaySt().list||[];return `今日 ${L.filter(x=>x[2]).length+1} / ${L.length}問目`;})():`${pos+1} / ${queue.length}`;')
rep('else{r.w++;r.last="×"; r.iv=0; r.d=DAY()+1; if(today&&!queue[pos].again) queue.push({p:it.p.id,id:id,again:1}); }\n  if(today){ const st=todaySt(); st.n++; if(ok) st.ok++; }',
    'else{r.w++;r.last="×"; r.iv=0; r.d=DAY()+1; }\n  if(today){ const st=todaySt(); st.n++; if(ok) st.ok++; const x=(st.list||[])[queue[pos].i]; if(x) x[2]=ok?1:2; }')
rep('document.getElementById("doneSub").textContent="復習するものも、今日の新しい問題も残っていない。";',
    'document.getElementById("doneSub").textContent="今日の100問は終わり。続けるなら「あと20問」でランダムに足せる。";')
rep('document.getElementById("againAll").textContent=today?"新しい問題をあと20問":"もう一周";',
    'document.getElementById("againAll").textContent=today?"あと20問（ランダム）":"もう一周";')
open(out,'w',encoding='utf-8').write(s)
print('ok')
