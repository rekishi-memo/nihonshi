# 授業本文に立体の動く図（an3）を入れる（何度回してもよい。<!--an3:ID--> で見つけて入れ直す）
#   python3 add_anim3d.py <土台.html> <土台.html>
import re,json,sys
from anim3d import ANIMS,block
src,out=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1)); P={p['id']:p for p in packs}
def plain(h): return re.sub(r'<[^>]+>','',re.sub(r'<rt>[\s\S]*?</rt>','',h))
for p in packs:
    for l in p['lessons']: l['html']=re.sub(r'<!--an3:[^>]*-->[\s\S]*?<!--/an3-->','',l['html'])
bad=[]
for a in ANIMS:
    l=[l for l in P[a['pack']]['lessons'] if l['no']==a['no']][0]; h=l['html']; pos=None
    for mm in re.finditer(r'<p[^>]*>[\s\S]*?</p>',h):
        if a['after'] in plain(mm.group(0)): pos=mm.end(); break
    if pos is None: bad.append(a['id']); continue
    l['html']=h[:pos]+f"<!--an3:{a['id']}-->"+block(a['id'],a['fn'](),a['cap'])+"<!--/an3-->"+h[pos:]
print('anims',len(ANIMS)-len(bad),'not-found',bad)
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
