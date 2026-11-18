# 世界地図の陸の形（tools/geo_world.json）をつくる。もと：Natural Earth 1:50m land（パブリックドメイン）
#   python3 -I mk_world.py <ne_50m_land.geojson> geo_world.json
#   日本を真ん中に置く地図（太平洋が中央）にするため、西経25度より西の島・大陸は経度に360を足す（島ごとに）。
import json,sys,math
src,out=sys.argv[1],sys.argv[2]
d=json.load(open(src,encoding='utf-8'))
def dp(P,tol):
    if len(P)<4: return P
    keep=[False]*len(P); keep[0]=keep[-1]=True; st=[(0,len(P)-1)]
    while st:
        a,b=st.pop(); ax,ay=P[a]; bx,by=P[b]; dx,dy=bx-ax,by-ay; L=math.hypot(dx,dy); best,bi=-1,-1
        for i in range(a+1,b):
            px,py=P[i]; dd=abs(dy*(px-ax)-dx*(py-ay))/L if L else math.hypot(px-ax,py-ay)
            if dd>best: best,bi=dd,i
        if best>tol: keep[bi]=True; st+=[(a,bi),(bi,b)]
    return [p for p,k in zip(P,keep) if k]
rings=[]
for f in d['features']:
    g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for poly in polys:
        R=poly[0]
        if max(p[1] for p in R)<-58: continue            # 南極は入れない
        lon=sum(p[0] for p in R)/len(R); sh=360 if lon<-25 else 0
        Q=[(p[0]+sh,p[1]) for p in R]
        Q=dp(Q,0.12)
        if len(Q)<4: continue
        a=abs(sum(Q[i-1][0]*Q[i][1]-Q[i][0]*Q[i-1][1] for i in range(len(Q))))/2
        if a<0.6: continue                                # 小さな島は省く（約0.6平方度未満）
        rings.append([[round(x,2),round(y,2)] for x,y in Q])
json.dump({'land':rings,'source':'Natural Earth 1:50m land（パブリックドメイン）。日本中心の地図にするため、西経25度より西は経度に360を足した。南極と小さな島は省いた'},open(out,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print('rings',len(rings),'pts',sum(len(r) for r in rings))
