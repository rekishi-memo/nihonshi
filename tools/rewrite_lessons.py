# 書き直した授業本文を、既存のセットに差しこむ（id・一問一答・穴埋めはそのまま）。
#   python3 rewrite_lessons.py chusei chusei1_text ../app/source.html ../app/source.html
#   そのあと post.py → add_maps.py → pack_out.py
# 本文中の {VIZ} は、元の授業にあった図（<div class='viz'>…）に置きかえる。
import json,re,sys,importlib
from buildpack import load_rd,rubify_fn,SINGLE
pid,mod,src,out=sys.argv[1:5]
T=importlib.import_module(mod)
rub=rubify_fn(load_rd(getattr(T,'EXTRA_RD','')))
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
p=[x for x in packs if x['id']==pid][0]
for l in p['lessons']:
    d=T.L.get(l['no'])
    if not d: continue
    old=l['html']
    vizs=re.findall(r"<div class='viz'>[\s\S]*?</svg></div></div>",old)
    qs=re.findall(r"<details class='qcheck'>[\s\S]*?</details>",old)
    h=rub(re.sub(r'《([^》]+)》',r"<span class='kw'>\1</span>",d['html']))
    for w,r in SINGLE.items(): h=h.replace(f"<span class='kw'>{w}</span>",f"<span class='kw'><ruby>{w}<rt>{r}</rt></ruby></span>",1)
    for v in vizs: h=h.replace('{VIZ}',v,1)
    if '{Q}' in h: h=h.replace('{Q}',''.join(qs[:2]))
    assert '{VIZ}' not in h, l['no']
    l['html']=h
    if d.get('title'): l['title']=d['title']
    l['colHtml']=''; l['colTitle']=''
print('rewritten',[k for k in T.L])
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
