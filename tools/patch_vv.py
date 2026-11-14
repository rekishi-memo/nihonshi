# キャラクターの声（VOICEVOX で前もって作った音声ファイル）で授業を聞けるようにする。2026-11-14 ユーザーの指示。
#   python3 patch_vv.py ../app/source.html ../app/source.html   （patch_tts.py・patch_guide.py のあとに当てる）
# - 音声は ../audio/<pack id>/<授業の番号2桁>/<声のID>.m4a、一覧と文ごとの時刻は ../audio/voices.json（vv_make.py が作る）。
#   index.html の1ファイル構成の例外：音声だけは別ファイル（同じサイトの中）。外のサイトからは何も読み込まない。
# - 「声：」のメニューに、その授業にある「キャラクターの声」と「端末の声」を並べる。キャラの声がない授業は端末の声で読む。
# - 授業の原稿（vvItems）のハッシュが voices.json と合わないとき（授業の文を直したあと）は、キャラの声を出さない。
# - 再生は <audio>。iPhone は再生を始めるのに指でのタップが要るので、最初のタップで無音を鳴らして「鳴らせる状態」にしておく。
#   音声は fetch してから blob の URL で鳴らす（sw.js がキャッシュに残すので、一度聞いた授業はオフラインでも聞ける）。
# - 画面を消しても止めない（端末の声のときだけ、画面を消すと一時停止）。ロック画面に授業名とクレジットを出す。
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
if 'function vvItems' in s:
    print('already'); sys.exit(0)
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:80]); s=s.replace(a,b)

# 1) ttsCollect に「枠も全部入れる」(all) と、枠かどうか (box) を足す
rep('''function ttsCollect(){ const p=cur(), l=p.lessons[lIdx], d=ttsDictFor(l), items=[];
  const add=(el,raw)=>{ const t=ttsNorm(ttsApplyDict(ttsApplyRd(raw),d)); const ss=ttsSplit(t); if(ss.length) items.push({el,sents:ss}); };''',
'''function ttsCollect(all){ const p=cur(), l=p.lessons[lIdx], d=ttsDictFor(l), items=[], bx=all||tts.cfg.box;
  const add=(el,raw,box)=>{ const t=ttsNorm(ttsApplyDict(ttsApplyRd(raw),d)); const ss=ttsSplit(t); if(ss.length) items.push({el,sents:ss,box:!!box}); };''')
rep('''    else if(tts.cfg.box&&(el.classList.contains("yodan")||el.classList.contains("deep"))) add(el,ttsTextOf(el));
    else if(tts.cfg.box&&el.classList.contains("nyushi")) add(el,ttsTextOf(el));
    else if(tts.cfg.box&&el.classList.contains("point")) add(el,"まとめ。"+ttsTextOf(el)); });''',
'''    else if(bx&&(el.classList.contains("yodan")||el.classList.contains("deep"))) add(el,ttsTextOf(el),1);
    else if(bx&&el.classList.contains("nyushi")) add(el,ttsTextOf(el),1);
    else if(bx&&el.classList.contains("point")) add(el,"まとめ。"+ttsTextOf(el),1); });''')

