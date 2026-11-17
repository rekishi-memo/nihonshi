# 授業に入れる地図（ベクター）をつくる。2026-11-17 作り直し（ユーザーの指摘「地図汚いから丁寧に作って欲しい」
#   「丸数字を書いて外に地名を書くのはやめて、書けるなら地図の上に書いちゃって」）。
#
# 海岸線：日本は地球地図日本（国土地理院、1:100万。出典：地球地図日本）の tools/geo_japan.json、
#   朝鮮半島・中国などは Natural Earth 1:10m（パブリックドメイン）から東アジアだけ切り出した tools/geo_eastasia.json。
#   地図ごとに範囲で切りぬいて、画面の0.35pxより細かい折れ目を間引いた線を、その地図の SVG にそのまま入れる。
#   （前は日本の白地図の画像をなぞった線を全地図で使い回していたので、粗かった）
# 地名：番号の札と外の一覧はやめ、点のとなりに直接書く。ほかの地名・点・地図のふちと重ならない置き場所を、
#   点のまわり8方向から選ぶ（ひとつずつ目で確かめて、だめなら maps_def.py の pos で決める）。
#
#   from jmap import jmap
#   html = jmap('源平の争乱', (129.5,141,31,38),
#               points=[(1,'一の谷',135.10,34.65), ...],   # (番号, 名前, 経度, 緯度[, ずらしx, ずらしy[, 置き場所]])
#               routes=[([(lon,lat),...],'sea')],           # 'road' 実線 / 'road2' 青の実線 / 'sea' 点線 / 'arrow' 矢印つき点線
#               areas=[('加賀',136.6,36.4)],                # 地域名（うすい文字）
#               note='…')
#   名前は「── 」より前だけを地図に書く（後ろの説明は本文で読む）。（　）の中も書かない。ふりがなは書かない。
#   置き場所は 'r' 'l' 't' 'b' 'tr' 'br' 'tl' 'bl'。番号とずらしは、前の形のなごり（使わない）。
import hashlib, json, math, os, re
HERE=os.path.dirname(os.path.abspath(__file__))
_G=None
def _geo():
    global _G
    if _G is None:
        ea=json.load(open(os.path.join(HERE,'geo_eastasia.json'),encoding='utf-8'))
        jp=json.load(open(os.path.join(HERE,'geo_japan.json'),encoding='utf-8'))
        _G={'land':ea['land'],'jp':jp['land'],'lake':ea['lake']}
    return _G

W=330.0          # 画面での地図の幅（px）。文字・点・線の太さはこれに合わせる
FS=11.5          # 地名の文字の大きさ
SEA='#0F1626'; LAND='#263250'; COAST='#A88E4E'
FONT="font-family:'Hiragino Sans','Noto Sans JP',system-ui,sans-serif;"

def _f(v): return f"{v:.1f}".rstrip('0').rstrip('.')

def _merc(lat): return math.log(math.tan(math.pi/4+math.radians(lat)/2))

class _Proj:
    def __init__(s,bbox):
        s.lon0,s.lon1,s.lat0,s.lat1=bbox
        s.k=W/math.radians(s.lon1-s.lon0)
        s.y1=_merc(s.lat1)
        s.H=(s.y1-_merc(s.lat0))*s.k
    def __call__(s,lon,lat): return (math.radians(lon-s.lon0)*s.k, (s.y1-_merc(lat))*s.k)

def _clip(poly,x0,y0,x1,y1):
    # Sutherland–Hodgman で四角に切りぬく
    def cut(P,inside,inter):
        out=[]
        for i in range(len(P)):
            a,b=P[i-1],P[i]
            if inside(b):
                if not inside(a): out.append(inter(a,b))
                out.append(b)
            elif inside(a): out.append(inter(a,b))
        return out
    def ix(a,b,x): t=(x-a[0])/(b[0]-a[0]); return (x,a[1]+t*(b[1]-a[1]))
    def iy(a,b,y): t=(y-a[1])/(b[1]-a[1]); return (a[0]+t*(b[0]-a[0]),y)
    P=poly
    for inside,inter in ((lambda p:p[0]>=x0,lambda a,b:ix(a,b,x0)),(lambda p:p[0]<=x1,lambda a,b:ix(a,b,x1)),
                         (lambda p:p[1]>=y0,lambda a,b:iy(a,b,y0)),(lambda p:p[1]<=y1,lambda a,b:iy(a,b,y1))):
        if not P: break
        P=cut(P,inside,inter)
    return P

