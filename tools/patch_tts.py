# 授業の読み上げ（試し：古代① 授業01 だけ）を入れる。2026-11-14 ユーザーの指示。
#   python3 patch_tts.py ../app/source.html ../app/source.html
# しくみ：端末の声（Web Speech API の speechSynthesis）を使う。外から何も読み込まないので、オフラインでも動く。
#  - ふりがなのある語は、ふりがな（カタカナにして）だけを読む。漢字とふりがなを二重に読まない。
#  - 2回目からふりがなが付いていない語も、授業の中や全セットのふりがなから読みを引いて読む（読みが一つに決まる語だけ）。
#  - 「（古代② 授業03）」のような参照、問いのカード、表、難関私大の欄は読まない。
#  - 広げるときは TTS_TRIAL に pack の id と授業の番号（0から）を足す。全授業にするなら ttsAllowed を true にする。
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
if 'id="ttsBar"' in s:
    print('already'); sys.exit(0)

CSS=r'''
  /* 読み上げ（試し） */
  .tts-bar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:2px 0 16px;}
  .tts-bar[hidden]{display:none;}
  .tts-bar button{font-family:var(--gothic);font-size:12.5px;font-weight:600;padding:7px 13px;border-radius:999px;border:1px solid var(--gold-deep);background:transparent;color:var(--gold);cursor:pointer;-webkit-tap-highlight-color:transparent;}
  .tts-bar button.tts-main{background:var(--gold);color:#1a140a;border-color:var(--gold);}
  .tts-bar select.tts-sub{font-family:var(--gothic);font-size:12.5px;font-weight:500;padding:7px 12px;border-radius:999px;border:1px solid var(--line,rgba(255,255,255,.18));background:transparent;color:var(--ivory-dim);-webkit-appearance:none;appearance:none;}
  .tts-bar select.tts-sub option{color:#1a140a;}
  .tts-bar button.tts-sub{border-color:var(--line,rgba(255,255,255,.18));color:var(--ivory-dim);font-weight:500;}
  .tts-bar .tts-hint{flex-basis:100%;font-size:11.5px;color:var(--ash);line-height:1.6;}
  #lBody .tts-cur{background:rgba(201,162,74,.13);border-radius:8px;box-shadow:0 0 0 6px rgba(201,162,74,.13);transition:background .2s;}
  #lTitle.tts-cur{background:rgba(201,162,74,.13);border-radius:6px;}

'''
a="  /* ふりがな：<ruby>を独自の要素に置きかえて"
assert s.count(a)==1; s=s.replace(a,CSS+a)

a='      <p class="theme" id="lTheme">—</p>\n'
assert s.count(a)==1; s=s.replace(a,a+'      <div class="tts-bar" id="ttsBar" hidden></div>\n')

a='function showLesson(i){\n  const p=cur();'
assert s.count(a)==1; s=s.replace(a,'function showLesson(i){\n  ttsStop();\n  const p=cur();')
a='  else cb.style.display="none";\n}'
assert s.count(a)==1; s=s.replace(a,'  else cb.style.display="none";\n  ttsRender();\n}')
a='function switchSec(k){ '
assert s.count(a)==1; s=s.replace(a,'function switchSec(k){ if(k!=="lesson") ttsStop(); ')

