# 語句の重要度（hindo.py）をアプリに反映する。何度回してもよい。
#   python3 apply_rank.py ../app/source.html ../app/source.html
# 1) JS の TERM_RANK（本文の色 A/B/C）を hindo.py から作り直す
# 2) 一問一答の重要度 i を hindo.py から付け直す（A=5, B=4, それ以外=3）。難易度 d は i=5→1、i=4→2、i=3 は今の値のまま
import json,re,sys
from hindo import RANK
src,out=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
js='/*TERM_RANK*/const TERM_RANK='+json.dumps(RANK,ensure_ascii=False,separators=(',',':'))+';/*/TERM_RANK*/'
if '/*TERM_RANK*/' in s: s=re.sub(r'/\*TERM_RANK\*/[\s\S]*?/\*/TERM_RANK\*/',lambda m:js,s)
else: s=s.replace('/* ---- 重要度ランク（A＝必ず／B＝覚える／C＝流れで） ---- */','/* ---- 重要度ランク（A＝必ず／B＝覚える／C＝流れで） ---- */\n'+js,1)
def rk(a):
    a=re.sub(r'[（(].*?[）)]','',a).strip()
    if a in RANK: return RANK[a]
    parts=[x.strip() for x in re.split(r'[・／/]',a) if x.strip()]
    rs=[RANK.get(x) for x in parts]
    if parts and all(rs): return min(rs)
    return None
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
from collections import Counter
c=Counter()
for p in packs:
    for q in p['quiz']:
        r=rk(q.get('mark') or q['a']) or rk(q['a'])
        q['i']={'A':5,'B':4}.get(r,3)
        if q['i']==5: q['d']=1
        elif q['i']==4: q['d']=2
        c[q['i']]+=1
print('quiz i',dict(c))
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
