# 設定画面（⚙ 設定）を作る。声はここで、サンプルを聞きながら選ぶ。2026-11-14 ユーザーの指示。
#   python3 patch_settings.py ../app/source.html ../app/source.html   （patch_tts → patch_guide → patch_vv のあとに当てる）
# - 右上の「⚙ データ」を「⚙ 設定」にする。設定の中に：読み上げの声（▶で試し聞き）／速さ／枠も読む／使い方ガイド／データ／クレジット。
#   データ管理（記録の書き出し・読みこみ、セットの取りこみ）は、設定の中のボタンから今までの画面を開く。
# - 声のサンプルは ../audio/samples/<声のID>.m4a（vv_sample.py が作る）。端末の声は「この声で読みます」と読む。
# - 授業の読み上げバーは「▶ 読み上げ／■ 停止／速さ／声：◯◯ ›」。「声：」を押すと設定の声の欄が開く。
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
if 'id="setModal"' in s:
    print('already'); sys.exit(0)
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:80]); s=s.replace(a,b)

CSS=r'''
  /* 設定画面 */
  .st-sec{margin:16px 0 4px;}
  .st-sec h4{font-family:var(--gothic);font-size:12px;letter-spacing:.12em;color:var(--gold-deep);margin-bottom:8px;}
  .st-sec .st-sub{font-size:12px;color:var(--ash);line-height:1.7;margin:-2px 0 8px;}
  .st-grp{font-family:var(--gothic);font-size:11.5px;color:var(--ash);margin:10px 0 6px;}
  .st-list{border:1px solid var(--line);border-radius:12px;overflow:hidden;}
  .st-voice{display:flex;align-items:center;gap:10px;padding:9px 12px;border-top:1px solid var(--line-soft);cursor:pointer;-webkit-tap-highlight-color:transparent;}
  .st-voice:first-child{border-top:none;}
  .st-voice.on{background:rgba(212,189,130,.10);}
  .st-play{flex:0 0 auto;width:34px;height:34px;border-radius:50%;border:1px solid var(--gold-deep);background:transparent;color:var(--gold);font-size:13px;cursor:pointer;}
  .st-play.playing{background:var(--gold);color:#1a140a;}
  .st-vname{flex:1;min-width:0;font-size:14px;color:var(--ivory);line-height:1.4;}
  .st-vname small{display:block;font-size:11px;color:var(--ash);margin-top:2px;}
  .st-check{flex:0 0 auto;width:20px;text-align:center;color:var(--gold);font-weight:800;visibility:hidden;}
  .st-voice.on .st-check{visibility:visible;}
  .st-seg{display:flex;flex-wrap:wrap;gap:6px;}
  .st-seg button{font-family:var(--gothic);font-size:12.5px;padding:7px 12px;border-radius:999px;border:1px solid var(--line);background:transparent;color:var(--ivory-dim);cursor:pointer;}
  .st-seg button.on{background:var(--gold);border-color:var(--gold);color:#1a140a;font-weight:700;}
  .st-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:11px 12px;border:1px solid var(--line);border-radius:12px;font-size:13.5px;color:var(--ivory-dim);margin-bottom:8px;}
  .st-row small{display:block;font-size:11.5px;color:var(--ash);margin-top:2px;}
  .st-sw{flex:0 0 auto;width:48px;height:28px;border-radius:999px;border:none;background:var(--line);position:relative;cursor:pointer;}
  .st-sw::after{content:"";position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%;background:#fff;transition:left .15s;}
  .st-sw.on{background:var(--gold);}
  .st-sw.on::after{left:23px;}
  .st-btn{display:block;width:100%;text-align:left;font-family:var(--gothic);font-size:13.5px;padding:12px;border:1px solid var(--line);border-radius:12px;background:transparent;color:var(--ivory-dim);cursor:pointer;margin-bottom:8px;}
  .st-credit{font-size:11.5px;line-height:1.8;color:var(--ash);}

'''
rep("  /* ふりがな：<ruby>を独自の要素に置きかえて",CSS+"  /* ふりがな：<ruby>を独自の要素に置きかえて")
rep('<button class="ghost" id="dataBtn">⚙ データ</button>','<button class="ghost" id="setBtn">⚙ 設定</button><button class="ghost" id="dataBtn" hidden>⚙ データ</button>')

