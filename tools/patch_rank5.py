# 重要度を5段（共テ必修・私大頻出・私大・難関私大・色なし）にする（2026-11-13）。ボタンや凡例の名前は patch_rank6.py で付け直した。アプリの表示を直す一回きりのパッチ。何度かけても同じ。
#   python3 patch_rank5.py ../app/source.html ../app/source.html
import re,sys
src,out=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    if b in s and a not in s: return
    assert s.count(a)==cnt,(a[:60],s.count(a)); s=s.replace(a,b)
# CSS
rep("""  #lBody .kw.rk-A{font-weight:800;color:var(--gold-bright,#f3d27a);}
  #lBody .kw.rk-B{font-weight:400;color:var(--gold);}
  #lBody .kw.rk-C{font-weight:400;color:#ffffff;}""",
"""  #lBody .kw.rk-A{font-weight:800;color:var(--gold-bright,#f3d27a);}
  #lBody .kw.rk-B{font-weight:600;color:var(--gold);}
  #lBody .kw.rk-C{font-weight:400;color:#c7b98f;}
  #lBody .kw.rk-D,#lBody .kw.rk-X,#lColumn .kw.rk-X{color:inherit;font-weight:inherit;}
  #lBody .deep .kw.rk-D,#lColumn .kw.rk-D{color:#cdb2ff;font-weight:700;}
  .nk-words{border:1px solid #b39ddb;background:rgba(179,157,219,.09);border-radius:10px;padding:9px 12px !important;color:var(--ivory) !important;}
  .nk-words b{color:#d7c8f0;}""")
rep(""".rk-legend .b b{font-weight:400;color:var(--gold);} .rk-legend .c b{font-weight:400;color:#fff;}""",
""".rk-legend .b b{font-weight:600;color:var(--gold);} .rk-legend .c b{font-weight:400;color:#c7b98f;} .rk-legend .d b{font-weight:700;color:#cdb2ff;}""")
# 一問一答の重要度 → 本文の色
rep("""(p.quiz||[]).forEach(q=>{const r=(q.i>=5)?"A":(q.i>=4?"B":"C"); put(q.a,r); put(q.mark,r);});""",
"""(p.quiz||[]).forEach(q=>{const r=(q.i>=5)?"A":(q.i>=4?"B":(q.i>=3?"C":"D")); put(q.a,r); put(q.mark,r);});""")
rep("""  const G=globalRank(); if(G[text]) return G[text];
  return "C";
}""","""  const G=globalRank(); if(G[text]) return G[text];
  return "X";
}
const RK_NAME={A:"幹",B:"枝",C:"葉",D:"難関私大",X:"＋α"};""")
rep("""  root.querySelectorAll(".kw").forEach(el=>{ if(el.closest(".yodan")){el.classList.remove("rk-A","rk-B","rk-C");return;} const c=el.cloneNode(true); c.querySelectorAll("rt,.rtx").forEach(r=>r.remove());
    const t=c.textContent.trim(), r=rankOf(p,t);
    el.classList.remove("rk-A","rk-B","rk-C","rk-dup");""",
"""  root.querySelectorAll(".kw").forEach(el=>{ if(el.closest(".yodan")){el.classList.remove("rk-A","rk-B","rk-C","rk-D","rk-X");return;} const c=el.cloneNode(true); c.querySelectorAll("rt,.rtx").forEach(r=>r.remove());
    const t=c.textContent.trim(), r=rankOf(p,t);
    el.classList.remove("rk-A","rk-B","rk-C","rk-D","rk-X","rk-dup");""")
