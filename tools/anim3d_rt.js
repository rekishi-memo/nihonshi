/*AN3-BEGIN*/
/* 動く図（an3）v2：セット（古代① など）ひとまとまりを1本の動画にする。外部ライブラリなしの小さな3D描画。
   見た目：夜の中に浮かぶ「地図の盤」。陸は少し厚みのある台地、遺跡などは盤から浮かぶ丸い展示台（プレート）の上に置く。
   すべて時刻 t の関数で描くので、章やバーでどこへでも飛べる。データは tools/anim3d.py（window.AN3_DATA）。 */
(function(){
"use strict";
const C={bg0:"#070b16",bg1:"#111a30",sea:"#132341",sea2:"#1b2f55",board:"#0d1628",land:"#6f8b78",land2:"#3d5547",coast:"#b9d0b2",gold:"#d4bd82",ivory:"#f1ece0",red:"#e07a5f"};
const FONT="'Zen Kaku Gothic New','Hiragino Sans','Noto Sans JP',system-ui,sans-serif";
function ez(u){ return u<0?0:u>1?1:u<.5?2*u*u:1-Math.pow(-2*u+2,2)/2; }
function lerp(a,b,u){ return a+(b-a)*u; }
function cl(v,a,b){ return v<a?a:v>b?b:v; }
function inR(r,t){ return !r||(t>=r[0]&&t<=r[1]); }
function prog(r,t){ return !r?0:cl((t-r[0])/((r[1]-r[0])||1),0,1); }
function env(on,t,fi,fo){ if(!on) return 1; return cl(Math.min((t-on[0])/(fi||0.4),(on[1]-t)/(fo||0.4)),0,1); }
function rnd(seed){ let s=Math.abs(Math.floor(seed*9301+49297))%233280; return ()=>{ s=(s*9301+49297)%233280; return s/233280; }; }
function light(hex,L){ const n=parseInt(hex.slice(1),16), f=v=>Math.min(255,Math.round(v*L)).toString(16).padStart(2,'0'); return '#'+f((n>>16)&255)+f((n>>8)&255)+f(n&255); }
function shade(hex,L){ const n=parseInt(hex.slice(1),16); return `rgb(${Math.min(255,Math.round(((n>>16)&255)*L))},${Math.min(255,Math.round(((n>>8)&255)*L))},${Math.min(255,Math.round((n&255)*L))})`; }
function kf(arr,t){ if(t<=arr[0][0]) return arr[0].slice(1);
  for(let i=1;i<arr.length;i++) if(t<=arr[i][0]){ const a=arr[i-1],b=arr[i],u=ez((t-a[0])/((b[0]-a[0])||1)); return a.slice(1).map((v,k)=>lerp(v,b[k+1],u)); }
  return arr[arr.length-1].slice(1); }
function camAt(S,t){ const K=S.cam; let a=K[0],b=K[0],u=0;
  if(t>=K[K.length-1][0]) a=b=K[K.length-1];
  else for(let i=1;i<K.length;i++) if(t<=K[i][0]){ a=K[i-1]; b=K[i]; u=ez((t-a[0])/((b[0]-a[0])||1)); break; }
  const la=Math.log(a[3]),lb=Math.log(b[3]),d=Math.exp(lerp(la,lb,u)); let w=u;
  if(Math.abs(lb-la)>1.2){ w=(Math.log(d)-la)/(lb-la); w=cl(lb>la?w*w:1-(1-w)*(1-w),0,1); }   // 遠ざかるときは先に上がってから動き、近づくときは先に動いてから降りる
  return {x:lerp(a[1],b[1],w),z:lerp(a[2],b[2],w),d,p:lerp(a[4],b[4],u),y:lerp(a[5],b[5],u)}; }
function pathLen(P){ const L=[0]; for(let i=1;i<P.length;i++) L.push(L[i-1]+Math.hypot(P[i][0]-P[i-1][0],P[i][1]-P[i-1][1])); return L; }
function pathAt(P,L,u){ const s=u*L[L.length-1]; for(let i=1;i<P.length;i++) if(s<=L[i]){ const v=(s-L[i-1])/((L[i]-L[i-1])||1); return [lerp(P[i-1][0],P[i][0],v),lerp(P[i-1][1],P[i][1],v)]; } return P[P.length-1].slice(0,2); }
function capHTML(s){ return s.replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])).replace(/【([^】]+)】/g,"<b>$1</b>"); }

class Player{
  constructor(el,S,G){
    this.el=el; this.S=S; this.G=G; this.t=0; this.play=false; this.last=0; this.raf=0;
    const rl=(S.ruler||[]).map(r=>`<span style="flex:${r[1]-r[0]}" data-a="${r[0]}" data-b="${r[1]}">${r[2]}</span>`).join("");
    el.innerHTML=`<div class="an3-stage"><canvas></canvas><div class="an3-ruler">${rl}</div><div class="an3-chap"></div>`+
      `<div class="an3-year"><i></i><b></b><span></span><i></i></div><div class="an3-cap"></div><button class="an3-btn" aria-label="再生">▶</button></div>`+
      `<div class="an3-bar"><div class="an3-prog"><i></i>${(S.chapters||[]).map(c=>`<em style="left:${100*c[0]/S.dur}%"></em>`).join("")}</div>`+
      `<div class="an3-chips">${(S.chapters||[]).map((c,i)=>`<span data-i="${i}">${c[2]?c[2]+" ":""}${c[1].replace(/【|】/g,"")}</span>`).join("")}</div></div>`;
    this.cv=el.querySelector("canvas"); this.g=this.cv.getContext("2d"); this.q=s=>el.querySelector(s);
    this.prep();
    const st=this.q(".an3-stage"); st.addEventListener("click",()=>this.toggle());
    this.q(".an3-prog").addEventListener("click",e=>{ e.stopPropagation(); const r=e.currentTarget.getBoundingClientRect(); this.seek(cl((e.clientX-r.left)/r.width,0,1)*S.dur); });
    el.querySelectorAll(".an3-chips span").forEach(c=>c.addEventListener("click",e=>{ e.stopPropagation(); this.seek(S.chapters[+c.dataset.i][0]+0.01); if(!this.play) this.toggle(); }));
    this.ro=new ResizeObserver(()=>{ this.size(); this.draw(); }); this.ro.observe(st);
    this.size(); this.draw(); this.ui();
  }
  prep(){ const S=this.S; this.byId={};
    for(const o of S.objs){ if(o.id) this.byId[o.id]=o;
      if(o.relpath&&o.pl&&this.byId[o.pl]){ const pa=this.byId[o.pl].at; o.path=o.relpath.map(q=>[pa[0]+q[0],pa[1]+q[1]]); }
      if(o.path) o._L=pathLen(o.path);
      if(o.k==="crowd"){ const R=rnd(o.seed||1),pts=[];
        for(let i=0;i<o.n;i++){ if(o.form==="rows"){ const cols=Math.ceil(Math.sqrt(o.n*1.6)), c=i%cols, r=Math.floor(i/cols); pts.push([(c-(cols-1)/2)*o.r*3.2/cols,r*o.r*0.45,R()]); continue; }
          if(o.form==="ring"){ const a=i/o.n*Math.PI*2; pts.push([Math.cos(a)*o.r,Math.sin(a)*o.r,R()]); continue; }
          const a=R()*Math.PI*2,d=Math.sqrt(R())*(o.r||0); pts.push([Math.cos(a)*d,Math.sin(a)*d*0.85,R()]); }
        o._p=pts; } } }
  size(){ const st=this.q(".an3-stage"), w=st.clientWidth, h=st.clientHeight, zr=w?Math.max(1,st.getBoundingClientRect().width/w):1, dpr=Math.min((window.devicePixelRatio||1)*zr,3);   // 拡大（zoom）されているぶん、細かく描く
    this.W=w; this.H=h; this.cv.width=Math.round(w*dpr); this.cv.height=Math.round(h*dpr); this.cv.style.width=w+"px"; this.cv.style.height=h+"px"; this.g.setTransform(dpr,0,0,dpr,0,0); }
  toggle(){ this.play=!this.play; if(this.play){ if(this.t>=this.S.dur-0.05) this.t=0; this.last=performance.now(); this.loop(); } else cancelAnimationFrame(this.raf); this.ui(); }
  seek(t){ this.t=cl(t,0,this.S.dur); this.last=performance.now(); this.draw(); }
  loop(){ this.raf=requestAnimationFrame(now=>{ if(!this.play) return; this.t+=Math.min(0.1,(now-this.last)/1000); this.last=now;
    if(this.t>=this.S.dur){ this.t=this.S.dur; this.play=false; this.draw(); this.ui(); return; } this.draw(); this.loop(); }); }
  stop(){ this.play=false; cancelAnimationFrame(this.raf); if(this.ro) this.ro.disconnect(); }
  ui(){ const b=this.q(".an3-btn"); b.textContent=this.t>=this.S.dur-0.05?"↻":"▶"; b.classList.toggle("hide",this.play); }