# 2) 再生・一時停止・停止・段落タップをキャラの声にも対応させる
rep('''function ttsPlay(){ if(!ttsOK()) return; if(tts.st==="idle"){ tts.items=ttsCollect(); tts.k=0; tts.s=0; }
  tts.st="play"; tts.gen++; speechSynthesis.cancel(); ttsRender(); setTimeout(()=>{ if(tts.st==="play") ttsSpeak(); },80); }
function ttsPause(){ if(tts.st!=="play") return; tts.st="pause"; tts.gen++; try{speechSynthesis.cancel();}catch(e){} ttsRender(); }
function ttsStop(){ const was=tts.st!=="idle"; tts.st="idle"; tts.gen++; tts.items=[]; tts.k=0; tts.s=0;
  if(was&&ttsOK()){ try{speechSynthesis.cancel();}catch(e){} } document.querySelectorAll(".tts-cur").forEach(x=>x.classList.remove("tts-cur")); }
function ttsJump(el){ const i=tts.items.findIndex(x=>x.el===el); if(i<0) return; tts.k=i; tts.s=0; tts.st="pause"; ttsPlay(); }''',
'''function ttsPlay(){
  if(tts.st==="idle"){ const v=vvCur(); tts.mode=v?"vv":"device"; tts.items=v?vvItems():ttsCollect(); tts.k=0; tts.s=0; tts.vvSeek=true; }
  if(tts.mode==="vv"){ vvUnlock(); tts.st="play"; ttsRender(); vvStart(); return; }
  if(!ttsOK()) return;
  tts.st="play"; tts.gen++; speechSynthesis.cancel(); ttsRender(); setTimeout(()=>{ if(tts.st==="play") ttsSpeak(); },80); }
function ttsPause(){ if(tts.st!=="play") return; tts.st="pause"; tts.gen++;
  if(tts.mode==="vv"){ if(VV.audio) VV.audio.pause(); } else { try{speechSynthesis.cancel();}catch(e){} } ttsRender(); }
function ttsStop(){ const was=tts.st!=="idle"; tts.st="idle"; tts.gen++; tts.items=[]; tts.k=0; tts.s=0;
  VV.cur=""; if(VV.audio&&!VV.audio.paused){ VV.switching=true; VV.audio.pause(); VV.switching=false; }   // cur を空に：あとから届く pause の知らせを無視する
  if(was&&ttsOK()){ try{speechSynthesis.cancel();}catch(e){} } document.querySelectorAll(".tts-cur").forEach(x=>x.classList.remove("tts-cur")); }
function ttsJump(el){ const i=tts.items.findIndex(x=>x.el===el); if(i<0) return; tts.k=i; tts.s=0;
  if(tts.mode==="vv"){ const T=tts.vvT; if(VV.audio&&T&&T[i]&&VV.audio.src===VV.cur){ VV.audio.currentTime=T[i][0]; ttsMark(el); if(VV.audio.paused){ tts.st="play"; VV.audio.play().catch(()=>{}); ttsRender(); } return; }
    tts.vvSeek=true; tts.st="pause"; ttsPlay(); return; }
  tts.st="pause"; ttsPlay(); }
/* 声を変えたとき・枠の設定を変えたときに、いまの段落から読みなおす */
function ttsRestartAt(el){ const was=tts.st; ttsStop(); if(was==="idle") { ttsRender(); return; } ttsPlay(); if(el){ const i=tts.items.findIndex(x=>x.el===el); if(i>0){ tts.k=i; if(tts.mode==="device"){ tts.gen++; speechSynthesis.cancel(); setTimeout(()=>{ if(tts.st==="play") ttsSpeak(); },80); } } }
  if(was==="pause"){ ttsPause(); } }

/* ---- キャラクターの声（VOICEVOX で前もって作った音声）。一覧は audio/voices.json ---- */
const VV={man:null,audio:null,blobs:new Map(),cur:"",unlocked:false,switching:false,loading:false,prevT:0};
function vvItems(){ return ttsCollect(true); }
function vvHash(items){ let h=0x811c9dc5; const t=items.map(x=>(x.box?"#":"")+x.sents.join("|")).join("\\n");
  for(let i=0;i<t.length;i++){ h^=t.charCodeAt(i); h=Math.imul(h,16777619)>>>0; } return h.toString(16); }
function vvLoadMan(){ if(location.protocol==="file:") return; try{ fetch("audio/voices.json",{cache:"no-cache"}).then(r=>r.ok?r.json():null).then(j=>{ if(j&&j.lessons){ VV.man=j; if(tts.st==="idle") ttsRender(); } }).catch(()=>{}); }catch(e){} }
function vvLesson(){ return VV.man?VV.man.lessons[activeId+":"+lIdx]||null:null; }
/* この授業で使えるキャラの声（原稿が音声と同じときだけ） */
function vvAvail(){ const e=vvLesson(); if(!e) return []; if(e._ok==null){ try{ e._ok=vvHash(vvItems())===e.hash; }catch(err){ e._ok=false; } }
  return e._ok?VV.man.voices.filter(v=>e.by[v.id]):[]; }
function vvCur(){ const m=/^vv:(\\d+)$/.exec(tts.cfg.voice||""); if(!m) return null; return vvAvail().find(v=>v.id===+m[1])||null; }
function vvWanted(){ const m=/^vv:(\\d+)$/.exec(tts.cfg.voice||""); return m&&VV.man?VV.man.voices.find(v=>v.id===+m[1])||null:null; }
function vvLabel(v){ return v.name+(v.style&&!/^(ノーマル|ふつう)$/.test(v.style)?"（"+v.style+"）":""); }
function vvSilent(){ const n=2400, b=new ArrayBuffer(44+n*2), d=new DataView(b), w=(o,t)=>{ for(let i=0;i<t.length;i++) d.setUint8(o+i,t.charCodeAt(i)); };
  w(0,"RIFF"); d.setUint32(4,36+n*2,true); w(8,"WAVE"); w(12,"fmt "); d.setUint32(16,16,true); d.setUint16(20,1,true); d.setUint16(22,1,true);
  d.setUint32(24,24000,true); d.setUint32(28,48000,true); d.setUint16(32,2,true); d.setUint16(34,16,true); w(36,"data"); d.setUint32(40,n*2,true);
  return URL.createObjectURL(new Blob([b],{type:"audio/wav"})); }
function vvEl(){ if(VV.audio) return VV.audio; const a=new Audio(); a.preload="auto"; a.setAttribute("playsinline",""); try{ a.preservesPitch=true; a.webkitPreservesPitch=true; }catch(e){}
  a.addEventListener("timeupdate",vvTick);
  a.addEventListener("ended",()=>{ if(tts.mode==="vv"&&tts.st!=="idle"&&a.src===VV.cur){ ttsStop(); ttsRender(); toast("読み上げおわり"); } });
  a.addEventListener("pause",()=>{ if(!VV.switching&&tts.mode==="vv"&&tts.st==="play"&&a.src===VV.cur&&!a.ended){ tts.st="pause"; ttsRender(); } });
  a.addEventListener("play",()=>{ if(!VV.switching&&tts.mode==="vv"&&tts.st==="pause"&&a.src===VV.cur){ tts.st="play"; ttsRender(); } });
  VV.audio=a; return a; }
/* iPhone：最初のタップの中で一度鳴らしておくと、あとで（読みこみが終わってから）鳴らせる */
function vvUnlock(){ const a=vvEl(); if(VV.unlocked) return; VV.unlocked=true; VV.switching=true; try{ a.src=vvSilent(); const p=a.play(); if(p&&p.catch) p.catch(()=>{}); }catch(e){} VV.switching=false; }
async function vvBlob(url){ if(VV.blobs.has(url)) return VV.blobs.get(url); const r=await fetch(url); if(!r.ok) throw new Error("HTTP "+r.status);
  const u=URL.createObjectURL(await r.blob()); VV.blobs.set(url,u); return u; }
function vvWaitMeta(a){ return a.readyState>=1?Promise.resolve():new Promise((res,rej)=>{ const ok=()=>{ off(); res(); }, ng=()=>{ off(); rej(new Error("audio")); }, off=()=>{ a.removeEventListener("loadedmetadata",ok); a.removeEventListener("error",ng); };
  a.addEventListener("loadedmetadata",ok); a.addEventListener("error",ng); }); }
async function vvStart(){ const v=vvCur(), e=vvLesson(); if(!v||!e){ tts.mode="device"; ttsStop(); ttsPlay(); return; }
  const info=e.by[v.id], my=++tts.gen, a=vvEl(); tts.vvT=info.t; tts.vvV=v;
  try{ VV.loading=true; ttsRender(); const src=await vvBlob(info.f); if(my!==tts.gen||tts.st!=="play") return;
    VV.switching=true; const fresh=a.src!==src||VV.cur!==src; if(a.src!==src){ a.src=src; } VV.cur=src; a.playbackRate=tts.cfg.rate; a.defaultPlaybackRate=tts.cfg.rate;
    await vvWaitMeta(a); if(my!==tts.gen||tts.st!=="play"){ VV.switching=false; return; }
    if(tts.vvSeek||fresh){ const t=(info.t[tts.k]||[0])[0]||0; if(Math.abs(a.currentTime-t)>0.3) a.currentTime=t; } tts.vvSeek=false; a.playbackRate=tts.cfg.rate;
    await a.play(); VV.switching=false; vvMedia(v); vvTick(); }
  catch(err){ VV.switching=false; if(my!==tts.gen) return; tts.st="pause";
    toast(navigator.onLine===false?"オフラインです。キャラの声は、ネットにつないで一度聞いた授業だけオフラインで聞けます":"音声を読みこめませんでした。もう一度押してください"); }
  finally{ if(my===tts.gen){ VV.loading=false; ttsRender(); } } }
function vvTick(){ if(tts.mode!=="vv"||tts.st!=="play") return; const a=VV.audio, T=tts.vvT; if(!a||!T||a.src!==VV.cur) return; const ct=a.currentTime;
  let k=0; for(let i=0;i<T.length;i++){ if(T[i][0]<=ct+0.05) k=i; else break; }
  const it=tts.items[k];
  if(it&&it.box&&!tts.cfg.box){ let j=k+1; while(j<tts.items.length&&tts.items[j].box) j++;
    if(j<T.length){ a.currentTime=T[j][0]; k=j; } else { ttsStop(); ttsRender(); toast("読み上げおわり"); return; } }
  if(tts.items[k]&&(k!==tts.k||!tts.items[k].el.classList.contains("tts-cur"))){ tts.k=k; ttsMark(tts.items[k].el); } }
function vvMedia(v){ if(!("mediaSession" in navigator)) return; try{ const p=cur(), l=p.lessons[lIdx];
  navigator.mediaSession.metadata=new MediaMetadata({title:"授業"+(l.no||lIdx+1)+"　"+(l.title||""),artist:v.credit,album:p.title});
  navigator.mediaSession.setActionHandler("play",()=>{ if(tts.st==="pause") ttsPlay(); });
  navigator.mediaSession.setActionHandler("pause",()=>ttsPause()); }catch(e){} }
/* 声を選んだとき、止まっていれば少しだけ試しに鳴らす */
async function vvPreview(v){ const e=vvLesson(); if(!e||!e.by[v.id]) return; const a=vvEl(); vvUnlock(); const my=++tts.gen;
  try{ const info=e.by[v.id], src=await vvBlob(info.f); if(my!==tts.gen||tts.st!=="idle") return; VV.switching=true; a.src=src; VV.cur=""; await vvWaitMeta(a);
    a.currentTime=(info.t[1]||info.t[0])[0]; a.playbackRate=tts.cfg.rate; await a.play(); VV.switching=false;
    setTimeout(()=>{ if(my===tts.gen&&tts.st==="idle"){ VV.switching=true; a.pause(); VV.switching=false; } },4000); }catch(err){ VV.switching=false; } }
vvLoadMan();''')

