# 音声エンジン（VOICEVOX の OpenJTalk）に全授業の読み上げ文を読ませ、アプリの中の正しい読みと食いちがう語を見つける。2026-11-15。
#   node tts_export.js /tmp/yomi.json
#   <VOICEVOX の venv>/bin/python tts_check.py <VOICEVOX のフォルダ> /tmp/yomi.json [--write]
#   --write で、食いちがった語を tts_force.json に足す（g＝読みが一つの語は全授業で、l＝読みが授業ごとにちがう語はその授業だけ）。
#   足したあと patch を当てなおして、もう一度点検し、食いちがいが 0 になることを確かめる。
import sys,os,json,re,collections
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
HERE=os.path.dirname(os.path.abspath(__file__))
VV,INP=sys.argv[1],sys.argv[2]; WRITE='--write' in sys.argv
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
isK=lambda c: bool(c) and bool(re.match(r'[一-鿿々〆ヶ]',c))
D=json.load(open(INP,encoding='utf-8'))
G=D['g']
bad=collections.defaultdict(list); n=0; nwords=0
for L in D['L']:
    loc=L['loc']
    words={w:(loc.get(w) or G.get(w)) for w in set(list(G)+list(loc))}
    for s in L['s']:
        hits=[w for w in words if w in s]
        if not hits: continue
        hits.sort(key=len,reverse=True)
        kana=None
        for w in hits:
            i=s.find(w); ok_pos=False
            while i>=0:
                if not isK(s[i-1] if i>0 else '') and not isK(s[i+len(w)] if i+len(w)<len(s) else ''): ok_pos=True; break
                i=s.find(w,i+1)
            if not ok_pos: continue
            if any(w!=x and w in x and x in s for x in hits): continue   # もっと長い語の一部
            if kana is None: kana=norm(''.join(m.text for a in syn.create_accent_phrases(s,SID) for m in a.moras)); n+=1
            rs=words[w]; nwords+=1
            if not any(norm(r) in kana for r in rs): bad[w].append((L['k'],rs,s))
print('sentences analysed',n,'word checks',nwords,'misread words',len(bad))
for w,v in sorted(bad.items(),key=lambda x:-len(x[1]))[:400]:
    print(f'{w}\t{"/".join(v[0][1])}\t{len(v)}\t{v[0][0]}\t{v[0][2][:60]}')
if WRITE:
    fp=os.path.join(HERE,'tts_force.json'); F=json.load(open(fp,encoding='utf-8')) if os.path.exists(fp) else {'g':{},'l':{}}
    for w,v in bad.items():
        for k,rs,s in v:
            if len(rs)==1 and len(G.get(w,rs))<=1: F['g'][w]=rs[0]
            else: F['l'].setdefault(k,{})[w]=rs[0]
    json.dump(F,open(fp,'w',encoding='utf-8'),ensure_ascii=False,indent=0,sort_keys=True)
    print('written',len(F['g']),sum(len(x) for x in F['l'].values()))
