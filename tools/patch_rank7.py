# 本文の色を見分けやすくする／難関私大の枠の語をタップすると本文の同じ語にとんで光らせる（2026-11-13 ユーザーの指示
#   「金色視認で区別しにくいから何か変えたい。難関私大の語は本文は色なしなんだし、まとめてる枠から飛べるようにタップしたらハイライト」）。
#   共テ必修＝金の太字（いちばん大事なので目立つ金のまま）／私大頻出＝水色／私大＝うすい緑。ふりがなも同じ系統の色にする。
#   python3 patch_rank7.py ../app/source.html ../app/source.html （何度かけても同じ）
import sys
src,out=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
def rep(a,b):
    global s
    if b in s: return
    assert s.count(a)==1,a[:60]; s=s.replace(a,b)
rep("""  #lBody .kw.rk-A{font-weight:800;color:var(--gold-bright,#f3d27a);}
  #lBody .kw.rk-B{font-weight:600;color:var(--gold);}
  #lBody .kw.rk-C{font-weight:400;color:#c7b98f;}""",
"""  #lBody .kw.rk-A{font-weight:800;color:#F5D06A;}
  #lBody .kw.rk-B{font-weight:600;color:#7CC8FF;}
  #lBody .kw.rk-C{font-weight:400;color:#96D6A4;}
  #lBody .kw.rk-B .rtx,#lBody .kw.rk-B rt{color:#5d9fd0;-webkit-text-fill-color:#5d9fd0;}
  #lBody .kw.rk-C .rtx,#lBody .kw.rk-C rt{color:#6fa87c;-webkit-text-fill-color:#6fa87c;}
  #lBody .kw:is(.rk-D,.rk-X,.rk-dup) .rtx,#lBody .kw:is(.rk-D,.rk-X,.rk-dup) rt{color:var(--ash);-webkit-text-fill-color:var(--ash);}
  #lColumn .nk-words .kw{cursor:pointer;border-bottom:1px dashed #cdb2ff;padding:0 1px;}
  #lBody .kw.nk-hit{color:#fff !important;font-weight:700 !important;background:rgba(179,157,219,.5);border-radius:4px;box-shadow:0 0 0 3px rgba(179,157,219,.5);transition:background .4s,box-shadow .4s;}
  #nkBack{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:60;border:1px solid #b39ddb;background:#2a2340;color:#e6dcff;border-radius:99px;padding:9px 16px;font-size:13px;font-weight:700;box-shadow:0 4px 14px rgba(0,0,0,.4);}""")
rep(""".rk-legend .a b{font-weight:800;color:var(--gold-bright,#f3d27a);}""",""".rk-legend .a b{font-weight:800;color:#F5D06A;}""")
rep(""".rk-legend .b b{font-weight:600;color:var(--gold);} .rk-legend .c b{font-weight:400;color:#c7b98f;}""",""".rk-legend .b b{font-weight:600;color:#7CC8FF;} .rk-legend .c b{font-weight:400;color:#96D6A4;}""")
rep("""lg.innerHTML='<span class="a"><b>太い金＝共テ必修</b> 共テ・私大どちらでも土台</span><span class="b"><b>金＝私大頻出</b> 共テでも出ることがある</span><span class="c"><b>うすい色＝私大</b> 細かめの語</span><span class="d"><b>紫＝難関私大</b> 本文は色なし。下の枠で</span>';""",
"""lg.innerHTML='<span class="a"><b>金の太字＝共テ必修</b> 共テ・私大どちらでも土台</span><span class="b"><b>水色＝私大頻出</b> 共テでも出ることがある</span><span class="c"><b>緑＝私大</b> 細かめの語</span><span class="d"><b>紫＝難関私大</b> 本文は色なし。下の枠でタップ</span>';""")
rep("""<p class="nk-words"><b>難関私大をめざすなら、本文のこの語も：</b>""","""<p class="nk-words"><b>難関私大をめざすなら、本文のこの語も（タップで本文の場所へ）：</b>""")
rep("""  applyRanks(document.getElementById("lColumn"),p); { const lg=document.querySelector("#lColumn .rk-legend"); if(lg) lg.remove(); }""",
"""  applyRanks(document.getElementById("lColumn"),p); { const lg=document.querySelector("#lColumn .rk-legend"); if(lg) lg.remove(); }
  document.querySelectorAll("#lColumn .nk-words .kw").forEach(k=>k.addEventListener("click",e=>{e.preventDefault();e.stopPropagation();nkJump(k.textContent.trim());}));""")
rep("""function applyRanks(root,p){""","""/* 難関私大の枠の語 → 本文の同じ語にとんで光らせる。下に「枠にもどる」ボタンを出す */
function nkJump(t){
  const hits=[...document.querySelectorAll("#lBody .kw")].filter(e=>{ if(e.closest(".deep,.yodan")) return false; const c=e.cloneNode(true); c.querySelectorAll("rt,.rtx").forEach(r=>r.remove()); return c.textContent.trim()===t; });
  if(!hits.length) return;
  document.querySelectorAll("#lBody .nk-hit").forEach(e=>e.classList.remove("nk-hit"));
  hits.forEach(e=>e.classList.add("nk-hit"));
  hits[0].scrollIntoView({behavior:"smooth",block:"center"});
  clearTimeout(nkJump._t); nkJump._t=setTimeout(()=>hits.forEach(e=>e.classList.remove("nk-hit")),5000);
  let b=document.getElementById("nkBack");
  if(!b){ b=document.createElement("button"); b.id="nkBack"; b.textContent="↓ 難関私大の枠にもどる"; document.body.appendChild(b);
    b.addEventListener("click",()=>{ const c=document.getElementById("lColumn"); if(c) c.scrollIntoView({behavior:"smooth",block:"start"}); b.style.display="none"; }); }
  b.style.display="block"; clearTimeout(nkJump._b); nkJump._b=setTimeout(()=>{b.style.display="none";},12000);
}
function applyRanks(root,p){""")
# 授業や画面を切りかえたら「枠にもどる」ボタンを消す
rep("""  document.querySelectorAll("#lColumn .nk-words .kw").forEach(k=>k.addEventListener("click",e=>{e.preventDefault();e.stopPropagation();nkJump(k.textContent.trim());}));""",
"""  document.querySelectorAll("#lColumn .nk-words .kw").forEach(k=>k.addEventListener("click",e=>{e.preventDefault();e.stopPropagation();nkJump(k.textContent.trim());}));
  { const nb=document.getElementById("nkBack"); if(nb) nb.style.display="none"; }""")
rep("""function switchSec(k){""","""function switchSec(k){ { const nb=document.getElementById("nkBack"); if(nb) nb.style.display="none"; }""")
open(out,'w',encoding='utf-8').write(s); print('ok')
