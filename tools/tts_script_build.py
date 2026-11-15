# tools/tts_script/<pack id>.py（読み上げ台本）をまとめて tools/tts_script.json にする。
#   python3 tts_script_build.py
import os,json,importlib.util,glob
HERE=os.path.dirname(os.path.abspath(__file__)); out={}
for f in sorted(glob.glob(os.path.join(HERE,'tts_script','*.py'))):
    pid=os.path.basename(f)[:-3]; sp=importlib.util.spec_from_file_location('s_'+pid,f); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    for i,pairs in m.S.items(): out[f'{pid}:{i}']=[[a,b] for a,b in pairs]
json.dump(out,open(os.path.join(HERE,'tts_script.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
print('lessons',len(out),'pairs',sum(len(v) for v in out.values()))