  // ── カメラ ──
  setCam(t){ const c=camAt(this.S,t), p=c.p*Math.PI/180, y=c.y*Math.PI/180;
    const fx=Math.cos(p)*Math.sin(y), fy=-Math.sin(p), fz=Math.cos(p)*Math.cos(y);
    const ty=(this.G.plateY||3)*cl((60-c.d)/40,0,1);
    this.e=[c.x-fx*c.d,ty+c.d*Math.sin(p),c.z-fz*c.d]; this.f=[fx,fy,fz];
    const rl=Math.hypot(fz,fx)||1; this.r=[fz/rl,0,-fx/rl];
    const f=this.f,r=this.r; this.u=[r[1]*f[2]-r[2]*f[1],r[2]*f[0]-r[0]*f[2],r[0]*f[1]-r[1]*f[0]]; if(this.u[1]<0) this.u=this.u.map(v=>-v);
    this.F=(this.H*0.5)/Math.tan(25*Math.PI/180); this.near=c.d*0.02; this.cd=c.d; this.lh=Math.min(c.d*0.0045,6); }
  tc(x,y,z){ const dx=x-this.e[0],dy=y-this.e[1],dz=z-this.e[2],r=this.r,u=this.u,f=this.f; return [dx*r[0]+dy*r[1]+dz*r[2],dx*u[0]+dy*u[1]+dz*u[2],dx*f[0]+dy*f[1]+dz*f[2]]; }
  sc(c){ return [this.W/2+c[0]*this.F/c[2],this.H*0.5-c[1]*this.F/c[2]]; }
  P(x,y,z){ const c=this.tc(x,y,z); return c[2]>this.near?[...this.sc(c),c[2]]:null; }
  clip(pts3){ const n=this.near,out=[];
    for(let i=0;i<pts3.length;i++){ const a=pts3[(i+pts3.length-1)%pts3.length],b=pts3[i],ai=a[2]>n,bi=b[2]>n;
      if(bi){ if(!ai){ const u=(n-a[2])/(b[2]-a[2]); out.push([lerp(a[0],b[0],u),lerp(a[1],b[1],u),n]); } out.push(b); }
      else if(ai){ const u=(n-a[2])/(b[2]-a[2]); out.push([lerp(a[0],b[0],u),lerp(a[1],b[1],u),n]); } }
    return out.map(c=>this.sc(c)); }
  pathP(pp){ const g=this.g; g.moveTo(pp[0][0],pp[0][1]); for(let i=1;i<pp.length;i++) g.lineTo(pp[i][0],pp[i][1]); g.closePath(); }
  fillP(pp){ this.g.beginPath(); this.pathP(pp); this.g.fill(); }
  ring(R,y){ const c=[]; for(let i=0;i<R.length;i+=2) c.push(this.tc(R[i],y,R[i+1])); return c; }
  onScreen(c){ for(const q of c) if(q[2]>this.near){ const s=this.sc(q); if(s[0]>-this.W&&s[0]<2*this.W&&s[1]>-this.H&&s[1]<2*this.H) return true; } return false; }

