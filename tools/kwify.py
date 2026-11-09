# usage: python3 kwify.py module.py no term [term...]  : そのL['no']ブロックの P("…") 内で最初に出る語を《語》にする
import sys,re
mod,no,*terms=sys.argv[1:]
t=open(mod,encoding='utf-8').read()
i=t.index(f"L['{no}']=dict("); j=t.find("\nL['",i+5); j=len(t) if j<0 else j
b=t[i:j]
for w in terms:
    if '《'+w+'》' in b: print('already',w); continue
    done=False
    for m in re.finditer(r'\bP\("((?:[^"\\]|\\.)*)"\)',b):
        s=m.group(1); k=s.find(w)
        if k<0: continue
        # 《…》の中でないこと
        if s[:k].count('《')>s[:k].count('》'): continue
        s2=s[:k]+'《'+w+'》'+s[k+len(w):]
        b=b[:m.start(1)]+s2+b[m.end(1):]; done=True; break
    print('kw' if done else 'MISS',w)
t=t[:i]+b+t[j:]
open(mod,'w',encoding='utf-8').write(t)
