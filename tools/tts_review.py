# 読みの「目による点検」用の一覧をつくる。2026-11-16（ユーザーの指摘：藤原氏を「ふじわらうじ」、倭王武を「わおうたけ」、ふり返りを「ふりがえり」と読んでいた）。
#   node tts_export.js /tmp/yomi.json
#   <VOICEVOX の venv>/bin/python tts_review.py <VOICEVOX のフォルダ> /tmp/yomi.json <出力フォルダ> [pack id ...]
# エンジン（OpenJTalk）が実際に読んだかなを、文の中の漢字のかたまりごとに切り出して、
#   <出力フォルダ>/<pack id>.tsv に「語・エンジンの読み・前後・回数・最初の文」を書く。
# アプリのふりがな・用語集の読みと一致した語も「ok」として残す（ふりがな自体のまちがいも見落とさないため、全部を人が見る）。
# 見て、まちがいは tts_force.json（全授業で同じ読み）か台本 tts_script/（その場の読み）で直し、もう一度この一覧を作って確かめる。
# 点検ずみの「語→読み」は tts_reviewed.tsv にためていき、次からは新しい語・読みだけを一覧に出す。
import sys,os,json,re,collections
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
HERE=os.path.dirname(os.path.abspath(__file__))
VV,INP,OUT=sys.argv[1],sys.argv[2],sys.argv[3]; ONLY=set(sys.argv[4:])
ort=Onnxruntime.load_once(filename=os.path.join(VV,'voicevox_onnxruntime-linux-x64-1.17.3/lib/libvoicevox_onnxruntime.so.1.17.3'))
syn=Synthesizer(ort,OpenJtalk(os.path.join(VV,'open_jtalk_dic_utf_8-1.11')))
with VoiceModelFile.open(os.path.join(VV,'models','1.vvm')) as m: syn.load_voice_model(m)
SID=14
def kata(s): return ''.join(chr(ord(c)+0x60) if 'ぁ'<=c<='ゖ' else c for c in s)
V={}
for row,v in [('アカサタナハマヤラワガザダバパァャヮ','ア'),('イキシチニヒミリギジヂビピィ','イ'),('ウクスツヌフムユルグズヅブプゥュヴ','ウ'),('エケセテネヘメレゲゼデベペェ','エ'),('オコソトノホモヨロヲゴゾドボポォョ','オ')]:
    for c in row: V[c]=v
def norm(s):
    s=kata(s).replace('ヂ','ジ').replace('ヅ','ズ').replace('ヲ','オ')
    s=re.sub(r'[^ァ-ヶー]','',s); o=[]
    for c in s:
        if c=='ー' and o: c=V.get(o[-1],c)
        elif c=='ウ' and o and V.get(o[-1])=='オ': c='オ'
        elif c=='イ' and o and V.get(o[-1])=='エ': c='エ'
        o.append(c)
    return ''.join(o)
KANA=re.compile(r'[ぁ-ゖァ-ヵヷ-ヺー]+')
PUNCT=set('、。，．,.「」『』（）()〔〕［］【】・…！？!?：:；;“”"\'　 ‥―—–-〜~')
def toks(s):
    out=[]; buf=''; kind=None
    for c in s:
        k='p' if c in PUNCT else ('k' if KANA.fullmatch(c) else 'w')
        if k=='p':
            if buf: out.append((kind,buf)); buf=''; kind=None
            continue
        if k!=kind and buf: out.append((kind,buf)); buf=''
        kind=k; buf+=c
    if buf: out.append((kind,buf))
    return out
def pat(t):
    n=norm(t); out=[]; i=0
    M={'ハ':'[ハワ]','ヘ':'[ヘエ]','オ':'[オウ]','エ':'[エイ]','ウ':'[ウオ]','イ':'[イエ]'}
    while i<len(n):
        if n[i:i+2] in('イウ','イオ'): out.append('(?:イウ|ユウ|ユオ|イオ|イエ)'); i+=2; continue   # 「いう」は「ユウ」と読む
        out.append(M.get(n[i],re.escape(n[i]))); i+=1
    return ''.join(out)
ISO={}
def iso(t):
    # その語だけを読ませたときのかな（切り分けの目安）
    if t not in ISO:
        try: ISO[t]=norm(''.join(m.text for a in syn.create_accent_phrases(t,SID) for m in a.moras))
        except Exception: ISO[t]='ー'*len(t)
    return ISO[t]
