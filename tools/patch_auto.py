# 「自動で次へ」：授業を読み終えたら、次の授業（セットの最後なら次のセット）へ進み、画面も移して読み続ける。2026-11-15 ユーザーの指示。
#   python3 patch_auto.py ../app/source.html ../app/source.html   （patch_tts → patch_guide → patch_vv → patch_settings のあとに当てる）
# - 読み上げバーの「自動で次へ：オン／オフ」と、設定画面の「授業を読み終えたら次へ進む」で切りかえる（localStorage の nihonshi_tts の auto）。
# - 本文の段落がない授業（整理カードなど）はとばす。最後の授業まで読んだら止まる。
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
if 'function ttsDone' in s:
    print('already'); sys.exit(0)
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:80]); s=s.replace(a,b)

rep('''  const it=tts.items[tts.k]; if(!it){ ttsStop(); toast("読み上げおわり"); return; }''','''  const it=tts.items[tts.k]; if(!it){ ttsDone(); return; }''')
rep('''if(tts.mode==="vv"&&tts.st!=="idle"&&a.src===VV.cur){ ttsStop(); ttsRender(); toast("読み上げおわり"); }''','''if(tts.mode==="vv"&&tts.st!=="idle"&&a.src===VV.cur){ ttsDone(); }''')
rep('''    if(j<T.length){ a.currentTime=T[j][0]; k=j; } else { ttsStop(); ttsRender(); toast("読み上げおわり"); return; } }''','''    if(j<T.length){ a.currentTime=T[j][0]; k=j; } else { ttsDone(); return; } }''')

JS=r'''/* ---- 自動で次へ：読み終えたら次の授業へ進んで読み続ける ---- */
function ttsDone(){ if(!tts.cfg.auto){ ttsStop(); ttsRender(); toast("読み上げおわり"); return; }
  (async()=>{ for(let n=0;n<60;n++){ const p=cur();
      if(lIdx<p.lessons.length-1) showLesson(lIdx+1);
      else { const nx=nextPackId(1); if(!nx){ ttsStop(); ttsRender(); toast("最後の授業まで読みました"); return; } await goPack(nx,0); }
      if(ttsAllowed()) break; }
    toLessonTop(); const l=cur().lessons[lIdx]; toast("次へ："+cur().title.replace(/（.*$/,"")+" 授業"+(l.no||lIdx+1));
    setTimeout(()=>{ if(tts.st==="idle") ttsPlay(); },500); })(); }

'''
rep("/* ---- 設定画面 ---- */",JS+"/* ---- 設定画面 ---- */")
rep('''<button type="button" class="tts-sub" data-a="voice">声：${ttsVoiceName()} ›</button>`+''',
    '''<button type="button" class="tts-sub" data-a="voice">声：${ttsVoiceName()} ›</button><button type="button" class="tts-sub${tts.cfg.auto?" tts-on":""}" data-a="auto">自動で次へ：${tts.cfg.auto?"オン":"オフ"}</button>`+''')
rep('''    else if(a==="voice"){ stOpen(true); }''','''    else if(a==="voice"){ stOpen(true); }
    else if(a==="auto"){ tts.cfg.auto=!tts.cfg.auto; ttsSave(); ttsRender(); toast(tts.cfg.auto?"読み終えたら、次の授業へ進みます":"自動で次へ：オフ"); }''')
rep('''  .tts-bar .tts-hint{''','''  .tts-bar button.tts-sub.tts-on{border-color:var(--gold-deep);color:var(--gold);font-weight:600;}
  .tts-bar .tts-hint{''')
# 設定画面
rep('''    <div class="st-sec"><h4>使い方ガイド</h4>''','''    <div class="st-sec"><h4>自動で次へ</h4><div class="st-row"><span>授業を読み終えたら、次の授業へ進む<small>画面も次の授業に移り、読み上げが続きます</small></span><button class="st-sw" id="stAuto" aria-label="自動で次へ"></button></div></div>
    <div class="st-sec"><h4>使い方ガイド</h4>''')
rep('''  document.getElementById("stBox").classList.toggle("on",!!tts.cfg.box);''','''  document.getElementById("stBox").classList.toggle("on",!!tts.cfg.box); document.getElementById("stAuto").classList.toggle("on",!!tts.cfg.auto);''')
rep('''  if(e.target.id==="stGuide"){''','''  if(e.target.id==="stAuto"){ tts.cfg.auto=!tts.cfg.auto; ttsSave(); stRender(); ttsRender(); return; }
  if(e.target.id==="stGuide"){''')
# ガイド
rep("<li>読んでいる途中で<b>段落をタップ</b>すると、そこから読む</li>",
    "<li>読んでいる途中で<b>段落をタップ</b>すると、そこから読む</li><li><span class='g-ui sub'>自動で次へ</span> をオンにすると、授業を読み終えたら<b>次の授業へ進んで読み続ける</b>（画面も進む）</li>")
open(dst,'w',encoding='utf-8').write(s); print('ok')
