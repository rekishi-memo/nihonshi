# 前に授業の本文に入れていた動く図（<!--an3:ID-->）を取りのぞく。2026-11-17 から動く図はセットごとの1本にしたので、授業の本文には入れない。
#   python3 add_anim3d.py <土台.html> <土台.html>
import re,json,sys
src,out=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1)); n=0
for p in packs:
    for l in p['lessons']:
        h=re.sub(r'<!--an3:[^>]*-->[\s\S]*?<!--/an3-->','',l['html'])
        if h!=l['html']: n+=1; l['html']=h
print('removed',n)
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
