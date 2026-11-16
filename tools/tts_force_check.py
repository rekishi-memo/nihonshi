# tts_force.json の読みを、エンジンがそのとおりに読むか一つずつ確かめる。2026-11-16。
#   <VOICEVOX の venv>/bin/python tts_force_check.py <VOICEVOX のフォルダ> [--write]
# アプリはふつう読みをカタカナにして渡すが、カタカナだと読みがくずれる語がある（コウニンキャクシキ→キヤク など）。
# カタカナで読みがくずれて、ひらがななら正しい語は、--write で「~ひらがな」（ひらがなのまま渡す）に直す。どちらでもくずれる語は一覧に出す。
import sys,os,json,re
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
HERE=os.path.dirname(os.path.abspath(__file__)); VV=sys.argv[1]; WRITE='--write' in sys.argv
ort=Onnxruntime.load_once(filename=os.path.join(VV,'voicevox_onnxruntime-linux-x64-1.17.3/lib/libvoicevox_onnxruntime.so.1.17.3'))
syn=Synthesizer(ort,OpenJtalk(os.path.join(VV,'open_jtalk_dic_utf_8-1.11')))
with VoiceModelFile.open(os.path.join(VV,'models','1.vvm')) as m: syn.load_voice_model(m)
def kata(s): return ''.join(chr(ord(c)+0x60) if 'ぁ'<=c<='ゖ' else c for c in s)
V={}
for row,v in [('アカサタナハマヤラワガザダバパァャヮ','ア'),('イキシチニヒミリギジヂビピィ','イ'),('ウクスツヌフムユルグズヅブプゥュヴ','ウ'),('エケセテネヘメレゲゼデベペェ','エ'),('オコソトノホモヨロヲゴゾドボポォョ','オ')]:
    for c in row: V[c]=v
def norm(s):
    s=kata(s).replace('ヂ','ジ').replace('ヅ','ズ').replace('ヲ','オ').replace('ハ','ワ').replace('ヘ','エ')
    s=re.sub(r'[^ァ-ヶー]','',s); o=[]
    for c in s:
        if c=='ー' and o: c=V.get(o[-1],c)
        elif c=='ウ' and o and V.get(o[-1])=='オ': c='オ'
        elif c=='イ' and o and V.get(o[-1])=='エ': c='エ'
        o.append(c)
    return ''.join(o)
def say(t):
    try: return norm(''.join(m.text for a in syn.create_accent_phrases(t,14) for m in a.moras))
    except Exception: return '?'
fp=os.path.join(HERE,'tts_force.json'); F=json.load(open(fp,encoding='utf-8'))
fixed=0; bad=[]
for scope,d in [('g',F['g'])]+[(k,v) for k,v in F['l'].items()]:
    for w,r in list(d.items()):
        hira=r[1:] if r.startswith('~') else r
        want=norm(hira)
        if r.startswith('~'):
            if say(hira+'。')!=want: bad.append((scope,w,r,say(hira+'。')))
            continue
        k=say(kata(hira)+'。')
        if k==want: continue
        h=say(hira+'。')
        if h==want:
            fixed+=1; print('hira',scope,w,r,k)
            if WRITE: d[w]='~'+hira
        else: bad.append((scope,w,r,k+' / '+h))
for b in bad: print('BAD',*b)
print('kata→hira',fixed,'bad',len(bad))
if WRITE: json.dump(F,open(fp,'w',encoding='utf-8'),ensure_ascii=False,indent=0,sort_keys=True)
