# rate.py のあとに使う。古いセット（古代〜近世・貨幣史）は教科書の範囲の問題ばかりで rate.py では難易度3が出ないので、
# もとの手付けで難易度3だった問題のうち、まとめにも入試欄にも出ない細かい語（重要度3）は3のまま残す。基本語は除く。
#   python3 rate_keep_old.py 付け直す前.html 付け直した後.html 出力.html
import json,re,sys
OLD=['kodai','kodai2','kodai3','kodai4','kodai5','chusei','chusei2','chusei3','chusei4','chusei5','chusei6','kinsei','kinsei2','kinsei3','kinsei4','kinsei5','theme_kahei']
BASIC=set('環濠集落 魏志倭人伝 ワカタケル大王 氏姓制度 高地性集落 横穴式石室 稲荷山古墳の鉄剣・江田船山古墳の鉄刀 太政官 国司 清和天皇 延喜の荘園整理令 本地垂迹説 荘園公領制 南都・北嶺 院庁下文 令旨 兵粮米 鎮西奉行 生野銀山'.split())
a,b,out=sys.argv[1:4]
get=lambda f: re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',open(f,encoding='utf-8').read())
pa=json.loads(get(a).group(1)); O={p['id']:{q['id']:q.get('d') for q in p['quiz']} for p in pa}
s=open(b,encoding='utf-8').read(); m=get(b); pb=json.loads(m.group(1)); n=0
for p in pb:
    if p['id'] not in OLD: continue
    for q in p['quiz']:
        if O[p['id']].get(q['id'])==3 and q['i']==3 and q['a'] not in BASIC: q['d']=3; n+=1
print('kept d=3:',n)
s=s[:m.start(1)]+json.dumps(pb,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