def align(tk,R):
    # 文の切れ目（かな）を手がかりに、漢字のかたまりがどのかなに当たるかを決める。
    # 単独で読ませたかなに長さ・中身がいちばん近い当て方を選ぶ（メモ化して指数時間にならないようにする）。
    import functools,sys as _s; _s.setrecursionlimit(10000)
    P=[re.compile(pat(t)) if k=='k' else None for k,t in tk]
    E=[iso(t) if k=='w' else '' for k,t in tk]
    INF=10**9
    @functools.lru_cache(None)
    def f(i,p):
        if i==len(tk): return (0,()) if p==len(R) else (INF,())
        if P[i] is not None:
            m=P[i].match(R,p)
            if not m: return (INF,())
            c,r=f(i+1,m.end()); return (c,((p,m.end()),)+r)
        best=(INF,())
        for q in range(p+1,len(R)+1):
            seg=R[p:q]; cost=0 if seg==E[i] else abs(len(seg)-len(E[i]))+1
            if cost>=best[0]: 
                if q-p>len(E[i]): break
                continue
            c,r=f(i+1,q)
            if c+cost<best[0]: best=(c+cost,((p,q),)+r)
        return best
    c,r=f(0,0)
    return None if c>=INF else r
D=json.load(open(INP,encoding='utf-8')); G=D['g']
rev={}
rp=os.path.join(HERE,'tts_reviewed.tsv')
if os.path.exists(rp):
    for l in open(rp,encoding='utf-8'):
        if l.startswith('#') or '\t' not in l: continue
        w,r=l.rstrip('\n').split('\t')[:2]; rev.setdefault(w,set()).add(norm(r))
os.makedirs(OUT,exist_ok=True)
per=collections.defaultdict(lambda: collections.OrderedDict()); fails=collections.defaultdict(list)
for L in D['L']:
    pid=L['k'].split(':')[0]
    if ONLY and pid not in ONLY: continue
    loc=L['loc']
    for s in L['s']:
        tk=toks(s)
        if not any(k=='w' for k,_ in tk): continue
        raw=re.sub(r'[^ァ-ヶー]','',kata(''.join(m.text for a in syn.create_accent_phrases(s,SID) for m in a.moras))); kana=norm(raw)
        sp=align(tk,kana)
        if sp is None: fails[pid].append((L['k'],s,raw)); continue
        for i,(k,t) in enumerate(tk):
            if k!='w': continue
            r=raw[sp[i][0]:sp[i][1]]
            if not re.search(r'[一-鿿々〆ヶ0-9０-９A-Za-zＡ-Ｚａ-ｚ]',t): continue
            pre=tk[i-1][1][-3:] if i>0 and tk[i-1][0]=='k' else ''
            post=tk[i+1][1][:3] if i+1<len(tk) and tk[i+1][0]=='k' else ''
            key=(pre,t,post,r)
            refs=(loc.get(t) or [])+(G.get(t) or [])
            rk=t+(f'({post[:1]})' if len(t)==1 and post else '')   # 1字の語は、すぐあとのかなも合わせて点検ずみかを見る（市が／市の…で読みが変わる）
            st='rev' if norm(r) in rev.get(rk,()) else ('ok' if any(norm(x)==norm(r) for x in refs) else '')
            e=per[pid].get(key)
            if e: e[0]+=1
            else: per[pid][key]=[1,st,'/'.join(refs),L['k'],s]
for pid in sorted(set(per)|set(fails)):
    rows=per[pid]
    with open(os.path.join(OUT,pid+'.tsv'),'w',encoding='utf-8') as f:
        for (pre,t,post,r),(n,st,refs,k,s) in rows.items():
            f.write(f'{st}\t{pre}[{t}]{post}\t{r}\t{refs}\t{n}\t{k}\t{s}\n')
        for k,s,kana in fails[pid]: f.write(f'FAIL\t\t{kana}\t\t\t{k}\t{s}\n')
    c=collections.Counter(v[1] for v in rows.values())
    print(pid,'語',len(rows),'未点検',c[''],'ok',c['ok'],'点検ずみ',c['rev'],'照合できず',len(fails[pid]))