HTML='''<div class="modal" id="setModal" role="dialog" aria-modal="true" aria-label="設定">
  <div class="modal-card">
    <div class="m-top"><h3>設定</h3><button class="m-close" id="stClose" aria-label="閉じる">✕</button></div>
    <div class="st-sec" id="stVoiceSec"><h4>読み上げの声</h4><p class="st-sub">▶ で試しに聞けます。名前をタップすると、その声にします。<br>キャラクターの声は、音声のある授業だけ。ない授業は端末の声で読みます。</p><div id="stVoices"></div></div>
    <div class="st-sec"><h4>読み上げの速さ</h4><div class="st-seg" id="stRates"></div></div>
    <div class="st-sec"><h4>読み上げの枠</h4><div class="st-row"><span>枠も読む<small>「入試ではこう出る」「まとめ」「ちょっと脱線」など</small></span><button class="st-sw" id="stBox" aria-label="枠も読む"></button></div></div>
    <div class="st-sec"><h4>使い方ガイド</h4><div class="st-row"><span>アプリを開いたときに表示する</span><button class="st-sw" id="stGuide" aria-label="アプリを開いたときに使い方を表示する"></button></div><button class="st-btn" id="stGuideNow">使い方を見る ›</button></div>
    <div class="st-sec"><h4>データ</h4><button class="st-btn" id="stData">学習記録の書き出し・読みこみ、セットの取りこみ ›</button></div>
    <div class="st-sec"><h4>クレジット</h4><p class="st-credit" id="stCredit">キャラクターの声：VOICEVOX</p></div>
  </div>
</div>
'''
rep('<div class="modal" id="dataModal">',HTML+'<div class="modal" id="dataModal">')

# 読み上げバー：声はボタン（設定を開く）。枠の切りかえは設定へ
rep('''${ttsVoiceSel()}<button type="button" class="tts-sub" data-a="box">枠も読む：${tts.cfg.box?"オン":"オフ"}</button>`+''',
    '''<button type="button" class="tts-sub" data-a="voice">声：${ttsVoiceName()} ›</button>`+''')
rep('''    else if(a==="stop"){ ttsStop(); ttsRender(); }''','''    else if(a==="stop"){ ttsStop(); ttsRender(); }
    else if(a==="voice"){ stOpen(true); }''')

