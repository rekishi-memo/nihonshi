# 語句の重要度（juyo.py：共テ必修・私大頻出・私大・難関私大・色なし）をアプリに反映する。何度回してもよい。
#   python3 apply_rank.py ../app/source.html ../app/source.html
# 1) JS の TERM_RANK（本文の色 A＝共テ必修／B＝私大頻出／C＝私大／D＝難関私大／X＝色なし）を作り直す
# 2) 一問一答の重要度 i（共テ必修5・私大頻出4・私大3・難関私大2）と難易度 d（共テ必修1・私大頻出2・私大2・難関私大3、年や数を答える問題は1段上げる）を付け直す
# 3) 本文に自動で色をつける語の一覧 kw_rank.txt を書き出す（次の post.py の kw_all.js が読む）
import json,re,sys
from juyo import rank_for_packs, write_kw_rank
src,out=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
RANK=rank_for_packs(packs)
js='/*TERM_RANK*/const TERM_RANK='+json.dumps(RANK,ensure_ascii=False,separators=(',',':'))+';/*/TERM_RANK*/'
s=re.sub(r'/\*TERM_RANK\*/[\s\S]*?/\*/TERM_RANK\*/',lambda mm:js,s)
def rk(a):
    a=re.sub(r'[（(].*?[）)]','',a or '').strip()
    if a in RANK: return RANK[a]
    parts=[x.strip() for x in re.split(r'[・／/]',a) if x.strip()]
    rs=[RANK.get(x) for x in parts]
    if parts and all(rs): return min(rs)   # A<B<C<D<X の順で一番高いもの
    return None
from collections import Counter
c=Counter()
for p in packs:
    for q in p['quiz']:
        r=rk(q.get('mark')) or rk(q['a']) or 'C'
        q['i']={'A':5,'B':4,'C':3,'D':2}.get(r,3)
        q['d']={'A':1,'B':2,'C':2,'D':3}.get(r,2)
        if re.search(r'[0-9０-９]',q['a']) or re.search(r'何年|何人|何万|何％|何%|いくら|何倍',q['q']): q['d']=min(3,q['d']+1)
        c[q['i']]+=1
print('quiz i',dict(sorted(c.items())))
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
print('kw_rank.txt',write_kw_rank(packs))