rep("""    lg.innerHTML='<span class="a"><b>太字の金＝A</b> 必ず覚える</span><span class="b"><b>普通の金＝B</b> 覚える</span><span class="c"><b>白＝C</b> 流れの中で</span>';""",
"""    lg.innerHTML='<span class="a"><b>太い金＝幹</b> 共テの土台</span><span class="b"><b>金＝枝</b> 共テ・私大の標準</span><span class="c"><b>うすい色＝葉</b> 私大の細かめ</span><span class="d"><b>紫＝難関私大</b> 本文では色なし。下の枠で</span>';""")
# 授業の下の「難関私大」枠：本文に出てきた難関私大の語を並べる
rep("""  document.getElementById("lColumn").innerHTML=l.colHtml?`<details class="fold"><summary><span class="col-tag">深掘り</span><span class="col-ttl">${l.colTitle||"コラム"}</span><span class="chev">▾</span></summary><div class="fold-body">${l.colHtml}</div></details>`:"";""",
"""  const nkw=[]; document.querySelectorAll("#lBody .kw.rk-D").forEach(k=>{ if(k.closest(".deep,.yodan")) return; const c=k.cloneNode(true); c.querySelectorAll("rt,.rtx").forEach(r=>r.remove()); const t=c.textContent.trim(); if(t&&!nkw.includes(t)) nkw.push(t); });
  const nkHtml=nkw.length?`<p class="nk-words"><b>難関私大をめざすなら、本文のこの語も：</b>${nkw.map(t=>`<span class='kw'>${t}</span>`).join("・")}</p>`:"";
  document.getElementById("lColumn").innerHTML=(l.colHtml||nkHtml)?`<details class="fold"><summary><span class="col-tag">難関私大</span><span class="col-ttl">${l.colHtml?(l.colTitle||"深掘り"):"難関私大で問われる語"}${nkw.length?`（本文の語 ${nkw.length}）`:""}</span><span class="chev">▾</span></summary><div class="fold-body">${nkHtml}${l.colHtml||""}</div></details>`:"";
  applyRanks(document.getElementById("lColumn"),p); { const lg=document.querySelector("#lColumn .rk-legend"); if(lg) lg.remove(); }""")
# 穴埋めの隠し方
rep("""<div class="cz-rk" id="czRk"><button class="ghost" data-m="A">Aだけ隠す</button><button class="ghost" data-m="AB">A・Bを隠す</button><button class="ghost" data-m="ABC" aria-pressed="true">全部隠す</button></div>""",
"""<div class="cz-rk" id="czRk"><button class="ghost" data-m="A">幹だけ</button><button class="ghost" data-m="AB">幹・枝</button><button class="ghost" data-m="ABCX" aria-pressed="true">葉まで</button><button class="ghost" data-m="ABCXD">難関私大まで</button></div>""")
rep("""let czMode="ABC";""","""let czMode="ABCX";""")
# 一問一答の絞りこみ
rep("""  .modes{display:flex;gap:7px;}""","""  .modes{display:flex;gap:7px;flex-wrap:wrap;}""")
rep("""        <button data-mode="top" aria-pressed="false">最頻出</button>
        <button data-mode="freq" aria-pressed="false">頻出</button>""",
"""        <button data-mode="kan" aria-pressed="false">幹</button>
        <button data-mode="eda" aria-pressed="false">幹＋枝</button>
        <button data-mode="nan" aria-pressed="false">難関</button>
        <button data-mode="freq" aria-pressed="false">頻出</button>""")
rep("""  if(mode==="top")l=l.filter(d=>(d.x||0)>=4); if(mode==="freq")l=l.filter(d=>d.x===2||d.x===3);""",
"""  if(mode==="kan")l=l.filter(d=>(d.i||0)>=5); if(mode==="eda")l=l.filter(d=>(d.i||0)>=4); if(mode==="nan")l=l.filter(d=>(d.i||3)<=2); if(mode==="freq")l=l.filter(d=>(d.x||0)>=2);""")
# カードの重要度に名前をそえる
rep("""<span class="rate"><em>重要度</em><span class="stars">${starHtml(q.i)}</span></span>""",
"""<span class="rate"><em>重要度</em><span class="stars">${starHtml(q.i)}</span> ${({5:"幹",4:"枝",3:"葉",2:"難関私大"})[q.i]||""}</span>""")
rep("""        if(rk==="C"||used.has(w)||(prev&&KJ.test(prev))||(nxt&&KJ.test(nxt))) return w;""",
"""        if((rk!=="A"&&rk!=="B")||used.has(w)||(prev&&KJ.test(prev))||(nxt&&KJ.test(nxt))) return w;""")
# 共テ必修・私大頻出は、同じ段落の2回目からはふつうの文字にする（アイヌ史の「アイヌ」のように何度も出る語で、太字だらけにならないように）
rep("""    if(r==="C"){ if(seenC.has(t)){ el.classList.add("rk-dup"); return; } seenC.add(t); }""",
"""    if(r==="C"){ if(seenC.has(t)){ el.classList.add("rk-dup"); return; } seenC.add(t); }
    if(r==="A"||r==="B"){ const blk=el.closest("p,li,.vr,div"); const key=t; if(blk){ blk._rk=blk._rk||new Set(); if(blk._rk.has(key)){ el.classList.add("rk-dup"); return; } blk._rk.add(key); } }""")
open(out,'w',encoding='utf-8').write(s); print('ok')
