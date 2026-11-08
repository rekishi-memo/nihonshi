# 授業本文に地図を入れる（何度回してもよい。前に入れた地図は <!--jm:ID--> で見つけて入れ直す）
#   python3 add_maps.py ../app/source.html ../app/source.html
import re,json,sys
from jmap import jmap
from maps_def import MAPS

src,out=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
P={p['id']:p for p in packs}

def plain(h): return re.sub(r'<[^>]+>','',re.sub(r'<rt>[\s\S]*?</rt>','',h))

# 前に入れた地図を消す
for p in packs:
    for l in p['lessons']:
        l['html']=re.sub(r'<!--jm:[^>]*-->[\s\S]*?<!--/jm-->','',l['html'])

bad=[]
for mp in MAPS:
    from buildpack import locate
    _,l=locate(list(P.values()),mp['pack'],mp['no'])
    h=l['html']; pos=None
    for mm in re.finditer(r'<p[^>]*>[\s\S]*?</p>',h):
        if mp['after'] in plain(mm.group(0)): pos=mm.end(); break
    if pos is None: bad.append(mp['id']); continue
    block=f"<!--jm:{mp['id']}-->"+jmap(**mp['map'])+"<!--/jm-->"
    l['html']=h[:pos]+block+h[pos:]
print('maps',len(MAPS)-len(bad),'not-found',bad)
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
