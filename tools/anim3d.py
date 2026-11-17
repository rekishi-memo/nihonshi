# 立体の動く図（アニメーション）の中身をつくる（2026-11-17 ユーザー「アニメーション、モーションでわかるような説明」「3dで、立体的に」）。
#   中身＝地面（陸の形）＋時間ごとのカメラ・人形・船・文字。描くのはアプリの中の an3（tools/anim3d_rt.js）。
#   距離の単位は km。x＝東、z＝北、y＝上。原点は場面ごとに決める。
import json,math,os,html
from jmap import _geo,_clip,_dp

def _proj(o):
    lon0,lat0=o; kx=111.32*math.cos(math.radians(lat0)); ky=110.95
    return lambda lon,lat:((lon-lon0)*kx,(lat-lat0)*ky)

def ground(bbox,origin,focus=(),tol=2.5,ftol=0.12,minarea=6,mid=(),mtol=0.5):
    """陸の形を km の平らな多角形（ぬり）と、海岸線（県境をのぞいた線）にする。focus（経度緯度の四角）にかかる島はこまかく残す"""
    lon0,lon1,lat0,lat1=bbox; P=_proj(origin); G=_geo(); fills=[]; coasts=[]
    def hit(R,b):
        xs=[p[0] for p in R]; ys=[p[1] for p in R]
        return not(max(xs)<b[0] or min(xs)>b[1] or max(ys)<b[2] or min(ys)>b[3])
    inb=lambda p:lon0<=p[0]<=lon1 and lat0<=p[1]<=lat1
    from collections import Counter
    cnt=Counter()
    for R in G['jp']:
        for i in range(len(R)):
            a,b=tuple(R[i-1]),tuple(R[i]); cnt[(min(a,b),max(a,b))]+=1
    FB=[(P(f[0],f[2]),P(f[1],f[3])) for f in focus]
    MB=[(P(f[0],f[2]),P(f[1],f[3])) for f in mid]
    def infoc(q): return 2 if any(a[0]<=q[0]<=b[0] and a[1]<=q[1]<=b[1] for a,b in FB) else (1 if any(a[0]<=q[0]<=b[0] and a[1]<=q[1]<=b[1] for a,b in MB) else 0)
    def dpv(K,t):
        # 注目の四角の中はこまかく、外はあらく（区間ごとに Douglas–Peucker）
        if t!=ftol: return _dp(K,t)
        out=[]; i=0; n=len(K)
        while i<n-1:
            f=infoc(K[i]); j=i+1
            while j<n-1 and infoc(K[j])==f: j+=1
            seg=_dp(K[i:j+1],(tol,mtol,ftol)[f])
            out+=seg if not out else seg[1:]; i=j
        return out
    def flat(K,fine):
        o=[]
        for x,z in K: o+=[round(x,2 if fine else 1),round(z,2 if fine else 1)]
        return o
    for key in ('land','jp'):
        for R in G[key]:
            if not hit(R,bbox): continue
            fine=any(hit(R,f) for f in tuple(focus)+tuple(mid)); t=ftol if fine else tol
            C=_clip([tuple(p) for p in R],lon0,lat0,lon1,lat1)
            if len(C)<3: continue
            K=[P(x,y) for x,y in C]
            K=dpv(K+[K[0]],t)[:-1]
            if len(K)<3: continue
            a=abs(sum(K[i-1][0]*K[i][1]-K[i][0]*K[i-1][1] for i in range(len(K))))/2
            if a<(minarea*0.02 if fine else minarea): continue
            fills.append(flat(K,fine))
            # 海岸線：ほかの県と共有していない辺だけをつなぐ
            n=len(R); coast=[cnt[(min(tuple(R[i-1]),tuple(R[i])),max(tuple(R[i-1]),tuple(R[i])))]==1 if key=='jp' else True for i in range(n)]
            if all(coast):
                start=0
            elif not any(coast): continue
            else: start=next(i for i in range(n) if not coast[i])
            run=[]
            for j in range(n+1):
                i=(start+j)%n
                if coast[i] and inb(R[i-1]) and inb(R[i]):
                    if not run: run=[tuple(R[i-1])]
                    run.append(tuple(R[i]))
                else:
                    if len(run)>1:
                        L=[P(x,y) for x,y in run]; L=dpv(L,t)
                        if len(L)>1: coasts.append(flat(L,fine))
                    run=[]
            if len(run)>1:
                L=[P(x,y) for x,y in run]; L=dpv(L,t)
                if len(L)>1: coasts.append(flat(L,fine))
    return fills,coasts

