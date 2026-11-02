# 書き直し用：セットの授業本文（プレーン）・一問一答の答え・図・地図の位置を書き出す
#   python3 dump_pack.py kodai > out.txt
import json,re,sys
from collections import defaultdict
pid=sys.argv[1]
s=open('../app/source.html').read(); m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s)
p=[x for x in json.loads(m.group(1)) if x['id']==pid][0]
from maps_def import MAPS
A=defaultdict(list)
for q in p['quiz']: A[q['link']].append(q.get('mark') or q['a'])
print(p['title'],p['range'])
for c in p['cloze']: print('CLOZE',c['title'],re.findall(r'\[\[(.*?)\]\]',c['text']))
for l in p['lessons']:
    h=l['html']
    nviz=len(re.findall(r"<div class='viz'>[\s\S]*?</svg></div></div>",h))
    h=re.sub(r'<!--jm[\s\S]*?/jm-->','[MAP]',h); h=re.sub(r"<div class='viz'>[\s\S]*?</svg></div></div>",'[VIZ]',h)
    h=re.sub(r'<rt>.*?</rt>','',h); h=re.sub(r'<svg[\s\S]*?</svg>','',h)
    h=re.sub(r"<div class='(\w+)'>",lambda mm:'\n['+mm.group(1)+'] ',h); h=re.sub(r'<p>','\n',h); h=re.sub(r'<summary>','\n[Q] ',h)
    h=re.sub(r'<[^>]+>','',h)
    print(f"\n===== {l['no']} {l['navTitle']} | {l['title']} | VIZ={nviz} MAPS={[mp['after'] for mp in MAPS if mp['pack']==pid and mp['no']==l['no']]}")
    print('ANS:',' / '.join(A[l['no']]))
    print(h)
