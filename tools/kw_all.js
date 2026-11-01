const fs=require('fs');
const src=fs.readFileSync(process.argv[2],'utf8');
const m=src.match(/const DEFAULT_PACKS = (\[[\s\S]*?\n\]);/);
const packs=eval(m[1]);
if(process.argv[4]){const np=JSON.parse(fs.readFileSync(process.argv[4],'utf8')); const i=packs.findIndex(p=>p.id===np.id); if(i>=0) packs[i]=np; else packs.push(np);}
const STOP=new Set(`外孫 外祖父 姻戚 勅書 庇護 謀反 朝貢 陶磁器 巡礼 化身 疫神 疫病 飢饉 吉凶 往生 念仏 釈迦 遺構 屏風 障子 円座 七夕 相撲 戸籍 計帳 雑徭 郡家 郡衙 乱妨 下人 国府 摂津 伊予 下総 常陸 下野 上野 上総 陸奥 出羽 伊豆 伊賀 出雲 安芸 豊後 相模 遠江 土佐 阿波 佐渡 信濃 長門 越後 越前 肥後 対馬 壱岐 尾張 備後 播磨 石見 但馬 木曽 津軽 大宰府 博多湾 上皇 法皇 公家 武家 幕府 別当 執事 世襲 追討 一門 一家 祭祀 知行 評定 先例 嫡子 庶子 家督 坐禅 戒律 煩悩 香料 刀剣 漆器 生糸 灌漑 離合集散 地縁的 血縁的 一騎打ち 鍛冶 細川 斯波 畠山 赤松 一色 京極 酒屋 仲間 大津 平野 石山 今井 品川 小浜 桑名 内裏 近衛 女房 後宮 本地 本朝 皇朝 十二銭 行商人 鹿児島 成功 講 寄進 延喜 天暦の治 南都 北嶺 治承 寿永の乱 五山 十刹の制 東海 東山両道 寄子制 説話 肥後国 阿波国 法会 離宮 乳母 女院 俸禄 双六 叙位 院司 勅撰 釈迦如来像 阿弥陀如来像 金剛 金春 観世 宝生 北山 南山 山北 山南 中稲 晩稲 早稲`.split(/\s+/));
const LOCAL_OK=new Set(['成功','寄進']); // allowed only from a pack's own quiz/terms
function addTo(set,s){ if(!s) return; s=String(s).trim(); if(s.includes('・')&&s.length>=4) set.add(s.replace(/[（(].*?[）)]/g,'').trim());
 for(const part of s.split(/[・／\/]/)) for(const p2 of part.split(/[（）()]/)){ const t=p2.trim(); if(t.length>=2 && !/^[0-9０-９]+年?$/.test(t)) set.add(t);} }
const G=new Set();
const local={};
for(const p of packs){ const L=new Set(); for(const q of p.quiz||[]){addTo(L,q.a);addTo(L,q.mark);} for(const t of p.terms||[]) addTo(L,t.term); local[p.id]=L; for(const x of L) G.add(x); }
for(const f of ['ruby.txt','ruby2.txt','ruby3.txt','ruby4.txt','ruby5.txt','ruby6.txt','ruby7.txt','ruby8.txt','ruby9.txt','ruby10.txt','ruby11.txt','ruby12.txt']) for(const l of fs.readFileSync(f,'utf8').trim().split('\n')){const k=l.split(':')[0]; if(k.length>=2) G.add(k);}
for(const w of fs.readFileSync('kw_extra.txt','utf8').split(/\s+/)) if(w.length>=2) G.add(w);
for(const s of STOP) G.delete(s);
const esc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
function vocabFor(pid){ const V=new Set(G); for(const x of local[pid]) if(!STOP.has(x)||LOCAL_OK.has(x)) V.add(x); return [...V].sort((a,b)=>b.length-a.length); }
const BLOCK=new Set(['中山道','宮内大臣','小学校令','中学校令','師範学校令','小作人','小作農','小作地','硫黄島','資本家','小作料','宇治川電気','主義政党','改正法案','為替相場','村役人','三浦半島','大人気','清国人','上人語録','修正法','山田寺','狗奴国','近畿中央部','島原城','大都市','近畿地方','金閣寺』','中国人','外国人','韓国人','異国人','立憲国民党','国民党']);
function procHtml(html,V){ V=[...new Set([...V,...BLOCK])].sort((a,b)=>b.length-a.length);
  const re=new RegExp(V.map(esc).join('|'),'g');
  const seen=new Set(); let out=''; let i=0; const stack=[]; // span stack: true if no-touch
  const noTouch=()=>stack.some(x=>x);
  // pre-mark existing kw terms as seen
  for(const mm of html.matchAll(/<span class='kw'>([\s\S]*?)<\/span>/g)) seen.add(mm[1].replace(/<rt>[\s\S]*?<\/rt>/g,'').replace(/<[^>]+>/g,''));
  while(i<html.length){
    if(html.startsWith('<ruby>',i)){
      const j=html.indexOf('</ruby>',i); const whole=html.slice(i,j+7);
      const base=whole.replace(/<rt>[\s\S]*?<\/rt>/,'').replace(/<[^>]+>/g,'');
      let hit=null; if(!noTouch()){ for(const t of V){ if(t.length<=base.length && base.includes(t)){ hit=t; break; } } }
      if(hit){ out+="<span class='kw'>"+whole+"</span>"; } else out+=whole;
      i=j+7; continue;
    }
    if(html[i]==='<'){
      const j=html.indexOf('>',i); const tag=html.slice(i,j+1);
      if(/^<span\b/.test(tag)) stack.push(/class='(kw|tag|qmk|tp)'/.test(tag));
      else if(tag==='</span>') stack.pop();
      else if(/^<svg\b/.test(tag)) stack.push(true);
      else if(tag==='</svg>') stack.pop();
      out+=tag; i=j+1; continue;
    }
    let j=html.indexOf('<',i); if(j<0) j=html.length;
    const text=html.slice(i,j);
    if(noTouch()) out+=text;
    else out+=text.replace(re,w=>BLOCK.has(w)?w:"<span class='kw'>"+w+"</span>");
    i=j;
  }
  return out;
}
let before=0,after=0;
for(const p of packs){ const V=vocabFor(p.id); for(const l of p.lessons||[]){ for(const k of ['html','colHtml']){ if(!l[k]) continue; before+=(l[k].match(/class='kw'/g)||[]).length; l[k]=procHtml(l[k],V); after+=(l[k].match(/class='kw'/g)||[]).length; } } }
console.log('kw before',before,'after',after);
packs.sort((a,b)=>(a.order||0)-(b.order||0)); const js=JSON.stringify(packs,null,1);
if(js.includes('</script')) throw 'script tag in content';
const out=src.replace(m[0],'const DEFAULT_PACKS = '+js+';');
fs.writeFileSync(process.argv[3],out);
const sc=out.match(/<script>([\s\S]*?)<\/script>/g).pop().replace(/^<script>|<\/script>$/g,'');
fs.writeFileSync('check_last.js',sc);
// sample
for(const id of ['kinsei']){const k=packs.find(p=>p.id===id); console.log('---',id); console.log(k.lessons[1].html.replace(/<rt>[\s\S]*?<\/rt>/g,'').replace(/<span class='kw'>/g,'【').replace(/<\/span>/g,'】').replace(/<[^>]+>/g,'').slice(0,700));}
