# 古い授業の「型どおりの冒頭の問い」「冒頭の問いに戻ろう（答えの段落）」と、本文のくり返しにすぎない難関＋枠を消す。
#   python3 declutter.py ../app/source.html ../app/source.html [packid ...]
import json,re,sys
from hook_old import HOOK
src,out=sys.argv[1],sys.argv[2]; only=set(sys.argv[3:])
def plain(h): return re.sub(r'<[^>]+>','',re.sub(r'<rt>[^<]*</rt>','',h or ''))
s=open(src,encoding='utf-8').read()
m=re.search(r'const DEFAULT_PACKS = (\[[\s\S]*?\n\]);',s); packs=json.loads(m.group(1))
K=re.compile(r'[一-龥ァ-ヶー]{2,}')
st={'q':0,'a':0,'deep':0}
for p in packs:
    if only and p['id'] not in only: continue
    H=HOOK.get(p['id'],{})
    ans=[(q.get('mark') or q['a']) for q in p['quiz']]
    for l in p['lessons']:
        h=l['html']; d=H.get(l['no'],{})
        for key in ('q','a'):
            t=plain(d.get(key,''))[:18]
            if not t: continue
            for mm in re.finditer(r'<p>[\s\S]*?</p>',h):
                if plain(mm.group(0)).startswith(t):
                    h=h[:mm.start()]+h[mm.end():]; st[key]+=1; break
        # 答えの段落の型（「冒頭の問いに戻ろう」「冒頭の問いの答えはこれだ」）がほかにも残っていれば消す
        for mm in list(re.finditer(r'<p>[\s\S]*?</p>',h))[::-1]:
            if re.match(r'(冒頭の問いに戻ろう|冒頭の問いの答え)',plain(mm.group(0))):
                h=h[:mm.start()]+h[mm.end():]; st['a']+=1
        # 本文のくり返しにすぎない難関＋枠
        body=plain(re.sub(r"<div class='deep'>[\s\S]*?</div>",'',h))
        def rep(mm):
            t=plain(mm.group(0)).replace('難関＋','')
            ws=set(K.findall(t))
            if not ws: return mm.group(0)
            cover=sum(1 for w in ws if w in body)/len(ws)
            only_here=[a for a in ans if a in t and a not in body]
            if cover>=0.85 and not only_here:
                st['deep']+=1; return ''
            return mm.group(0)
        h=re.sub(r"<div class='deep'>[\s\S]*?</div>",rep,h)
        l['html']=h
print(st)
s=s[:m.start(1)]+json.dumps(packs,ensure_ascii=False,indent=1)+s[m.end(1):]
open(out,'w',encoding='utf-8').write(s)
