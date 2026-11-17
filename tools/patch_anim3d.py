# 動く図（an3）のしくみとデータを、アプリの土台に入れる（何度回してもよい。前に入れたものは目印で入れ直す）
#   python3 patch_anim3d.py <土台.html>
#   CSS＝anim3d.css、JS＝anim3d_rt.js、データ＝anim3d.py の build()（window.AN3_DATA）。
#   授業のタブの上に「○○を、動く図で」の入口を出し、押すと全画面で再生する。読み上げ・音声には関係しない。
import re,sys,os,json
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H)
import anim3d
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
css=open(os.path.join(H,'anim3d.css'),encoding='utf-8').read().strip()
js=open(os.path.join(H,'anim3d_rt.js'),encoding='utf-8').read().strip()
data='window.AN3_DATA='+json.dumps(anim3d.build(),ensure_ascii=False,separators=(',',':'))+';'
s=re.sub(r'\n?/\*AN3CSS-BEGIN\*/[\s\S]*?/\*AN3CSS-END\*/\n?','\n',s)
s=re.sub(r'<script>/\*AN3DATA\*/[\s\S]*?</script>\n?','',s)
s=re.sub(r'<script>/\*AN3-BEGIN\*/[\s\S]*?/\*AN3-END\*/</script>\n?','',s)
i=s.index('</style>'); s=s[:i].rstrip('\n')+'\n'+css+'\n'+s[i:]
i=s.rindex('</body>'); s=s[:i]+'<script>/*AN3DATA*/'+data+'</script>\n<script>'+js+'</script>\n'+s[i:]
hook='linkRefs(document.getElementById("lBody"));'
call=' if(window.an3Mount) an3Mount(document.getElementById("lBody"));'
if hook+call not in s:
    assert s.count(hook)==1; s=s.replace(hook,hook+call)
open(f,'w',encoding='utf-8').write(s); print('an3 patched',len(data))
