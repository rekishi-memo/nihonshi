# tts_review.py の一覧（<pack>.tsv）で、目で見て正しいとした「語→読み」を tts_reviewed.tsv にためる。2026-11-16。
#   python3 tts_accept.py <出力フォルダ>/<pack id>.tsv
#   まちがいを tts_force.json・台本で直して一覧を作りなおし、残りが全部正しいと確かめてから実行する（未点検の行をすべて「点検ずみ」にする）。
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); rp=os.path.join(HERE,'tts_reviewed.tsv')
have=set()
if os.path.exists(rp): have={tuple(l.rstrip('\n').split('\t')[:2]) for l in open(rp,encoding='utf-8') if '\t' in l and not l.startswith('#')}
new=[]
for fp in sys.argv[1:]:
    for l in open(fp,encoding='utf-8'):
        p=l.rstrip('\n').split('\t')
        if p[0]!='': continue
        w=p[1][p[1].index('[')+1:p[1].index(']')]; post=p[1][p[1].index(']')+1:][:1]
        k=(w+(f'({post})' if len(w)==1 and post else ''),p[2])
        if k not in have: have.add(k); new.append(k)
with open(rp,'a',encoding='utf-8') as f:
    if os.path.getsize(rp) if os.path.exists(rp) else 0: pass
    for k in new: f.write('\t'.join(k)+'\n')
print('added',len(new),'total',len(have))
