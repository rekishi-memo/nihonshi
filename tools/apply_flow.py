# 授業の頭に「前の授業からの流れ」、おしまいに「次の授業へ」を入れる（2026-11-09 ユーザーの指示「授業の順番だけでなく流れもわかりやすく。面白く」）。
# 中身は flow_data.py の F（キー＝授業の src）。post.py の最後で毎回かかる（何度かけても同じ結果）。
import re
from flow_data import F
PAT=re.compile(r"<!--flow-->[\s\S]*?<!--/flow-->")
def box(cls,tag,t): return f"<!--flow--><div class='flow{cls}'><span class='bx-tag'>{tag}</span>{t}</div><!--/flow-->"
def apply(packs):
    n=0
    for p in packs:
        for l in p['lessons']:
            h=PAT.sub('',l['html']); v=PAT.sub('',l.get('visual') or '')
            f=F.get(l.get('src') or f"{p['id']}-{l['no']}")
            if f:
                prev,nxt=f
                if prev: h=box('','前の授業から',prev)+h
                if nxt:  # 授業の図（visual）があればその後ろ、つまり授業のいちばん最後に置く
                    if v: v=v+box(' next','次の授業へ',nxt)
                    else: h=h+box(' next','次の授業へ',nxt)
                n+=1
            l['html']=h
            if 'visual' in l: l['visual']=v
    return n
