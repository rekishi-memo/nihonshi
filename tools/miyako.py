# 都の中の配置図（藤原京・平城京・平安京）。2026-11-17 ユーザーの指示「都の形とかどこに何があるとかの図もつくって」。
# 地図ではなく、条坊（碁盤の目）を1マス＝1坊として描いた模式図。北が上、東が右（左京＝東、右京＝西）。
# 位置の出典は教科書の図の一般的な描き方（条・坊の番号）。くわしい場所は「おおよそ」。
FONT="font-family:'Hiragino Sans','Noto Sans JP',system-ui,sans-serif;"
BG='#0F1626'; GRID='#33406A'; GOLD='#D4BD82'; RED='#E07A5F'; TXT='#F3E9CF'; DIM='#8E9AB8'
HALO=f"paint-order:stroke;stroke:{BG};stroke-width:3px;stroke-linejoin:round;"

def _f(v): return f"{v:.1f}".rstrip('0').rstrip('.')

class _P:
    def __init__(s,cols,rows,u,ox,oy): s.cols,s.rows,s.u,s.ox,s.oy=cols,rows,u,ox,oy
    def x(s,c): return s.ox+c*s.u
    def y(s,r): return s.oy+r*s.u

def _t(x,y,t,size=11,fill=TXT,anchor='middle',bold=True):
    w='font-weight:700;' if bold else ''
    return f"<text x='{_f(x)}' y='{_f(y)}' text-anchor='{anchor}' style='fill:{fill};font-size:{size}px;{w}{FONT}{HALO}'>{t}</text>"

def _grid(P,c0,c1,r0,r1):
    el=[f"<rect x='{_f(P.x(c0))}' y='{_f(P.y(r0))}' width='{_f(P.x(c1)-P.x(c0))}' height='{_f(P.y(r1)-P.y(r0))}' style='fill:#1C2440;stroke:{GOLD};stroke-width:1.2;'/>"]
    for c in range(c0+1,c1): el.append(f"<line x1='{_f(P.x(c))}' y1='{_f(P.y(r0))}' x2='{_f(P.x(c))}' y2='{_f(P.y(r1))}' style='stroke:{GRID};stroke-width:.8;'/>")
    for r in range(r0+1,r1): el.append(f"<line x1='{_f(P.x(c0))}' y1='{_f(P.y(r))}' x2='{_f(P.x(c1))}' y2='{_f(P.y(r))}' style='stroke:{GRID};stroke-width:.8;'/>")
    return el

def _box(P,c0,r0,c1,r1,fill,label,size=11):
    el=[f"<rect x='{_f(P.x(c0))}' y='{_f(P.y(r0))}' width='{_f(P.x(c1)-P.x(c0))}' height='{_f(P.y(r1)-P.y(r0))}' style='fill:{fill};stroke:{GOLD};stroke-width:1;'/>"]
    if label: el.append(_t((P.x(c0)+P.x(c1))/2,(P.y(r0)+P.y(r1))/2+size*0.38,label,size))
    return el

def _spot(P,c,r,label,anchor='middle',dy=-7,color=RED):
    x,y=P.x(c),P.y(r)
    return [f"<rect x='{_f(x-4)}' y='{_f(y-4)}' width='8' height='8' style='fill:{color};stroke:{BG};stroke-width:1;'/>",
            _t(x+(0 if anchor=='middle' else (7 if anchor=='start' else -7)),y+(dy if anchor=='middle' else 4),label,10.5,TXT,anchor)]

def _wrap(title,note,W,H,el):
    svg=f"<svg viewBox='0 0 {_f(W)} {_f(H)}' width='100%' role='img' aria-label='{title}'><rect width='{_f(W)}' height='{_f(H)}' style='fill:{BG};'/>"+''.join(el)+"</svg>"
    cap=f"図 ── {title}"+(f"（{note}）" if note else '')
    return f"<div class='viz jm'><div class='viz-cap'>{cap}</div><div class='mapwrap'>{svg}</div></div>"

def heijo():
    # 平城京：右京4坊＋左京4坊、一条〜九条。外京＝左京の五〜七坊の一条〜五条。宮は一条〜二条の中央2坊
    u=24; P=_P(11,9,u,22,30); W=P.x(11)+40; H=P.y(9)+36
    el=_grid(P,0,8,0,9)+_grid(P,8,11,0,5)
    el+=_box(P,3,0,5,2,'rgba(224,122,95,.45)','平城宮',11.5)
    el.append(f"<line x1='{_f(P.x(4))}' y1='{_f(P.y(2))}' x2='{_f(P.x(4))}' y2='{_f(P.y(9))}' style='stroke:{GOLD};stroke-width:3.2;'/>")
    el.append(_t(P.x(4)+6,P.y(4.6),'朱雀大路',10,GOLD,'start'))
    el.append(_t(P.x(4)+6,P.y(2)+12,'朱雀門',9.5,DIM,'start',False))
    el.append(_t(P.x(4),P.y(9)+14,'羅城門',10.5,TXT))
    el.append(_t(P.x(2),P.y(9)+28,'右京（西）',11,DIM,'middle',False)); el.append(_t(P.x(6),P.y(9)+28,'左京（東）',11,DIM,'middle',False))
    el.append(_t(P.x(9.5),P.y(5)+14,'外京',11,DIM,'middle',False))
    el+=_spot(P,6.5,7.5,'東市'); el+=_spot(P,2.5,7.5,'西市')   # 東市＝左京八条三坊、西市＝右京八条二坊
    el+=_spot(P,7.5,5.5,'大安寺'); el+=_spot(P,2.5,5.5,'薬師寺'); el+=_spot(P,2.5,4.5,'唐招提寺')
    el+=_spot(P,1,0.5,'西大寺','middle',-7)
    el+=_spot(P,10.5,2.5,'興福寺','end'); el+=_spot(P,10.5,3.7,'元興寺','end')
    el+=[f"<rect x='{_f(P.x(11)+8)}' y='{_f(P.y(0.6)-4)}' width='8' height='8' style='fill:{RED};stroke:{BG};stroke-width:1;'/>",_t(P.x(11)+12,P.y(0.6)-9,'東大寺',10.5)]
    el.append(_t(P.x(-0.3),P.y(0)-8,'北',10,DIM,'start',False))
    return _wrap('平城京のつくり','1マス＝1坊（約530m）。宮は都の北のまん中、朱雀大路の東が左京・西が右京。位置はおおよそ',W,H,el)

