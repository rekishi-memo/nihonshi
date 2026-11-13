# 本文の色を金の濃淡（patch_rank7 の前）にもどす。難関私大の枠からタップでとんで光らせるしくみはそのまま（2026-11-13 ユーザーの指示「やっぱり色戻して。難関私大で出るやつはそのままで」）。
#   python3 patch_rank8.py ../app/source.html ../app/source.html （何度かけても同じ）
import sys
src,out=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
R=[
("""  #lBody .kw.rk-A{font-weight:800;color:#F5D06A;}
  #lBody .kw.rk-B{font-weight:600;color:#7CC8FF;}
  #lBody .kw.rk-C{font-weight:400;color:#96D6A4;}
  #lBody .kw.rk-B .rtx,#lBody .kw.rk-B rt{color:#5d9fd0;-webkit-text-fill-color:#5d9fd0;}
  #lBody .kw.rk-C .rtx,#lBody .kw.rk-C rt{color:#6fa87c;-webkit-text-fill-color:#6fa87c;}
""","""  #lBody .kw.rk-A{font-weight:800;color:var(--gold-bright,#f3d27a);}
  #lBody .kw.rk-B{font-weight:600;color:var(--gold);}
  #lBody .kw.rk-C{font-weight:400;color:#c7b98f;}
"""),
(""".rk-legend .a b{font-weight:800;color:#F5D06A;}""",""".rk-legend .a b{font-weight:800;color:var(--gold-bright,#f3d27a);}"""),
(""".rk-legend .b b{font-weight:600;color:#7CC8FF;} .rk-legend .c b{font-weight:400;color:#96D6A4;}""",""".rk-legend .b b{font-weight:600;color:var(--gold);} .rk-legend .c b{font-weight:400;color:#c7b98f;}"""),
("""<span class="a"><b>金の太字＝共テ必修</b> 共テ・私大どちらでも土台</span><span class="b"><b>水色＝私大頻出</b> 共テでも出ることがある</span><span class="c"><b>緑＝私大</b> 細かめの語</span>""",
 """<span class="a"><b>太い金＝共テ必修</b> 共テ・私大どちらでも土台</span><span class="b"><b>金＝私大頻出</b> 共テでも出ることがある</span><span class="c"><b>うすい色＝私大</b> 細かめの語</span>"""),
]
for a,b in R:
    if b in s and a not in s: continue
    assert s.count(a)==1,a[:60]; s=s.replace(a,b)
open(out,'w',encoding='utf-8').write(s); print('ok')