# 3) 声のメニュー：キャラの声と端末の声
rep('''function ttsVoiceSel(){ const vs=ttsVoices(); if(!vs.length) return ""; if(!tts.voice) tts.voice=ttsPickVoice(); const cu=tts.voice?(tts.voice.voiceURI||tts.voice.name):"";
  const seen={}; return `<select class="tts-sub tts-voice" aria-label="読み上げの声">${vs.map(v=>{ let lb=ttsVLabel(v); seen[lb]=(seen[lb]||0)+1; if(seen[lb]>1) lb+=" "+seen[lb]; const k=v.voiceURI||v.name;
    return `<option value="${k.replace(/"/g,"&quot;")}"${k===cu?" selected":""}>声：${lb}</option>`; }).join("")}</select>`; }''',
'''function ttsVoiceSel(){ const vs=ttsVoices(), cv=vvAvail(); if(!vs.length&&!cv.length) return ""; if(!tts.voice) tts.voice=ttsPickVoice();
  const vc=vvCur(), cu=vc?"vv:"+vc.id:(tts.voice?(tts.voice.voiceURI||tts.voice.name):"");
  const seen={}, dev=vs.map(v=>{ let lb=ttsVLabel(v); seen[lb]=(seen[lb]||0)+1; if(seen[lb]>1) lb+=" "+seen[lb]; const k=v.voiceURI||v.name;
    return `<option value="${k.replace(/"/g,"&quot;")}"${k===cu?" selected":""}>声：${lb}</option>`; }).join("");
  const ch=cv.map(v=>`<option value="vv:${v.id}"${"vv:"+v.id===cu?" selected":""}>声：${vvLabel(v)}</option>`).join("");
  return `<select class="tts-sub tts-voice" aria-label="読み上げの声">${ch?`<optgroup label="キャラクターの声（VOICEVOX）">${ch}</optgroup>`:""}${dev?`<optgroup label="端末の声">${dev}</optgroup>`:""}</select>`; }''')

