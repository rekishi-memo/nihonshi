# 授業の読み上げを入れる（はじめは古代① 授業01 だけで試し、2026-11-14 に全授業へ広げた）。2026-11-14 ユーザーの指示。
#   python3 patch_tts.py ../app/source.html ../app/source.html
# しくみ：端末の声（Web Speech API の speechSynthesis）を使う。外から何も読み込まないので、オフラインでも動く。
#  - ふりがなのある語は、ふりがな（カタカナにして）だけを読む。漢字とふりがなを二重に読まない。
#  - 2回目からふりがなが付いていない語も、授業の中や全セットのふりがなから読みを引いて読む（読みが一つに決まる語だけ）。
#  - 「（古代② 授業03）」のような参照、問いのカード、表、難関私大の欄は読まない。
#  - 本文の段落がある授業ならどれでも出る（ttsAllowed）。「▶ …」の案内行・思い出そう・整理するのリンク・表・図は読まない。
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
import os,json
_fp=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tts_force.json')
FORCE=json.load(open(_fp,encoding='utf-8')) if os.path.exists(_fp) else {'g':{},'l':{}}
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
  .tts-bar select.tts-voice{max-width:100%;}
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

JS=r'''/* ---- 授業の読み上げ（全授業）。端末の声（Web Speech API）を使うので、オフラインでも動く ---- */
const TTS_KEY="nihonshi_tts";          // 速さ・枠を読むかの設定だけ（学習記録とは別）
const TTS_RATES=[0.8,1,1.2,1.3,1.4,1.5];
const tts={st:"idle",items:[],k:0,s:0,gen:0,voice:null,cfg:Object.assign({rate:1,box:true},lsGet(TTS_KEY)||{})};
if(!TTS_RATES.includes(+tts.cfg.rate)) tts.cfg.rate=1; else tts.cfg.rate=+tts.cfg.rate;
let _ttsDict=null;
/* 読みの置きかえ：音声エンジンに全授業を読ませて確かめ、読みまちがえた語だけを正しい読み（ふりがな・用語集のよみ）に置きかえる。
   tools/tts_check.py が作る tools/tts_force.json（g＝全授業、l＝その授業だけ）。それ以外の語は漢字のまま読ませる */
let TTS_FORCE=@@FORCE@@; let _ttsCurD=null;
/* 機械が読みまちがえやすい語の読み（声のためだけ。画面のふりがなは変えない）。授業を足すたびに、読み上げの文字列を確かめて足す */
const TTS_RD={"ナイフ形石器":"ナイフがたせっき","笠懸村":"かさかけむら","第四紀":"だいよんき","槍先形":"やりさきがた","柄のみぞ":"えのみぞ","洞穴":"ほらあな","20歳":"はたち","白滝遺跡群":"しらたきいせきぐん"};
function ttsApplyRd(t){ for(const k in TTS_RD) t=t.split(k).join(TTS_RD[k]); return t; }
function ttsOK(){ return typeof window!=="undefined"&&"speechSynthesis" in window&&typeof SpeechSynthesisUtterance!=="undefined"; }
function ttsReadP(el){ return el.tagName==="P"&&!el.classList.contains("xhint")&&!el.classList.contains("more")&&!el.classList.contains("seiri-intro"); }
/* 読み上げは全授業（本文の段落がある授業）で出す */
function ttsAllowed(){ const b=document.getElementById("lBody"); return !!(b&&[...b.children].some(ttsReadP)); }
/* 日本語の声の一覧。iPhone で「拡張」「プレミアム」の声をダウンロードすると、ここに増える */
function ttsVoices(){ try{ return speechSynthesis.getVoices().filter(v=>/^ja/i.test(v.lang)); }catch(e){ return []; } }
function ttsVLabel(v){ const u=(v.voiceURI||"")+" "+v.name; return v.name.replace(/\s*[（(].*[)）]\s*$/,"")+(/premium|プレミアム/i.test(u)?"（プレミアム）":/enhanced|拡張/i.test(u)?"（拡張）":""); }
function ttsPickVoice(){ const vs=ttsVoices(); if(!vs.length) return null;
  if(tts.cfg.voice){ const v=vs.find(x=>(x.voiceURI||x.name)===tts.cfg.voice); if(v) return v; }
  const sc=v=>{ const u=(v.voiceURI||"")+" "+v.name; return (/premium|プレミアム/i.test(u)?5:/enhanced|拡張/i.test(u)?4:0)+(v.localService?2:0)+(/kyoko|o-ren|otoya|hattori/i.test(v.name)?1:0); };
  return vs.slice().sort((a,b)=>sc(b)-sc(a))[0]; }
if(ttsOK()&&speechSynthesis.addEventListener) speechSynthesis.addEventListener("voiceschanged",()=>{ tts.voice=ttsPickVoice(); if(tts.st==="idle") ttsRender(); });
const ttsKata=t=>t.replace(/[ぁ-ゖ]/g,c=>String.fromCharCode(c.charCodeAt(0)+0x60));
const ttsIsKan=c=>!!c&&/[㐀-鿿々〆ヶ]/.test(c);
/* 読みの辞書：ふりがなの「漢字 → 読み」。読みが一つに決まる語だけ使う（2字以上） */
function ttsPairs(h,into){ const RE=/<ruby>([^<]+)<rt>([^<]+)<\/rt><\/ruby>/g; let m;
  while(m=RE.exec(h||"")){ const b=m[1].trim(), r=m[2].trim(); if(b.length<2||!ttsIsKan(b[0])&&!ttsIsKan(b[b.length-1])) continue; (into[b]=into[b]||{})[r]=1; } return into; }
function ttsGlobal(){ if(_ttsDict) return _ttsDict; const seen={};
  Object.keys(packsById).forEach(id=>(packsById[id].lessons||[]).forEach(l=>ttsPairs((l.html||"")+(l.colHtml||""),seen)));
  _ttsDict={}; for(const b in seen){ const rs=Object.keys(seen[b]); if(rs.length===1) _ttsDict[b]=rs[0]; } return _ttsDict; }
function ttsDictFor(l){ const d=Object.assign({},TTS_FORCE.g||{},(TTS_FORCE.l||{})[activeId+":"+lIdx]||{}); _ttsCurD=d; return d; }
/* 漢字の語を、前後が漢字でないところだけ読みに置きかえる（長い語から） */
function ttsApplyDict(t,d){ const keys=Object.keys(d).filter(k=>t.indexOf(k)>=0).sort((a,b)=>b.length-a.length); if(!keys.length) return t;
  const re=new RegExp(keys.map(k=>k.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).join("|"),"g");
  return t.replace(re,(m,i,all)=>{ const pv=all[i-1], nx=all[i+m.length]; return (ttsIsKan(pv)||ttsIsKan(nx))?m:ttsKata(d[m]); }); }
/* 記号を声にしやすく直す */
const TTS_CIRC="①②③④⑤⑥⑦⑧⑨⑩";
/* かっこ（　）の中身を、授業らしく読む（2026-11-15 ユーザーの指示）。
   語句の言いかえ →「、すなわち◯◯」「。つまり、◯◯だ」／年 →「527年の磐井の乱」「。643年のことだ」
   「のちの」「いまの」→「、のちの◯◯」／説明の文 → 前後に区切って、そのまま読む */
const TTS_YR=/^(?:紀元前)?[0-9０-９]{1,4}(?:年|世紀|年代)?(?:ごろ|頃)?(?:\s*(?:[〜～\-]|から)\s*[0-9０-９]{1,4}(?:年|世紀)?(?:ごろ|頃)?)?$/;
let _ttsAlt=0; const ttsConj=()=>(_ttsAlt++%2?"つまり":"すなわち");
function ttsYear(y){ y=y.replace(/\s*[〜～\-]\s*/g,"から"); return /(年|世紀|ごろ|頃|年代)$/.test(y)?y:y+"年"; }
function ttsParen(t,plain){ let out="", rest=t, g=0;
  while(g++<60){ const m=/（([^（）]{1,140})）/.exec(rest); if(!m){ out+=rest; break; }
    let pre=out+rest.slice(0,m.index); const y=m[1].trim(), post=rest.slice(m.index+m[0].length), nx=post.charAt(0);
    const end=/^\s*([。！？」』]|$)/.test(post), ptc=/^[をはがにでともへのやだか]/.test(nx), sep=ptc||/^[、。！？」』]/.test(nx)?"":"、";
    let ins="";
    if(!y){ ins=""; }
    else if(plain&&/[一-鿿々ァ-ヶーA-Za-z0-9０-９」』]$/.test(pre)&&(end||/^[、・]/.test(nx))){   // まとめ・入試の枠：「増鏡（公家）」→「増鏡は公家」
      const it=y.split(/、/).map(x=>x.trim()).filter(Boolean), body=TTS_YR.test(y)?ttsYear(y):(it.length>1&&it.every(x=>x.length<=12&&!/[とやにをはがで]$/.test(x))?it.join("と"):it.join("、"));
      ins="は"+(y.length>18?"、":"")+body; }
    else if(TTS_YR.test(y)){ const yy=ttsYear(y), mm=/[一-鿿々ァ-ヶーＡ-Ｚａ-ｚA-Za-z0-9０-９・]+(?:の[一-鿿々ァ-ヶーＡ-Ｚａ-ｚA-Za-z0-9０-９・]+)*$/.exec(pre);
      if(mm&&mm[0].length<=24&&!/^[0-9０-９]/.test(mm[0])){ if(end) ins="。"+yy+"のことだ"; else pre=pre.slice(0,mm.index)+yy+"の"+mm[0]; }
      else ins=end?"。"+yy+"のことだ":"、"+yy+sep; }
    else if(/^(のちの|のちに|後の|いまの|今の|現在の|もとの|もと|旧)/.test(y)){
      if(/^(のちに)/.test(y)||y.length>16) ins=end?"。これは"+y:"、これは"+y+"、"; else ins=end?"、"+y+"だ":"、"+y+sep; }
    else if(y.length>18||(/[をはがにでと]/.test(y)&&/[るたいだうすくむれ]$/.test(y))||(/[をはがで]/.test(y)&&y.length>=6)||(y.length<=4&&/[るたうくすむ]$/.test(y)&&!/[ァ-ヶ一-鿿]$/.test(y))){
      ins=end?"。"+y+(/[るたいだうすくむれ。]$/.test(y)?"":"だ"):"、"+y+"、"; }
    else { const it=y.split(/、/).map(x=>x.trim()).filter(Boolean), yr=it.filter(x=>TTS_YR.test(x)); let body;
      if(it.length===2&&yr.length===1){ body=ttsYear(yr[0])+"の"+it.find(x=>!TTS_YR.test(x)); }
      else if(it.length>1&&it.every(x=>x.length<=12&&!/[0-9０-９]/.test(x)&&!/[とやにをはがで]$/.test(x))) body=it.join("や");
      else body=it.join("、");
      const c=ttsConj(); ins=end?"。"+c+"、"+body+"だ":"、"+c+body+sep; }
    out=pre+ins; rest=post; }
  return out.replace(/[（）]/g,"、").replace(/、\s*、/g,"、").replace(/、([。！？」』])/g,"$1").replace(/。\s*。/g,"。").replace(/^[、。\s]+/,""); }
/* 枠の見出しを、講師の話し方にする */
const TTS_TAGS={"入試ではこう出る":"入試では、こう出るよ","ちょっと脱線":"ちょっと脱線するね","前の授業から":"まず、前の授業のふり返りから","次の授業へ":"では、次の授業へつなげよう","難関＋":"難関大学をめざす人へ、もう一歩"};
/* 記号を、講師がしゃべるように：＝はイコール、「A：B」は「Aは、B」、「A→B」は「AからBへ」（長いときは「A、そしてB」）、「A・B」の2つ並びは「AとB」 */
function ttsSym(t){
  t=t.replace(/\s*[＝=]\s*/g,"イコール");
  t=t.replace(/([^\s、。：:「」（）]{1,14})[：:](?!\d)\s*/g,"$1は、").replace(/[：:](?!\d)/g,"、");
  t=t.replace(/(^|[、。\s「（])([^、。・\s→⇒「」（）]{1,12})[→⇒]([^、。・\s→⇒「」（）]{1,12})(?=[、。・\s」）]|$)/g,(m,a,x,y)=>a+x+"から"+y+"へ");
  t=t.replace(/\s*[→⇒]\s*/g,"、そして");
  t=t.replace(/(^|[、。\s「（は])([^、。・\s「」（）]{1,12})・([^、。・\s「」（）]{1,12})(?=[、。\s」）はがをにでの]|$)/g,(m,a,x,y)=>(/^[ァ-ヶー]+$/.test(x)&&/^[ァ-ヶー]+$/.test(y))?m:a+x+"と"+y);
  return t; }
function ttsNorm(t,plain){ return ttsParen(ttsSym(t.replace(/（[^（）]*授業\s*\d{2}[^（）]*）/g,"").replace(/（[\s、・,]*）/g,"")),plain)
  .replace(/(\d{3,4})\.(\d{1,2})\.(\d{1,2})/g,"$1年$2月$3日").replace(/[①-⑩]/g,c=>(TTS_CIRC.indexOf(c)+1)+"、")
  .replace(/([^\s、。（）「」＞]+)＞([^\s、。（）「」＞]+)/g,"$1が$2を上回り").replace(/＞/g,"より大きい").replace(/\s*\bvs\.?\s*/gi,"たい").replace(/[：:](?!\d)/g,"、").replace(/[―—]/g,"、")
  .replace(/(\d)\s*[〜～]\s*(\d)/g,"$1から$2").replace(/[〜～]/g,"から").replace(/[→⇒]/g,"、").replace(/[＝=]/g,"、").replace(/×/g,"と")
  .replace(/[・／\/]/g,"、").replace(/＋/g,"と").replace(/[■▶▼★☆※◆●○]/g,"").replace(/[ 　\s]+/g," ").replace(/、\s*、/g,"、").replace(/^[、\s]+/,"").trim(); }
/* 1つの段落・枠を、読む文字列にする（ふりがなは読みだけ、参照ボタン・問いのカードは読まない） */
function ttsTextOf(el){ let out="";
  const walk=n=>{ if(n.nodeType===3){ out+=n.nodeValue; return; } if(n.nodeType!==1) return;
    const c=n.classList, tg=n.tagName;
    if(c.contains("rtx")||tg==="RT"||tg==="RP"||c.contains("xref")||tg==="BUTTON"||tg==="svg"||tg==="SVG"||c.contains("qcheck")) return;
    if(c.contains("rbx")||tg==="RUBY"){ const r=n.querySelector(".rtx,rt"); if(r){ const base=[...n.childNodes].filter(x=>x!==r&&!(x.nodeType===1&&x.tagName==="RP")).map(x=>x.textContent).join("").trim();
        out+=(_ttsCurD&&_ttsCurD[base]!=null)?ttsKata(r.textContent.trim()):base; return; } }
    if(c.contains("bx-tag")||c.contains("yd-tag")){ const tg=n.textContent.trim(); out+=(TTS_TAGS[tg]||tg.replace(/＋/g,"プラス"))+"。"; return; }
    if(tg==="B"&&n.parentNode&&n.parentNode.classList&&(n.parentNode.classList.contains("yodan")||n.parentNode.classList.contains("deep"))){ n.childNodes.forEach(walk); if(!/[。！？]$/.test(out)) out+="。"; return; }
    n.childNodes.forEach(walk); };
  walk(el); return out; }
function ttsSplit(t){ const a=t.match(/[^。！？]*[。！？]+[」』）]*|[^。！？]+$/g)||[]; return a.map(x=>x.trim()).filter(x=>x&&/[^\s。、」』）]/.test(x)); }
function ttsCollect(){ _ttsAlt=0; const p=cur(), l=p.lessons[lIdx], d=ttsDictFor(l), items=[];
  const add=(el,raw)=>{ const t=ttsNorm(ttsApplyDict(ttsApplyRd(raw),d)); const ss=ttsSplit(t); if(ss.length) items.push({el,sents:ss}); };
  const ti=document.getElementById("lTitle"); add(ti,"授業"+(+(l.no||lIdx+1))+"。"+ttsTextOf(ti)+"。");
  [...document.getElementById("lBody").children].forEach(el=>{
    if(ttsReadP(el)) add(el,ttsTextOf(el));
    else if(el.classList.contains("flow")) add(el,ttsTextOf(el));
    else if(tts.cfg.box&&(el.classList.contains("yodan")||el.classList.contains("deep"))) add(el,ttsTextOf(el));
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
function ttsVoiceSel(){ const vs=ttsVoices(); if(!vs.length) return ""; if(!tts.voice) tts.voice=ttsPickVoice(); const cu=tts.voice?(tts.voice.voiceURI||tts.voice.name):"";
  const seen={}; return `<select class="tts-sub tts-voice" aria-label="読み上げの声">${vs.map(v=>{ let lb=ttsVLabel(v); seen[lb]=(seen[lb]||0)+1; if(seen[lb]>1) lb+=" "+seen[lb]; const k=v.voiceURI||v.name;
    return `<option value="${k.replace(/"/g,"&quot;")}"${k===cu?" selected":""}>声：${lb}</option>`; }).join("")}</select>`; }
function ttsRender(){ const bar=document.getElementById("ttsBar"); if(!bar) return;
  if(!ttsOK()||!ttsAllowed()){ bar.hidden=true; bar.innerHTML=""; return; } bar.hidden=false;
  const main=tts.st==="play"?"⏸ 一時停止":(tts.st==="pause"?"▶ つづきから":"▶ 読み上げ");
  bar.innerHTML=`<button type="button" class="tts-main" data-a="main">${main}</button>`+(tts.st!=="idle"?`<button type="button" data-a="stop">■ 停止</button>`:"")+
    `<select class="tts-sub tts-rate" aria-label="読み上げの速さ">${TTS_RATES.map(r=>`<option value="${r}"${r===tts.cfg.rate?" selected":""}>速さ ${r}倍</option>`).join("")}</select>${ttsVoiceSel()}<button type="button" class="tts-sub" data-a="box">枠も読む：${tts.cfg.box?"オン":"オフ"}</button>`+
    `<span class="tts-hint">${tts.st==="idle"?"授業を声で読みます。ふりがなの読みで読みます。":"段落をタップすると、そこから読みます。"}</span>`; }
document.addEventListener("click",e=>{ const b=e.target.closest("#ttsBar button"); if(b){ e.preventDefault(); const a=b.dataset.a;
    if(a==="main"){ tts.st==="play"?ttsPause():ttsPlay(); }
    else if(a==="stop"){ ttsStop(); ttsRender(); }
    else if(a==="box"){ tts.cfg.box=!tts.cfg.box; ttsSave(); if(tts.st!=="idle"){ const curEl=(tts.items[tts.k]||{}).el, wasPlay=tts.st==="play";
        tts.gen++; speechSynthesis.cancel(); tts.items=ttsCollect(); let i=tts.items.findIndex(x=>x.el===curEl);
        if(i<0&&curEl){ i=tts.items.findIndex(x=>curEl.compareDocumentPosition(x.el)&Node.DOCUMENT_POSITION_FOLLOWING); if(i<0) i=tts.items.length; tts.s=0; }
        tts.k=Math.max(0,i); if(wasPlay){ tts.st="pause"; ttsPlay(); } } ttsRender(); }
    return; }
  if(tts.st==="idle") return; if(e.target.closest("button,a,summary,details,.kw,.xref,input,select")) return;
  const el=e.target.closest("#lBody > p, #lBody > .flow, #lBody > .yodan, #lBody > .deep, #lBody > .nyushi, #lBody > .point, #lTitle"); if(el) ttsJump(el); });
document.addEventListener("change",e=>{ const vsel=e.target.closest("#ttsBar .tts-voice"); if(vsel){ const v=ttsVoices().find(x=>(x.voiceURI||x.name)===vsel.value); if(!v) return;
    tts.voice=v; tts.cfg.voice=vsel.value; ttsSave();
    if(tts.st==="play"){ tts.gen++; speechSynthesis.cancel(); setTimeout(()=>{ if(tts.st==="play") ttsSpeak(); },80); }
    else if(tts.st==="idle"){ try{ speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance("この声で読みます。"); u.lang="ja-JP"; u.voice=v; u.rate=tts.cfg.rate; speechSynthesis.speak(u); }catch(err){} }
    return; }
  const sel=e.target.closest("#ttsBar .tts-rate"); if(!sel) return; const r=+sel.value; if(!TTS_RATES.includes(r)) return;
  tts.cfg.rate=r; ttsSave(); if(tts.st==="play"){ tts.gen++; speechSynthesis.cancel(); setTimeout(()=>{ if(tts.st==="play") ttsSpeak(); },80); } });
document.addEventListener("visibilitychange",()=>{ if(document.hidden) ttsPause(); });

'''
JS=JS.replace('@@FORCE@@',json.dumps(FORCE,ensure_ascii=False,separators=(',',':')))
a="/* ふりがなの置きかえ */"
assert s.count(a)==1; s=s.replace(a,JS+a)
open(dst,'w',encoding='utf-8').write(s); print('ok')
