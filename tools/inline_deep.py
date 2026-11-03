# 深掘り（colHtml）を授業の流れの中に移す。各項目を、いちばん関係の深い段落のすぐ後ろに「難関＋」の枠として差しこむ。
# post.py から呼ばれる。単独でも  python3 inline_deep.py ../app/source.html ../app/source.html
import re,json,sys
def plain(h): return re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',h or ''))
def items_of(col):
    out=[]
    for p in re.findall(r'<p[^>]*>([\s\S]*?)</p>',col):
        mm=re.match(r'\s*<b>■\s*([\s\S]*?)</b>\s*　?([\s\S]*)',p)
        if mm: out.append((mm.group(1),mm.group(2)))
        else:
            mm=re.match(r'\s*<b>([\s\S]*?)</b>\s*([\s\S]*)',p)
            out.append((mm.group(1).rstrip('：:'),mm.group(2)) if mm and len(plain(mm.group(1)))<25 else ('',p))
    return out
def terms(h):
    t=set(plain(x) for x in re.findall(r"<span class='kw'>([\s\S]*?)</span>",h))
    t|=set(re.findall(r'[一-龥ァ-ヶー]{2,}',plain(h)))
    return {x for x in t if len(x)>=2}
def convert(l):
    if l.get('keepCol'): return False  # 深掘り欄に残す授業は本文に移さない
    col=l.get('colHtml') or ''
    if not col: return False
    h=l['html']; paras=list(re.finditer(r'<p>[\s\S]*?</p>',h))
    ins={}
    for title,text in items_of(col):
        ts=terms(title+text); best=None; bs=0
        for i,m in enumerate(paras):
            pt=plain(m.group(0)); sc=sum(len(x) for x in ts if x in pt)
            if sc>bs: bs,best=sc,i
        box="<div class='deep'><span class='bx-tag'>難関＋</span>"+(f"<b>{title}</b>　" if title else '')+text+"</div>"
        key=paras[best].end() if best is not None and bs>=4 else None
        ins.setdefault(key,[]).append(box)
    tail=''.join(ins.pop(None,[]))
    for pos in sorted(ins,reverse=True): h=h[:pos]+''.join(ins[pos])+h[pos:]
    if tail:
        i=h.find("<div class='point'>")
        h=h[:i]+tail+h[i:] if i>=0 else h+tail
    l['html']=h; l['colHtml']=''; l['colTitle']=''
    return True
if __name__=='__main__':
    src,out=sys.argv[1],sys.argv[2]
    s=open(src,encoding='utf-8').read()
    m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
    n=sum(convert(l) for p in packs for l in p['lessons'])
    print('inlined lessons',n)
    s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
    open(out,'w',encoding='utf-8').write(s)
