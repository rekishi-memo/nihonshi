# 読み上げで「漢字のまま読ませてよい語」（tts_keep.txt）を決める。2026-11-14。
#   python3 tts_yomi.py tts_words.tsv tts_keep.txt
# 考え方：アプリのふりがな（約5400語）から、漢字1字ごとの読みを推定する（EM で読みを字に割りふる）。
#   語のどの字も「その字でよく使われる読み」なら、端末の声も正しく読めるとみて漢字のまま残す。
#   特別な読み（大王＝おおきみ、三浦＝さんぽ、上野＝こうずけ など）の語は、ふりがなの読みに置きかえて読ませる。
#   ふつうは別の読みになる語（神輿＝しんよ、定子＝ていし など）は NEED_FORCE に入れて、必ず読みに置きかえる。
import re,sys,collections,math
NEED_FORCE=set("神輿 定子 彰子 漢書 後漢書 大人 神人 家人 公事 名主 上方 目代 田堵 下人 大王 本所 公領 人夫 生糸 仲間 寄合 年寄 頭 宗氏 和人 国人 天下人".split())
src,dst=sys.argv[1],sys.argv[2]
rows=[l.rstrip('\n').split('\t') for l in open(src,encoding='utf-8') if l.strip()]
def hira(s): return ''.join(chr(ord(ch)-0x60) if 'ァ'<=ch<='ヶ' else ch for ch in s)
isK=lambda ch: bool(re.match(r'[㐀-鿿〆ヶ]',ch))
DV=str.maketrans('がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ','かきくけこさしすせそたちつてとはひふへほはひふへほ')
def norm(s):
    s=s[0].translate(DV)+s[1:]
    if len(s)>=2 and s[-1] in 'っつくちき': s=s[:-1]+'#'
    return s
SMALL='ゃゅょぁぃぅぇぉっー'
def allsegs(base,read,limit=4000):
    out=[]
    def rec(i,j,acc):
        if len(out)>limit: return
        if i==len(base):
            if j==len(read): out.append(tuple(acc))
            return
        ch=base[i]
        if ch=='々' and acc: ch=acc[-1][0]
        elif not isK(ch):
            h=hira(ch)
            if ch in '・、 ＝=': rec(i+1,j,acc); return
            if read[j:j+1]==h or (h=='ー' and j<len(read)): rec(i+1,j+1,acc)
            return
        for L in range(1,5):
            if j+L>len(read): break
            s=read[j:j+L]
            if s[0] in SMALL: break
            rec(i+1,j+L,acc+[(ch,s)])
    rec(0,0,[]); return out
words=[]
for c,b,r in rows:
    b=b.strip(); r=hira(r.strip())
    if b and r: words.append((b,r,allsegs(b,r)))
lp=lambda P,ch,s: math.log(max(P.get((ch,norm(s)),0),1e-6))
P=None
for it in range(8):
    C=collections.Counter()
    for b,r,S in words:
        if not S or len(S)>4000: continue
        if P is None: ws=[1.0]*len(S)
        else:
            ls=[sum(lp(P,ch,s) for ch,s in sg) for sg in S]; mx=max(ls); ws=[math.exp(x-mx) for x in ls]
        z=sum(ws)
        for sg,w in zip(S,ws):
            for ch,s in sg: C[(ch,norm(s))]+=w/z
    T=collections.Counter()
    for (ch,s),v in C.items(): T[ch]+=v
    P={k:v/T[k[0]] for k,v in C.items()}
best={}
HC=collections.Counter(); HT=collections.Counter()
for b,r,S in words:
    if not S: continue
    sg=max(S,key=lambda sg: sum(lp(P,ch,s) for ch,s in sg)); best[(b,r)]=sg
    for ch,s in sg: HC[(ch,norm(s))]+=1; HT[ch]+=1
reads=collections.defaultdict(set)
for b,r,S in words: reads[b].add(r)
keep=set()
for (b,r),sg in best.items():
    if b in NEED_FORCE or len(reads[b])>1 or not sg: continue
    th=0.2 if len(sg)>=4 else 0.5
    if all(HC[(ch,norm(s))]>=3 and HC[(ch,norm(s))]/HT[ch]>=th for ch,s in sg): keep.add(b)
open(dst,'w',encoding='utf-8').write('\n'.join(sorted(keep))+'\n')
print('keep',len(keep),'of',len(reads))
