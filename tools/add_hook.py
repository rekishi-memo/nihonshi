import sys; sys.exit("add_hook.py は使わない（型どおりの問いは授業を平坦にした。2026-11-02 に declutter.py で消した）")
# 古い授業に「冒頭の問い」「答えの段落」「まとめ（point）」を足す。データは hook_old.py の HOOK。
#   python3 add_hook.py ../app/source.html ../app/source.html
# すでに足してあるものは足さない（問いの書き出しで判定）。
import json,re,sys
from hook_old import HOOK
src,out=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
plain=lambda t: re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',t))
n=0
for p in packs:
    for l in p['lessons']:
        d=HOOK.get(p['id'],{}).get(l['no'])
        if not d: continue
        h=l['html']
        key0=plain(d.get('q') or d.get('a') or d.get('pt'))[:20]
        if key0 in plain(h) and (not d.get('q') or plain(h).startswith(key0)): continue
        if d.get('q'): h="<p>"+d['q']+"</p>"+h
        ans=("<p>"+d['a']+"</p>") if d.get('a') else ""
        pt=("<div class='point'>"+d['pt']+"</div>") if d.get('pt') and "class='point'" not in h else ""
        if not (ans or pt): continue
        for key in ("<div class='point'>","<div class='nyushi'>"):
            i=h.find(key)
            if i>=0: h=h[:i]+ans+pt+h[i:]; break
        else: h=h+ans+pt
        l['html']=h; n+=1
print('hooked',n)
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
