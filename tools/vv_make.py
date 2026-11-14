# VOICEVOX で授業の音声ファイルを作る（キャラクターの声で読み上げ）。2026-11-14。
#   1) node vv_dump.js /tmp/vv_in.json kodai:0            … 読み上げ原稿（アプリと同じ文の区切り・読み）を書き出す
#   2) <VOICEVOX の venv>/bin/python vv_make.py <VOICEVOX のフォルダ> /tmp/vv_in.json [声のID ...]
#      → ../audio/<pack id>/<授業の番号2桁>/<声のID>.m4a と、../audio/voices.json（どの授業にどの声があるか・文ごとの時刻）
# VOICEVOX のフォルダには、models/*.vvm、open_jtalk_dic_utf_8-1.11/、voicevox_onnxruntime-linux-x64-1.17.3/ を置く。
#   取り方：GitHub の VOICEVOX/voicevox_core・onnxruntime-builder・voicevox_vvm の Releases、r9y9/open_jtalk の Releases から直接。
# 声の一覧は vv_voices.json（クレジット表記も）。利用規約：https://github.com/VOICEVOX/voicevox_vvm （2026-11-14 ユーザーが同意）
# 授業の文を直したら、その授業の音声を作りなおす（アプリは原稿のハッシュを比べ、合わなければ端末の声で読む）。
import sys,os,json,wave,subprocess,dataclasses,time
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
VV,INP=sys.argv[1],sys.argv[2]; ONLY=set(int(x) for x in sys.argv[3:])
VOICES=json.load(open(os.path.join(HERE,'vv_voices.json'),encoding='utf-8'))
if ONLY: VOICES=[v for v in VOICES if v['id'] in ONLY]
SR=24000; GAP_S=0.12; GAP_P=0.45   # 文と文のあいだ・段落と段落のあいだ（秒）
BR=os.environ.get('VV_BR','20k')   # 音質。20k で1授業およそ0.7MB（全授業×1声で約270MB）。GitHub Pages は1GBまで
ort=Onnxruntime.load_once(filename=os.path.join(VV,'voicevox_onnxruntime-linux-x64-1.17.3/lib/libvoicevox_onnxruntime.so.1.17.3'))
syn=Synthesizer(ort,OpenJtalk(os.path.join(VV,'open_jtalk_dic_utf_8-1.11')),cpu_num_threads=os.cpu_count() or 4)
loaded=set()
def need(vvm):
    if vvm in loaded: return
    with VoiceModelFile.open(os.path.join(VV,'models',f'{vvm}.vvm')) as m: syn.load_voice_model(m)
    loaded.add(vvm)
def pcm(text,sid):
    q=syn.create_audio_query(text,sid)
    q=dataclasses.replace(q,pre_phoneme_length=0.05,post_phoneme_length=0.08)
    w=syn.synthesis(q,sid)
    import io
    with wave.open(io.BytesIO(w)) as f:
        assert f.getframerate()==SR and f.getnchannels()==1 and f.getsampwidth()==2
        return f.readframes(f.getnframes())
man_p=os.path.join(ROOT,'audio','voices.json')
man=json.load(open(man_p,encoding='utf-8')) if os.path.exists(man_p) else {'v':1,'voices':[],'lessons':{}}
allv={v['id']:v for v in json.load(open(os.path.join(HERE,'vv_voices.json'),encoding='utf-8'))}
lessons=json.load(open(INP,encoding='utf-8'))
def save():
    order=[v['id'] for v in allv.values()]
    ids=sorted({int(i) for e in man['lessons'].values() for i in e['by']},key=lambda i:order.index(i) if i in allv else 999)
    man['voices']=[allv[i] for i in ids if i in allv]
    tmp=man_p+'.tmp'; json.dump(man,open(tmp,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':')); os.replace(tmp,man_p)
for L in lessons:
    key=f"{L['pid']}:{L['i']}"; ent=man['lessons'].get(key)
    if not ent or ent.get('hash')!=L['hash']: ent={'hash':L['hash'],'by':{}}   # 原稿が変わったら作りなおし
    man['lessons'][key]=ent
    d=os.path.join(ROOT,'audio',L['pid'],f"{L['i']:02d}"); os.makedirs(d,exist_ok=True)
    for v in VOICES:
        if str(v['id']) in ent['by'] and os.path.exists(os.path.join(ROOT,ent['by'][str(v['id'])]['f'])): continue   # もう作ってある（原稿も同じ）
        need(v['vvm']); t0=time.time(); buf=bytearray(); times=[]
        for k,it in enumerate(L['items']):
            if k: buf+=b'\0\0'*int(SR*GAP_P)
            st=[]
            for j,s in enumerate(it['sents']):
                if j: buf+=b'\0\0'*int(SR*GAP_S)
                st.append(round(len(buf)/2/SR,2)); buf+=pcm(s,v['id'])
            times.append(st)
        buf+=b'\0\0'*int(SR*0.3)
        out=os.path.join(d,f"{v['id']}.m4a")
        subprocess.run(['ffmpeg','-y','-loglevel','error','-f','s16le','-ar',str(SR),'-ac','1','-i','-','-c:a','aac','-b:a',BR,'-movflags','+faststart',out],input=bytes(buf),check=True)
        ent['by'][str(v['id'])]={'f':os.path.relpath(out,ROOT).replace(os.sep,'/'),'d':round(len(buf)/2/SR,2),'t':times,'kb':os.path.getsize(out)//1024}
        print(key,v['name'],v.get('style',''),f"{len(buf)/2/SR:.0f}s",f"{os.path.getsize(out)//1024}KB",f"{time.time()-t0:.0f}s",flush=True)
    save()
save()
print('manifest',man_p)
