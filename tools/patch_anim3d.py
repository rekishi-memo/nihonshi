# 立体の動く図（an3）のしくみを、アプリの土台に入れる（何度回してもよい。前に入れたものは目印で入れ直す）
#   python3 patch_anim3d.py <土台.html>
#   CSS＝anim3d.css、JS＝anim3d_rt.js。授業を表示したあとに an3Mount を呼ぶ。読み上げは段落（<p>）だけなので、動く図は読まない。
import re,sys,os
H=os.path.dirname(os.path.abspath(__file__))
f=sys.argv[1]; s=open(f,encoding='utf-8').read()
css=open(os.path.join(H,'anim3d.css'),encoding='utf-8').read().strip()
js=open(os.path.join(H,'anim3d_rt.js'),encoding='utf-8').read().strip()
s=re.sub(r'\n?/\*AN3CSS-BEGIN\*/[\s\S]*?/\*AN3CSS-END\*/\n?','\n',s)
s=re.sub(r'\n?<script>/\*AN3-BEGIN\*/[\s\S]*?/\*AN3-END\*/</script>','',s)
i=s.index('</style>'); s=s[:i].rstrip('\n')+'\n'+css+'\n'+s[i:]
i=s.rindex('</body>'); s=s[:i]+'<script>'+js+'</script>\n'+s[i:]
hook='linkRefs(document.getElementById("lBody"));'
call=' if(window.an3Mount) an3Mount(document.getElementById("lBody"));'
if hook+call not in s:
    assert s.count(hook)==1; s=s.replace(hook,hook+call)
open(f,'w',encoding='utf-8').write(s); print('an3 patched')
