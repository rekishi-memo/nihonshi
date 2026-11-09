# 過去問に出た回数（kakomon_freq.json）を一問一答の x に入れる（2026-11-09 ユーザーの指示「頻出かどうかは過去問で決める」）。
# kakomon_freq.json は「語 → 出た試験の数」だけ（問題文は入れない）。数え方は HANDOVER.md「過去問の頻出度」を参照。
# post.py の最後で毎回かかる。アプリ側は x>=2 を「最頻出」、x==1 を「頻出」として絞りこむ。
import json,os
def apply(packs):
    T=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'kakomon_freq.json'),encoding='utf-8'))['terms']
    n=[0,0,0]
    for p in packs:
        for q in p['quiz']:
            x=T.get(q['a'],{}).get('n',0)
            if x: q['x']=x
            else: q.pop('x',None)
            n[min(x,2)]+=1
    return n
