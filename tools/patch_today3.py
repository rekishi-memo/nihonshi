#!/usr/bin/env python3
"""今日のぶんを「1日ごとの記録」にする（1回だけ当てるパッチ）。
   prog._today に n（今日こたえた数）・ok（正解数）・hist（過去の日 [day,n,ok]）を足す。
   アプリを閉じて開き直しても、今日の何問目か・正答率が続きから出る。
   使い方: python3 patch_today3.py ../app/source.html"""
import sys
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
if 'function todaySt(' in s: print('already'); sys.exit()
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)

rep('''  const day=DAY(); let st=prog._today; if(!st||st.day!==day) st={day:day,nw:[]};''',
'''  const day=DAY(); const st=todaySt();''')
rep('''function todayItems(more){''',
'''function todaySt(){ const day=DAY(); let st=prog._today;
  if(!st||st.day!==day){ const h=(st&&st.hist)||[]; if(st&&st.n) h.push([st.day,st.n,st.ok||0]); st={day:day,nw:[],n:0,ok:0,hist:h.slice(-90)}; prog._today=st; }
  if(st.n==null){st.n=0;st.ok=0;} if(!st.hist)st.hist=[]; return st; }
function dayLabel(d){ const t=new Date(d*864e5); return (t.getUTCMonth()+1)+"/"+t.getUTCDate(); }
function todayItems(more){''')
rep('''  document.getElementById("todayCnt").textContent=today?"今日のぶん（全範囲から）":(n?`今日のぶん：復習 ${t.dueAll}・新しい ${t.nw.length}`:"今日のぶんは終わり ✓");''',
'''  const st=todaySt(), dn=st.n?`（今日 ${st.n}問すみ）`:"";
  document.getElementById("todayCnt").textContent=today?`今日のぶん：${st.n}問すみ・のこり ${Math.max(0,queue.length-pos)}`:(n?`今日のぶん：復習 ${t.dueAll}・新しい ${t.nw.length}${dn}`:`今日のぶんは終わり ✓${dn}`);''')
rep('''  document.getElementById("cNo").textContent=`${pos+1} / ${queue.length}`;''',
'''  document.getElementById("cNo").textContent=today?`今日 ${todaySt().n+1}問目・のこり ${queue.length-pos}`:`${pos+1} / ${queue.length}`;
  if(today) todayCount();''')
rep('''  await setRec(id,r,it.p.id); run.total++;''',
'''  if(today){ const st=todaySt(); st.n++; if(ok) st.ok++; }
  await setRec(id,r,it.p.id); run.total++;''')
rep('''  if(today){ document.getElementById("againWeak").style.display="none"; if(empty){''',
'''  if(today){ const st=todaySt(); if(st.n){ document.getElementById("doneRate").textContent=Math.round(st.ok/st.n*100)+"%";
      const h=st.hist.slice(-5).reverse().map(x=>`${dayLabel(x[0])} ${x[1]}問`).join("・");
      document.getElementById("doneSub").textContent=`今日は ${st.n}問やって ${st.ok}問 正解`+(h?`（これまで：${h}）`:""); }
    document.getElementById("againWeak").style.display="none"; if(empty&&!st.n){''')
open(f,'w',encoding='utf-8').write(s); print('patched')
