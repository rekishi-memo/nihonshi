# 一度きりのパッチ（2026-11-09）：「今日のぶん」を、一問一答を開いたときに自動で出す（上の金色のボタンはやめる）。
#   python3 patch_today2.py ../app/source.html
import sys
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
if 'todayOff' in s: sys.exit('already patched')
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)
rep("""  <button class="today-btn" id="todayBtn"><span>今日のぶん</span><small id="todayCnt"></small></button>\n""","")
rep("""<div class="today-bar" id="todayBar"><span>今日のぶん（全範囲から）</span><button id="todayExit">ふつうの一問一答へ</button></div>""",
    """<div class="today-bar" id="todayBar"><span id="todayCnt">今日のぶん</span><button id="todayExit">ふつうの一問一答へ</button></div>""")
rep("  .today-bar{display:none;","  .today-bar{display:flex;")
rep("let today=false;","let today=false, todayOff=false; /* todayOff＝「ふつうの一問一答へ」を押したあと（開き直すまで自動では出さない） */")
rep("""function todayCount(){ const t=todayItems(false); const el=document.getElementById("todayCnt");
  el.textContent=(t.dueAll+t.nw.length)?`復習 ${t.dueAll}・新しい ${t.nw.length}`:"今日は終わり ✓"; }""",
"""function todayCount(){ const t=todayItems(false), n=t.dueAll+t.nw.length;
  document.getElementById("todayCnt").textContent=today?"今日のぶん（全範囲から）":(n?`今日のぶん：復習 ${t.dueAll}・新しい ${t.nw.length}`:"今日のぶんは終わり ✓");
  document.getElementById("todayExit").textContent=today?"ふつうの一問一答へ":(n?"今日のぶんへ →":"あと20問やる →"); return n; }""")
rep("""async function startToday(more){
  const t=todayItems(more); await sSet(PROG_KEY,prog);
  today=true;""","""function startToday(more){
  const t=todayItems(more); sSet(PROG_KEY,prog);
  today=true;""")
rep("""function exitToday(){ today=false; document.getElementById("quizWrap").classList.remove("is-today"); }""",
"""function exitToday(){ if(!today) return; today=false; document.getElementById("quizWrap").classList.remove("is-today"); todayCount(); }""")
rep("""  document.getElementById("sec-"+k).classList.add("active");""",
"""  document.getElementById("sec-"+k).classList.add("active");
  if(k==="quiz"&&!today&&!todayOff&&todayCount()>0) startToday(false);  /* 一問一答を開いたら、まず今日のぶん */""")
rep("""document.getElementById("todayBtn").addEventListener("click",()=>startToday(false));
document.getElementById("todayExit").addEventListener("click",()=>{exitToday();startRun();});""",
"""document.getElementById("todayExit").addEventListener("click",()=>{ if(today){todayOff=true;startRun();} else {todayOff=false;startToday(todayCount()===0);} });""")
open(f,'w',encoding='utf-8').write(s); print('patched')
