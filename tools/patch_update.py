# 新しい版が出たら「新しい版があります。タップで更新」を出す（2026-11-18。ホーム画面のアプリは閉じずに戻ると古い版のままのことがあり、
#   ユーザーが「（読み上げの）2倍が選択肢にない」と言った）。何度回してもよい。
#   ・<meta name="app-build" content="__APP_BUILD__">：pack_out.py が中身から作る番号に置きかえる
#   ・アプリに戻ったとき（5分に1回まで）と開いて4秒後に、公開中の index.html の頭だけ読み、番号がちがえば知らせる
#   ・sw.js は「build-check」の問い合わせを保存しない
import re,sys
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
if 'name="app-build"' not in s:
    s=s.replace('<meta charset="UTF-8">','<meta charset="UTF-8">\n<meta name="app-build" content="__APP_BUILD__">',1)
assert 'name="app-build"' in s
css='''/*UPDCSS-BEGIN*/
  #updBar{position:fixed;left:50%;bottom:calc(16px + env(safe-area-inset-bottom));transform:translateX(-50%);z-index:10001;padding:11px 18px;border-radius:24px;border:1px solid var(--gold);background:#141c30;color:var(--ivory);font-family:inherit;font-size:13px;white-space:nowrap;box-shadow:0 12px 32px rgba(0,0,0,.55);cursor:pointer;}
  #updBar b{color:var(--gold);margin-left:4px;}
/*UPDCSS-END*/'''
js='''<script>/*UPD-BEGIN*/
(function(){ "use strict";
  if(location.protocol==="file:") return;
  const mine=((document.querySelector('meta[name="app-build"]')||{}).content)||"";
  let last=0, shown=false;
  async function check(force){ const now=Date.now(); if(shown||(!force&&now-last<5*60000)) return; last=now;
    try{ const r=await fetch("index.html?build-check",{cache:"no-store",headers:{Range:"bytes=0-2047"}}); if(!r.ok) return;
      const rd=r.body.getReader(), dec=new TextDecoder(); let txt="";
      while(txt.length<2000){ const x=await rd.read(); if(x.done) break; txt+=dec.decode(x.value,{stream:true}); }
      rd.cancel().catch(()=>{});
      const m=txt.match(/name="app-build" content="([^"]+)"/);
      if(m&&mine&&m[1]!==mine&&m[1].indexOf("APP_BUILD")<0) show(); }catch(e){} }
  function show(){ shown=true; const b=document.createElement("button"); b.id="updBar"; b.type="button"; b.innerHTML="新しい版があります。<b>タップで更新</b>"; b.addEventListener("click",()=>location.reload()); document.body.appendChild(b); }
  setTimeout(()=>check(true),4000);
  document.addEventListener("visibilitychange",()=>{ if(!document.hidden) check(false); });
  window.addEventListener("pageshow",e=>{ if(e.persisted) check(true); });
})();
/*UPD-END*/</script>'''
s=re.sub(r'\n?/\*UPDCSS-BEGIN\*/[\s\S]*?/\*UPDCSS-END\*/\n?','\n',s)
s=re.sub(r'<script>/\*UPD-BEGIN\*/[\s\S]*?/\*UPD-END\*/</script>\n?','',s)
i=s.index('</style>'); s=s[:i].rstrip('\n')+'\n'+css+'\n'+s[i:]
i=s.rindex('</body>'); s=s[:i]+js+'\n'+s[i:]
open(f,'w',encoding='utf-8').write(s); print('update check patched')
