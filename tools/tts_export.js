// 読みの点検用：全授業の読み上げ文（アプリと同じ）と、アプリの中の正しい読み（ふりがな・用語集のよみ）を書き出す。
//   node tts_export.js <出力.json>   → python tts_check.py（VOICEVOX の venv で）が使う
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const out=process.argv[2];
 const b=await chromium.launch();const p=await b.newPage();
 await p.addInitScript(()=>{ try{localStorage.setItem('nihonshi_guide','hide');}catch(e){} });
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));await p.waitForTimeout(900);
 const r=await p.evaluate(async()=>{
   const add=(m,b,rd)=>{ b=(b||'').trim(); rd=(rd||'').trim(); if(b.length<2||!rd||!/[一-鿿々]/.test(b)) return; (m[b]=m[b]||{})[rd]=1; };
   const G={}; const RE=/<ruby>([^<]+)<rt>([^<]+)<\/rt><\/ruby>/g;
   Object.keys(packsById).forEach(id=>{ const pk=packsById[id], j=JSON.stringify(pk); let m; RE.lastIndex=0; while(m=RE.exec(j)) add(G,m[1],m[2]);
     (pk.terms||[]).forEach(t=>add(G,t.term,t.reading)); });
   const L=[]; switchSec('lesson');
   for(const id of packOrder){ activeId=id; renderActivePack(); const n=packsById[id].lessons.length;
     for(let i=0;i<n;i++){ showLesson(i); await new Promise(r=>requestAnimationFrame(r)); if(!ttsAllowed()) continue;
       const l=packsById[id].lessons[i], loc={}; let m; const h=(l.html||'')+(l.colHtml||''); RE.lastIndex=0; while(m=RE.exec(h)) add(loc,m[1],m[2]);
       const it=vvItems(); L.push({k:id+':'+i,loc:Object.fromEntries(Object.entries(loc).map(([k,v])=>[k,Object.keys(v)])),s:it.flatMap(x=>x.sents)}); } }
   return {g:Object.fromEntries(Object.entries(G).map(([k,v])=>[k,Object.keys(v)])),L}; });
 fs.writeFileSync(out,JSON.stringify(r)); console.log('readings',Object.keys(r.g).length,'lessons',r.L.length,'sentences',r.L.reduce((a,x)=>a+x.s.length,0));
 await b.close();})();