# 4) バー：キャラの声なら端末の声がなくても出す。クレジット・読みこみ中・キャラの声がない授業の案内
rep('''  if(!ttsOK()||!ttsAllowed()){ bar.hidden=true; bar.innerHTML=""; return; } bar.hidden=false;''',
'''  if(!ttsAllowed()||(!ttsOK()&&!vvAvail().length)){ bar.hidden=true; bar.innerHTML=""; return; } bar.hidden=false;''')
rep('''    `<span class="tts-hint">${tts.st==="idle"?"授業を声で読みます。ふりがなの読みで読みます。":"段落をタップすると、そこから読みます。"}</span>`; }''',
'''    `<span class="tts-hint">${ttsHint()}</span>`; }
function ttsHint(){ const vc=(tts.st!=="idle"&&tts.mode==="vv")?tts.vvV:vvCur(), want=vvWanted();
  let h=VV.loading?"音声を読みこんでいます…":(tts.st==="idle"?"授業を声で読みます。ふりがなの読みで読みます。":"段落をタップすると、そこから読みます。");
  if(vc) h+=`<br>音声：${vc.credit}`;
  else if(want) h+=`<br>この授業には「${vvLabel(want)}」の声がまだないので、端末の声で読みます。`;
  return h; }''')

# 5) 声を選んだとき
rep('''document.addEventListener("change",e=>{ const vsel=e.target.closest("#ttsBar .tts-voice"); if(vsel){ const v=ttsVoices().find(x=>(x.voiceURI||x.name)===vsel.value); if(!v) return;
    tts.voice=v; tts.cfg.voice=vsel.value; ttsSave();''',
'''document.addEventListener("change",e=>{ const vsel=e.target.closest("#ttsBar .tts-voice");
  if(vsel&&/^vv:/.test(vsel.value)){ const v=vvAvail().find(x=>"vv:"+x.id===vsel.value); if(!v) return; tts.cfg.voice=vsel.value; ttsSave();
    if(tts.st!=="idle"){ ttsRestartAt((tts.items[tts.k]||{}).el); } else { ttsRender(); vvPreview(v); } return; }
  if(vsel){ const v=ttsVoices().find(x=>(x.voiceURI||x.name)===vsel.value); if(!v) return;
    const wasVV=tts.st!=="idle"&&tts.mode==="vv"; tts.voice=v; tts.cfg.voice=vsel.value; ttsSave();
    if(wasVV){ ttsRestartAt((tts.items[tts.k]||{}).el); return; }
    if(tts.st==="idle"&&VV.audio&&!VV.audio.paused){ VV.switching=true; VV.audio.pause(); VV.switching=false; }''')
