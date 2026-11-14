// VOICEVOX で音声を作るための「読み上げ原稿」を書き出す（アプリの読み上げと同じ文の区切り・読み）。
//   node vv_dump.js <出力.json> <pack id>:<授業の番号(0から)> ...   例：node vv_dump.js /tmp/x.json kodai:0
// 枠（入試ではこう出る・まとめなど）も全部入れて書き出す。アプリは「枠も読む：オフ」のとき、その部分をとばして再生する。
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const [out,...targets]=process.argv.slice(2);
 const b=await chromium.launch();const p=await (await b.newContext()).newPage();
 await p.addInitScript(()=>{ try{localStorage.setItem('nihonshi_guide','hide');}catch(e){} });
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));await p.waitForTimeout(900);
 const res=[];
 for(const t of targets){ const [pid,i]=t.split(':');
   const r=await p.evaluate(async([pid,i])=>{ activeId=pid; renderActivePack(); switchSec('lesson'); showLesson(+i); await new Promise(r=>requestAnimationFrame(r));
     const it=vvItems(); return {pid,i:+i,hash:vvHash(it),items:it.map(x=>({box:x.box,sents:x.sents}))}; },[pid,i]);
   res.push(r); }
 fs.writeFileSync(out,JSON.stringify(res)); console.log('lessons',res.length,'sentences',res.reduce((s,x)=>s+x.items.reduce((a,y)=>a+y.sents.length,0),0));
 await b.close();})();
