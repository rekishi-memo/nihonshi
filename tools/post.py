import json,re,subprocess,sys
src,out,pid=sys.argv[1],sys.argv[2],sys.argv[3]
r=subprocess.run(['node','kw_all.js',src,out+'.tmp'],capture_output=True,text=True); print((r.stdout or r.stderr).split('\n')[0])
s=open(out+'.tmp',encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
for p in packs:
    for l in p.get('lessons',[]):
        for k in ('html','colHtml'):
            h=l.get(k) or ''
            for a,ra in [('鎌倉','かまくら'),('室町','むろまち'),('江戸','えど')]:
                pat=r"<span class='kw'>(?:<ruby>)?"+a+r"(?:<rt>[^<]*</rt></ruby>)?</span><ruby>幕府<rt>[^<]*</rt></ruby>"
                h=re.sub(pat,f"<span class='kw'><ruby>{a}幕府<rt>{ra}ばくふ</rt></ruby></span>",h)
            h=re.sub(r"([中外異])<span class='kw'>((?:<ruby>)?国人(?:<rt>[^<]*</rt></ruby>)?)</span>",lambda mm: mm.group(1)+re.sub(r'<rt>[^<]*</rt>|</?ruby>','',mm.group(2)),h)
            h=re.sub(r"(?:<span class='kw'>)?(?:<ruby>)?大都(?:<rt>[^<]*</rt></ruby>)?(?:</span>)?市","大都市",h)
            h=re.sub(r"島<span class='kw'>((?:<ruby>)?原城(?:<rt>[^<]*</rt></ruby>)?)</span>",lambda mm:"島"+re.sub(r'<rt>[^<]*</rt>|</?ruby>','',mm.group(1)),h)
            h=re.sub(r"狗<span class='kw'>((?:<ruby>)?奴国(?:<rt>[^<]*</rt></ruby>)?)</span>",lambda mm:"狗"+re.sub(r'<rt>[^<]*</rt>|</?ruby>','',mm.group(1)),h)
            h=re.sub(r"([使念鳴事書旅図学会博物])<ruby>館<rt>やかた</rt></ruby>",r"\1館",h)  # 公使館・記念館などは「かん」
            l[k]=h
from inline_deep import convert  # 深掘りを授業の流れの中に移す
for _p in packs:
    for _l in _p['lessons']: convert(_l)
p=[x for x in packs if x['id']==pid][0]
bad=[]
for q in p['quiz']:
    mark=q.get('mark') or q['a']; l=[x for x in p['lessons'] if x['no']==q['link']][0]
    kws=[re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',x)) for x in re.findall(r"<span class='kw'>([\s\S]*?)</span>",l['html'])]
    if not any(mark in t for t in kws): bad.append(q['link']+':'+mark)
print('not-kw',bad)
K=re.compile(r'[\u4e00-\u9fff々]'); emb=set()
for l in p['lessons']:
    h=re.sub(r'<rt>[^<]*</rt>','',l['html']).replace("<span class='kw'>","\x01").replace('</span>','\x02'); h=re.sub(r'<[^>]+>','',h)
    for mm in re.finditer(r'\x01([^\x01\x02]*)\x02',h):
        b=h[mm.start()-1:mm.start()]; a=h[mm.end():mm.end()+1]
        if (b and K.match(b)) or (a and K.match(a)): emb.add(b+'['+mm.group(1)+']'+a)
print('embedded:',' '.join(sorted(emb)))
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