JS=r'''/* ---- 授業の読み上げ（試し：古代① 授業01 だけ）。端末の声（Web Speech API）を使うので、オフラインでも動く ---- */
const TTS_TRIAL={kodai:[0]};          // 読み上げを出す授業（pack の id → 授業の番号。0 から）
const TTS_KEY="nihonshi_tts";          // 速さ・枠を読むかの設定だけ（学習記録とは別）
const TTS_RATES=[0.8,1,1.2,1.3,1.4,1.5];
const tts={st:"idle",items:[],k:0,s:0,gen:0,voice:null,cfg:Object.assign({rate:1,box:true},lsGet(TTS_KEY)||{})};
if(!TTS_RATES.includes(+tts.cfg.rate)) tts.cfg.rate=1; else tts.cfg.rate=+tts.cfg.rate;
let _ttsDict=null;
/* 機械が読みまちがえやすい語の読み（声のためだけ。画面のふりがなは変えない）。授業を足すたびに、読み上げの文字列を確かめて足す */
const TTS_RD={"ナイフ形石器":"ナイフがたせっき","笠懸村":"かさかけむら","第四紀":"だいよんき","槍先形":"やりさきがた","柄のみぞ":"えのみぞ","洞穴":"ほらあな","20歳":"はたち","白滝遺跡群":"しらたきいせきぐん"};
function ttsApplyRd(t){ for(const k in TTS_RD) t=t.split(k).join(TTS_RD[k]); return t; }
function ttsOK(){ return typeof window!=="undefined"&&"speechSynthesis" in window&&typeof SpeechSynthesisUtterance!=="undefined"; }
function ttsAllowed(){ const a=TTS_TRIAL[activeId]; return !!(a&&a.includes(lIdx)); }
function ttsPickVoice(){ try{ const vs=speechSynthesis.getVoices().filter(v=>/^ja/i.test(v.lang)); if(!vs.length) return null;
  const sc=v=>(/premium|enhanced|拡張|プレミアム/i.test(v.name)?4:0)+(v.localService?2:0)+(/kyoko|o-ren|otoya|hattori/i.test(v.name)?1:0);
  return vs.sort((a,b)=>sc(b)-sc(a))[0]; }catch(e){ return null; } }
if(ttsOK()&&speechSynthesis.addEventListener) speechSynthesis.addEventListener("voiceschanged",()=>{ tts.voice=ttsPickVoice(); });
const ttsKata=t=>t.replace(/[ぁ-ゖ]/g,c=>String.fromCharCode(c.charCodeAt(0)+0x60));
const ttsIsKan=c=>!!c&&/[㐀-鿿々〆ヶ]/.test(c);
/* 読みの辞書：ふりがなの「漢字 → 読み」。読みが一つに決まる語だけ使う（2字以上） */
function ttsPairs(h,into){ const RE=/<ruby>([^<]+)<rt>([^<]+)<\/rt><\/ruby>/g; let m;
  while(m=RE.exec(h||"")){ const b=m[1].trim(), r=m[2].trim(); if(b.length<2||!ttsIsKan(b[0])&&!ttsIsKan(b[b.length-1])) continue; (into[b]=into[b]||{})[r]=1; } return into; }
function ttsGlobal(){ if(_ttsDict) return _ttsDict; const seen={};
  Object.keys(packsById).forEach(id=>(packsById[id].lessons||[]).forEach(l=>ttsPairs((l.html||"")+(l.colHtml||""),seen)));
  _ttsDict={}; for(const b in seen){ const rs=Object.keys(seen[b]); if(rs.length===1) _ttsDict[b]=rs[0]; } return _ttsDict; }
function ttsDictFor(l){ const d=Object.assign({},ttsGlobal()), loc=ttsPairs(l.html||"",{});
  for(const b in loc){ const rs=Object.keys(loc[b]); if(rs.length===1) d[b]=rs[0]; } return d; }
/* 漢字の語を、前後が漢字でないところだけ読みに置きかえる（長い語から） */
function ttsApplyDict(t,d){ const keys=Object.keys(d).filter(k=>t.indexOf(k)>=0).sort((a,b)=>b.length-a.length); if(!keys.length) return t;
  const re=new RegExp(keys.map(k=>k.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).join("|"),"g");
  return t.replace(re,(m,i,all)=>{ const pv=all[i-1], nx=all[i+m.length]; return (ttsIsKan(pv)||ttsIsKan(nx))?m:ttsKata(d[m]); }); }
/* 記号を声にしやすく直す */
function ttsNorm(t){ return t.replace(/（[^（）]*授業\s*\d{2}[^（）]*）/g,"").replace(/（[\s、・,]*）/g,"")
  .replace(/(\d)\s*[〜～]\s*(\d)/g,"$1から$2").replace(/[〜～]/g,"から").replace(/[→⇒]/g,"、").replace(/[＝=]/g,"、").replace(/×/g,"と")
  .replace(/[・／]/g,"、").replace(/[■▶▼★☆※◆●○]/g,"").replace(/[ 　\s]+/g," ").replace(/、\s*、/g,"、").replace(/^[、\s]+/,"").trim(); }
/* 1つの段落・枠を、読む文字列にする（ふりがなは読みだけ、参照ボタン・問いのカードは読まない） */
function ttsTextOf(el){ let out="";
  const walk=n=>{ if(n.nodeType===3){ out+=n.nodeValue; return; } if(n.nodeType!==1) return;
    const c=n.classList, tg=n.tagName;
    if(c.contains("rtx")||tg==="RT"||tg==="RP"||c.contains("xref")||tg==="BUTTON"||tg==="svg"||tg==="SVG"||c.contains("qcheck")) return;
    if(c.contains("rbx")||tg==="RUBY"){ const r=n.querySelector(".rtx,rt"); if(r){ out+=ttsKata(r.textContent.trim()); return; } }
    if(c.contains("bx-tag")||c.contains("yd-tag")){ out+=n.textContent.trim()+"。"; return; }
    if(tg==="B"&&n.parentNode&&n.parentNode.classList&&n.parentNode.classList.contains("yodan")){ n.childNodes.forEach(walk); if(!/[。！？]$/.test(out)) out+="。"; return; }
    n.childNodes.forEach(walk); };
  walk(el); return out; }
function ttsSplit(t){ const a=t.match(/[^。！？]*[。！？]+[」』）]*|[^。！？]+$/g)||[]; return a.map(x=>x.trim()).filter(x=>x&&/[^\s。、」』）]/.test(x)); }
function ttsCollect(){ const p=cur(), l=p.lessons[lIdx], d=ttsDictFor(l), items=[];
  const add=(el,raw)=>{ const t=ttsNorm(ttsApplyDict(ttsApplyRd(raw),d)); const ss=ttsSplit(t); if(ss.length) items.push({el,sents:ss}); };
  const ti=document.getElementById("lTitle"); add(ti,"授業"+(+(l.no||lIdx+1))+"。"+ttsTextOf(ti)+"。");
  [...document.getElementById("lBody").children].forEach(el=>{
    if(el.tagName==="P"&&!el.classList.contains("xhint")) add(el,ttsTextOf(el));
    else if(tts.cfg.box&&el.classList.contains("yodan")) add(el,ttsTextOf(el));
    else if(tts.cfg.box&&el.classList.contains("nyushi")) add(el,ttsTextOf(el));
    else if(tts.cfg.box&&el.classList.contains("point")) add(el,"まとめ。"+ttsTextOf(el)); });
  return items; }
function ttsMark(el){ document.querySelectorAll(".tts-cur").forEach(x=>x.classList.remove("tts-cur")); if(!el) return; el.classList.add("tts-cur");
  const r=el.getBoundingClientRect(), vh=window.innerHeight; if(r.top<70||r.top>vh*0.6) window.scrollTo(0,Math.max(0,r.top+window.scrollY-110)); }
function ttsSpeak(){ const my=++tts.gen;
  while(tts.k<tts.items.length&&tts.s>=tts.items[tts.k].sents.length){ tts.k++; tts.s=0; }
  const it=tts.items[tts.k]; if(!it){ ttsStop(); toast("読み上げおわり"); return; }
  if(tts.s===0||!it.el.classList.contains("tts-cur")) ttsMark(it.el);
  const u=new SpeechSynthesisUtterance(it.sents[tts.s]); u.lang="ja-JP"; if(!tts.voice) tts.voice=ttsPickVoice(); if(tts.voice) u.voice=tts.voice;
  u.rate=tts.cfg.rate; u.pitch=1;
  u.onend=()=>{ if(my!==tts.gen||tts.st!=="play") return; tts.s++; ttsSpeak(); };
  u.onerror=e=>{ if(my!==tts.gen||tts.st!=="play") return; if(e&&(e.error==="interrupted"||e.error==="canceled")) return; tts.s++; ttsSpeak(); };
  speechSynthesis.speak(u); }
/* 一時停止は「止めて、いまの文から読みなおす」にする（iPhone の pause/resume は不安定なため） */
function ttsPlay(){ if(!ttsOK()) return; if(tts.st==="idle"){ tts.items=ttsCollect(); tts.k=0; tts.s=0; }
  tts.st="play"; tts.gen++; speechSynthesis.cancel(); ttsRender(); setTimeout(()=>{ if(tts.st==="play") ttsSpeak(); },80); }
function ttsPause(){ if(tts.st!=="play") return; tts.st="pause"; tts.gen++; try{speechSynthesis.cancel();}catch(e){} ttsRender(); }
function ttsStop(){ const was=tts.st!=="idle"; tts.st="idle"; tts.gen++; tts.items=[]; tts.k=0; tts.s=0;
  if(was&&ttsOK()){ try{speechSynthesis.cancel();}catch(e){} } document.querySelectorAll(".tts-cur").forEach(x=>x.classList.remove("tts-cur")); }
function ttsJump(el){ const i=tts.items.findIndex(x=>x.el===el); if(i<0) return; tts.k=i; tts.s=0; tts.st="pause"; ttsPlay(); }
function ttsSave(){ lsSet(TTS_KEY,tts.cfg); }
function ttsRender(){ const bar=document.getElementById("ttsBar"); if(!bar) return;
  if(!ttsOK()||!ttsAllowed()){ bar.hidden=true; bar.innerHTML=""; return; } bar.hidden=false;
  const main=tts.st==="play"?"⏸ 一時停止":(tts.st==="pause"?"▶ つづきから":"▶ 読み上げ");
  bar.innerHTML=`<button type="button" class="tts-main" data-a="main">${main}</button>`+(tts.st!=="idle"?`<button type="button" data-a="stop">■ 停止</button>`:"")+
    `<select class="tts-sub tts-rate" aria-label="読み上げの速さ">${TTS_RATES.map(r=>`<option value="${r}"${r===tts.cfg.rate?" selected":""}>速さ ${r}倍</option>`).join("")}</select><button type="button" class="tts-sub" data-a="box">枠も読む：${tts.cfg.box?"オン":"オフ"}</button>`+
    `<span class="tts-hint">${tts.st==="idle"?"授業を声で読みます（ためし）。ふりがなの読みで読みます。":"段落をタップすると、そこから読みます。"}</span>`; }
document.addEventListener("click",e=>{ const b=e.target.closest("#ttsBar button"); if(b){ e.preventDefault(); const a=b.dataset.a;
    if(a==="main"){ tts.st==="play"?ttsPause():ttsPlay(); }
    else if(a==="stop"){ ttsStop(); ttsRender(); }
    else if(a==="box"){ tts.cfg.box=!tts.cfg.box; ttsSave(); if(tts.st!=="idle"){ const curEl=(tts.items[tts.k]||{}).el, wasPlay=tts.st==="play";
        tts.gen++; speechSynthesis.cancel(); tts.items=ttsCollect(); let i=tts.items.findIndex(x=>x.el===curEl);
        if(i<0&&curEl){ i=tts.items.findIndex(x=>curEl.compareDocumentPosition(x.el)&Node.DOCUMENT_POSITION_FOLLOWING); if(i<0) i=tts.items.length; tts.s=0; }
        tts.k=Math.max(0,i); if(wasPlay){ tts.st="pause"; ttsPlay(); } } ttsRender(); }
    return; }
  if(tts.st==="idle") return; if(e.target.closest("button,a,summary,details,.kw,.xref,input,select")) return;
  const el=e.target.closest("#lBody > p, #lBody > .yodan, #lBody > .nyushi, #lBody > .point, #lTitle"); if(el) ttsJump(el); });
document.addEventListener("change",e=>{ const sel=e.target.closest("#ttsBar .tts-rate"); if(!sel) return; const r=+sel.value; if(!TTS_RATES.includes(r)) return;
  tts.cfg.rate=r; ttsSave(); if(tts.st==="play"){ tts.gen++; speechSynthesis.cancel(); setTimeout(()=>{ if(tts.st==="play") ttsSpeak(); },80); } });
document.addEventListener("visibilitychange",()=>{ if(document.hidden) ttsPause(); });

'''
a="/* ふりがなの置きかえ */"
assert s.count(a)==1; s=s.replace(a,JS+a)
open(dst,'w',encoding='utf-8').write(s); print('ok')
