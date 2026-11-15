// 台本を書く対象を書き出す：かっこ・記号のある文と、「入試ではこう出る」「まとめ」の枠（アプリの読み上げと同じ、漢字のままの文）。
//   node tts_todo.js <pack id> → 標準出力に「授業番号 / 種類 / 文」
const {chromium}=require('playwright');const path=require('path');
(async()=>{const pid=process.argv[2];const b=await chromium.launch();const p=await b.newPage();
 await p.addInitScript(()=>{ try{localStorage.setItem('nihonshi_guide','hide');}catch(e){} });
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));await p.waitForTimeout(900);
 const H=require('fs').readFileSync(path.join(__dirname,'tts_homograph.txt'),'utf8').split('\n').filter(l=>!l.startsWith('#')).join(' ').split(/\s+/).filter(Boolean);
 const r=await p.evaluate(async([pid,H])=>{ const out=[]; activeId=pid; renderActivePack(); switchSec('lesson');
   for(let i=0;i<packsById[pid].lessons.length;i++){ showLesson(i); await new Promise(r=>requestAnimationFrame(r)); if(!ttsAllowed()) continue;
     [...document.getElementById('lBody').children].forEach(el=>{ const c=el.className||''; const box=/nyushi|point/.test(c);
       if(!(ttsReadP(el)||/flow|yodan|deep/.test(c)||box)) return;
       let raw=(/point/.test(c)?"では、まとめよう。":"")+ttsTextOf(el); raw=ttsRefStrip(raw).replace(/\s+/g,' ').trim();
       if(box){ out.push([i,c.split(' ')[0],raw]); return; }
       (function(t){ const o=[]; let d=0,cur=''; for(const ch of t){ cur+=ch; if(ch==='（') d++; else if(ch==='）') d=Math.max(0,d-1); else if(ch==='。'&&d===0){ o.push(cur); cur=''; } } if(cur.trim()) o.push(cur); return o; })(raw).forEach(s=>{ s=s.trim(); if(/[（＝→：〔]/.test(s.replace(/（）/g,''))) out.push([i,'p',s]); else if(H.some(w=>s.includes(w))) out.push([i,'h',s]); }); }); }
   return out; },[pid,H]);
 r.forEach(x=>console.log(x.join(" | "))); await b.close();})();
