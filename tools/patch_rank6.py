# 重要度の名前を、ユーザーのたとえ（幹・枝・葉）ではなく「どの試験のために覚える語か」で付け直す（2026-11-13 ユーザーの指摘「幹枝葉は例えで出した。なんで真似するかな」）。
#   python3 patch_rank6.py ../app/source.html ../app/source.html （何度かけても同じ）
import sys
src,out=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
R=[
('<button data-mode="kan" aria-pressed="false">幹</button>','<button data-mode="kan" aria-pressed="false">共テ必修</button>'),
('<button data-mode="eda" aria-pressed="false">幹＋枝</button>','<button data-mode="eda" aria-pressed="false">私大頻出</button>'),
('<button data-mode="nan" aria-pressed="false">難関</button>','<button data-mode="nan" aria-pressed="false">難関私大</button>'),
('<button data-mode="freq" aria-pressed="false">頻出</button>','<button data-mode="freq" aria-pressed="false">過去問</button>'),
('<button class="ghost" data-m="A">幹だけ</button><button class="ghost" data-m="AB">幹・枝</button><button class="ghost" data-m="ABCX" aria-pressed="true">葉まで</button><button class="ghost" data-m="ABCXD">難関私大まで</button>',
 '<button class="ghost" data-m="A">共テ必修</button><button class="ghost" data-m="AB">私大頻出まで</button><button class="ghost" data-m="ABCX" aria-pressed="true">私大まで</button><button class="ghost" data-m="ABCXD">難関私大まで</button>'),
('''lg.innerHTML='<span class="a"><b>太い金＝幹</b> 共テの土台</span><span class="b"><b>金＝枝</b> 共テ・私大の標準</span><span class="c"><b>うすい色＝葉</b> 私大の細かめ</span><span class="d"><b>紫＝難関私大</b> 本文では色なし。下の枠で</span>';''',
 '''lg.innerHTML='<span class="a"><b>太い金＝共テ必修</b> 共テ・私大どちらでも土台</span><span class="b"><b>金＝私大頻出</b> 共テでも出ることがある</span><span class="c"><b>うすい色＝私大</b> 細かめの語</span><span class="d"><b>紫＝難関私大</b> 本文は色なし。下の枠で</span>';'''),
('''${({5:"幹",4:"枝",3:"葉",2:"難関私大"})[q.i]||""}''','''${({5:"共テ必修",4:"私大頻出",3:"私大",2:"難関私大"})[q.i]||""}'''),
('''const RK_NAME={A:"幹",B:"枝",C:"葉",D:"難関私大",X:"＋α"};''','''const RK_NAME={A:"共テ必修",B:"私大頻出",C:"私大",D:"難関私大",X:""};'''),
('  .modes{display:flex;gap:7px;flex-wrap:wrap;}','  .modes{display:grid;gap:7px;grid-template-columns:repeat(3,1fr);}'),
]
for a,b in R:
    if b in s: continue
    assert s.count(a)==1,a[:50]; s=s.replace(a,b)
open(out,'w',encoding='utf-8').write(s); print('ok')
