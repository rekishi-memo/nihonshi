// 台本の書き漏らしを探す：かっこ・記号のある文（と枠）のうち、どの台本の「元の文」にも入っていないものを出す。
//   node tts_script_cover.js <pack id ...>
const {execFileSync}=require('child_process');const fs=require('fs');const path=require('path');
const S=JSON.parse(fs.readFileSync(path.join(__dirname,'tts_script.json'),'utf8'));
for(const pid of process.argv.slice(2)){
  const out=execFileSync('node',[path.join(__dirname,'tts_todo.js'),pid],{encoding:'utf8'}).split('\n').filter(Boolean);
  for(const line of out){ const [i,kind,...rest]=line.split(' | '); const s=rest.join(' | '); const L=S[pid+':'+i]||[];
    const covered=L.some(([a])=>a.includes(s.replace(/（）/g,'（）'))||a.includes(s));
    const onlyEmpty=/（）/.test(s)&&!/[（＝→：〔](?!）)/.test(s.replace(/（）/g,''));
    if(!covered&&!onlyEmpty) console.log(pid+':'+i+' | '+kind+' | '+s.slice(0,120)); } }