  draw(){ const g=this.g,W=this.W,H=this.H,S=this.S,G=this.G,t=this.t; if(!W) return;
    this.setCam(t);
    const bg=g.createRadialGradient(W/2,H*0.42,H*0.1,W/2,H*0.5,H*0.9); bg.addColorStop(0,C.bg1); bg.addColorStop(1,C.bg0); g.fillStyle=bg; g.fillRect(0,0,W,H);
    // 盤（海）：厚みのある板。世界地図があるときは、世界の板がいちばん外側になる
    this.far=!!G.world&&this.cd>12000;   // とても遠いときは、日本のまわりのこまかい地図を描かない（世界のあらい地図だけ）
    const WB=G.world?G.world.board:G.board, th=Math.max(this.cd*0.05,8), items0=[];
    const corners=[[WB[0],WB[1]],[WB[2],WB[1]],[WB[2],WB[3]],[WB[0],WB[3]]];
    for(let i=0;i<4;i++){ const a=corners[i],b=corners[(i+1)%4]; this.face([[a[0],0,a[1]],[a[0],-th,a[1]],[b[0],-th,b[1]],[b[0],0,b[1]]],C.board,items0,1); }
    items0.sort((a,b)=>b.z-a.z); items0.forEach(it=>it.d());
    const seaG=g.createLinearGradient(0,0,0,H); seaG.addColorStop(0,C.sea2); seaG.addColorStop(1,C.sea);
    const top=this.clip(corners.map(q=>this.tc(q[0],0,q[1]))); if(top.length>2){ g.fillStyle=seaG; this.fillP(top); }
    if(G.world){   // 世界の陸（平ら・あらい）。日本のまわりは、このあと、こまかい地図で上がきする
      g.fillStyle=C.land; g.strokeStyle=C.land; g.lineWidth=1; const wr=[];
      for(const R of G.world.ground){ const c=this.ring(R,0); if(!this.onScreen(c)&&R.length<400) continue; const pp=this.clip(c); if(pp.length>2){ g.beginPath(); this.pathP(pp); g.fill(); g.stroke(); wr.push(pp); } }
      g.strokeStyle=C.coast; g.globalAlpha=0.55; g.lineWidth=0.8; for(const pp of wr){ g.beginPath(); this.pathP(pp); g.stroke(); } g.globalAlpha=1;
      if(!this.far){ const B=G.board, bt=this.clip([[B[0],B[1]],[B[2],B[1]],[B[2],B[3]],[B[0],B[3]]].map(q=>this.tc(q[0],0,q[1]))); if(bt.length>2){ g.fillStyle=seaG; this.fillP(bt); } }
    }
    this.grid();
    // 氷期の陸橋など（時間で出たり消えたりする陸）
    for(const o of S.objs) if(o.k==="shelf"){ const a=kf(o.a,t)[0]; if(a<=0.01) continue; g.globalAlpha=a; g.fillStyle=C.land; g.strokeStyle=C.land; g.lineWidth=1;
      for(const R of o.polys){ const pp=this.clip(this.ring(R,0)); if(pp.length>2){ g.beginPath(); this.pathP(pp); g.fill(); g.stroke(); } } g.globalAlpha=1; }
    // 陸：側面（暗い色）→上面
    const lh=this.lh, tops=[];
    g.fillStyle=C.land2; g.strokeStyle=C.land2; g.lineWidth=1;
    for(const R of (this.far?[]:G.ground)){ const c=this.ring(R,0); if(!this.onScreen(c)&&R.length<400) continue; const pp=this.clip(c); if(pp.length>2){ g.beginPath(); this.pathP(pp); g.fill(); g.stroke(); } tops.push(R); }
    g.fillStyle=C.land; g.strokeStyle=C.land;
    for(const R of tops){ const pp=this.clip(this.ring(R,lh)); if(pp.length>2){ g.beginPath(); this.pathP(pp); g.fill(); g.stroke(); } }
    g.strokeStyle=C.coast; g.lineWidth=0.9; g.globalAlpha=0.7; g.beginPath();
    for(const R of (this.far?[]:G.coast)){ let prev=null; for(let i=0;i<R.length;i+=2){ const c=this.tc(R[i],lh,R[i+1]);
        if(prev&&prev[2]>this.near&&c[2]>this.near){ const p=this.sc(prev),q=this.sc(c); if(!((p[0]<0&&q[0]<0)||(p[0]>W&&q[0]>W)||(p[1]<0&&q[1]<0)||(p[1]>H&&q[1]>H))){ g.moveTo(p[0],p[1]); g.lineTo(q[0],q[1]); } }
        prev=c; } }
    g.stroke(); g.globalAlpha=1;
    for(const o of S.objs) if(inR(o.on,t)&&o.k==="tint") this.tint(o,t);
    for(const o of S.objs) if(inR(o.on,t)&&o.k==="trees") this.trees(o,t);
    this.labels(t);
    this.ph={}; let up=0; for(const o of S.objs) if(o.k==="plate"){ this.ph[o.id]=this.plateH(o,t); up=Math.max(up,this.ph[o.id]/o.h); }
    if(up>0){ g.fillStyle=`rgba(5,8,16,${0.62*up})`; g.fillRect(0,0,W,H); }   // 展示台が上がっているあいだは、地図を暗くする
    const items=[];
    for(const o of S.objs){ if(!inR(o.on,t)) continue; const k=o.k;
      if(k==="plate") this.plate(o,t,items); else if(k==="box") this.boxO(o,t,items); else if(k==="bldg") this.bldg(o,t,items);
      else if(k==="hut") this.hut(o,t,items); else if(k==="pagoda") this.pagoda(o,t,items); else if(k==="castle") this.castle(o,t,items); else if(k==="mound") this.mound(o,t,items); else if(k==="mounds") this.mounds(o,t,items); else if(k==="field") this.field(o,t,items);
      else if(k==="moat") this.moat(o,t,items); else if(k==="crowd") this.crowd(o,t,items); else if(k==="icon") this.icon(o,t,items);
      else if(k==="icons") this.icons(o,t,items); else if(k==="pin") this.pin(o,t,items); }
    items.sort((a,b)=>b.z-a.z); for(const it of items) it.d();
    for(const o of S.objs) if(inR(o.on,t)&&o.k==="route") this.route(o,t);
    for(const o of S.objs) if(inR(o.on,t)&&o.k==="arc") this.arc(o,t);
    for(const o of S.objs) if(inR(o.on,t)&&o.k==="tag") this.tagO(o,t);
    this.fx(t); this.texts(t);
    this.q(".an3-prog i").style.width=(100*t/S.dur)+"%";
  }
  grid(){ const g=this.g,B=this.G.world?this.G.world.board:this.G.board,st=this.cd>6000?1800:(this.G.gstep||400); g.strokeStyle="rgba(150,176,232,.07)"; g.lineWidth=1; g.beginPath();
    for(let x=Math.ceil(B[0]/st)*st;x<=B[2];x+=st){ const a=this.P(x,0,B[1]),b=this.P(x,0,B[3]); if(a&&b){ g.moveTo(a[0],a[1]); g.lineTo(b[0],b[1]); } }
    for(let z=Math.ceil(B[1]/st)*st;z<=B[3];z+=st){ const a=this.P(B[0],0,z),b=this.P(B[2],0,z); if(a&&b){ g.moveTo(a[0],a[1]); g.lineTo(b[0],b[1]); } }
    g.stroke(); }
  base(o){ return (o.pl?(this.ph[o.pl]||0):this.lh)+(o.y||0); }
  pos(o){ if(o.pl&&o.rel){ const p=this.byId[o.pl]; return [p.at[0]+o.rel[0],p.at[1]+o.rel[1]]; } return o.at; }
  vis(o,t){ let a=env(o.on,t,o.fi||0.4,o.fo||0.4); if(o.pl){ const p=this.byId[o.pl]; a*=cl((this.ph[o.pl]||0)/(p.h*0.9)-0.1,0,1); } return a; }
  labels(t){ const g=this.g; g.textAlign="center"; g.textBaseline="middle";
    for(const L of this.S.labels||[]){ if(L.on&&!inR(L.on,t)) continue; const d=this.cd; if(d<L.d[0]*0.6||d>L.d[1]*1.6) continue;
      let a=1; if(d<L.d[0]) a=(d-L.d[0]*0.6)/(L.d[0]*0.4); if(d>L.d[1]) a=1-(d-L.d[1])/(L.d[1]*0.6); if(L.on) a*=env(L.on,t,0.5,0.5);
      const q=this.P(L.at[0],this.lh,L.at[1]); if(!q||a<=0) continue;
      g.globalAlpha=cl(a,0,1)*0.95; g.font=`${L.big?700:500} ${L.big?14:11}px ${FONT}`; g.lineWidth=3; g.strokeStyle="rgba(10,16,30,.8)"; g.strokeText(L.s,q[0],q[1]); g.fillStyle=L.big?C.gold:C.ivory; g.fillText(L.s,q[0],q[1]); }
    g.globalAlpha=1; }
  tag(x,y,s,a,lift){ if(a<=0) return; const g=this.g; g.globalAlpha=cl(a,0,1); g.font=`700 11px ${FONT}`; const w=g.measureText(s).width+14, yy=y-(lift||26);
    g.fillStyle="rgba(9,14,28,.85)"; g.strokeStyle=C.gold; g.lineWidth=0.8; g.beginPath(); g.moveTo(x-w/2,yy-10); g.lineTo(x+w/2,yy-10); g.lineTo(x+w/2,yy+10); g.lineTo(x-w/2,yy+10); g.closePath(); g.fill(); g.stroke();
    g.beginPath(); g.moveTo(x,yy+10); g.lineTo(x,y-4); g.stroke(); g.fillStyle=C.ivory; g.textAlign="center"; g.textBaseline="middle"; g.fillText(s,x,yy+0.5); g.globalAlpha=1; }
  tagO(o,t){ const at=this.pos(o); const q=this.P(at[0],this.base(o),at[1]); if(q) this.tag(q[0],q[1],o.s,this.vis(o,t),o.lift); }
  face(pts,col,items,nocull){ const a=pts[0],b=pts[1],d=pts[2]; const ux=b[0]-a[0],uy=b[1]-a[1],uz=b[2]-a[2],vx=d[0]-a[0],vy=d[1]-a[1],vz=d[2]-a[2];
    let nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx; const nl=Math.hypot(nx,ny,nz)||1; nx/=nl; ny/=nl; nz/=nl;
    let cx=0,cy=0,cz=0; for(const p of pts){ cx+=p[0]; cy+=p[1]; cz+=p[2]; } cx/=pts.length; cy/=pts.length; cz/=pts.length;
    if(!nocull&&nx*(this.e[0]-cx)+ny*(this.e[1]-cy)+nz*(this.e[2]-cz)<0) return;
    const L=0.5+0.5*Math.max(0,nx*-0.42+ny*0.82+nz*-0.38), cc=this.tc(cx,cy,cz); if(cc[2]<=this.near) return; const zz=this._zfix!=null?this._zfix:cc[2];
    const pp=this.clip(pts.map(p=>this.tc(p[0],p[1],p[2]))); if(pp.length<3) return; const al=this._alpha==null?1:this._alpha;
    items.push({z:zz,d:()=>{ const g=this.g; g.globalAlpha=al; g.fillStyle=shade(col,L); this.fillP(pp); g.strokeStyle="rgba(0,0,0,.15)"; g.lineWidth=0.5; g.stroke(); g.globalAlpha=1; }}); }
  prism(poly,y0,y1,col,items,topCol){ const n=poly.length;
    this.face(poly.map(p=>[p[0],y1,p[1]]).reverse(),topCol||col,items);
    for(let i=0;i<n;i++){ const a=poly[i],b=poly[(i+1)%n]; this.face([[a[0],y0,a[1]],[a[0],y1,a[1]],[b[0],y1,b[1]],[b[0],y0,b[1]]],col,items); } }
  lathe(x,y,z,prof,seg,col,items){ for(let j=1;j<prof.length;j++){ const [r0,h0]=prof[j-1],[r1,h1]=prof[j];
      for(let i=0;i<seg;i++){ const a0=i/seg*Math.PI*2,a1=(i+1)/seg*Math.PI*2; const P0=[x+Math.cos(a0)*r0,y+h0,z+Math.sin(a0)*r0],P1=[x+Math.cos(a1)*r0,y+h0,z+Math.sin(a1)*r0],Q0=[x+Math.cos(a0)*r1,y+h1,z+Math.sin(a0)*r1],Q1=[x+Math.cos(a1)*r1,y+h1,z+Math.sin(a1)*r1];
        if(r1<1e-9) this.face([P0,Q0,P1],col,items); else if(r0<1e-9) this.face([P0,Q1,Q0],col,items); else this.face([P0,Q0,Q1,P1],col,items); } }
    const lt=prof[prof.length-1]; if(lt[0]>1e-9){ const top=[]; for(let i=seg-1;i>=0;i--){ const a=i/seg*Math.PI*2; top.push([x+Math.cos(a)*lt[0],y+lt[1],z+Math.sin(a)*lt[0]]); } this.face(top,col,items); } }
  plateH(o,t){ return o.h*ez(prog(o.rise,t))*(1-ez(prog(o.fall,t))); }
  plate(o,t,items){ const h=this.ph[o.id]; if(h<=o.h*0.02) return; const [x,z]=o.at, n=28, R=o.r*(0.3+0.7*cl(h/o.h,0,1)), y0=h-o.th;
    const top=[],side=o.side||"#4a3a2c"; this._zfix=2e11;
    for(let i=n-1;i>=0;i--){ const a=i/n*Math.PI*2; top.push([x+Math.cos(a)*R,h,z+Math.sin(a)*R]); }
    this.face(top,o.c||"#8c9a6a",items);
    for(let i=0;i<n;i++){ const a0=i/n*Math.PI*2,a1=(i+1)/n*Math.PI*2; this.face([[x+Math.cos(a0)*R,y0,z+Math.sin(a0)*R],[x+Math.cos(a0)*R,h,z+Math.sin(a0)*R],[x+Math.cos(a1)*R,h,z+Math.sin(a1)*R],[x+Math.cos(a1)*R,y0,z+Math.sin(a1)*R]],side,items); }
    this._zfix=null;
    const a=this.P(x,this.lh,z),b=this.P(x,y0,z); if(a&&b) items.push({z:1e12,d:()=>{ const g=this.g,gr=g.createLinearGradient(a[0],a[1],b[0],b[1]); gr.addColorStop(0,"rgba(212,189,130,0)"); gr.addColorStop(1,"rgba(212,189,130,.55)"); g.strokeStyle=gr; g.lineWidth=2; g.beginPath(); g.moveTo(a[0],a[1]); g.lineTo(b[0],b[1]); g.stroke(); }}); }
  boxO(o,t,items){ const a=this.vis(o,t); if(a<=0) return; const [x,z]=this.pos(o), y=this.base(o), gr=o.grow?ez(prog(o.grow,t)):1; if(gr<=0) return; this._alpha=a;
    const w=o.w/2,d=o.d/2; this.prism([[x-w,z-d],[x+w,z-d],[x+w,z+d],[x-w,z+d]],y,y+o.h*gr,o.c,items,o.top); this._alpha=null; }
  bldg(o,t,items){ const a=this.vis(o,t); if(a<=0) return; const [x,z]=this.pos(o), y=this.base(o)+(o.lift||0); this._alpha=a;
    const w=o.w/2,d=o.d/2; this.prism([[x-w,z-d],[x+w,z-d],[x+w,z+d],[x-w,z+d]],y,y+o.h,o.c,items);
    const Y=y+o.h,T=Y+o.roof,X0=x-w*1.18,X1=x+w*1.18,Z0=z-d*1.25,Z1=z+d*1.25;
    this.face([[X0,Y,Z0],[x-w*0.6,T,z],[x+w*0.6,T,z],[X1,Y,Z0]],o.r,items); this.face([[X1,Y,Z1],[x+w*0.6,T,z],[x-w*0.6,T,z],[X0,Y,Z1]],o.r,items);
    this.face([[X0,Y,Z1],[x-w*0.6,T,z],[X0,Y,Z0]],o.r,items); this.face([[X1,Y,Z0],[x+w*0.6,T,z],[X1,Y,Z1]],o.r,items);
    if(o.lift){ const pw=Math.min(w,d)*0.12; for(const [px,pz] of [[x-w*0.8,z-d*0.8],[x+w*0.8,z-d*0.8],[x+w*0.8,z+d*0.8],[x-w*0.8,z+d*0.8]]) this.prism([[px-pw,pz-pw],[px+pw,pz-pw],[px+pw,pz+pw],[px-pw,pz+pw]],y-o.lift,y,"#6b5038",items); }
    this._alpha=null; }
  pagoda(o,t,items){ const a=this.vis(o,t); if(a<=0) return; const [x,z]=this.pos(o); let y=this.base(o); this._alpha=a; const w=o.w, n=o.n||5, th=o.h/n;
    for(let k=0;k<n;k++){ const s=w*(1-k*0.1); this.prism([[x-s*0.32,z-s*0.32],[x+s*0.32,z-s*0.32],[x+s*0.32,z+s*0.32],[x-s*0.32,z+s*0.32]],y,y+th*0.55,o.c||"#8a3a2a",items);
      const r=s*0.62; this.prism([[x-r,z-r],[x+r,z-r],[x+r,z+r],[x-r,z+r]],y+th*0.55,y+th*0.7,o.r||"#3a3f4a",items); y+=th*0.7; }
    this.prism([[x-w*0.05,z-w*0.05],[x+w*0.05,z-w*0.05],[x+w*0.05,z+w*0.05],[x-w*0.05,z+w*0.05]],y,y+th*1.2,"#c9a24a",items); this._alpha=null; }
  castle(o,t,items){ const a=this.vis(o,t); if(a<=0) return; const [x,z]=this.pos(o); let y=this.base(o); this._alpha=a; const w=o.w;
    this.prism([[x-w*0.6,z-w*0.5],[x+w*0.6,z-w*0.5],[x+w*0.6,z+w*0.5],[x-w*0.6,z+w*0.5]],y,y+w*0.35,"#8d8a82",items); y+=w*0.35;
    for(let k=0;k<3;k++){ const s=1-k*0.25; this.prism([[x-w*0.42*s,z-w*0.34*s],[x+w*0.42*s,z-w*0.34*s],[x+w*0.42*s,z+w*0.34*s],[x-w*0.42*s,z+w*0.34*s]],y,y+w*0.22,"#efeae0",items);
      const r=1.25; this.prism([[x-w*0.42*s*r,z-w*0.34*s*r],[x+w*0.42*s*r,z-w*0.34*s*r],[x+w*0.42*s*r,z+w*0.34*s*r],[x-w*0.42*s*r,z+w*0.34*s*r]],y+w*0.22,y+w*0.28,"#3a3f4a",items); y+=w*0.28; }
    this._alpha=null; }
  hut(o,t,items){ const a=this.vis(o,t); if(a<=0) return; const [x,z]=this.pos(o),y=this.base(o),r=o.r,h=o.h; this._alpha=a;
    this.lathe(x,y,z,[[r,0],[r*0.96,h*0.12],[r*0.12,h*0.92],[0,h]],8,o.c||"#8a6a42",items); this._alpha=null; }
  // 前方後円墳：丸い部分と四角い部分を段に重ねる
  moundAt(x,z,y,L,h,angDeg,col,moat,items){ const ang=angDeg*Math.PI/180, ca=Math.cos(ang),sa=Math.sin(ang), rot=(u,v)=>[x+u*ca-v*sa,z+u*sa+v*ca], R=L*0.3, tiers=3;
    if(moat){ const pp=[]; for(let i=0;i<=12;i++){ const q=Math.PI*0.5+i/12*Math.PI; pp.push(rot(-L*0.2+Math.cos(q)*R*1.5,Math.sin(q)*R*1.5)); }
      const ring=[...pp,rot(L*0.62,-R*1.6),rot(L*0.62,R*1.6)]; this._zfix=1e11; this.face(ring.map(p=>[p[0],y+L*0.002,p[1]]).reverse(),"#2b4f7a",items,1); this._zfix=null; }
    for(let k=0;k<tiers;k++){ const s=1-k*0.22, y0=y+h*k/tiers, y1=y+h*(k+1)/tiers;
      const circ=[]; for(let i=0;i<14;i++){ const q=i/14*Math.PI*2; circ.push(rot(-L*0.2+Math.cos(q)*R*s,Math.sin(q)*R*s)); }
      this.prism(circ,y0,y1,col,items,light(col,1.15));
      const fw=R*1.15*s, nw=R*0.55*s, f0=-L*0.2+R*0.4, f1=L*0.5-k*L*0.04;
      this.prism([rot(f0,-nw),rot(f1,-fw),rot(f1,fw),rot(f0,nw)],y0,y+h*(k+0.8)/tiers,col,items,light(col,1.15)); } }
  mound(o,t,items){ const a=this.vis(o,t); if(a<=0) return; const gr=o.grow?ez(prog(o.grow,t)):1; if(gr<=0.01) return; const [x,z]=this.pos(o);
    this._alpha=a; this.moundAt(x,z,this.base(o),o.L*(0.5+0.5*gr),o.h*gr,o.a||0,o.c||"#5f7d4d",o.moat,items); this._alpha=null; }
  mounds(o,t,items){ // 地図の上にたくさん（大きさは画面で見える大きさに合わせる）
    for(let k=0;k<o.list.length;k++){ const [x,z,sc]=o.list[k], t0=o.on[0]+(o.stagger||0)*k; if(t<t0) continue; let a=env([t0,o.on[1]],t,0.4,0.6); if(o.fade&&o.fade[k]!=null) a*=1-prog([o.fade[k],o.fade[k]+0.8],t); if(a<=0) continue;
      const gr=ez(prog([t0,t0+0.6],t)); const q=this.P(x,this.lh,z); if(!q) continue; const L=cl(o.px*(sc||1)*q[2]/this.F,0,1e9);
      this._alpha=a; this.moundAt(x,z,this.lh,L,L*0.16*gr,o.a||-30,o.c||"#7aa060",false,items); this._alpha=null; } }
  field(o,t,items){ const a=this.vis(o,t); if(a<=0) return; const [x,z]=this.pos(o),y=this.base(o)+o.w*0.004, n=o.n||3, gr=o.grow?prog(o.grow,t):1; this._alpha=a;
    this._zfix=1e11; const cw=o.w/n,cd=o.d/n; for(let i=0;i<n;i++) for(let j=0;j<n;j++){ const k=i*n+j; if(k/(n*n)>=gr) continue; const x0=x-o.w/2+i*cw+cw*0.06,z0=z-o.d/2+j*cd+cd*0.06,x1=x0+cw*0.88,z1=z0+cd*0.88;
      this.face([[x0,y,z1],[x1,y,z1],[x1,y,z0],[x0,y,z0]],(i+j)%2?(o.c1||"#7fa35a"):(o.c2||"#5f8f74"),items,1); }
    this._alpha=null; this._zfix=null; }
  moat(o,t,items){ const a=this.vis(o,t); if(a<=0) return; const [x,z]=this.pos(o),y=this.base(o)+o.w*0.02; this._alpha=a; this._zfix=1e11;
    for(const r of o.rs){ const n=28,w=o.w; for(let i=0;i<n;i++){ const a0=i/n*Math.PI*2,a1=(i+1)/n*Math.PI*2;
        this.face([[x+Math.cos(a0)*r,y,z+Math.sin(a0)*r],[x+Math.cos(a1)*r,y,z+Math.sin(a1)*r],[x+Math.cos(a1)*(r+w),y,z+Math.sin(a1)*(r+w)],[x+Math.cos(a0)*(r+w),y,z+Math.sin(a0)*(r+w)]],o.c||"#2b4f7a",items,1); } }
    this._alpha=null; this._zfix=null; }
  tint(o,t){ const a=kf(o.a,t)[0]; if(a<=0.01) return; const g=this.g; g.globalAlpha=a; g.fillStyle=o.c;
    for(const R of o.polys){ const pp=this.clip(this.ring(R,this.lh*1.01)); if(pp.length>2) this.fillP(pp); } g.globalAlpha=1; }
  trees(o,t){ const g=this.g, a=env(o.on,t,1,1); if(a<=0) return; g.globalAlpha=a;
    for(const p of o.pts){ const q=this.P(p[0],this.lh,p[1]); if(!q) continue; const s=cl(o.h*this.F/q[2],1.6,6); g.fillStyle=o.cols[p[2]]; g.beginPath(); g.moveTo(q[0],q[1]-s*1.7); g.lineTo(q[0]+s*0.6,q[1]); g.lineTo(q[0]-s*0.6,q[1]); g.closePath(); g.fill(); }
    g.globalAlpha=1; }
  crowd(o,t,items){ const a0=this.vis(o,t); if(a0<=0) return; const g=this.g; const [cx,cz]=o.path?pathAt(o.path,o._L,ez(prog(o.move,t))):this.pos(o); const y=this.base(o);
    const jit=o.jit&&inR(o.jit,t)?1:0, hopOn=o.hop&&inR(o.hop,t)?1:0, rise=o.rise?ez(prog(o.rise,t)):1;
    for(let i=0;i<o._p.length;i++){ const pt=o._p[i]; let x=cx+pt[0], z=cz+pt[1];
      if(jit){ x+=Math.sin(t*9+pt[2]*40)*o.h*0.3; z+=Math.cos(t*7+pt[2]*31)*o.h*0.3; }
      const hop=hopOn?Math.abs(Math.sin(t*10+pt[2]*6))*o.h*0.3:0;
      const f=this.P(x,y+hop,z); if(!f) continue; const hp=o.h*this.F/f[2]; if(hp<0.6) continue;
      const av=a0*cl((rise-pt[2]*0.5)/0.5,0,1); if(av<=0) continue;
      const col=o.cols?o.cols[i%o.cols.length]:o.c;
      items.push({z:f[2],d:()=>person(g,f[0],f[1],Math.min(hp,o.max||1e9),col,o.flag,av,o.hair)}); } }
  icon(o,t,items){ const a=this.vis(o,t); if(a<=0) return; const [x,z]=o.path?pathAt(o.path,o._L,ez(prog(o.move,t))):this.pos(o); const bob=o.float?Math.sin(t*2+(o.ph||0))*o.s*0.08:0;
    const pop=o.pop?ez(prog([o.on[0],o.on[0]+0.5],t)):1;
    const f=this.P(x,this.base(o)+(o.float||0)+bob,z); if(!f) return; let s=o.s*this.F/f[2]*(0.5+0.5*pop); if(o.min) s=Math.max(s,o.min); if(o.max) s=Math.min(s,o.max); if(s<1) return;
    items.push({z:f[2]-(o.front?1e6:0),d:()=>drawIcon(this.g,o.i,f[0],f[1],s,o.c,a)}); }
  icons(o,t,items){ for(let k=0;k<o.list.length;k++){ const it=o.list[k], t0=o.on[0]+(o.stagger||0)*k; if(t<t0) continue;
      this.icon({k:"icon",i:it[2]||o.i,at:o.pl?null:[it[0],it[1]],rel:o.pl?[it[0],it[1]]:null,s:o.s,c:it[3]||o.c,on:[t0,o.on[1]],pop:1,min:o.min,max:o.max,y:o.y,pl:o.pl,float:o.float},t,items); } }
  pin(o,t,items){ const a=this.vis(o,t); if(a<=0) return; const [x,z]=this.pos(o), y=this.base(o); const f=this.P(x,y,z); if(!f) return; const hgt=o.hp||26;
    items.push({z:f[2]-1e5,d:()=>{ const g=this.g; g.globalAlpha=a; g.strokeStyle=C.gold; g.lineWidth=1.4; g.beginPath(); g.moveTo(f[0],f[1]); g.lineTo(f[0],f[1]-hgt); g.stroke();
      g.fillStyle=o.c||C.red; g.beginPath(); g.arc(f[0],f[1]-hgt,5,0,7); g.fill(); g.globalAlpha=1; if(o.s) this.tag(f[0],f[1]-hgt,o.s,a,20); }}); }
  route(o,t){ const u=prog(o.draw,t), a=env(o.on,t,0.3,o.fo||0.6); if(u<=0||a<=0) return; const g=this.g, P=o.path, L=o._L, tot=L[L.length-1], s=ez(u)*tot;
    const pts=[]; for(let i=0;i<P.length;i++){ if(L[i]<=s) pts.push(P[i]); else { const v=(s-L[i-1])/(L[i]-L[i-1]); pts.push([lerp(P[i-1][0],P[i][0],v),lerp(P[i-1][1],P[i][1],v)]); break; } }
    const sp=pts.map(p=>this.P(p[0],this.lh,p[1])).filter(Boolean); if(sp.length<2) return;
    g.globalAlpha=a; g.strokeStyle=o.c||C.gold; g.lineWidth=o.w||2; g.setLineDash(o.dash===0?[]:[6,4]); g.lineDashOffset=-t*18; g.beginPath(); g.moveTo(sp[0][0],sp[0][1]); for(const q of sp) g.lineTo(q[0],q[1]); g.stroke(); g.setLineDash([]);
    const n=o.n||1, gap=tot*0.025;
    for(let k=0;k<n;k++){ const sk=s-k*gap; if(sk<0) break; const h=pathAt(P,L,sk/tot), h2=pathAt(P,L,Math.max(0,sk-tot*0.01)/tot), q=this.P(h[0],this.lh,h[1]), q2=this.P(h2[0],this.lh,h2[1]); if(!q) continue;
      const fl=q2&&q2[0]>q[0]?-1:1; g.save(); g.translate(q[0],q[1]); g.scale(fl,1); drawIcon(g,o.i||"ship",0,0,o.is||18,o.ic,a); g.restore(); }
    g.globalAlpha=1; }
  arc(o,t){ const u=ez(prog(o.draw,t)), a=env(o.on,t,0.3,o.fo||0.5); if(u<=0||a<=0) return; const g=this.g, N=40, H=o.hgt||Math.hypot(o.b[0]-o.a[0],o.b[1]-o.a[1])*0.25;
    const pts=[]; for(let i=0;i<=N*u;i++){ const v=i/N; const q=this.P(lerp(o.a[0],o.b[0],v),this.lh+4*v*(1-v)*H,lerp(o.a[1],o.b[1],v)); if(q) pts.push(q); }
    if(pts.length<2) return; g.globalAlpha=a; g.strokeStyle=o.c||C.gold; g.lineWidth=o.w||1.8; g.setLineDash(o.dash?[5,4]:[]); g.beginPath(); g.moveTo(pts[0][0],pts[0][1]); for(const q of pts) g.lineTo(q[0],q[1]); g.stroke(); g.setLineDash([]);
    const h=pts[pts.length-1]; if(o.i&&u<1) drawIcon(g,o.i,h[0],h[1]+6,o.is||14,o.ic,a); else { g.fillStyle=o.c||C.gold; g.beginPath(); g.arc(h[0],h[1],2.6,0,7); g.fill(); }
    g.globalAlpha=1; }
  fx(t){ const g=this.g,W=this.W,H=this.H;
    for(const f of this.S.fx||[]){
      if(f.k==="flash"&&t>=f.t&&t<f.t+0.4){ g.fillStyle=`rgba(241,236,224,${(1-(t-f.t)/0.4)*0.6})`; g.fillRect(0,0,W,H); }
      if(f.k==="dim"&&inR(f.on,t)){ g.fillStyle=`rgba(5,8,16,${0.45*env(f.on,t,0.5,0.5)})`; g.fillRect(0,0,W,H); } } }
  texts(t){ const S=this.S; let cap=null,year=null,chap=null;
    for(const x of S.text){ if(t<x.t||t>x.t+x.d) continue; if(x.k==="cap") cap=x; else if(x.k==="year") year=x; }
    for(const c of S.chapters||[]) if(t>=c[0]) chap=c;
    const set=(sel,x,fill)=>{ const el=this.q(sel), key=x?x[0]!=null?String(x[0]):x.t+":"+x.s:""; if(el.dataset.k!==key){ el.dataset.k=key; if(x) fill(el,x); el.classList.remove("on"); void el.offsetWidth; if(x) el.classList.add("on"); } };
    set(".an3-cap",cap,(el,x)=>{ el.innerHTML=capHTML(x.s); });
    set(".an3-year",year,(el,x)=>{ const b=el.querySelector("b"); b.textContent=x.s; b.style.fontSize=(x.s.length<=4?44:x.s.length<=6?34:26)+"px"; el.querySelector("span").textContent=x.sub||""; });
    set(".an3-chap",chap,(el,x)=>{ el.innerHTML=`<em>授業${x[2]||""}</em>${capHTML(x[1])}`; });
    this.el.querySelectorAll(".an3-ruler span").forEach(s=>s.classList.toggle("on",t>=+s.dataset.a&&t<+s.dataset.b));
    this.el.querySelectorAll(".an3-chips span").forEach((s,i)=>{ const c=S.chapters[i],n=S.chapters[i+1]; s.classList.toggle("on",t>=c[0]&&(!n||t<n[0])); }); }
}
function person(g,x,y,h,col,flag,a,hair){ if(a<=0) return; g.globalAlpha=a; const w=h*0.44;
  g.fillStyle="rgba(0,0,0,.25)"; g.beginPath(); g.ellipse(x,y,w*0.55,w*0.16,0,0,7); g.fill();
  g.fillStyle=col; g.beginPath(); g.moveTo(x-w/2,y); g.lineTo(x-w*0.28,y-h*0.66); g.lineTo(x+w*0.28,y-h*0.66); g.lineTo(x+w/2,y); g.closePath(); g.fill();
  g.fillStyle=shade(col,0.72); g.beginPath(); g.moveTo(x+w*0.06,y); g.lineTo(x+w*0.08,y-h*0.66); g.lineTo(x+w*0.28,y-h*0.66); g.lineTo(x+w/2,y); g.closePath(); g.fill();
  g.fillStyle=hair||"#e9d6b4"; g.beginPath(); g.arc(x,y-h*0.8,h*0.15,0,7); g.fill();
  if(flag&&h>5){ g.strokeStyle="#2a2a2a"; g.lineWidth=Math.max(0.6,h*0.04); g.beginPath(); g.moveTo(x+w*0.25,y-h*0.5); g.lineTo(x+w*0.25,y-h*1.3); g.stroke(); g.fillStyle=flag; g.fillRect(x+w*0.25,y-h*1.3,h*0.28,h*0.36); }
  g.globalAlpha=1; }