def _dp(P,tol):
    # Douglas–Peucker（閉じた線は2つに分けて）
    if len(P)<4: return P
    keep=[False]*len(P); keep[0]=keep[-1]=True; st=[(0,len(P)-1)]
    while st:
        a,b=st.pop(); ax,ay=P[a]; bx,by=P[b]; dx,dy=bx-ax,by-ay; L=math.hypot(dx,dy)
        best,bi=-1,-1
        for i in range(a+1,b):
            px,py=P[i]
            d=abs(dy*(px-ax)-dx*(py-ay))/L if L else math.hypot(px-ax,py-ay)
            if d>best: best,bi=d,i
        if best>tol: keep[bi]=True; st+=[(a,bi),(bi,b)]
    return [p for p,k in zip(P,keep) if k]

def _path(rings):
    # 相対座標（前の点からの差）で書いて、データを小さくする。誤差がたまらないよう、丸めたあとの位置から差をとる
    out=[]
    for R in rings:
        px,py=round(R[0][0],1),round(R[0][1],1); seg=[f"M{_f(px)} {_f(py)}l"]
        nums=[]
        for x,y in R[1:]:
            x,y=round(x,1),round(y,1); dx,dy=round(x-px,1),round(y-py,1)
            if dx==0 and dy==0: continue
            nums.append(f"{_f(dx)} {_f(dy)}"); px,py=x,y
        seg.append(' '.join(nums).replace(' -','-')); out.append(''.join(seg)+'z')
    return ''.join(out)

def _chaikin(R,n=2):
    for _ in range(n):
        Q=[]
        for i in range(len(R)):
            a,b=R[i],R[(i+1)%len(R)]
            Q+=[(0.75*a[0]+0.25*b[0],0.75*a[1]+0.25*b[1]),(0.25*a[0]+0.75*b[0],0.25*a[1]+0.75*b[1])]
        R=Q
    return R

def _shapes(pr,key,tol=0.35,minarea=0.6):
    m=6; res=[]
    for ring in _geo()[key]:
        if key=='lake': ring=_chaikin([tuple(p) for p in ring])   # 湖は点が少ない（Natural Earth）ので、角をまるめる
        xs=[p[0] for p in ring]; ys=[p[1] for p in ring]
        if max(xs)<pr.lon0-1 or min(xs)>pr.lon1+1 or max(ys)<pr.lat0-1 or min(ys)>pr.lat1+1: continue
        P=[pr(x,y) for x,y in ring]
        P=_clip(P,-m,-m,W+m,pr.H+m)
        if len(P)<3: continue
        P=_dp(P+[P[0]],tol)[:-1]
        if len(P)<3: continue
        a=abs(sum(P[i-1][0]*P[i][1]-P[i][0]*P[i-1][1] for i in range(len(P))))/2
        if a<minarea: continue
        res.append(P)
    return res

def _plain(h):
    h=re.sub(r'<rt>[\s\S]*?</rt>','',h); h=re.sub(r'<[^>]+>','',h)
    h=h.split('──')[0]
    h=re.sub(r'（[^）]*）','',h)
    return h.strip()

def _tw(t,fs):
    return sum(fs*(0.62 if ord(c)<0x2E80 else 1.0) for c in t)

# 都の範囲（経度・緯度の四角：西・南・東・北）。地図の上で5px以上になるときは点ではなく四角で描く。
#   大きさ：藤原京 約5.3km四方（大藤原京説、宮は中央）／平城京 東西約4.3km・南北約4.8km＋外京（東へ約1.6km）／
#   長岡京 東西約4.3km・南北約5.3km／平安京 東西約4.5km・南北約5.2km。位置は宮・朱雀大路の跡から決めた（おおよそ）
MIYAKO={
 '藤原京':[(135.7787,34.4786,135.8363,34.5264)],
 '平城京':[(135.7721,34.6475,135.8191,34.6940),(135.8191,34.6750,135.8366,34.6940)],
 '長岡京':[(135.6809,34.8980,135.7279,34.9460)],
 '平安京':[(135.7184,34.9825,135.7677,35.0300)],
}
POS={'r':(1,0),'l':(-1,0),'t':(0,-1),'b':(0,1),'tr':(1,-1),'br':(1,1),'tl':(-1,-1),'bl':(-1,1)}
FS2=9.5   # 2行目（説明）の文字の大きさ
def _lines(t):
    a,_,b=t.partition('|'); return a.strip(),b.strip()
