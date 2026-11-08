import os
HERE=os.path.dirname(os.path.abspath(__file__))
import json,re
def load_rd(extra=''):
    rd={}
    for i in range(1,13):
        f=os.path.join(HERE,('ruby.txt' if i==1 else f'ruby{i}.txt'))
        for l in open(f,encoding='utf-8').read().strip().split('\n'):
            a,b=l.split(':'); rd[a]=b
    # 成功は「じょうごう（売官）」と「せいこう」で読みが変わるので外す。売官の意味のときは各ビルドの追加辞書で指定する
    for bad in ['三浦','藩','元','聖','講','西軍','東軍','大都','ナウマンゾウ','成功','名','結','館','座']: rd.pop(bad,None)
    src=open(os.path.join(HERE,'build1.py'),encoding='utf-8').read()
    ex=re.search(r'extra="([^"]*)"',src).group(1)+' '+extra
    for kv in ex.split():
        a,b=kv.split(':',1); rd[a]=b
    rd.pop('ナウマンゾウ',None)
    return rd
def locate(packs,pid,no):
    # 授業を「もとの場所」（src＝'セットid-番号'）で探す。並べ替え（reorder.py）のあとも *_text.py などの番号がそのまま使える
    key=f'{pid}-{no}'
    for p in packs:
        for l in p['lessons']:
            if l.get('src')==key: return p,l
    p=[x for x in packs if x['id']==pid][0]
    return p,[l for l in p['lessons'] if l['no']==no][0]
def next_id(p):
    return max([q['id'] for q in p['quiz']]+[p.get('idMax',0)])+1
def rubify_fn(rd):
    keys=sorted(rd,key=len,reverse=True); pat=re.compile('|'.join(map(re.escape,keys)))
    def rubify(html):
        seen=set(); out=[]; inr=0
        for tok in re.split(r'(<[^>]+>)',html):
            if tok.startswith('<'):
                t=tok.lower()
                if t.startswith('<ruby'): inr+=1
                elif t.startswith('</ruby'): inr-=1
                out.append(tok); continue
            if inr: out.append(tok); continue
            def rep(mm):
                w=mm.group(0)
                if w in seen: return w
                seen.add(w); return f'<ruby>{w}<rt>{rd[w]}</rt></ruby>'
            out.append(pat.sub(rep,tok))
        return ''.join(out)
    return rubify
SINGLE={"臣":"おみ","連":"むらじ","君":"きみ","直":"あたい","姓":"かばね","甕":"かめ","壺":"つぼ","鉢":"はち","禊":"みそぎ","祓":"はらえ","氏":"うじ","伴":"とも","部":"べ","鍬":"くわ","鋤":"すき","租":"そ","調":"ちょう","庸":"よう","戸":"こ","評":"こおり"}
def Q(q,a): return "<details class='qcheck'><summary><span class='qmk'>？</span><span>"+q+"</span><span class='tp'>タップで確認</span></summary><div class='qa'>"+a+"</div></details>"
def build(base_in,base_out,pid,H,meta,customQ,newvis,oldmap,adds,extra_rd='',extra_vis={}):
    s=open(base_in,encoding='utf-8').read()
    m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
    p=[x for x in packs if x['id']==pid][0]
    old={l['no']:l for l in p['lessons']}
    def oldQ(no):
        q=re.search(r"<details class='qcheck'>[\s\S]*?</details>",old[no]['html']) if no in old else None
        return q.group(0) if q else ''
    rubify=rubify_fn(load_rd(extra_rd))
    lessons=[]
    for no,nav,title,unit,theme,src,qsrc in meta:
        h=H[no].replace('\n','')
        h=re.sub(r'《([^》]+)》',r"<span class='kw'>\1</span>",h)
        h=rubify(h)
        for w,r in SINGLE.items():
            h=h.replace(f"<span class='kw'>{w}</span>",f"<span class='kw'><ruby>{w}<rt>{r}</rt></ruby></span>",1)
        if '{Q}' in h:
            qq=customQ.get(no) if qsrc=='C' else (oldQ(qsrc) if qsrc else '')
            h=h.replace('{Q}',qq or '')
        L={"no":no,"navTitle":nav,"title":title,"unitLink":unit,"theme":theme,"html":h}
        if src and src in old:
            o=old[src]; L["visual"]=o.get('visual','')+extra_vis.get(no,''); L["colTitle"]=o.get('colTitle',''); L["colHtml"]=o.get('colHtml',''); L["exam"]=o.get('exam','')
        else:
            L["visual"]=newvis.get(no,'')+extra_vis.get(no,''); L["colTitle"]=""; L["colHtml"]=""; L["exam"]=""
        lessons.append(L)
    p['lessons']=lessons
    plain=lambda t: re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',t))
    txt={L['no']:plain(L['html']) for L in lessons}
    for q in p['quiz']:
        a=q.get('mark') or q['a']
        hit=[n for n in txt if a in txt[n]]
        q['link']=hit[0] if hit else oldmap.get(q.get('link'),q.get('link') or lessons[0]['no'])
        if q['link'] not in txt: q['link']=lessons[0]['no']
        q['unit']=[x for x in lessons if x['no']==q['link']][0]['unitLink']
    have={q['a'] for q in p['quiz']}
    nid=max(q['id'] for q in p['quiz'])+1; added=0; miss=[]
    for no,q,a,d,i in adds:
        if a in have: continue
        if a not in txt[no]: miss.append(no+':'+a); continue
        p['quiz'].append({"id":nid,"unit":[x for x in lessons if x['no']==no][0]['unitLink'],"link":no,"q":q,"a":a,"exp":"","d":d,"i":i,"f":4}); nid+=1; added+=1; have.add(a)
    s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
    open(base_out,'w',encoding='utf-8').write(s)
    print(pid,'lessons',len(lessons),'quiz added',added,'total',len(p['quiz']),'missing',miss)
def addquiz(base,pid,adds):
    s=open(base,encoding='utf-8').read()
    m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
    p=[x for x in packs if x['id']==pid][0]
    plain=lambda t: re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',t))
    txt={L['no']:plain(L['html']) for L in p['lessons']}
    have={q['a'] for q in p['quiz']}; nid=next_id(p)
    for no,q,a,d,i in adds:
        if a in have or a not in txt[no]: continue
        p['quiz'].append({"id":nid,"unit":[x for x in p['lessons'] if x['no']==no][0]['unitLink'],"link":no,"q":q,"a":a,"exp":"","d":d,"i":i,"f":4}); nid+=1
    s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
    open(base,'w',encoding='utf-8').write(s)
