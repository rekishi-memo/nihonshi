# 古い授業の本文をプレーンテキストで書き出す（見直し用）。python3 dump_old.py kodai > out.txt
import json,re,sys
s=open('../app/source.html',encoding='utf-8').read()
P={p['id']:p for p in json.loads(re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s).group(1))}
pl=lambda t: re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',t))
for l in P[sys.argv[1]]['lessons']:
    h=re.sub(r"<div class='(deep|viz|vs|yodan)'[\s\S]*?</div>","",l['html'])
    h=re.sub(r"<details class='qcheck'>[\s\S]*?</details>","",h)
    print('■',l['no'],l['title'],'／',l['navTitle'],'／',l['theme']); print(pl(h.replace('</p>','\n').replace('</div>','\n'))); print()
