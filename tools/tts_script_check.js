// 台本の「元の文」が、いまの授業の読み上げ文（漢字のまま）に本当にあるかを確かめる。ないもの＝授業の文が変わった・写しまちがい。
//   node tts_script_check.js [pack id ...]
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{const S=JSON.parse(fs.readFileSync(path.join(__dirname,'tts_script.json'),'utf8')); const only=process.argv.slice(2);
 const b=await chromium.launch();const p=await b.newPage();
 await p.addInitScript(()=>{ try{localStorage.setItem('nihonshi_guide','hide');}catch(e){} });
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));await p.waitForTimeout(900);
 const bad=await p.evaluate(async([S,only])=>{ const bad=[]; switchSec('lesson');
   for(const key of Object.keys(S)){ const [pid,i]=key.split(':'); if(only.length&&!only.includes(pid)) continue; activeId=pid; renderActivePack(); showLesson(+i); await new Promise(r=>requestAnimationFrame(r));
     const raws=[...document.getElementById('lBody').children].map(el=>(((el.className||'').includes('point')?"では、まとめよう。":"")+ttsTextOf(el)).replace(/x/,"x")).map(t=>ttsRefStrip(t));
     const all=raws.join('\n');
     for(const [a] of S[key]) if(all.indexOf(a)<0) bad.push(key+' | '+a.slice(0,70)); }
   return bad; },[S,only]);
 console.log('not found',bad.length); bad.forEach(x=>console.log(x)); await b.close(); process.exit(bad.length?1:0);})();