# 速さ：キャラの声なら音声の再生速度を変える
rep('''  tts.cfg.rate=r; ttsSave(); if(tts.st==="play"){ tts.gen++; speechSynthesis.cancel(); setTimeout(()=>{ if(tts.st==="play") ttsSpeak(); },80); } });''',
'''  tts.cfg.rate=r; ttsSave(); if(tts.mode==="vv"&&tts.st!=="idle"){ if(VV.audio){ VV.audio.playbackRate=r; VV.audio.defaultPlaybackRate=r; } return; }
  if(tts.st==="play"){ tts.gen++; speechSynthesis.cancel(); setTimeout(()=>{ if(tts.st==="play") ttsSpeak(); },80); } });''')
# 枠の切りかえ：キャラの声なら、再生はそのまま（枠に来たらとばす）
rep('''    else if(a==="box"){ tts.cfg.box=!tts.cfg.box; ttsSave(); if(tts.st!=="idle"){''',
'''    else if(a==="box"){ tts.cfg.box=!tts.cfg.box; ttsSave(); if(tts.st!=="idle"&&tts.mode==="vv"){ vvTick(); ttsRender(); return; } if(tts.st!=="idle"){''')
# 画面を消したとき：キャラの声は止めない
rep('''document.addEventListener("visibilitychange",()=>{ if(document.hidden) ttsPause(); });''',
'''document.addEventListener("visibilitychange",()=>{ if(document.hidden&&tts.mode!=="vv") ttsPause(); });''')
# tts の状態に mode を足す
rep('''const tts={st:"idle",items:[],k:0,s:0,gen:0,voice:null,''','''const tts={st:"idle",mode:"device",items:[],k:0,s:0,gen:0,voice:null,vvT:null,vvV:null,vvSeek:false,''')

