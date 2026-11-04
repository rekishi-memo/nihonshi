# 授業に知識を足す（本文の段落・深掘り欄・一問一答）。
#   python3 merge_add.py <pid> <text_module.py> <add_data.py> ../app/source.html
# add_data.py には RD="語:よみ ..."（新しい語の読み）と A={'07':dict(p=["本文に足す段落（《語》で色）",...], col=[("見出し","本文"),...],
#                               q=[("問い","答え","ひとこと解説"),...]), ...}
# 1) 本文の段落は、その授業の「入試ではこう出る」（N(...)）の直前に P(...) として差しこむ
# 2) col は深掘り欄の末尾に足す
# t は表（[(見出し,[(左,右),...],(左見出し,右見出し))]）。本文の「入試ではこう出る」の直前に入る
# 3) 一問一答はセットの末尾に、今の最大 id の次から足す（既存の id は変えない）。同じ答え＋同じ問いは足さない
# このあと rewrite_lessons.py → post.py → add_maps.py → apply_rank.py → pack_out.py を通す。
import json,re,sys,runpy
pid,modf,addf,src=sys.argv[1:5]
D=runpy.run_path(addf); A=D['A']
t=open(modf,encoding='utf-8').read()
if D.get('RD'):  # 読みがなを EXTRA_RD の末尾に足す（「語:よみ 語:よみ」）
    k=t.index('EXTRA_RD="'); e=t.index('"',k+10)
    new=' '.join(x for x in D['RD'].split() if x.split(':')[0]+':' not in t[k:e])
    if new: t=t[:e]+' '+new+t[e:]
def block(no):
    i=t.index(f"L['{no}']=dict(")
    j=t.find("\nL['",i+5)
    return i,(len(t) if j<0 else j)
for no,d in A.items():
    i,j=block(no); b=t[i:j]
    for x in d.get('p',[]):
        if x in b: continue
        ins='P('+json.dumps(x,ensure_ascii=False)+')+\n'
        for pat in ('\nN(','+N(','\nPT(','+PT('):
            k=b.rfind(pat)
            if k>=0: break
        assert k>=0,no
        k+=1  # 「N(」の直前に入れる
        b=b[:k]+ins+b[k:]
    for tb in d.get('t',[]):  # 表：(見出し, [(左,右),...], (左の見出し,右の見出し))。授業の「入試ではこう出る」の直前に入れる
        cap,rows,hd=(list(tb)+[('項目','内容')])[:3]
        html="<div class='viz vtab'><div class='viz-cap'>表 ── "+cap+"</div><div class='vs'><div class='vh'><span>"+hd[0]+"</span><span>"+hd[1]+"</span></div>"+''.join(f"<div class='vr'><span>{x}</span><span>{y}</span></div>" for x,y in rows)+"</div></div>"
        if cap in b: continue
        ins=json.dumps(html,ensure_ascii=False)+'+\n'
        for pat in ('\nN(','+N(','\nPT(','+PT('):
            k=b.rfind(pat)
            if k>=0: break
        assert k>=0,no
        b=b[:k+1]+ins+b[k+1:]
    cols=[c for c in d.get('col',[]) if c[1] not in b]
    if cols:
        add=''.join(f"\n({json.dumps(a,ensure_ascii=False)},{json.dumps(x,ensure_ascii=False)})," for a,x in cols)
        k=b.find('col=[')
        if k>=0: b=b[:k+5]+add+b[k+5:]
        else:
            k=b.rstrip().rfind(')')
            b=b[:k]+',\ncol=['+add+']'+b[k:]
    t=t[:i]+b+t[j:]
open(modf,'w',encoding='utf-8').write(t)
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
p=[x for x in packs if x['id']==pid][0]
have={(q['q'],q['a']) for q in p['quiz']}; ans={q['a'] for q in p['quiz']}
n=0
for no,d in A.items():
    unit=next((q['unit'] for q in p['quiz'] if q['link']==no),p['lessons'][int(no)-1]['navTitle'])
    for qq in d.get('q',[]):
        q,a,e=(list(qq)+[''])[:3]
        if (q,a) in have or a in ans: continue
        p['quiz'].append(dict(id=max(x['id'] for x in p['quiz'])+1,unit=unit,link=no,q=q,a=a,exp=e,d=3,i=3,f=3)); n+=1; ans.add(a)
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(src,'w',encoding='utf-8').write(s)
print('merged',pid,'quiz+',n)
