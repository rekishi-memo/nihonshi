# 動く図（an3）を「場面の並び」で書くための道具（テーマ史用。2026-11-18）。
#   s=Story('テーマ史：貨幣史'); s.era('古代'); s.ch('01','銭をつくったのに'); s.map(…); s.plate(…); return s.done()
#   map＝地図の上の場面、plate＝地図から浮かぶ展示台の場面。字幕の長さから場面の長さを決める（1字0.1秒ほど）。
#   中身は、そのセットの授業（とくに「まとめ」）に書いてある事実だけ。
import math
from anim3d import P

def dur_for(caps,extra=0.0): return round(sum(max(3.0,len(c)*0.12) for c in caps)+0.8+extra,1)

class Story:
    def __init__(s,title):
        s.title=title; s.t=0.0; s.objs=[]; s.text=[]; s.labels=[]; s.cam=[]; s.chapters=[]; s.eras=[]; s.prev=None; s.np=0
    def era(s,name):
        if s.eras: s.eras[-1][1]=round(s.t,2)
        s.eras.append([round(s.t,2),None,name])
    def ch(s,no,title): s.chapters.append([round(s.t,2),title,no])
    def _caps(s,t0,caps,dur):
        w=[max(3.0,len(c)*0.12) for c in caps]; k=(dur-0.5)/sum(w); tt=t0+0.3
        for c,wi in zip(caps,w):
            d=wi*k; s.text.append(dict(k='cap',t=round(tt,2),d=round(d-0.15,2),s=c)); tt+=d
    def _year(s,t,year,sub):
        if year: s.text.append(dict(k='year',t=round(t,2),d=2.6,s=year,sub=sub or ''))
    def map(s,lon,lat,d,caps,year=None,sub=None,p=54,y=0,dur=None,fn=None,drift=4):
        """地図の場面。fn(t0,t1) で、この場面に出すものを足す"""
        dur=dur or dur_for(caps); t0=s.t; x,z=P(lon,lat)
        s.cam.append([round(t0+(1.6 if s.cam else 0),2),x,z,d,p,y]); s.cam.append([round(t0+dur,2),x,z,round(d*0.93,1),p,y+drift])
        s._year(t0+0.6,year,sub); s._caps(t0,caps,dur)
        if fn: fn(t0,t0+dur)
        s.prev=('map',lon,lat); s.t=round(t0+dur,2)
    def plate(s,lon,lat,caps,build,year=None,sub=None,dur=None,c='#7d8a5a',side='#4a3a2c',yaw=-10,p=32,fn=None):
        """展示台の場面。build(add,win)：add(k=…, rel=[x,z], …) で台の上に置く（大きさは km。台の半径は6）"""
        dur=dur or dur_for(caps,1.4); t0=s.t; s.np+=1; pid=f'q{s.np}'
        if s.prev and s.prev[0]=='plate':
            mx,mz=P((lon+s.prev[1])/2,(lat+s.prev[2])/2); s.cam.append([round(t0+0.8,2),mx,mz,600,50,0])
        x,z=P(lon,lat)
        s.cam.append([round(t0+1.8,2),x,z,13,p,yaw]); s.cam.append([round(t0+dur,2),x,z,11.5,p+2,yaw+18])
        rise=[round(t0+0.4,2),round(t0+1.8,2)]; fall=[round(t0+dur-1.0,2),round(t0+dur+0.3,2)]
        s.objs.append(dict(k='plate',id=pid,at=[x,z],r=6.0,h=3.0,th=0.9,c=c,side=side,rise=rise,fall=fall,on=[rise[0],fall[1]]))
        win=[round(t0+1.8,2),round(t0+dur-0.6,2)]
        def add(**k):
            k['pl']=pid; k.setdefault('on',win); s.objs.append(k); return k
        build(add,win)
        s._year(t0+1.2,year,sub); s._caps(t0+0.6,caps,dur-0.6)
        if fn: fn(t0,t0+dur)
        s.prev=('plate',lon,lat); s.t=round(t0+dur,2)
    # ── 地図の上のもの（時刻は絶対）──
    def ob(_s,**k): _s.objs.append(k); return k
    def arc(s,a,b,t0,t1,dur=1.6,c='#d4bd82',**k):
        return s.ob(k='arc',a=P(*a),b=P(*b),draw=[round(t0,2),round(t0+dur,2)],on=[round(t0,2),round(t1,2)],c=c,w=k.pop('w',1.6),**k)
    def icons(s,i,pts,t0,t1,stagger=0.2,sz=60,mn=14,mx=24,**k):
        return s.ob(k='icons',i=i,list=[P(*q) if len(q)==2 else [*P(q[0],q[1]),*q[2:]] for q in pts],s=sz,min=mn,max=mx,stagger=stagger,on=[round(t0,2),round(t1,2)],**k)
    def tag(s,txt,lonlat,t0,t1,**k): return s.ob(k='tag',s=txt,at=P(*lonlat),on=[round(t0,2),round(t1,2)],**k)
    def pin(s,txt,lonlat,t0,t1,c='#d4bd82',**k): return s.ob(k='pin',s=txt,at=P(*lonlat),on=[round(t0,2),round(t1,2)],c=c,**k)
    def lab(s,txt,lonlat,t0,t1,d=(300,8000),big=False):
        L=dict(s=txt,at=P(*lonlat),d=list(d),on=[round(t0,2),round(t1,2)])
        if big: L['big']=1
        s.labels.append(L)
    def crowd(s,lonlat,t0,t1,n=6,r=25,h=30,c='#7a6a52',**k):
        return s.ob(k='crowd',n=n,r=r,h=h,max=k.pop('max',12),c=c,seed=k.pop('seed',len(s.objs)+1),at=P(*lonlat),on=[round(t0,2),round(t1,2)],**k)
    def move(s,path,t0,t1,n=8,r=25,h=30,c='#7a6a52',**k):
        return s.ob(k='crowd',n=n,r=r,h=h,max=k.pop('max',12),c=c,seed=k.pop('seed',len(s.objs)+1),path=[P(*q) for q in path],move=[round(t0,2),round(t1-0.4,2)],on=[round(t0,2),round(t1,2)],**k)
    def done(s):
        if s.eras: s.eras[-1][1]=round(s.t,2)
        last=s.cam[-1]; cam=s.cam+[[round(s.t+1.0,2),*last[1:]]]
        return dict(title=s.title,dur=round(s.t+1.0,1),cam=cam,objs=s.objs,text=s.text,labels=s.labels,fx=[],
                    ruler=[[a,b,n] for a,b,n in s.eras],chapters=s.chapters)