// 小さな絵（遺物・動物など）。s は高さ（px）、足もとが (x,y)
function drawIcon(g,i,x,y,s,col,a){ g.save(); g.globalAlpha=a; g.translate(x,y); const k=s/20; g.scale(k,k); g.lineJoin="round";
  const P=(d,f,st,lw)=>{ const p=new Path2D(d); if(f){ g.fillStyle=f; g.fill(p); } if(st){ g.strokeStyle=st; g.lineWidth=lw||1; g.stroke(p); } };
  switch(i){
  case "zou": P("M-13 0 L-13 -8 Q-14 -15 -6 -16 L5 -16 Q12 -16 12 -9 L15 -4 L14 2 L12 1 L12 -5 L10 -5 L10 0 L6 0 L6 -6 L-6 -6 L-6 0 L-10 0 L-10 -6 Z",col||"#8a8072","#3a352e",0.8); P("M10 -12 l3 3",null,"#efe6d0",1.2); break;
  case "mammoth": P("M-13 0 L-13 -9 Q-13 -17 -4 -18 L6 -17 Q13 -15 12 -8 L14 -2 Q15 2 12 2 L11 -3 L10 -3 L10 0 L6 0 L6 -6 L-6 -6 L-6 0 L-10 0 L-10 -6 Z",col||"#7a5236","#2e2016",0.8); P("M11 -6 q5 2 3 6",null,"#efe6d0",1.4); break;
  case "deer": P("M-10 0 L-10 -8 L6 -9 L9 -14 L12 -13 L10 -8 L10 0 L7 0 L7 -5 L-6 -5 L-6 0 Z",col||"#9a6b3e"); P("M9 -14 l-2 -5 M10 -14 l2 -5",null,"#5a3a22",1); break;
  case "point": P("M0 -20 L5 -6 L3 0 L-3 0 L-5 -6 Z",col||"#5b5f66","#22262c",0.8); break;
  case "blade": P("M-8 -4 L8 -4 L8 -1 L-8 -1 Z M-8 -9 L8 -9 L8 -6 L-8 -6 Z M-8 -14 L8 -14 L8 -11 L-8 -11 Z",col||"#2e3238"); break;
  case "pot": P("M-7 0 Q-11 -6 -8 -12 Q-10 -17 -9 -20 L9 -20 Q10 -17 8 -12 Q11 -6 7 0 Z",col||"#a0663e","#5a3622",0.8); P("M-8 -15 h16 M-9 -9 h18 M-8 -4 h16",null,"rgba(60,30,15,.6)",0.8); P("M-9 -20 l-2 -3 l4 1 l3 -2 l3 2 l3 -2 l3 2 l4 -1 l-2 3",col||"#a0663e"); break;
  case "dogu": P("M0 -20 Q6 -20 6 -14 Q6 -11 3 -10 L9 -8 L9 -5 L4 -6 L5 0 L1 0 L0 -4 L-1 0 L-5 0 L-4 -6 L-9 -5 L-9 -8 L-3 -10 Q-6 -11 -6 -14 Q-6 -20 0 -20 Z",col||"#b07a4a","#5a3a22",0.8); P("M-4.5 -15 h3.5 v1.6 h-3.5 Z M1 -15 h3.5 v1.6 h-3.5 Z","#3a2414"); break;
  case "shell": P("M-8 0 Q-10 -10 0 -14 Q10 -10 8 0 Z",col||"#e9e2cf","#8f8673",0.8); P("M0 0 L0 -13 M-4 0 L-3 -12 M4 0 L3 -12",null,"#a59c86",0.6); break;
  case "stone": P("M-6 0 L-7 -6 L-3 -10 L4 -9 L7 -4 L6 0 Z",col||"#7d828a","#3c4046",0.8); break;
  case "rice": P("M0 0 Q1 -10 -4 -18 M0 0 Q-1 -9 5 -17 M0 0 L0 -19",null,"#c9a74a",1.4); P("M-6 -14 l2 -2 M-5 -10 l2 -2 M5 -14 l-2 -2 M4 -10 l-2 -2 M-1 -17 l1 -2",null,"#e8cf7a",1.6); break;
  case "knife": P("M-10 -4 Q-10 -12 0 -12 Q10 -12 10 -4 Z",col||"#7a7f86","#30343a",0.8); P("M-3 -8 a1.3 1.3 0 1 0 0.01 0 M3 -8 a1.3 1.3 0 1 0 0.01 0","#22262c"); break;
  case "dotaku": P("M-6 -18 L6 -18 L9 0 L-9 0 Z",col||"#5f9c8a","#2d5248",0.8); P("M-3 -18 Q0 -24 3 -18",null,col||"#5f9c8a",2); P("M-7 -12 h14 M-8 -6 h16",null,"#2d5248",0.7); break;
  case "hoko": P("M0 -22 L3 -10 L2 0 L-2 0 L-3 -10 Z",col||"#5f9c8a","#2d5248",0.8); break;
  case "ken": P("M0 -22 L2.5 -18 L2 -4 L5 -4 L5 -2 L1.5 -2 L1.5 2 L-1.5 2 L-1.5 -2 L-5 -2 L-5 -4 L-2 -4 L-2.5 -18 Z",col||"#5f9c8a","#2d5248",0.8); break;
  case "mirror": P("M0 -10 m-10 0 a10 10 0 1 0 20 0 a10 10 0 1 0 -20 0",col||"#9fb0a6","#4c5a52",1); P("M0 -10 m-6 0 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0",null,"#5d6d64",0.8); P("M0 -10 m-2 0 a2 2 0 1 0 4 0 a2 2 0 1 0 -4 0","#5d6d64"); break;
  case "seal": P("M-6 0 L-6 -8 L6 -8 L6 0 Z",col||"#e2b84a","#8a6a1c",0.8); P("M-4 -8 Q-4 -15 0 -15 Q4 -15 4 -8",col||"#e2b84a","#8a6a1c",0.8); break;
  case "sword": P("M-1.5 -22 L1.5 -22 L1.5 -3 L4 -3 L4 -1 L1.2 -1 L1.2 3 L-1.2 3 L-1.2 -1 L-4 -1 L-4 -3 L-1.5 -3 Z",col||"#8d8f92","#3e4044",0.8); P("M-0.6 -19 v14",null,"#e2b84a",0.9); break;
  case "scroll": P("M-9 -16 L9 -16 L9 -2 L-9 -2 Z",col||"#efe4c4","#8a7a52",0.8); P("M-6 -12 h12 M-6 -9 h12 M-6 -6 h8",null,"#6a5a3a",0.7); break;
  case "buddha": P("M0 -21 a3.5 3.5 0 1 0 0.01 0 Z M-7 0 Q-8 -8 -4 -12 L4 -12 Q8 -8 7 0 Z",col||"#d8b85a","#7a6020",0.8); P("M-9 -12 a9 9 0 0 1 18 0",null,"rgba(232,207,122,.5)",1); break;
  case "sue": P("M-6 0 Q-9 -6 -6 -11 L-3 -13 L-3 -17 L3 -17 L3 -13 L6 -11 Q9 -6 6 0 Z",col||"#7c818a","#3c4046",0.8); break;
  case "haji": P("M-8 0 Q-11 -7 -7 -13 L7 -13 Q11 -7 8 0 Z",col||"#c07a4e","#6a3a20",0.8); break;
  case "horse": P("M-12 0 L-11 -9 L4 -10 L8 -16 L12 -14 L9 -8 L9 0 L6 0 L6 -5 L-8 -5 L-8 0 Z",col||"#6a4a32"); P("M-11 -9 l-3 4",null,col||"#6a4a32",1.5); break;
  case "tooth": P("M-5 -16 Q0 -19 5 -16 L4 -6 L2 -2 L0 -7 L-2 -2 L-4 -6 Z",col||"#f1ecdf","#9a9384",0.8); break;
  case "coin": P("M0 -10 m-9 0 a9 9 0 1 0 18 0 a9 9 0 1 0 -18 0",col||"#b8864a","#5e4020",1); P("M-2.6 -12.6 h5.2 v5.2 h-5.2 Z","#3a2814"); break;
  case "koban": P("M0 -11 m-6.5 0 a6.5 10 0 1 0 13 0 a6.5 10 0 1 0 -13 0",col||"#e2c25a","#8a6a1c",1); P("M-4 -15 h8 M-4 -11 h8 M-4 -7 h8",null,"#b8952e",0.8); break;
  case "silver": P("M-8 0 Q-9 -6 -5 -9 Q0 -11 5 -9 Q9 -6 8 0 Z",col||"#c9cdd2","#6c7076",1); break;
  case "satsu": P("M-11 -15 h22 v12 h-22 Z",col||"#d9c99a","#7a6a42",1); P("M0 -9 m-3.5 0 a3.5 3.5 0 1 0 7 0 a3.5 3.5 0 1 0 -7 0",null,"#7a6a42",0.8); P("M-8 -12 h4 M4 -6 h4",null,"#7a6a42",0.8); break;
  case "book": P("M-9 -16 h8 q1 1 1 1 q0 -1 1 -1 h8 v14 h-8 q-1 0 -1 1 q0 -1 -1 -1 h-8 Z",col||"#c9b99a","#5a4a2a",0.9); P("M0 -15 v13",null,"#5a4a2a",0.8); break;
  case "torii": P("M-11 -17 h22 l-1 2 h-20 Z M-9 -13 h18 v1.6 h-18 Z M-7 -15 h2 v15 h-2 Z M5 -15 h2 v15 h-2 Z",col||"#c8483a"); break;
  case "pagoda": P("M-1 -22 h2 v3 h-2 Z M-8 -19 h16 l-3 2 h-10 Z M-5 -17 h10 v3 h-10 Z M-9 -14 h18 l-3 2 h-12 Z M-5 -12 h10 v3 h-10 Z M-10 -9 h20 l-3 2 h-14 Z M-6 -7 h12 v7 h-12 Z",col||"#7a4a3a","#2a1a12",0.6); break;
  case "ship": P("M-12 -4 L12 -4 L8 0 L-9 0 Z",col||"#6a4a32"); P("M-1 -4 V-20",null,"#3a2a1a",1); P("M-1 -19 L9 -8 L-1 -8 Z",col?"#e9e0c8":"#e9e0c8"); break;
  case "steamer": P("M-13 -4 L13 -4 L9 0 L-10 0 Z",col||"#2e3440"); P("M-8 -9 h14 v5 h-14 Z","#c9c2b0"); P("M-2 -15 h4 v6 h-4 Z","#8a3a2a"); P("M0 -17 q3 -3 7 -2",null,"rgba(200,200,200,.8)",1.6); break;
  case "train": P("M-13 -10 h9 v8 h-9 Z M-3 -9 h7 v7 h-7 Z M5 -9 h7 v7 h-7 Z",col||"#2e3440"); P("M-12 -14 h3 v4 h-3 Z","#2e3440"); P("M-11 -1 a1.6 1.6 0 1 0 0.1 0 M-6 -1 a1.6 1.6 0 1 0 0.1 0 M0 -1 a1.6 1.6 0 1 0 0.1 0 M8 -1 a1.6 1.6 0 1 0 0.1 0","#111"); P("M-11 -16 q2 -3 6 -3",null,"rgba(220,220,220,.8)",1.6); break;
  case "letter": P("M-10 -14 h20 v12 h-20 Z",col||"#efe6d0","#7a6a4a",1); P("M-10 -14 L0 -7 L10 -14",null,"#7a6a4a",1); break;
  case "fire": P("M0 -20 Q7 -12 5 -5 Q4 0 0 0 Q-4 0 -5 -5 Q-6 -11 0 -20 Z",col||"#e8743a"); P("M0 -11 Q3 -7 2 -3 Q1 0 0 0 Q-2 0 -2 -3 Q-2 -6 0 -11 Z","#f4c95a"); break;
  case "wave": P("M-12 0 Q-12 -12 -2 -14 Q6 -15 8 -9 Q3 -11 0 -7 Q4 -6 6 -3 Q2 -4 0 0 Z",col||"#5f9ccf","#2d5a85",0.8); break;
  case "quake": P("M-12 -6 l4 -6 l4 10 l4 -12 l4 12 l4 -8 l4 4",null,col||"#e07a5f",2); break;
  case "flag": P("M-6 0 V-20",null,"#5a5a5a",1.2); P("M-6 -20 h14 v9 h-14 Z",col||"#f1ece0","#999",0.6); P("M1 -15.5 m-2.6 0 a2.6 2.6 0 1 0 5.2 0 a2.6 2.6 0 1 0 -5.2 0","#c8483a"); break;
  case "cross": P("M-1.6 -20 h3.2 v20 h-3.2 Z M-7 -15 h14 v3 h-14 Z",col||"#e9e0c8"); break;
  case "bank": P("M-11 0 h22 v-2 h-22 Z M-9 -2 h2 v-9 h-2 Z M-3.5 -2 h2 v-9 h-2 Z M1.5 -2 h2 v-9 h-2 Z M7 -2 h2 v-9 h-2 Z M-11 -11 h22 L0 -18 Z",col||"#d9d2c0","#6a6458",0.6); break;
  case "smoke": P("M0 0 q-4 -4 0 -8 q4 -4 0 -9 q-3 -3 1 -6",null,col||"rgba(200,200,200,.7)",2.4); break;
  case "sick": P("M0 -20 a3.5 3.5 0 1 0 0.01 0 Z M-6 0 Q-7 -8 -4 -12 L4 -12 Q7 -8 6 0 Z",col||"#8a8f98"); P("M5 -19 q3 -2 5 1",null,"#7fb3d5",1.2); break;
  case "scale": P("M0 -20 v18 M-9 -16 h18 M-6 0 h12",null,col||"#d4bd82",1.6); P("M-9 -16 l-4 7 h8 Z M9 -16 l-4 7 h8 Z",col||"#d4bd82"); break;
  case "crown": P("M-9 -2 L-10 -14 L-5 -8 L0 -16 L5 -8 L10 -14 L9 -2 Z",col||"#e2b84a","#8a6a1c",0.8); break;
  case "bell": P("M-6 -16 Q-7 -6 -9 0 L9 0 Q7 -6 6 -16 Q0 -20 -6 -16 Z",col||"#8a7a5a","#3a2e1a",0.8); break;
  case "woman": P("M0 -20 a3.6 3.6 0 1 0 0.01 0 Z M-7 0 Q-6 -9 -3 -12 L3 -12 Q6 -9 7 0 Z",col||"#c8483a"); P("M-3.6 -20 q-2 5 -1 9 M3.6 -20 q2 5 1 9",null,"#2a2420",1.6); break;
  case "factory": P("M-12 0 V-9 L-6 -13 V-9 L0 -13 V-9 L6 -13 V0 Z",col||"#8a4a3a"); P("M7 0 V-20 h3 V0 Z","#6a3a2a"); P("M8.5 -21 q-3 -3 1 -6",null,"rgba(210,210,210,.7)",2); break;
  case "en": P("M-10 0 Q-10 -9 0 -9 Q10 -9 10 0 Z",col||"#7aa060","#3e5a30",0.8); break;
  case "bale": P("M-8 0 Q-10 -6 -8 -12 L8 -12 Q10 -6 8 0 Z",col||"#d8c27a","#7a6a3a",0.8); P("M-9 -4 h18 M-9 -8 h18",null,"#7a6a3a",0.8); break;
  case "q": g.font="700 20px "+FONT; g.fillStyle=col||"#f1ece0"; g.textAlign="center"; g.textBaseline="alphabetic"; g.fillText("？",0,0); break;
  default: P("M0 -10 m-6 0 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0",col||"#d4bd82");
  }
  g.restore(); g.globalAlpha=1; }

