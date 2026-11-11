#!/usr/bin/env python3
"""「← もとの授業にもどる」に × をつけて消せるようにする／「テーマ史：内閣史 授業03」のように授業まで名ざしできるようにする（1回だけ当てるパッチ）。
   2026-11-11 ユーザーの指示「横にバツボタンで消せるようにしないと一生出る」。
   使い方: python3 patch_back.py ../app/source.html"""
import sys
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
if 'id="backX"' in s: print('already'); sys.exit()
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:70]); s=s.replace(a,b)
# 見た目：ボタン2つを横にならべた帯にする
rep('''  #backBtn{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(14px + env(safe-area-inset-bottom));z-index:60;font-family:var(--gothic);font-size:13px;font-weight:700;color:#1a140a;
    background:linear-gradient(180deg,var(--gold-bright),var(--gold));border:none;border-radius:22px;padding:10px 18px;box-shadow:0 4px 14px rgba(0,0,0,.5);cursor:pointer;white-space:nowrap;}''',
'''  #backBar{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(14px + env(safe-area-inset-bottom));z-index:60;display:flex;align-items:stretch;border-radius:22px;overflow:hidden;box-shadow:0 4px 14px rgba(0,0,0,.5);white-space:nowrap;}
  #backBar.hidden{display:none;}
  #backBtn,#backX{font-family:var(--gothic);font-size:13px;font-weight:700;color:#1a140a;background:linear-gradient(180deg,var(--gold-bright),var(--gold));border:none;cursor:pointer;}
  #backBtn{padding:10px 12px 10px 18px;}
  #backX{padding:10px 15px 10px 12px;border-left:1px solid rgba(26,20,10,.35);font-size:15px;line-height:1;}''')
rep('''  <button id="backBtn" class="hidden">← もとの授業にもどる</button>''',
'''  <div id="backBar" class="hidden"><button id="backBtn">← もとの授業にもどる</button><button id="backX" aria-label="このボタンを消す" title="このボタンを消す">×</button></div>''')
rep('''function showBack(){ document.getElementById("backBtn").classList.toggle("hidden",!backStack.length); }''',
'''function showBack(){ document.getElementById("backBar").classList.toggle("hidden",!backStack.length); }
document.getElementById("backX").addEventListener("click",()=>{ backStack=[]; showBack(); });''')
# テーマ史も「授業NN」まで名ざしできるようにする
rep('''|テーマ史[：〈]([^（）〉・、。]+)〉?|授業(\\d{2})((?:・\\d{2})*)/g;''',
    '''|テーマ史[：〈]([^（）〉・、。 　]+)〉?(?:[ 　の]*授業(\\d{2}))?|授業(\\d{2})((?:・\\d{2})*)/g;''')
rep('''      else if(m[5]) mk(m[0],packByLabel("テーマ史："+m[5]),null,ctx);
      else { mk("授業"+m[6],activeId,m[6],ctx); (m[7]||"").split("・").filter(Boolean).forEach(c=>{ tx("・"); mk(c,activeId,c,ctx); }); }''',
'''      else if(m[5]) mk(m[0],packByLabel("テーマ史："+m[5]),m[6]||null,ctx);
      else { mk("授業"+m[7],activeId,m[7],ctx); (m[8]||"").split("・").filter(Boolean).forEach(c=>{ tx("・"); mk(c,activeId,c,ctx); }); }''')
rep('''  body.querySelectorAll("p").forEach(p=>{ if(/^\\s*▶/.test(p.textContent)) p.classList.add("more"); });''',
    '''  body.querySelectorAll("p").forEach(p=>{ if(/^\\s*▶/.test(p.textContent)) p.classList.add("more"); });
  body.querySelectorAll("p.xhint").forEach(p=>p.remove());''')
open(f,'w',encoding='utf-8').write(s); print('patched')