# 6) ガイドの読み上げ・声のページを、iPhone の実際に合わせて書き直す
rep("<li><span class='g-ui sub'>声：Kyoko</span> で声を選べる（声の増やし方は次のページ）</li>",
    "<li><span class='g-ui sub'>声：…</span> で声を選べる。<b>キャラクターの声</b>（ずんだもん・四国めたん など）か、<b>端末の声</b>（Kyoko）</li>")
rep("<div class='g-note'>ふりがなのある語は、ふりがなの読みで読みます（漢字とふりがなを二重には読みません）。<br>画面を消したり、ほかのアプリに切りかえると止まります。もどったら「▶ つづきから」。</div>",
    "<div class='g-note'>ふりがなのある語は、ふりがなの読みで読みます（漢字とふりがなを二重には読みません）。<br>キャラクターの声は、画面を消しても続きます。端末の声は、画面を消すと止まるので、もどったら「▶ つづきから」。</div>")
i=s.index("<section class='g-slide' data-i='5'>"); j=s.index("</section>",i)+len("</section>")
s=s[:i]+("<section class='g-slide' data-i='5'><div class='g-ico'>🎙</div><h3>声のえらび方</h3>"
 "<ol class='g-list'><li>授業の <span class='g-ui sub'>声：…</span> を押す</li><li>上の<b>「キャラクターの声（VOICEVOX）」</b>から選ぶ。選ぶと少しだけ試しに読む</li>"
 "<li>キャラクターの声は、前もって作った音声です。<b>まだ一部の授業にしかありません</b>。ない授業では、自動で端末の声（Kyoko）で読みます</li>"
 "<li>ネットにつないで一度聞いた授業は、オフラインでもキャラクターの声で聞ける</li></ol>"
 "<div class='g-note'><b>端末の声について</b>：iPhone では、このアプリが使える端末の声は <b>Kyoko だけ</b>です（iPhone の制限）。設定で O-ren や Otoya をダウンロードしても、このアプリには出てきません。<br>Kyoko の高品質版を使いたいときは：設定 › アクセシビリティ › リーダーと読み上げ › 声 › 日本語 › Kyoko（拡張）をダウンロード → アプリを開き直して「声：」で選ぶ（出てこないこともあります）。</div>"
 "<div class='g-note' id='gCredits'>キャラクターの声：VOICEVOX</div></section>")+s[j:]
rep('''function guideOpen(i){ document.getElementById("guide").classList.add("open");''',
'''function guideCredits(){ const c=document.getElementById("gCredits"); if(!c) return; const cr=VV.man?[...new Set(VV.man.voices.map(v=>v.credit))]:[];
  c.textContent="キャラクターの声のクレジット："+(cr.length?cr.join("、"):"VOICEVOX"); }
function guideOpen(i){ guideCredits(); document.getElementById("guide").classList.add("open");''')
open(dst,'w',encoding='utf-8').write(s); print('ok')
