# 今日のぶんを「復習だけ」にする（2026-11-17 ユーザーの指示「一問一答の今日の分なんだけど、やっぱり復習だけにしよう」）。
#   python3 patch_today5.py ../app/source.html ../app/source.html
# しくみ：今日のぶん＝間隔がきた問題・まちがえたままの問題だけ（古い順に最大100問）。ランダムの新しい問題は入れない。
#   「あと20問」は、のこっている復習を20問足す（復習がもうなければ出さない）。
#   まだ解いたことのない問題は、セットごとのふつうの一問一答で解く → 解いたものが翌日以降の復習に入る。
#   その日すでに作ってあった「ランダム入り」の100問は、開いたときに、まだ解いていないランダムの問題をはずす（解いた記録はそのまま）。
import sys
src,out=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
if 'TODAY_REV_ONLY' in s: print('already'); open(out,'w',encoding='utf-8').write(s); sys.exit()
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:80]); s=s.replace(a,b)

rep('/* ---- 今日のぶん：1日100問を朝に決めて記録する（復習＋全範囲からランダム） ----',
    '/* ---- 今日のぶん：その日の復習（間隔がきた問題・まちがえたままの問題）を朝に決めて記録する。TODAY_REV_ONLY（2026-11-17：ランダムの新しい問題は入れない） ----')
rep('''function todayAdd(st,nRev,nAll){ const taken=new Set((st.list||[]).map(x=>x[0]+"|"+x[1])); const {due,rest}=todayPool(taken);
  due.sort((a,b)=>a.d-b.d); const rv=due.slice(0,nRev); shuffle(rest);
  const pick=rv.concat(rest.slice(0,Math.max(0,nAll-rv.length))); shuffle(pick);
  st.list=(st.list||[]).concat(pick.map(x=>[x.p,x.id,0])); }
function todayItems(more){ const st=todaySt();
  if(!st.list){ todayAdd(st,REV_MAX,DAY_N); }
  else if(more){ todayAdd(st,0,MORE_N); }''',
'''function todayAdd(st,n){ const taken=new Set((st.list||[]).map(x=>x[0]+"|"+x[1])); const {due}=todayPool(taken);
  due.sort((a,b)=>a.d-b.d); const pick=due.slice(0,n); shuffle(pick);
  st.list=(st.list||[]).concat(pick.map(x=>[x.p,x.id,0])); }
function todayDueLeft(st){ return todayPool(new Set((st.list||[]).map(x=>x[0]+"|"+x[1]))).due.length; }
function todayItems(more){ const st=todaySt();
  if(st.list&&!st.rv){ /* 前のしくみで作った今日のぶん：まだ解いていない問題は、復習の問題だけ残す */
    const due=new Set(todayPool(new Set()).due.map(x=>x.p+"|"+x.id));
    st.list=st.list.filter(x=>x[2]||due.has(x[0]+"|"+x[1])); st.rv=1; }
  if(!st.list){ st.list=[]; st.rv=1; todayAdd(st,DAY_N); }
  else if(more){ todayAdd(st,MORE_N); }''')
rep('''  document.getElementById("todayExit").textContent=today?"ふつうの一問一答へ":(t.left.length?"今日のぶんへ →":"あと20問やる →"); return t.left.length; }''',
    '''  if(!t.total) document.getElementById("todayCnt").textContent="今日の復習はなし";
  const more=todayDueLeft(st);
  document.getElementById("todayExit").textContent=today?"ふつうの一問一答へ":(t.left.length?"今日のぶんへ →":(more?"復習をあと20問 →":"ふつうの一問一答へ"));
  const none=(!today&&!t.left.length&&!more); document.getElementById("todayExit").dataset.none=none?"1":""; document.getElementById("todayExit").style.display=none?"none":"";
  if(none&&t.total) document.getElementById("todayCnt").textContent=`今日の復習は終わり ✓（${t.total}問）`; return t.left.length; }''')
rep('document.getElementById("doneSub").textContent="今日の100問は終わり。続けるなら「あと20問」でランダムに足せる。";',
    'document.getElementById("doneSub").textContent=todayDueLeft(todaySt())?"今日の復習は終わり。まだ残っている復習は「あと20問」で足せる。":"今日の復習は終わり。新しい問題は、セットごとの一問一答で解こう。解いた問題が、次の日からの復習に入る。";')
rep('document.getElementById("againAll").textContent=today?"あと20問（ランダム）":"もう一周";',
    'document.getElementById("againAll").textContent=today?"復習をあと20問":"もう一周"; if(today) document.getElementById("againAll").style.display=todayDueLeft(todaySt())?"":"none"; else document.getElementById("againAll").style.display="";')
rep('document.getElementById("todayExit").addEventListener("click",()=>{ if(today){todayOff=true;exitToday();renderQuizSection();} else {todayOff=false;startToday(todayCount()===0);} });',
    'document.getElementById("todayExit").addEventListener("click",e=>{ if(today){todayOff=true;exitToday();renderQuizSection();} else if(e.currentTarget.dataset.none==="1"){ toast("今日の復習は終わり。このセットの一問一答をどうぞ"); } else {todayOff=false;startToday(todayCount()===0);} });')
open(out,'w',encoding='utf-8').write(s)
print('ok')