JS=r'''/* ---- 設定画面 ---- */
function ttsVoiceName(){ const v=(tts.st!=="idle"&&tts.mode==="vv")?tts.vvV:vvCur(); if(v) return vvLabel(v);
  if(!tts.voice) tts.voice=ttsPickVoice(); return tts.voice?ttsVLabel(tts.voice):"端末の声"; }
const ST={audio:null,playing:""};
function stCount(id){ if(!VV.man) return 0; let n=0; for(const k in VV.man.lessons){ const e=VV.man.lessons[k]; if(e.by&&e.by[id]) n++; } return n; }
function stTotal(){ let n=0; Object.keys(packsById).forEach(id=>{ n+=(packsById[id].lessons||[]).length; }); return n; }
function stSel(){ const m=/^vv:(\d+)$/.exec(tts.cfg.voice||""); if(m) return tts.cfg.voice; if(!tts.voice) tts.voice=ttsPickVoice(); return tts.voice?(tts.voice.voiceURI||tts.voice.name):""; }
function stRender(){ const box=document.getElementById("stVoices"); if(!box) return; const sel=stSel(), tot=stTotal();
  const ch=(VV.man?VV.man.voices:[]).map(v=>{ const n=stCount(v.id), k="vv:"+v.id;
    return `<div class="st-voice${k===sel?" on":""}" data-v="${k}"><button type="button" class="st-play${ST.playing===k?" playing":""}" data-p="${k}" aria-label="${vvLabel(v)}を試しに聞く">${ST.playing===k?"■":"▶"}</button><div class="st-vname">${vvLabel(v)}<small>音声のある授業：${n} / ${tot}</small></div><span class="st-check">✓</span></div>`; }).join("");
  const seen={}, dev=ttsVoices().map(v=>{ let lb=ttsVLabel(v); seen[lb]=(seen[lb]||0)+1; if(seen[lb]>1) lb+=" "+seen[lb]; const k=v.voiceURI||v.name, e=k.replace(/"/g,"&quot;");
    return `<div class="st-voice${k===sel?" on":""}" data-v="${e}"><button type="button" class="st-play${ST.playing===k?" playing":""}" data-p="${e}" aria-label="${lb}を試しに聞く">${ST.playing===k?"■":"▶"}</button><div class="st-vname">${lb}<small>すべての授業で使える</small></div><span class="st-check">✓</span></div>`; }).join("");
  box.innerHTML=(ch?`<div class="st-grp">キャラクターの声（VOICEVOX）</div><div class="st-list">${ch}</div>`:(location.protocol==="file:"?"":`<div class="st-grp">キャラクターの声は、ネットにつないでいるときに読みこみます。</div>`))+
    (dev?`<div class="st-grp">端末の声（iPhone で使えるのは Kyoko だけ）</div><div class="st-list">${dev}</div>`:"");
  document.getElementById("stRates").innerHTML=TTS_RATES.map(r=>`<button type="button" data-r="${r}" class="${r===tts.cfg.rate?"on":""}">${r}倍</button>`).join("");
  document.getElementById("stBox").classList.toggle("on",!!tts.cfg.box);
  let gh=null; try{ gh=localStorage.getItem(GUIDE_KEY); }catch(e){} document.getElementById("stGuide").classList.toggle("on",gh!=="hide");
  const cr=VV.man?[...new Set(VV.man.voices.map(v=>v.credit))]:[]; document.getElementById("stCredit").textContent="キャラクターの声："+(cr.length?cr.join("、"):"VOICEVOX"); }
function stOpen(voice){ stRender(); document.getElementById("setModal").classList.add("open");
  if(voice){ const e=document.getElementById("stVoiceSec"); if(e) e.scrollIntoView({block:"start"}); } }
function stClose(){ stStopSample(); document.getElementById("setModal").classList.remove("open"); }
function stStopSample(){ if(ST.audio){ ST.audio.pause(); } try{ if(ST.playing&&!/^vv:/.test(ST.playing)) speechSynthesis.cancel(); }catch(e){} ST.playing=""; }
function stSample(k){ const was=ST.playing; stStopSample(); if(was===k){ stRender(); return; } if(tts.st==="play") ttsPause();
  if(/^vv:/.test(k)){ if(!ST.audio){ ST.audio=new Audio(); ST.audio.setAttribute("playsinline",""); ST.audio.addEventListener("ended",()=>{ ST.playing=""; stRender(); }); }
    ST.audio.src="audio/samples/"+k.slice(3)+".m4a"; ST.audio.playbackRate=tts.cfg.rate; ST.playing=k;
    const p=ST.audio.play(); if(p&&p.catch) p.catch(()=>{ ST.playing=""; stRender(); toast(navigator.onLine===false?"オフラインでは、一度聞いたサンプルだけ聞けます":"サンプルを読みこめませんでした"); }); }
  else { const v=ttsVoices().find(x=>(x.voiceURI||x.name)===k); if(!v) return; try{ const u=new SpeechSynthesisUtterance("この声で、授業を読みます。"); u.lang="ja-JP"; u.voice=v; u.rate=tts.cfg.rate;
    u.onend=()=>{ if(ST.playing===k){ ST.playing=""; stRender(); } }; ST.playing=k; speechSynthesis.speak(u); }catch(e){} }
  stRender(); }
function stChoose(k){ const el=(tts.items[tts.k]||{}).el, playing=tts.st!=="idle";
  if(/^vv:/.test(k)){ tts.cfg.voice=k; } else { const v=ttsVoices().find(x=>(x.voiceURI||x.name)===k); if(!v) return; tts.voice=v; tts.cfg.voice=k; }
  ttsSave(); if(playing) ttsRestartAt(el); else ttsRender(); stRender();
  const v=vvWanted(); toast(v?`声を「${vvLabel(v)}」にしました`+(stCount(v.id)<stTotal()?"（音声のない授業は端末の声で読みます）":""):"声を変えました"); }
document.getElementById("setBtn").addEventListener("click",()=>stOpen(false));
document.getElementById("stClose").addEventListener("click",stClose);
document.getElementById("setModal").addEventListener("click",e=>{ if(e.target.id==="setModal"){ stClose(); return; }
  const p=e.target.closest(".st-play"); if(p){ e.stopPropagation(); stSample(p.dataset.p); return; }
  const row=e.target.closest(".st-voice"); if(row){ stChoose(row.dataset.v); return; }
  const r=e.target.closest("#stRates button"); if(r){ const v=+r.dataset.r; tts.cfg.rate=v; ttsSave(); if(tts.mode==="vv"&&VV.audio){ VV.audio.playbackRate=v; VV.audio.defaultPlaybackRate=v; } else if(tts.st==="play"){ tts.gen++; speechSynthesis.cancel(); setTimeout(()=>{ if(tts.st==="play") ttsSpeak(); },80); } if(ST.audio) ST.audio.playbackRate=v; stRender(); ttsRender(); return; }
  if(e.target.id==="stBox"){ tts.cfg.box=!tts.cfg.box; ttsSave(); if(tts.st!=="idle"){ if(tts.mode==="vv") vvTick(); else ttsRestartAt((tts.items[tts.k]||{}).el); } stRender(); ttsRender(); return; }
  if(e.target.id==="stGuide"){ let h=null; try{ h=localStorage.getItem(GUIDE_KEY); localStorage.setItem(GUIDE_KEY,h==="hide"?"show":"hide"); }catch(err){} stRender(); return; }
  if(e.target.id==="stGuideNow"){ stClose(); guideOpen(0); return; }
  if(e.target.id==="stData"){ stClose(); openModal(); return; } });
if(ttsOK()&&speechSynthesis.addEventListener) speechSynthesis.addEventListener("voiceschanged",()=>{ if(document.getElementById("setModal").classList.contains("open")) stRender(); });

'''
rep("/* ふりがなの置きかえ */",JS+"/* ふりがなの置きかえ */")
# 音声の一覧が届いたら、設定画面も描きなおす
rep('''if(j&&j.lessons){ VV.man=j; if(tts.st==="idle") ttsRender(); }''','''if(j&&j.lessons){ VV.man=j; if(tts.st==="idle") ttsRender(); if(typeof stRender==="function"&&document.getElementById("setModal").classList.contains("open")) stRender(); }''')