const A3={list:[],pid:null};
function data(){ return window.AN3_DATA||null; }
function stopAll(){ A3.list.forEach(p=>p.stop()); A3.list=[]; A3.pid=null; }
// 「動画」タブの中身。そのセットの動画があれば再生器を置き、なければ、ある動画の一覧を出す
function render(){ const box=document.getElementById("an3Video"); if(!box) return;
  const sec=document.getElementById("sec-video"), on=sec&&sec.classList.contains("active");
  if(!on){ if(A3.list.length){ stopAll(); box.innerHTML=""; } return; }
  const D=data(), pid=(typeof activeId!=="undefined")?activeId:null;
  if(A3.pid===pid&&A3.list.length) return;
  stopAll();
  const S=D&&pid&&D.packs[pid];
  if(!S){ const have=D?Object.keys(D.packs).map(k=>`<button class="an3-go" data-p="${k}">${D.packs[k].title}</button>`).join(""):"";
    box.innerHTML=`<div class="an3-none"><b>このまとまりの動画は、まだありません</b><p>いま見られる動画：</p>${have}</div>`;
    box.querySelectorAll(".an3-go").forEach(b=>b.addEventListener("click",async()=>{ if(typeof goPack==="function"){ await goPack(b.dataset.p,0); } if(typeof switchSec==="function") switchSec("video"); render(); }));
    return; }
  box.innerHTML=`<div class="an3-head"><b>${S.title}</b><small>このまとまりを約${Math.round(S.dur/60)}分で。政治も文化も、流れで。画面をタップで再生・一時停止、下の章で飛べる。位置・人数・形はおおよそ</small></div><div class="an3"></div>`;
  A3.list.push(new Player(box.querySelector(".an3"),S,D)); A3.pid=pid; }
window.an3Sec=function(){ render(); };
window.an3Mount=function(){ render(); };
// 最初の表示がこの読みこみより先に終わっていることがある（iPhone）。読みこんだら一度、自分でも描く
render(); window.addEventListener("load",render);
document.addEventListener("visibilitychange",()=>{ if(document.hidden) A3.list.forEach(p=>{ if(p.play) p.toggle(); }); });
window.an3Debug=A3;
})();
/*AN3-END*/