def block(sid,scene,caption):
    js=json.dumps(scene,ensure_ascii=False,separators=(',',':'))
    return (f"<div class='viz an3w'><div class='viz-cap'>{caption}</div>"
            f"<div class='an3' data-an3=\"{html.escape(js,quote=True)}\"></div></div>")

# ───── モンゴル襲来（中世③ 01）─────
def mouko():
    O=(130.40,33.60); P=_proj(O)
    def p(lon,lat): x,z=P(lon,lat); return [round(x,2),round(z,2)]
    HAKATA=(130.15,130.60,33.45,33.75); KAMA=(139.45,139.65,35.25,35.40)
    g,gc=ground((115.0,142.5,27.5,42.5),O,focus=(HAKATA,KAMA),mid=((128.8,131.2,32.9,35.3),))
    kama=p(139.553,35.326); hk=p(130.40,33.61)
    def cam(t,lonlat,dist,pitch,yaw):
        x,z=p(*lonlat); return [t,x,z,dist,pitch,yaw]
    def route(*pts): return [p(*q) for q in pts]
    # 石築地（博多湾の海岸ぞい約20km。おおよそ）
    wall=route((130.262,33.603),(130.290,33.590),(130.315,33.588),(130.345,33.592),(130.372,33.596),(130.398,33.607),(130.418,33.622),(130.432,33.643),(130.440,33.662))
    bunei=route((128.60,35.13),(129.05,34.80),(129.25,34.20),(129.62,33.86),(130.05,33.72),(130.30,33.66),(130.37,33.63))
    tou=route((128.60,35.13),(129.05,34.80),(129.25,34.20),(129.62,33.86),(130.05,33.72),(130.24,33.70))
    tou2=route((130.24,33.70),(130.00,33.62),(129.80,33.48),(129.74,33.44))
    konan=route((121.75,29.90),(124.0,30.6),(126.5,31.6),(128.6,32.6),(129.45,33.25),(129.70,33.40))
    hole=p(121.0,40.6)
    S=dict(
     dur=62.0,
     ground=g,coast=gc,
     labels=[dict(s='鎌倉',at=kama,d=[0.5,900]),dict(s='博多',at=p(130.42,33.58),d=[12,1400]),dict(s='対馬',at=p(129.33,34.45),d=[60,2600]),
             dict(s='壱岐',at=p(129.72,33.80),d=[60,1400]),dict(s='高麗',at=p(127.6,36.6),d=[300,6000]),dict(s='元',at=p(116.8,36.0),d=[900,8000]),
             dict(s='大都',at=p(116.4,39.9),d=[900,8000]),dict(s='日本',at=p(136.5,36.0),d=[1200,8000]),dict(s='南宋（1279年に滅ぼされる）',at=p(119.5,30.0),d=[700,6000],on=[38,46]),
             dict(s='鷹島',at=p(129.74,33.43),d=[20,700],on=[44,62]),dict(s='博多湾',at=p(130.33,33.64),d=[8,200])],
     cam=[cam(0,(139.553,35.3276),0.15,24,16),cam(2.5,(139.553,35.3276),0.13,26,6),
          cam(5.0,(139.553,35.3276),0.22,32,0),cam(8.5,(134.0,35.6),1900,52,-12),cam(12.0,(124.5,38.4),2900,46,-20),cam(14.0,(123.0,39.4),2500,40,-18),
          cam(15.0,(124.0,39.0),2700,44,-14),cam(16.6,(139.553,35.3276),0.22,30,0),cam(18.2,(139.553,35.3276),0.15,26,10),
          cam(20.0,(129.4,34.3),420,46,-25),cam(25.0,(129.9,33.95),300,44,-20),cam(26.5,(130.39,33.61),24,34,-8),cam(32.0,(130.39,33.61),18,30,-14),
          cam(34.5,(130.37,33.62),30,52,0),cam(39.4,(130.37,33.62),26,50,10),cam(40.3,(130.2,33.6),260,56,4),
          cam(41.0,(126.0,32.6),2000,55,-10),cam(46.0,(128.2,33.4),900,50,-15),cam(49.0,(129.9,33.55),90,40,-20),
          cam(52.0,(129.80,33.48),70,38,-30),cam(56.5,(129.78,33.46),55,34,-40),cam(58.5,(127.5,36.0),3200,55,-10),cam(62.0,(127.5,36.0),3400,56,-8)],
     objs=[
      # 鎌倉：館と武士
      dict(k='bldg',at=p(139.5530,35.3290),w=0.040,d=0.024,h=0.013,roof=0.013,c='#6b4a35',r='#2f3a52',on=[0,19]),
      dict(k='bldg',at=p(139.5500,35.3282),w=0.018,d=0.015,h=0.009,roof=0.009,c='#6b4a35',r='#2f3a52',on=[0,19]),
      dict(k='bldg',at=p(139.5560,35.3282),w=0.018,d=0.015,h=0.009,roof=0.009,c='#6b4a35',r='#2f3a52',on=[0,19]),
      dict(k='bldg',at=p(139.5486,35.3300),w=0.016,d=0.014,h=0.008,roof=0.008,c='#5e4230',r='#2f3a52',on=[0,19]),
      dict(k='bldg',at=p(139.5575,35.3302),w=0.016,d=0.014,h=0.008,roof=0.008,c='#5e4230',r='#2f3a52',on=[0,19]),
      dict(k='hill',at=p(139.5470,35.3335),r=0.10,h=0.06,c='#4f6b45',on=[0,19]),dict(k='hill',at=p(139.5560,35.3350),r=0.12,h=0.07,c='#56724b',on=[0,19]),
      dict(k='hill',at=p(139.5640,35.3310),r=0.09,h=0.05,c='#4a6541',on=[0,19]),dict(k='hill',at=p(139.5410,35.3280),r=0.08,h=0.045,c='#56724b',on=[0,19]),
      dict(k='crowd',n=16,r=0.026,h=0.008,c='#3d5a8a',flag='#e8e0c8',seed=3,form='rows',at=[[0,*p(139.553,35.3268)]],on=[0,19],cheer=[17.0,18.6]),
      dict(k='crowd',n=1,r=0.0,h=0.010,c='#d4a64a',seed=1,at=[[0,*p(139.553,35.3282)]],on=[0,19],tag='北条時宗（18歳）',tagon=[1.6,6.0]),
      # 大陸の穴と元軍
      dict(k='pit',at=hole,r=[[9.6,0],[10.8,330],[14.4,330],[15.0,0]]),
      dict(k='crowd',n=150,r=280,h=95,c='#b8463a',seed=7,form='blob',at=[[0,*hole]],on=[10.0,14.9],rise=[10.0,11.8]),
      dict(k='crowd',n=26,r=120,h=95,c='#8a5a3a',seed=11,form='blob',at=[[0,*p(126.9,37.4)]],on=[11.3,14.9],rise=[11.3,12.6],tag='高麗も従わせた',tagon=[11.8,14.8]),
      # 文永の役
      dict(k='path',pts=bunei,c='#e07a5f',w=2.5,draw=[20.2,24.6],on=[20,34]),
      dict(k='fleet',n=34,r=14,sz=7,max=22,c='#5a3a2a',sail='#c9b28a',seed=5,path=bunei,move=[20.2,25.6],on=[20,26.2],fade=[25.6,26.2]),
      dict(k='fleet',n=14,r=2.0,sz=0.7,max=26,c='#5a3a2a',sail='#c9b28a',seed=6,path=route((130.35,33.67),(130.37,33.645)),move=[25.6,26.6],on=[25.6,33.6],leave=[31.4,33.6],leaveTo=p(130.28,33.74)),
      dict(k='crowd',n=46,r=1.6,h=0.75,c='#b8463a',seed=21,form='blob',at=[[25.6,*p(130.372,33.636)],[27.2,*p(130.372,33.602)],[29.5,*p(130.380,33.590)]],on=[25.6,31.6],fade=[31.0,31.6],jit=[28.2,31.0]),
      dict(k='crowd',n=34,r=1.9,h=0.75,c='#3d5a8a',flag='#e8e0c8',seed=22,form='blob',at=[[25.6,*p(130.40,33.555)],[28.0,*p(130.388,33.578)]],on=[25.6,34],jit=[28.2,31.0],spread=[28.2,1.6]),
      dict(k='boom',at=p(130.385,33.583),r=0.8,ts=[28.4,28.9,29.3,29.8,30.2,30.6],sp=1.6,seed=4),
      # 石築地
      dict(k='wall',pts=wall,h=0.35,th=0.18,c='#9a9384',build=[34.6,38.6],on=[34.6,62]),
      dict(k='crowd',n=26,r=0.0,h=0.6,c='#3d5a8a',flag='#e8e0c8',seed=31,line=wall,lineOff=-0.5,on=[37.5,62],rise=[37.5,38.8]),
      # 弘安の役
      dict(k='path',pts=tou,c='#e07a5f',w=2.5,draw=[41.6,45.0],on=[41,53]),
      dict(k='path',pts=konan,c='#e07a5f',w=2.5,draw=[41.6,46.0],on=[41,53]),
      dict(k='fleet',n=40,r=16,sz=7,c='#5a3a2a',sail='#c9b28a',seed=8,path=tou+tou2[1:],move=[41.6,50.5],hold=[46.2,48.2],on=[41,57.6],sink=[53.6,57.6]),
      dict(k='fleet',n=70,r=26,sz=7,c='#4a3a2a',sail='#b7a07a',seed=9,path=konan,move=[41.6,50.8],on=[41,57.6],sink=[53.6,57.6]),
      dict(k='tag',at=p(128.2,34.9),s='東路軍（朝鮮半島から）',on=[43.4,47.6]),
      dict(k='tag',at=p(125.0,30.9),s='江南軍（南宋の兵）',on=[43.4,47.6]),
     ],
     fx=[dict(k='speed',on=[14.8,16.6]),dict(k='flash',t=31.0),dict(k='storm',on=[52.6,57.8]),dict(k='flash',t=57.8)],
     text=[
      dict(k='year',t=0.6,d=2.2,s='1268',sub='モンゴルの国書が届く'),
      dict(k='cap',t=0.4,d=5.0,s='鎌倉。執権になったばかりの北条時宗は18歳'),
      dict(k='cap',t=5.4,d=4.4,s='国書の最後に「兵を用いることを、だれが好むだろうか」'),
      dict(k='cap',t=9.8,d=5.2,s='相手は、ユーラシアの半分を支配する元（都は大都）'),
      dict(k='cap',t=15.0,d=4.6,s='幕府は要求をはねつけた'),
      dict(k='year',t=19.4,d=2.4,s='1274',sub='文永の役'),
      dict(k='cap',t=19.8,d=5.6,s='元・高麗の約3万の軍が、対馬・壱岐をおそって博多湾へ'),
      dict(k='cap',t=25.8,d=2.8,s='上陸。九州の御家人が迎えうつ'),
      dict(k='cap',t=28.4,d=2.8,s='集団で動く元軍、火薬の玉「てつはう」。武士は苦戦'),
      dict(k='cap',t=31.2,d=3.2,s='元軍も損害が大きく、まもなく引きあげた'),
      dict(k='cap',t=34.6,d=4.9,s='時宗は次に備える。博多湾ぞいに石の防塁（石築地）約20km'),
      dict(k='cap',t=37.6,d=1.9,s='九州の守りは、御家人が交代で（異国警固番役）'),
      dict(k='year',t=41.0,d=2.4,s='1281',sub='弘安の役'),
      dict(k='cap',t=41.2,d=5.0,s='ふたたび。今度は約14万、二手に分かれて'),
      dict(k='cap',t=46.4,d=3.6,s='石築地があって、博多湾に上陸できない'),
      dict(k='cap',t=50.2,d=3.2,s='海の上で待つうちに……'),
      dict(k='cap',t=53.4,d=4.4,s='暴風雨。大きな損害を受けて引きあげた'),
      dict(k='card',t=58.4,d=3.6,s='モンゴル襲来（蒙古襲来）'),
      dict(k='cap',t=58.4,d=3.6,s='勝因は嵐だけじゃない。九州の武士の戦いと、高麗・南宋・ベトナムの抵抗'),
     ],
     chips=[[0,'1268 国書'],[19.4,'1274 文永の役'],[34.4,'石築地'],[41.0,'1281 弘安の役']],
    )
    return S

ANIMS=[dict(id='an3-mouko',pack='chusei3',no='01',after='二度の襲来を、あわせてモンゴル襲来',fn=mouko,
            cap='動く図 ── モンゴル襲来（タップで再生。位置・人数はおおよそ）')]

if __name__=='__main__':
    S=mouko(); n=sum(len(r)//2 for r in S['ground'])+sum(len(r)//2 for r in S['coast']); print('rings',len(S['ground']),'pts',n,'json',len(json.dumps(S,ensure_ascii=False,separators=(',',':'))))
