// 読み上げの「漢字のまま読む語」を決めるため、全授業のふりがな付きの語と、置きかえた回数を tts_words.tsv に書き出す。
// 使い方：node tts_words.js（index.html を作ってから。Playwright を使う）→ python3 tts_yomi.py tts_words.tsv tts_keep.txt
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await (await b.newContext()).newPage();
await p.goto('file://'+require('path').resolve(__dirname,'../index.html')+'');await p.waitForTimeout(900);
const r=await p.evaluate(async()=>{ const cnt={}; switchSec('lesson');
  const orig=ttsApplyDict; window.ttsApplyDict=function(t,d){ const keys=Object.keys(d).filter(k=>t.indexOf(k)>=0).sort((a,b)=>b.length-a.length);
    if(keys.length){ const re=new RegExp(keys.map(k=>k.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).join("|"),"g"); t.replace(re,(m,i,all)=>{ if(!(ttsIsKan(all[i-1])||ttsIsKan(all[i+m.length]))) cnt[m+'\t'+d[m]]=(cnt[m+'\t'+d[m]]||0)+1; return m; }); }
    return orig(t,d); };
  for(const id of packOrder){ activeId=id; renderActivePack(); for(let i=0;i<packsById[id].lessons.length;i++){ showLesson(i); await new Promise(r=>requestAnimationFrame(r));
    document.querySelectorAll('#lBody .rbx').forEach(x=>{ const r=x.querySelector('.rtx'); const base=[...x.childNodes].filter(n=>n!==r).map(n=>n.textContent).join(''); const k=base+'\t'+(r?r.textContent:''); cnt[k]=(cnt[k]||0)+1; });
    ttsCollect(); } }
  return cnt; });
const arr=Object.entries(r).sort((a,b)=>b[1]-a[1]); fs.writeFileSync(require('path').join(__dirname,'tts_words.tsv'),arr.map(([k,v])=>v+'\t'+k).join('\n'));
console.log('distinct',arr.length,'total',arr.reduce((s,x)=>s+x[1],0));await b.close();})();
