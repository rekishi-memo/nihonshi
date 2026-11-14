# 設定画面で試し聞きする、声ごとの短いサンプル音声を作る。2026-11-14。
#   <VOICEVOX の venv>/bin/python vv_sample.py <VOICEVOX のフォルダ> [声のID ...]
#   → ../audio/samples/<声のID>.m4a（数秒）。声の一覧は vv_voices.json。
import sys,os,json,io,wave,subprocess,dataclasses
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
VV=sys.argv[1]; ONLY=set(int(x) for x in sys.argv[2:])
TEXT=["この声で、授業を読みます。","1946年、群馬県の赤土の中から、人が打ち欠いた石のかけらが見つかった。"]
VOICES=[v for v in json.load(open(os.path.join(HERE,'vv_voices.json'),encoding='utf-8')) if not ONLY or v['id'] in ONLY]
SR=24000
ort=Onnxruntime.load_once(filename=os.path.join(VV,'voicevox_onnxruntime-linux-x64-1.17.3/lib/libvoicevox_onnxruntime.so.1.17.3'))
syn=Synthesizer(ort,OpenJtalk(os.path.join(VV,'open_jtalk_dic_utf_8-1.11')),cpu_num_threads=os.cpu_count() or 4)
loaded=set(); d=os.path.join(ROOT,'audio','samples'); os.makedirs(d,exist_ok=True)
for v in VOICES:
    if v['vvm'] not in loaded:
        with VoiceModelFile.open(os.path.join(VV,'models',f"{v['vvm']}.vvm")) as m: syn.load_voice_model(m)
        loaded.add(v['vvm'])
    buf=bytearray()
    for i,t in enumerate(TEXT):
        if i: buf+=b'\0\0'*int(SR*0.3)
        q=dataclasses.replace(syn.create_audio_query(t,v['id']),pre_phoneme_length=0.05,post_phoneme_length=0.1)
        with wave.open(io.BytesIO(syn.synthesis(q,v['id']))) as f: buf+=f.readframes(f.getnframes())
    out=os.path.join(d,f"{v['id']}.m4a")
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','s16le','-ar',str(SR),'-ac','1','-i','-','-c:a','aac','-b:a','40k','-movflags','+faststart',out],input=bytes(buf),check=True)
    print(v['name'],v['style'],f"{len(buf)/2/SR:.1f}s",os.path.getsize(out)//1024,'KB',flush=True)