# ガイドを設定画面に合わせる
rep("<li><span class='g-ui sub'>声：…</span> で声を選べる。<b>キャラクターの声</b>（ずんだもん・四国めたん など）か、<b>端末の声</b>（Kyoko）</li>",
    "<li><span class='g-ui sub'>声：… ›</span> を押すと、設定の声の欄が開く（次のページ）</li>")
rep("<li><span class='g-ui sub'>枠も読む</span> をオフにすると、「入試ではこう出る」「まとめ」などの枠をとばす</li>",
    "<li>右上の <span class='g-ui sub'>⚙ 設定</span> で「枠も読む」をオフにすると、「入試ではこう出る」「まとめ」などの枠をとばす</li>")
i=s.index("<section class='g-slide' data-i='5'>"); j=s.index("</section>",i)+len("</section>")
s=s[:i]+("<section class='g-slide' data-i='5'><div class='g-ico'>🎙</div><h3>声のえらび方</h3>"
 "<ol class='g-list'><li>右上の <span class='g-ui sub'>⚙ 設定</span>（または授業の <span class='g-ui sub'>声：… ›</span>）を押す</li>"
 "<li>「読み上げの声」の <b>▶</b> で試しに聞く</li><li>気に入った声の<b>名前をタップ</b>すると、その声になる（✓が付く）</li>"
 "<li><b>キャラクターの声</b>は前もって作った音声で、<b>まだ一部の授業にしかありません</b>（「音声のある授業」の数を見てね）。ない授業では、自動で端末の声で読みます</li>"
 "<li>ネットにつないで一度聞いた授業は、オフラインでもキャラクターの声で聞ける</li></ol>"
 "<div class='g-note'><b>端末の声について</b>：iPhone では、このアプリが使える端末の声は <b>Kyoko だけ</b>です（iPhone の制限）。設定で O-ren や Otoya をダウンロードしても、このアプリには出てきません。</div>"
 "<div class='g-note' id='gCredits'>キャラクターの声：VOICEVOX</div></section>")+s[j:]
rep("<span class='g-ui sub'>⚙ データ</span> →「記録を書き出す」","<span class='g-ui sub'>⚙ 設定</span> →「データ」→「記録を書き出す」")
open(dst,'w',encoding='utf-8').write(s); print('ok')
