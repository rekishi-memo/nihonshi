# 一度きりのパッチ（2026-11-10）：学習記録の書き出し・読みこみ（リンクや端末を変えるときの引っこし用）。
#   python3 patch_backup.py ../app/source.html
import sys
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
if 'id="bkOut"' in s: sys.exit('already patched')
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)
rep("""    <div class="m-block">
      <h4>取り込み（追加・上書き）</h4>""","""    <div class="m-block">
      <h4>学習記録の引っこし</h4>
      <p class="sub">正答の記録・今日のぶん・取りこんだセットを、まるごと書き出す／読みこむ。リンク（URL）や端末を変えるときに使う。</p>
      <div class="m-btns"><button class="ghost" id="bkOut">① 記録を書き出す</button><button class="ghost" id="bkCopy">コピー</button><button class="ghost" id="bkDl">ファイルで保存</button></div>
      <textarea class="io" id="bkBox" placeholder="「① 記録を書き出す」を押すと、ここに記録が出る。全部コピーしてメモなどに保存する。読みこむときは、保存した文字をここに貼る。"></textarea>
      <div class="m-btns"><label class="ghost" style="cursor:pointer">ファイルを選ぶ<input type="file" id="bkFile" accept=".json,.txt,application/json,text/plain" style="display:none"></label><button class="ghost" id="bkIn">② この記録を読みこむ</button></div>
      <p class="sub" id="bkMsg"></p>
    </div>

    <div class="m-block">
      <h4>取り込み（追加・上書き）</h4>""")
rep("""document.getElementById("resetProgBtn").addEventListener("click",resetProg);""","""document.getElementById("resetProgBtn").addEventListener("click",resetProg);
/* ---- 学習記録の引っこし（書き出し・読みこみ） ---- */
function bkStat(pr){ let n=0,c=0,w=0; for(const k in pr){ if(k==="_today") continue; for(const i in pr[k]){ const r=pr[k][i]; if(r&&(r.c+r.w)>0){n++;c+=r.c;w+=r.w;} } } return {n,c,w}; }
document.getElementById("bkOut").addEventListener("click",async()=>{
  const data={app:"nihonshi",v:2,saved:new Date().toISOString(),prog:await sGet(PROG_KEY)||{},active:await sGet(ACT_KEY),sec:await sGet(SEC_KEY),packs:await sGet(PK_KEY)||{}};
  document.getElementById("bkBox").value=JSON.stringify(data); const st=bkStat(data.prog);
  document.getElementById("bkMsg").textContent=`書き出した：解いた問題 ${st.n}問（○${st.c}回・×${st.w}回）。「コピー」か「ファイルで保存」で残す。`; });
document.getElementById("bkCopy").addEventListener("click",()=>{ const t=document.getElementById("bkBox"); if(!t.value){toast("先に書き出す");return;} t.select(); try{document.execCommand("copy");}catch(e){} if(navigator.clipboard)navigator.clipboard.writeText(t.value).catch(()=>{}); toast("コピーした"); });
document.getElementById("bkDl").addEventListener("click",()=>{ const v=document.getElementById("bkBox").value; if(!v){toast("先に書き出す");return;}
  const a=document.createElement("a"); a.href=URL.createObjectURL(new Blob([v],{type:"application/json"})); a.download="nihonshi-kiroku-"+new Date().toISOString().slice(0,10)+".json"; a.click(); toast("保存した"); });
document.getElementById("bkFile").addEventListener("change",e=>{ const f=e.target.files[0]; if(!f) return; const r=new FileReader(); r.onload=()=>{document.getElementById("bkBox").value=r.result; document.getElementById("bkMsg").textContent="ファイルを読んだ。「② この記録を読みこむ」を押す。";}; r.readAsText(f); });
document.getElementById("bkIn").addEventListener("click",async()=>{ const msg=document.getElementById("bkMsg"); let d;
  try{ d=JSON.parse(document.getElementById("bkBox").value.trim()); }catch(e){ msg.textContent="読めない。書き出した文字を、最初から最後まで全部貼る。"; return; }
  if(!d||d.app!=="nihonshi"||typeof d.prog!=="object"||!d.prog){ msg.textContent="このアプリの記録ではない。"; return; }
  const now=bkStat(await sGet(PROG_KEY)||{}), nw=bkStat(d.prog);
  if(!confirm(`いまの記録（解いた問題 ${now.n}問）を、読みこむ記録（${nw.n}問・${(d.saved||"").slice(0,10)} に書き出し）で置きかえる。よい？`)) return;
  await sSet(PROG_KEY,d.prog); if(d.packs&&typeof d.packs==="object") await sSet(PK_KEY,d.packs); if(d.active) await sSet(ACT_KEY,d.active); if(d.sec) await sSet(SEC_KEY,d.sec);
  msg.textContent="読みこんだ。画面を開き直す。"; setTimeout(()=>location.reload(),600); });""")
open(f,'w',encoding='utf-8').write(s); print('patched')
