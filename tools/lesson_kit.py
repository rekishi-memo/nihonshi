# 授業本文を書くための小さな道具（新しいセットのデータファイルから import する）
from buildpack import Q
def P(t): return '<p>'+t+'</p>'
def R(t): return "<div class='recall'><span class='bx-tag'>ここで思い出そう</span>"+t+"</div>"
def Y(title,t): return "<div class='yodan'><span class='yd-tag'>ちょっと脱線</span><b>"+title+"</b>"+t+"</div>"
def N(t): return "<div class='nyushi'><span class='bx-tag'>入試ではこう出る</span>"+t+"</div>"
def D(title,t): return "<div class='deep'><span class='bx-tag'>難関＋</span>"+(f"<b>{title}</b>　" if title else '')+t+"</div>"
def PT(t): return "<div class='point'>"+t+"</div>"
def vs(rows,h=('項目','内容')): return "<div class='vs'><div class='vh'><span>"+h[0]+"</span><span>"+h[1]+"</span></div>"+''.join(f"<div class='vr'><span>{a}</span><span>{b}</span></div>" for a,b in rows)+"</div>"
def viz(cap,inner): return "<div class='viz'><div class='viz-cap'>図 ── "+cap+"</div>"+inner+"</div>"
def link(a,b,label,kind): return {'from':a,'to':b,'label':label,'kind':kind}
