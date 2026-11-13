# 本文の「テーマ史：琉球・沖縄史」がタップで飛べなかった（名前の中の「・」で切れていた）のを直す。2026-11-13
#   python3 patch_xref2.py ../app/source.html ../app/source.html
import sys
src,out=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
a="|テーマ史[：〈]([^（）〉・、。 　]+)〉?(?:[ 　の]*授業(\\d{2}))?|"
b="|テーマ史[：〈]([^（）〉、。 　]+)〉?(?:[ 　の]*授業(\\d{2}))?|"
assert s.count(a)==1,s.count(a); s=s.replace(a,b)
a='else if(m[5]) mk(m[0],packByLabel("テーマ史："+m[5]),m[6]||null,ctx);'
b='else if(m[5]){ let lab=m[5], pid=packByLabel("テーマ史："+lab); while(!pid&&lab.indexOf("・")>0){ lab=lab.slice(0,lab.lastIndexOf("・")); pid=packByLabel("テーマ史："+lab); } mk(m[0],pid,m[6]||null,ctx); }'
assert s.count(a)==1; s=s.replace(a,b)
a2='let lab=m[5], pid=packByLabel("テーマ史："+lab); while(!pid&&lab.indexOf("・")>0)'
b2='let lab=m[5], pid=packByLabel("テーマ史："+lab); if(!pid){ const l2=lab.replace(/[へにのでをと]+$/,""); if(l2!==lab&&packByLabel("テーマ史："+l2)){ lab=l2; pid=packByLabel("テーマ史："+l2); } } while(!pid&&lab.indexOf("・")>0)'
assert s.count(a2)==1; s=s.replace(a2,b2)
open(out,'w',encoding='utf-8').write(s); print('ok')
# 2回目：名前のすぐ後ろの「へ」「に」などもつながって読まれるので、外して探す