def heian():
    # 平安京：右京4坊＋左京4坊、一条〜九条。大内裏は一条〜二条の中央（約1.2km）
    u=26; P=_P(8,9,u,66,30); W=P.x(8)+66; H=P.y(9)+36
    el=[]
    # 川
    el.append(f"<path d='M{_f(P.x(8)+26)} {_f(P.y(-0.8))} q-8 {_f(2.5*u)} 4 {_f(5*u)} t-6 {_f(5*u)}' style='fill:none;stroke:#7FB3D5;stroke-width:3;'/>")
    el.append(_t(P.x(8)+44,P.y(4.5),'鴨川',10,'#7FB3D5','middle',False))
    el.append(f"<path d='M{_f(P.x(0)-30)} {_f(P.y(-0.8))} q10 {_f(2.5*u)} -2 {_f(5*u)} t6 {_f(5*u)}' style='fill:none;stroke:#7FB3D5;stroke-width:3;'/>")
    el.append(_t(P.x(0)-46,P.y(4.5),'桂川',10,'#7FB3D5','middle',False))
    el+=_grid(P,0,8,0,9)
    el.append(f"<rect x='{_f(P.x(0))}' y='{_f(P.y(2))}' width='{_f(P.x(3)-P.x(0))}' height='{_f(P.y(9)-P.y(2))}' style='fill:rgba(15,22,38,.45);'/>")
    el+=_box(P,2.9,0,5.1,2,'rgba(224,122,95,.45)','大内裏',11.5)   # 東西約1.2km
    el.append(f"<line x1='{_f(P.x(4))}' y1='{_f(P.y(2))}' x2='{_f(P.x(4))}' y2='{_f(P.y(9))}' style='stroke:{GOLD};stroke-width:3.2;'/>")
    el.append(_t(P.x(4)+6,P.y(5.2),'朱雀大路',10,GOLD,'start'))
    el.append(_t(P.x(4),P.y(9)+14,'羅城門',10.5,TXT))
    el+=_spot(P,4.5,8.5,'東寺','start'); el+=_spot(P,3.5,8.5,'西寺','end')
    el+=_spot(P,5.5,6.5,'東市'); el+=_spot(P,2.5,6.5,'西市')
    el+=_spot(P,4.5,2.6,'神泉苑','start')
    el.append(_t(P.x(1.5),P.y(3.6),'右京',11,DIM,'middle',False)); el.append(_t(P.x(1.5),P.y(3.6)+13,'（湿地が多く',9,DIM,'middle',False)); el.append(_t(P.x(1.5),P.y(3.6)+25,'さびれた）',9,DIM,'middle',False))
    el.append(_t(P.x(6.5),P.y(3.6),'左京',11,DIM,'middle',False))
    el.append(_t(P.x(-0.1),P.y(0)-8,'北',10,DIM,'start',False))
    return _wrap('平安京のつくり','1マス＝1坊。東西約4.5km・南北約5.2km。寺は東寺と西寺だけ。位置はおおよそ',W,H,el)

def fujiwara():
    # 藤原京（大藤原京説）：十条十坊、宮は中央。大和三山が京の中に入る
    u=22; P=_P(10,10,u,30,24); W=P.x(10)+30; H=P.y(10)+30
    el=_grid(P,0,10,0,10)
    el+=_box(P,4,4,6,6,'rgba(224,122,95,.45)','藤原宮',11)
    el.append(f"<line x1='{_f(P.x(5))}' y1='{_f(P.y(6))}' x2='{_f(P.x(5))}' y2='{_f(P.y(10))}' style='stroke:{GOLD};stroke-width:3;'/>")
    el.append(_t(P.x(5)+6,P.y(8.2),'朱雀大路',10,GOLD,'start'))
    def mt(c,r,name,anchor='middle'):
        x,y=P.x(c),P.y(r)
        return [f"<path d='M{_f(x-9)} {_f(y+6)} L{_f(x)} {_f(y-7)} L{_f(x+9)} {_f(y+6)} Z' style='fill:#3E5A44;stroke:#9CC5A1;stroke-width:1;'/>",
                _t(x,y+18 if anchor=='middle' else y+4,name,10.5,'#CFE8D2','middle')]
    el+=mt(3.3,2.5,'耳成山'); el+=mt(7.8,6.7,'香具山'); el+=mt(1.4,7.1,'畝傍山')   # 宮の北やや西・東南・西南
    el.append(_t(P.x(-0.4),P.y(0)-8,'北',10,DIM,'start',False))
    return _wrap('藤原京のつくり','宮が京のまん中にある（平城京・平安京は北のまん中）。大和三山が京の中に入る。大きさは約5.3km四方とする説による',W,H,el)
