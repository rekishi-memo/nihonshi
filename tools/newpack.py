# 新しいセットを1つのデータファイル（例：kinsei6_data.py）からつくる汎用ビルダー。
#   python3 newpack.py kinsei6_data ../app/source.html ../app/source.html
#   そのあと post.py → rate.py → apply_rank.py → add_maps.py → pack_out.py
# データファイルに書くもの：
#   PACK = dict(id,title,subtitle,order,range, after='前に置くセットのid')
#   EXTRA_RD = "語:よみ ..."（ルビの追加）
#   LESSONS = [dict(no,nav,title,unit,theme,html,vis), ...]   html の《語》は色づけ（kw）、{Q} は確認問題
#   QS = {no: (問い, 答え)}                                      確認問題
#   QUIZ = [(no, 問い, 答え, d, i, 解説), ...]                    一問一答（id は並び順。足すときは必ず末尾に）
#   TERMS = [(語, よみ, タグ, 説明), ...]  GORO = [(語呂, 答え, メモ), ...]
#   RONJ = [dict(q,hint,points=[...]), ...]  TIMELINE = [(年, できごと), ...]
#   FIGURES = dict(title,nodes,links,dramas)  CLOZE = [dict(title,text), ...]
import json,re,sys,importlib
from buildpack import load_rd,rubify_fn,SINGLE,Q
mod,src,out=sys.argv[1:4]
D=importlib.import_module(mod)
rub=rubify_fn(load_rd(getattr(D,'EXTRA_RD','')))
def kw(h): return re.sub(r'《([^》]+)》',r"<span class='kw'>\1</span>",h)
lessons=[]
for L in D.LESSONS:
    h=rub(kw(L['html'].replace('\n','')))
    for w,r in SINGLE.items(): h=h.replace(f"<span class='kw'>{w}</span>",f"<span class='kw'><ruby>{w}<rt>{r}</rt></ruby></span>",1)
    if '{Q}' in h: h=h.replace('{Q}',Q(*D.QS[L['no']]))
    lessons.append({"no":L['no'],"navTitle":L['nav'],"title":L['title'],"unitLink":L['unit'],"theme":L['theme'],"html":h,"visual":L.get('vis',''),"colTitle":"","colHtml":"","exam":L.get('exam','')})
plain=lambda t: re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',t))
txt={L['no']:plain(L['html']) for L in lessons}
quiz=[]; miss=[]
for i,(no,q,a,d,imp,exp) in enumerate(D.QUIZ,1):
    if a not in txt[no]: miss.append(no+':'+a)
    quiz.append({"id":i,"unit":[L['unit'] for L in D.LESSONS if L['no']==no][0],"link":no,"q":q,"a":a,"exp":exp,"d":d,"i":imp,"f":4})
print('quiz',len(quiz),'answer-not-in-lesson',miss)
cloze=D.CLOZE; ans=[]
for c in cloze: ans+=re.findall(r'\[\[([^\]]+)\]\]',c['text'])
pl=''.join(re.sub(r'\[\[[^\]]+\]\]','□',c['text']) for c in cloze)
print('cloze',len(ans),'dup',[a for a in set(ans) if ans.count(a)>1],'leak',[a for a in set(ans) if a in pl],'not-in-lessons',[a for a in ans if not any(a in t for t in txt.values())])
P=D.PACK
pack={"id":P['id'],"title":P['title'],"subtitle":P['subtitle'],"order":P['order'],"range":P['range'],
 "timeline":[{"y":y,"t":t} for y,t in D.TIMELINE],"lessons":lessons,"quiz":quiz,
 "terms":[{"term":a,"reading":b,"tag":c,"desc":d} for a,b,c,d in D.TERMS],
 "goro":[{"phrase":a,"ans":b,"note":c} for a,b,c in D.GORO],"ronjutsu":D.RONJ,"cloze":cloze,"figures":D.FIGURES}
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
old=[p for p in packs if p['id']==P['id']]
if old and len(old[0]['quiz'])>len(quiz): sys.exit('一問一答が減っている（id がずれる）。中止')
packs=[p for p in packs if p['id']!=P['id']]
i=[k for k,p in enumerate(packs) if p['id']==P['after']][0]; packs.insert(i+1,pack)
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