# ── 展示台の上の決まった組み合わせ（大きさは km）──
def village(add,n=6,r=3.0,people=6):
    for i in range(n):
        a=i/n*math.pi*2+0.4; add(k='hut',rel=[round(math.cos(a)*r,2),round(math.sin(a)*r*0.9,2)],r=0.55,h=0.75,c='#8a6a42')
    if people: add(k='crowd',n=people,r=1.4,h=0.65,c='#8a6a4a',seed=7,rel=[0,0])
def houses(add,pts,c='#cdbd9a',r='#3a3f4a',w=0.9,d=0.7,h=0.42,roof=0.36):
    for q in pts: add(k='bldg',rel=list(q),w=w,d=d,h=h,roof=roof,c=c,r=r)
def town(add,rows=2,cols=4,x0=-3.0,z0=1.2,dx=1.6,dz=1.4,**k):
    houses(add,[(x0+i*dx,z0+j*dz) for j in range(rows) for i in range(cols)],**k)
def people(add,n,rel,r=1.2,c='#7a6a52',h=0.65,**k):
    add(k='crowd',n=n,r=r,h=h,c=c,seed=k.pop('seed',n*7+int(rel[0]*10)),rel=list(rel),**k)
def floaters(add,i,pts,s=1.1,y=0.6,fl=0.5,stagger=0.25,c=None):
    k=dict(k='icons',i=i,list=[list(q) for q in pts],s=s,stagger=stagger,y=y,float=fl)
    if c: k['c']=c
    add(**k)
def temple(add,x=1.6,z=1.0):
    add(k='pagoda',rel=[x,z],w=1.4,h=3.0)
    add(k='bldg',rel=[x-3.0,z-0.2],w=2.2,d=1.4,h=0.6,roof=0.7,c='#a84a3a',r='#3a3f4a')
def castle(add,x=0.6,z=1.0,w=2.2): add(k='castle',rel=[x,z],w=w)
def port(add,ships=3,kind='ship'):
    add(k='box',rel=[0,-3.2],w=10.5,d=3.4,h=0.03,c='#2b4f7a')
    floaters(add,kind,[(-3+i*2.6,-3.2) for i in range(ships)],s=1.4,y=0.05,fl=0.15,stagger=0.3)
    houses(add,[(-2.6,1.4),(-0.8,1.6),(1.0,1.4),(2.8,1.6)],c='#b9a27a',w=1.2,d=0.8)
def factory(add,x=0.0,z=1.0):
    add(k='box',rel=[x,z],w=3.4,d=1.6,h=0.9,c='#8a4a3a',top='#6a3a2a')
    for dx in (-1.0,0.4,1.4): add(k='box',rel=[x+dx,z+0.5],w=0.28,d=0.28,h=2.4,c='#6a3a2a')
    floaters(add,'smoke',[(x-1.0,z+0.5),(x+0.4,z+0.5),(x+1.4,z+0.5)],s=1.0,y=2.4,fl=0.3,stagger=0.15)
def western(add,pts=((-1.6,1.2),(1.4,1.4)),w=1.8):
    for q in pts: add(k='bldg',rel=list(q),w=w,d=1.1,h=0.9,roof=0.45,c='#e9e4d8',r='#5a6070')
def fields(add,rel=(-0.8,-1.3),w=5.0,d=3.2,n=4,win=None):
    k=dict(k='field',rel=list(rel),w=w,d=d,n=n)
    if win: k['grow']=[win[0],win[0]+1.4]
    add(**k)