def _box(x,y,t,fs,pos,gap=5.5,hw=0,hh=0):
    # hw・hh：都の四角のときの半分の幅・高さ（点のときは0）
    if pos.endswith('2'): pos=pos[:-1]; gap=22   # 「2」は、少し離して置き、点と線で結ぶ
    a,b=_lines(t)
    w=max(_tw(a,fs),_tw(b,FS2) if b else 0); h=fs*1.15+(FS2*1.2 if b else 0); dx,dy=POS[pos]
    if dx>0: x0=x+hw+gap
    elif dx<0: x0=x-hw-gap-w
    else: x0=x-w/2
    if dy<0: y0=y-hh-gap-h+(2 if dx else 0)
    elif dy>0: y0=y+hh+gap-(2 if dx else 0)
    else: y0=y-h/2
    return (x0,y0,x0+w,y0+h)

def _ov(a,b):
    return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))

def jmap(title,bbox,points=(),routes=(),areas=(),note='',legend_cols=None,base=None,labels=None,pos=None):
    pr=_Proj(bbox); H=pr.H
    el=[f"<rect x='0' y='0' width='{_f(W)}' height='{_f(H)}' style='fill:{SEA};'/>"]
    tol=0.45 if bbox[1]-bbox[0]>3 else 0.8   # 狭い範囲は、埋め立ての細かい凸凹を目立たせない
    land=_shapes(pr,'land',tol); jp=_shapes(pr,'jp',tol); lake=_shapes(pr,'lake',minarea=2)
    if land: el.append(f"<path d='{_path(land)}' style='fill:{LAND};stroke:{COAST};stroke-width:.8;stroke-linejoin:round;'/>")
    if jp:  # 日本は都道府県ごとの形なので、太い線で描いてから中をぬりなおし、県境を消して海岸線だけ残す
        d=_path(jp); jid='jm'+hashlib.md5(repr((title,bbox)).encode()).hexdigest()[:8]   # 同じ形を2回使うので、1回だけ定義する
        el.append(f"<defs><path id='{jid}' d='{d}'/></defs>")
        el.append(f"<use href='#{jid}' style='fill:{LAND};stroke:{COAST};stroke-width:2.2;stroke-linejoin:round;'/>")
        el.append(f"<use href='#{jid}' style='fill:{LAND};stroke:{LAND};stroke-width:1;stroke-linejoin:round;'/>")
    if lake: el.append(f"<path d='{_path(lake)}' style='fill:{SEA};stroke:{COAST};stroke-width:.7;stroke-linejoin:round;'/>")
    for pts,kind in routes:
        P=[pr(*p) for p in pts]; d='M'+' L'.join(f"{_f(x)} {_f(y)}" for x,y in P)
        if kind=='road': st="stroke:#E07A5F;stroke-width:2.4;"
        elif kind=='road2': st="stroke:#7FB3D5;stroke-width:2.4;"
        elif kind=='sea': st="stroke:#7FB3D5;stroke-width:2;stroke-dasharray:6 4;"
        else: st="stroke:#E07A5F;stroke-width:2.2;stroke-dasharray:6 4;"
        mk=" marker-end='url(#jm-ah)'" if kind=='arrow' else ''
        el.append(f"<path d='{d}' style='fill:none;stroke-linejoin:round;stroke-linecap:round;{st}'{mk}/>")
    # 置いた文字・点の四角（重なりを避ける）
    boxes=[]
    dots=[]; half=[]; rect_el=[]
    for i,p in enumerate(points):
        t=(labels[i] if labels and i<len(labels) and labels[i] else _plain(p[1]))
        R=MIYAKO.get(_lines(t)[0])
        if R:
            P=[(pr(w,n),pr(e,sth)) for w,sth,e,n in R]
            if P[0][1][0]-P[0][0][0]>=5:   # 都の本体が地図の上で5px以上あるときだけ、四角で描く（外京は本体にそえる）
                (x0,y0),(x1,y1)=P[0]
                for k,((a0,b0),(a1,b1)) in enumerate(P):
                    rect_el.append(f"<rect x='{_f(a0)}' y='{_f(b0)}' width='{_f(a1-a0)}' height='{_f(b1-b0)}' style='fill:rgba(224,122,95,{.55 if k==0 else .35});stroke:#E07A5F;stroke-width:1;'/>")
                X0=min(a[0] for a,b in P); X1=max(b[0] for a,b in P); Y0=min(a[1] for a,b in P); Y1=max(b[1] for a,b in P)
                dots.append(((X0+X1)/2,(Y0+Y1)/2)); half.append(((X1-X0)/2,(Y1-Y0)/2)); boxes.append((X0,Y0,X1,Y1)); continue
        x,y=pr(p[2],p[3]); dots.append((x,y)); half.append(None); boxes.append((x-3.5,y-3.5,x+3.5,y+3.5))
    txt=[]
    for name,lon,lat in areas:
        x,y=pr(lon,lat); w=_tw(name,11)+2
        x=min(max(x,w/2+3),W-w/2-3); y=min(max(y,13),H-4)   # 地図のふちからはみ出さない
        b=(x-w/2,y-9,x+w/2,y+3); boxes.append(b)
        txt.append(f"<text x='{_f(x)}' y='{_f(y)}' text-anchor='middle' style='fill:#8E9AB8;font-size:11px;letter-spacing:.12em;{FONT}'>{name}</text>")
    # 点の多いところから置く
    order=sorted(range(len(points)),key=lambda i:-sum(1 for j in range(len(points)) if j!=i and math.hypot(dots[i][0]-dots[j][0],dots[i][1]-dots[j][1])<60))
    lab=[None]*len(points); lines_el=[]
    for i in order:
        p=points[i]; x,y=dots[i]; t=(labels[i] if labels and i<len(labels) and labels[i] else _plain(p[1]))
        fixed=(pos or {}).get(_lines(t)[0]) or (p[6] if len(p)>6 else None)
        cands=[fixed] if fixed else ['r','l','t','b','tr','br','tl','bl']
        best=None
        for k,c in enumerate(cands):
            hw,hh=half[i] or (0,0)
            b=_box(x,y,t,FS,c,hw=hw,hh=hh)
            s=sum(_ov(b,o) for o in boxes)*10
            out=max(0,-b[0])+max(0,b[2]-W)+max(0,-b[1])+max(0,b[3]-H)
            s+=out*200+k*0.5
            if best is None or s<best[0]: best=(s,c,b)
        _,c,b=best
        # 地図のふちからはみ出したら、内側へ寄せる
        sx=max(0,2-b[0])-max(0,b[2]-(W-2)); sy=max(0,2-b[1])-max(0,b[3]-(H-2))
        b=(b[0]+sx,b[1]+sy,b[2]+sx,b[3]+sy)
        boxes.append(b); lab[i]=(t,b,c)
        if c.endswith('2') or sx or sy:   # 離して置いたときは、点から字へ細い線を引く
            cx=min(max(x,b[0]),b[2]); cy=min(max(y,b[1]),b[3])
            if math.hypot(cx-x,cy-y)>7: lines_el.append(f"<line x1='{_f(x)}' y1='{_f(y)}' x2='{_f(cx)}' y2='{_f(cy)}' style='stroke:#C9B98F;stroke-width:.8;'/>")
    dot_el=rect_el+[f"<circle cx='{_f(x)}' cy='{_f(y)}' r='3.3' style='fill:#E07A5F;stroke:{SEA};stroke-width:1.2;'/>" for (x,y),h in zip(dots,half) if not h]
    halo=f"paint-order:stroke;stroke:{SEA};stroke-width:3px;stroke-linejoin:round;"
    for t,b,c in [l for l in lab if l]:
        a,d=_lines(t); y1=b[1]+FS*0.93
        c=c.rstrip('2')
        if c in ('t','b'): xa,anc=(b[0]+b[2])/2,'middle'      # 上下に置いたら中央そろえ
        elif c in ('l','tl','bl'): xa,anc=b[2],'end'           # 左に置いたら、点の側（右）にそろえる
        else: xa,anc=b[0],'start'
        txt.append(f"<text x='{_f(xa)}' y='{_f(y1)}' text-anchor='{anc}' style='fill:#F3E9CF;font-size:{FS}px;font-weight:600;{FONT}{halo}'>{a}</text>")
        if d: txt.append(f"<text x='{_f(xa)}' y='{_f(y1+FS2*1.2)}' text-anchor='{anc}' style='fill:#C9B98F;font-size:{FS2}px;{FONT}{halo}'>{d}</text>")
    defs=("<defs><marker id='jm-ah' viewBox='0 0 10 10' refX='7' refY='5' markerWidth='4' markerHeight='4' orient='auto'>"
          "<path d='M0,0 L10,5 L0,10 z' style='fill:#E07A5F;'/></marker></defs>")
    svg=(f"<svg viewBox='0 0 {_f(W)} {_f(H)}' width='100%' role='img' aria-label='{title}'>"+defs+''.join(el)+''.join(lines_el)+''.join(dot_el)+''.join(txt)+"</svg>")
    cap=f"地図 ── {title}"+(f"（{note}）" if note else '')
    return f"<div class='viz jm'><div class='viz-cap'>{cap}</div><div class='mapwrap'>{svg}</div><div class='jm-src'>出典：地球地図日本（国土地理院）・Natural Earth</div></div>"
