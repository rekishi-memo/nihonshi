# 授業の本文（地の文）だけを書き直すための道具（2026-11-10 ユーザーの指示「授業が平易で面白くない。脱線もあっていい」）。
#   python3 relesson.py <module.py> <新しい本文.txt>
# 新しい本文.txt の書式（1行＝1ブロック。空行と # で始まる行は無視）：
#   == 01            … ここから授業01
#   P: 文章           … 段落（《語》で色）
#   Y: 見出し | 文章   … 「ちょっと脱線」の箱
#   R: 文章           … 「ここで思い出そう」の箱
#   @Q               … もとの「問い」の位置（{Q}）
#   @T1 @T2 …        … もとの本文にあった表・図など（P/R/Y 以外のかたまり）を、もとの順番の番号で置く
#   @R1 @R2 …        … もとの「ここで思い出そう」をそのまま置く
#   @N @PT           … もとの「入試ではこう出る」「まとめ」
# もとの P/R/Y は捨てて、新しい行で置きかえる。col（深掘り）などはそのまま。
# もとの本文にあった《語》が新しい本文から消えていたら、エラーで止まる（一問一答の答えが授業に出なくなるのを防ぐ）。
import sys,re,json
modf,newf=sys.argv[1:3]
t=open(modf,encoding='utf-8').read()
blocks={}; cur=None
for line in open(newf,encoding='utf-8'):
    line=line.rstrip('\n')
    if not line.strip() or line.startswith('#'): continue
    if line.startswith('== '): cur=line[3:].strip(); blocks[cur]=[]; continue
    blocks[cur].append(line)
def split_top(expr):
    # 「+」でつながれた最上位の項に分ける（文字列の中の + は無視）
    items=[]; buf=''; depth=0; q=None; i=0
    while i<len(expr):
        c=expr[i]
        if q:
            buf+=c
            if c=='\\': buf+=expr[i+1]; i+=1
            elif c==q: q=None
        elif c in '"\'': q=c; buf+=c
        elif c in '([': depth+=1; buf+=c
        elif c in ')]': depth-=1; buf+=c
        elif c=='+' and depth==0: items.append(buf.strip()); buf=''
        else: buf+=c
        i+=1
    if buf.strip(): items.append(buf.strip())
    return items
J=lambda s: json.dumps(s,ensure_ascii=False)
bad=False
for no,lines in blocks.items():
    mh=re.search(r"L\['"+re.escape(no)+r"'\]=dict\((?:title=(?:\"[^\"]*\"|'[^']*'),)?html=",t)
    if mh:
        i=mh.end()
        nxt=t.find("\nL['",i); nxt=len(t) if nxt<0 else nxt
        k=t.find(",\ncol=",i,nxt)
        if k<0: k=t.rindex(')',i,nxt)
    else:  # データ型のセット（gendai4_data.py など）：L01=( … ) の形
        head=f"L{no}=("
        i=t.index(head)+len(head)
        m2=re.compile(r"\nL\d\d=\(|\nLESSONS=\[").search(t,i)
        k=t.rindex(')',i,m2.start())
    old=t[i:k]
    items=split_top(old)
    others=[x for x in items if not re.match(r'(P|R|Y)\(',x)]
    N=[x for x in others if x.startswith('N(')]; PT=[x for x in others if x.startswith('PT(')]
    T=[x for x in others if not x.startswith(('N(','PT(')) and x not in ('"{Q}"',"'{Q}'")]
    RR=[x for x in items if x.startswith('R(')]
    out=[]; used=set()
    for ln in lines:
        if ln.startswith('P: '): out.append('P('+J(ln[3:])+')')
        elif ln.startswith('R: '): out.append('R('+J(ln[3:])+')')
        elif ln.startswith('Y: '):
            a,b=ln[3:].split(' | ',1); out.append('Y('+J(a)+','+J(b)+')')
        elif ln=='@Q': out.append('"{Q}"')
        elif ln=='@N': out+=N
        elif ln=='@PT': out+=PT
        elif re.match(r'@R\d+$',ln): out.append(RR[int(ln[2:])-1])
        elif re.match(r'@T\d+$',ln): n=int(ln[2:])-1; out.append(T[n]); used.add(n)
        else: sys.exit(f'{no}: わからない行: {ln[:40]}')
    miss=[n+1 for n in range(len(T)) if n not in used]
    if miss: print(f'{no}: 置いていない表など: @T{miss}', [T[m-1][:50] for m in miss]); bad=True
    new='\n'+'+\n'.join(out)
    kw=lambda s:set(re.findall(r'《([^》]+)》',s))
    lost=kw(old)-kw(new)
    if lost: print(f'{no}: 消えた《語》:',' '.join(sorted(lost))); bad=True
    t=t[:i]+new+t[k:]
    print(no,'P',sum(1 for x in out if x.startswith('P(')),'Y',sum(1 for x in out if x.startswith('Y(')),'字',sum(len(x) for x in out))
if bad: sys.exit('書きこまずに終了')
open(modf,'w',encoding='utf-8').write(t)
print('written',modf)
