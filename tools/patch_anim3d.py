# 動く図（an3）のしくみとデータを、アプリの土台に入れる（何度回してもよい。前に入れたものは目印で入れ直す）
#   python3 patch_anim3d.py <土台.html>
#   CSS＝anim3d.css、JS＝anim3d_rt.js、データ＝anim3d.py の build()（window.AN3_DATA）。
#   「動画」タブ（授業と一問一答のあいだ）をつくり、そのセットの動画をそこで再生する。読み上げ・音声には関係しない。
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
# 「動画」タブ（授業と一問一答のあいだ）
s=s.replace('{k:"lesson",l:"授業"},{k:"quiz",l:"一問一答"}','{k:"lesson",l:"授業"},{k:"video",l:"動画"},{k:"quiz",l:"一問一答"}')
assert '{k:"video",l:"動画"}' in s
if 'id="sec-video"' not in s:
    s=s.replace('  <section class="sec" id="sec-quiz">','  <section class="sec" id="sec-video"><div id="an3Video"></div></section>\n  <section class="sec" id="sec-quiz">',1)
sw='document.getElementById("sec-"+k).classList.add("active");'
if sw+' if(window.an3Sec) an3Sec(k);' not in s:
    assert s.count(sw)==1; s=s.replace(sw,sw+' if(window.an3Sec) an3Sec(k);')
hook='linkRefs(document.getElementById("lBody"));'
call=' if(window.an3Mount) an3Mount(document.getElementById("lBody"));'
if hook+call not in s:
    assert s.count(hook)==1; s=s.replace(hook,hook+call)
open(f,'w',encoding='utf-8').write(s); print('an3 patched',len(data))
