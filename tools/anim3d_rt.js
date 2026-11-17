/*AN3-BEGIN*/
/* 立体の動く図（an3）。外部ライブラリなしの小さな3D描画：地面は平らな多角形、建物と石垣は面、人と船は絵（いつもこちらを向く）。
   すべて「時刻 t の関数」で描くので、どこへでも飛べる。データは tools/anim3d.py がつくる（.an3 の data-an3）。 */
(function(){
"use strict";
const A3={list:[]};
const SKY0="#0b1222",SKY1="#24304f",SEA="#1a2742",SEA2="#22345a",LAND="#cdbd92",COAST="#8d7b52";
function ez(u){ return u<0?0:u>1?1:u<.5?2*u*u:1-Math.pow(-2*u+2,2)/2; }
function lerp(a,b,u){ return a+(b-a)*u; }
function cl(v,a,b){ return v<a?a:v>b?b:v; }
function inR(r,t){ return !r||(t>=r[0]&&t<=r[1]); }
function prog(r,t){ return !r?1:cl((t-r[0])/((r[1]-r[0])||1),0,1); }
function rnd(seed){ let s=seed*9301+49297; return ()=>{ s=(s*9301+49297)%233280; return s/233280; }; }
function kf(arr,t){ // [[t,a,b,...],...] → 値（イーズあり）
  if(t<=arr[0][0]) return arr[0].slice(1);
  for(let i=1;i<arr.length;i++) if(t<=arr[i][0]){ const a=arr[i-1],b=arr[i],u=ez((t-a[0])/((b[0]-a[0])||1)); return a.slice(1).map((v,k)=>lerp(v,b[k+1],u)); }
  return arr[arr.length-1].slice(1);
}
function camAt(S,t){ // [t,x,z,dist,pitch,yaw]（距離は対数で補間）
  const C=S.cam; let a=C[0],b=C[0],u=0;
  if(t>=C[C.length-1][0]){ a=b=C[C.length-1]; }
  else for(let i=1;i<C.length;i++) if(t<=C[i][0]){ a=C[i-1]; b=C[i]; u=ez((t-a[0])/((b[0]-a[0])||1)); break; }
  const d=Math.exp(lerp(Math.log(a[3]),Math.log(b[3]),u));
  // 距離が大きく変わるときは、注目点の移りを距離の変化に合わせる（ズームしながら横すべりしない）
  let w=u; const la=Math.log(a[3]),lb=Math.log(b[3]); if(Math.abs(lb-la)>1.5){ const ld=Math.log(d); w=cl((ld-la)/(lb-la),0,1); if(lb<la) w=1-cl((ld-lb)/(la-lb),0,1); }
  return {x:lerp(a[1],b[1],w),z:lerp(a[2],b[2],w),d,p:lerp(a[4],b[4],u),y:lerp(a[5],b[5],u)};
}
function pathLen(P){ let L=[0]; for(let i=1;i<P.length;i++) L.push(L[i-1]+Math.hypot(P[i][0]-P[i-1][0],P[i][1]-P[i-1][1])); return L; }
function pathAt(P,L,u){ const s=u*L[L.length-1]; for(let i=1;i<P.length;i++) if(s<=L[i]){ const v=(s-L[i-1])/((L[i]-L[i-1])||1); return [lerp(P[i-1][0],P[i][0],v),lerp(P[i-1][1],P[i][1],v),Math.atan2(P[i][1]-P[i-1][1],P[i][0]-P[i-1][0])]; } const n=P.length-1; return [P[n][0],P[n][1],0]; }

class Player{
  constructor(el,S){
    this.el=el; this.S=S; this.t=0; this.play=false; this.last=0; this.raf=0; this.vis=true;
    el.innerHTML=`<div class="an3-stage"><canvas></canvas><div class="an3-card"></div><div class="an3-year"><b></b><span></span></div><div class="an3-badge">▶▶ 早送り</div><div class="an3-cap"></div><button class="an3-btn" aria-label="再生">▶</button></div>`+
      `<div class="an3-bar"><div class="an3-prog"><i></i></div><div class="an3-chips">${(S.chips||[]).map((c,i)=>`<span data-i="${i}">${c[1]}</span>`).join("")}</div></div>`;
    this.cv=el.querySelector("canvas"); this.g=this.cv.getContext("2d");
    this.q=s=>el.querySelector(s);
    this.prep();
    const st=this.q(".an3-stage");
    st.addEventListener("click",()=>this.toggle());
    this.q(".an3-prog").addEventListener("click",e=>{ e.stopPropagation(); const r=e.currentTarget.getBoundingClientRect(); this.seek(cl((e.clientX-r.left)/r.width,0,1)*S.dur); });
    el.querySelectorAll(".an3-chips span").forEach(c=>c.addEventListener("click",e=>{ e.stopPropagation(); this.seek(S.chips[+c.dataset.i][0]); if(!this.play) this.toggle(); }));
    this.ro=new ResizeObserver(()=>{ this.size(); this.draw(); }); this.ro.observe(st);
    if("IntersectionObserver" in window){ this.io=new IntersectionObserver(es=>{ this.vis=es[0].isIntersecting; if(!this.vis&&this.play) this.toggle(); }); this.io.observe(el); }
    this.size(); this.draw();
  }
  prep(){ const S=this.S;
    for(const o of S.objs){
      if(o.path){ o._L=pathLen(o.path); }
      if(o.k==="path"){ o._L=pathLen(o.pts); }
      if(o.k==="wall"){ o._L=pathLen(o.pts); }
      if(o.line){ o._L=pathLen(o.line); }
      if(o.k==="crowd"||o.k==="fleet"){ const R=rnd(o.seed||1),pts=[];
        for(let i=0;i<o.n;i++){
          if(o.line){ pts.push([i/(Math.max(1,o.n-1)),0,R()]); continue; }
          if(o.form==="rows"){ const cols=Math.ceil(Math.sqrt(o.n*1.6)); const c=i%cols, r=Math.floor(i/cols); pts.push([(c-(cols-1)/2)*o.r*2/cols*1.6,r*o.r*0.45,R()]); continue; }
          const a=R()*Math.PI*2, d=Math.sqrt(R())*(o.r||0); pts.push([Math.cos(a)*d,Math.sin(a)*d*0.8,R()]); }
        o._p=pts; }
    }
  }
  size(){ const st=this.q(".an3-stage"), w=st.clientWidth, h=st.clientHeight, dpr=Math.min(window.devicePixelRatio||1,2);
    this.W=w; this.H=h; this.cv.width=Math.round(w*dpr); this.cv.height=Math.round(h*dpr); this.cv.style.width=w+"px"; this.cv.style.height=h+"px"; this.g.setTransform(dpr,0,0,dpr,0,0); }
  toggle(){ this.play=!this.play; if(this.play){ if(this.t>=this.S.dur-0.05) this.t=0; A3.list.forEach(p=>{ if(p!==this&&p.play) p.toggle(); }); this.last=performance.now(); this.loop(); } else cancelAnimationFrame(this.raf); this.ui(); }
  seek(t){ this.t=cl(t,0,this.S.dur); this.last=performance.now(); this.draw(); }
  loop(){ this.raf=requestAnimationFrame(now=>{ if(!this.play) return; this.t+=Math.min(0.1,(now-this.last)/1000); this.last=now;
      if(this.t>=this.S.dur){ this.t=this.S.dur; this.play=false; this.draw(); this.ui(); return; } this.draw(); this.loop(); }); }
  stop(){ this.play=false; cancelAnimationFrame(this.raf); if(this.ro) this.ro.disconnect(); if(this.io) this.io.disconnect(); }
  ui(){ const b=this.q(".an3-btn"); b.textContent=this.play?"":(this.t>=this.S.dur-0.05?"↻":"▶"); b.classList.toggle("hide",this.play); }

  // ── カメラ ──
  setCam(t){ const c=camAt(this.S,t), p=c.p*Math.PI/180, y=c.y*Math.PI/180;
    let sh=0; for(const f of this.S.fx) if(f.k==="storm"&&inR(f.on,t)) sh=c.d*0.004*Math.sin(t*37)*Math.min(1,(t-f.on[0])*2,(f.on[1]-t)*2);
    const fx=Math.cos(p)*Math.sin(y), fy=-Math.sin(p), fz=Math.cos(p)*Math.cos(y);
    this.e=[c.x-fx*c.d+sh, c.d*Math.sin(p), c.z-fz*c.d]; this.f=[fx,fy,fz];
    const r=[fz,0,-fx], rl=Math.hypot(r[0],r[2])||1; this.r=[r[0]/rl,0,r[2]/rl];
    const f=this.f, rr=this.r; this.u=[rr[1]*f[2]-rr[2]*f[1], rr[2]*f[0]-rr[0]*f[2], rr[0]*f[1]-rr[1]*f[0]];
    if(this.u[1]<0) this.u=this.u.map(v=>-v);
    this.F=(this.H*0.5)/Math.tan(26*Math.PI/180); this.near=c.d*0.01; this.cd=c.d; this.cam=c; }
  // world(x,z が地面、y が上) → カメラ座標
  tc(x,y,z){ const dx=x-this.e[0], dy=y-this.e[1], dz=z-this.e[2], r=this.r,u=this.u,f=this.f;
    return [dx*r[0]+dy*r[1]+dz*r[2], dx*u[0]+dy*u[1]+dz*u[2], dx*f[0]+dy*f[1]+dz*f[2]]; }
  sc(c){ return [this.W/2+c[0]*this.F/c[2], this.H*0.46-c[1]*this.F/c[2]]; }
  P(x,y,z){ const c=this.tc(x,y,z); return c[2]>this.near?[...this.sc(c),c[2]]:null; }
  poly(pts3){ // カメラ座標の多角形を手前の面で切ってから画面へ
    const n=this.near, out=[];
    for(let i=0;i<pts3.length;i++){ const a=pts3[(i+pts3.length-1)%pts3.length], b=pts3[i];
      const ai=a[2]>n, bi=b[2]>n;
      if(bi){ if(!ai){ const u=(n-a[2])/(b[2]-a[2]); out.push([lerp(a[0],b[0],u),lerp(a[1],b[1],u),n]); } out.push(b); }
      else if(ai){ const u=(n-a[2])/(b[2]-a[2]); out.push([lerp(a[0],b[0],u),lerp(a[1],b[1],u),n]); } }
    return out.map(c=>this.sc(c)); }

  draw(){ const g=this.g, W=this.W, H=this.H, S=this.S, t=this.t; if(!W) return;
    this.setCam(t);
    // 空と海
    const hz=this.P(this.e[0]+this.f[0]*1e5,0,this.e[2]+this.f[2]*1e5);
    const gr=g.createLinearGradient(0,0,0,H); gr.addColorStop(0,SKY0); gr.addColorStop(1,SKY1); g.fillStyle=gr; g.fillRect(0,0,W,H);
    const BIG=6e4, sea=[[-BIG,-BIG],[BIG,-BIG],[BIG,BIG],[-BIG,BIG]].map(q=>this.tc(this.e[0]+q[0],0,this.e[2]+q[1]));
    const sp=this.poly(sea); if(sp.length>2){ const top=hz?hz[1]:0; const sg=g.createLinearGradient(0,Math.max(0,top),0,H); sg.addColorStop(0,SEA2); sg.addColorStop(1,SEA); g.fillStyle=sg; this.fillP(sp); }
    // 陸
    g.fillStyle=LAND; g.strokeStyle=LAND; g.lineWidth=1; g.lineJoin="round";
    const coast=[];
    for(const R of S.ground){ const c=[]; for(let i=0;i<R.length;i+=2) c.push(this.tc(R[i],0,R[i+1]));
      let vis=false; for(const q of c) if(q[2]>this.near){ const s=this.sc(q); if(s[0]>-W&&s[0]<2*W&&s[1]>-H&&s[1]<2*H){ vis=true; break; } }
      if(!vis&&c.length<200) continue;
      const pp=this.poly(c); if(pp.length>2){ g.beginPath(); this.pathP(pp); g.fill(); g.stroke(); } }
    // 海岸線（県境は描かない）
    g.strokeStyle=COAST; g.lineWidth=1.1; g.beginPath();
    for(const R of (S.coast||[])){ let prev=null;
      for(let i=0;i<R.length;i+=2){ let c=this.tc(R[i],0,R[i+1]);
        if(prev){ let a=prev,b=c; if(a[2]>this.near||b[2]>this.near){
            if(a[2]<=this.near){ const u=(this.near-a[2])/(b[2]-a[2]); a=[lerp(a[0],b[0],u),lerp(a[1],b[1],u),this.near]; }
            if(b[2]<=this.near){ const u=(this.near-b[2])/(a[2]-b[2]); b=[lerp(b[0],a[0],u),lerp(b[1],a[1],u),this.near]; }
            const p=this.sc(a),q=this.sc(b); if(!((p[0]<0&&q[0]<0)||(p[0]>W&&q[0]>W)||(p[1]<0&&q[1]<0)||(p[1]>H&&q[1]>H))){ g.moveTo(p[0],p[1]); g.lineTo(q[0],q[1]); } } }
        prev=c; } }
    g.stroke();
    // 地面の上のもの（穴・線）
    for(const o of S.objs) if(o.k==="pit") this.pit(o,t);
    for(const o of S.objs) if(o.k==="path"&&inR(o.on,t)) this.path(o,t);
    // 地名
    this.labels(t);
    // 立つもの（奥から順に）
    const items=[];
    for(const o of S.objs){ if(!inR(o.on,t)) continue;
      if(o.k==="bldg") this.bldg(o,t,items);
      else if(o.k==="hill") this.hill(o,t,items);
      else if(o.k==="wall") this.wall(o,t,items);
      else if(o.k==="crowd") this.crowd(o,t,items);
      else if(o.k==="fleet") this.fleet(o,t,items);
      else if(o.k==="boom") this.boom(o,t,items); }
    items.sort((a,b)=>b.z-a.z); for(const it of items) it.d();
    for(const o of S.objs) if(o.k==="tag"&&inR(o.on,t)){ const q=this.P(o.at[0],0,o.at[1]); if(q) this.tag(q[0],q[1],o.s,prog([o.on[0],o.on[0]+0.4],t)*Math.min(1,(o.on[1]-t)/0.4)); }
    for(const o of S.objs) if(o.k==="crowd"&&o.tag&&inR(o.tagon,t)&&o._tagxy) this.tag(o._tagxy[0],o._tagxy[1],o.tag,prog([o.tagon[0],o.tagon[0]+0.4],t)*Math.min(1,(o.tagon[1]-t)/0.4));
    this.fx(t); this.texts(t);
    this.q(".an3-prog i").style.width=(100*t/S.dur)+"%";
  }
  pathP(pp){ const g=this.g; g.moveTo(pp[0][0],pp[0][1]); for(let i=1;i<pp.length;i++) g.lineTo(pp[i][0],pp[i][1]); g.closePath(); }
  fillP(pp){ const g=this.g; g.beginPath(); this.pathP(pp); g.fill(); }
  labels(t){ const g=this.g; g.textAlign="center"; g.textBaseline="middle";
    for(const L of this.S.labels){ if(L.on&&!inR(L.on,t)) continue; const d=this.cd; if(d<L.d[0]*0.6||d>L.d[1]*1.6) continue;
      let a=1; if(d<L.d[0]) a=(d-L.d[0]*0.6)/(L.d[0]*0.4); if(d>L.d[1]) a=1-(d-L.d[1])/(L.d[1]*0.6); if(L.on) a*=Math.min(1,(t-L.on[0])/0.5,(L.on[1]-t)/0.5);
      const q=this.P(L.at[0],0,L.at[1]); if(!q||a<=0) continue;
      g.globalAlpha=cl(a,0,1); g.font=`700 ${L.s.length>4?11:13}px ${A3.font}`; g.lineWidth=3; g.strokeStyle="rgba(20,26,44,.75)"; g.strokeText(L.s,q[0],q[1]); g.fillStyle="#f4ecd4"; g.fillText(L.s,q[0],q[1]); }
    g.globalAlpha=1; }
  tag(x,y,s,a){ if(a<=0) return; const g=this.g; g.globalAlpha=cl(a,0,1); g.font=`700 11px ${A3.font}`; const w=g.measureText(s).width+12;
    g.fillStyle="rgba(15,22,38,.86)"; g.strokeStyle="#d4bd82"; g.lineWidth=1; const yy=y-30;
    g.beginPath(); g.roundRect?g.roundRect(x-w/2,yy-10,w,20,5):g.rect(x-w/2,yy-10,w,20); g.fill(); g.stroke();
    g.beginPath(); g.moveTo(x,yy+10); g.lineTo(x,y-6); g.stroke();
    g.fillStyle="#f3e9cf"; g.textAlign="center"; g.textBaseline="middle"; g.fillText(s,x,yy+0.5); g.globalAlpha=1; }
  pit(o,t){ const r=kf(o.r,t)[0]; if(r<=0.5) return; const g=this.g, pts=[];
    for(let i=0;i<48;i++){ const a=i/48*Math.PI*2; pts.push(this.tc(o.at[0]+Math.cos(a)*r,0,o.at[1]+Math.sin(a)*r*0.85)); }
    const pp=this.poly(pts); if(pp.length<3) return;
    g.fillStyle="#0a0d16"; this.fillP(pp); g.strokeStyle="#e0b860"; g.lineWidth=2.5; g.shadowColor="#e0b860"; g.shadowBlur=12; g.beginPath(); this.pathP(pp); g.stroke(); g.shadowBlur=0; }
  path(o,t){ const u=prog(o.draw,t); if(u<=0) return; const g=this.g, P=o.pts, L=o._L, s=u*L[L.length-1];
    const pts=[]; for(let i=0;i<P.length;i++){ if(L[i]<=s) pts.push(P[i]); else { const v=(s-L[i-1])/(L[i]-L[i-1]); pts.push([lerp(P[i-1][0],P[i][0],v),lerp(P[i-1][1],P[i][1],v)]); break; } }
    const sp=pts.map(p=>this.P(p[0],0,p[1])).filter(Boolean); if(sp.length<2) return;
    g.strokeStyle=o.c; g.lineWidth=o.w; g.setLineDash([7,5]); g.lineDashOffset=-t*20; g.beginPath(); g.moveTo(sp[0][0],sp[0][1]); for(const q of sp) g.lineTo(q[0],q[1]); g.stroke(); g.setLineDash([]);
    const a=sp[sp.length-1], b=sp[sp.length-2], ang=Math.atan2(a[1]-b[1],a[0]-b[0]);
    g.fillStyle=o.c; g.beginPath(); g.moveTo(a[0]+Math.cos(ang)*7,a[1]+Math.sin(ang)*7); g.lineTo(a[0]+Math.cos(ang+2.5)*7,a[1]+Math.sin(ang+2.5)*7); g.lineTo(a[0]+Math.cos(ang-2.5)*7,a[1]+Math.sin(ang-2.5)*7); g.fill(); }
  // 面（建物・石垣）：法線で明るさを変え、裏の面は描かない
  face(pts,col,items){ const c=pts.map(p=>this.tc(p[0],p[1],p[2]));
    const a=pts[0],b=pts[1],d=pts[2]; const ux=b[0]-a[0],uy=b[1]-a[1],uz=b[2]-a[2], vx=d[0]-a[0],vy=d[1]-a[1],vz=d[2]-a[2];
    let nx=uy*vz-uz*vy, ny=uz*vx-ux*vz, nz=ux*vy-uy*vx; const nl=Math.hypot(nx,ny,nz)||1; nx/=nl; ny/=nl; nz/=nl;
    const cx=pts.reduce((s,p)=>s+p[0],0)/pts.length, cy=pts.reduce((s,p)=>s+p[1],0)/pts.length, cz=pts.reduce((s,p)=>s+p[2],0)/pts.length;
    if(nx*(this.e[0]-cx)+ny*(this.e[1]-cy)+nz*(this.e[2]-cz)<0) return;
    const L=0.55+0.45*Math.max(0,nx*-0.45+ny*0.8+nz*-0.4); const cc=this.tc(cx,cy,cz); if(cc[2]<=this.near) return;
    const pp=this.poly(c); if(pp.length<3) return;
    items.push({z:cc[2],d:()=>{ this.g.fillStyle=shade(col,L); this.fillP(pp); this.g.strokeStyle="rgba(0,0,0,.18)"; this.g.lineWidth=0.6; this.g.stroke(); }}); }
  box(x,z,w,d,h,y0,col,items){ const X0=x-w/2,X1=x+w/2,Z0=z-d/2,Z1=z+d/2,Y1=y0+h;
    this.face([[X0,Y1,Z0],[X0,Y1,Z1],[X1,Y1,Z1],[X1,Y1,Z0]],col,items);
    this.face([[X0,y0,Z0],[X0,Y1,Z0],[X1,Y1,Z0],[X1,y0,Z0]],col,items);
    this.face([[X1,y0,Z1],[X1,Y1,Z1],[X0,Y1,Z1],[X0,y0,Z1]],col,items);
    this.face([[X0,y0,Z1],[X0,Y1,Z1],[X0,Y1,Z0],[X0,y0,Z0]],col,items);
    this.face([[X1,y0,Z0],[X1,Y1,Z0],[X1,Y1,Z1],[X1,y0,Z1]],col,items); }
  bldg(o,t,items){ const [x,z]=o.at; this.box(x,z,o.w,o.d,o.h,0,o.c,items);
    const Y=o.h, T=o.h+o.roof, X0=x-o.w/2-o.w*0.08,X1=x+o.w/2+o.w*0.08,Z0=z-o.d/2-o.d*0.1,Z1=z+o.d/2+o.d*0.1;
    this.face([[X0,Y,Z0],[x-o.w*0.3,T,z],[x+o.w*0.3,T,z],[X1,Y,Z0]],o.r,items); this.face([[X1,Y,Z1],[x+o.w*0.3,T,z],[x-o.w*0.3,T,z],[X0,Y,Z1]],o.r,items);
    this.face([[X0,Y,Z1],[x-o.w*0.3,T,z],[X0,Y,Z0]],o.r,items); this.face([[X1,Y,Z0],[x+o.w*0.3,T,z],[X1,Y,Z1]],o.r,items); }
  hill(o,t,items){ const [x,z]=o.at, n=7, T=[x,o.h,z], R=rnd(o.at[0]*7+3), rr=[]; for(let i=0;i<n;i++) rr.push(o.r*(0.8+R()*0.4));
    for(let i=0;i<n;i++){ const a0=i/n*Math.PI*2, a1=(i+1)/n*Math.PI*2; this.face([[x+Math.cos(a0)*rr[i],0,z+Math.sin(a0)*rr[i]],T,[x+Math.cos(a1)*rr[(i+1)%n],0,z+Math.sin(a1)*rr[(i+1)%n]]],o.c,items); } }
  wall(o,t,items){ const u=prog(o.build,t), P=o.pts, L=o._L, s=u*L[L.length-1];
    for(let i=1;i<P.length;i++){ if(L[i-1]>=s) break; const e=Math.min(1,(s-L[i-1])/(L[i]-L[i-1]));
      const a=P[i-1], b=[lerp(P[i-1][0],P[i][0],e),lerp(P[i-1][1],P[i][1],e)]; const dx=b[0]-a[0],dz=b[1]-a[1],l=Math.hypot(dx,dz)||1, nx=-dz/l*o.th/2, nz=dx/l*o.th/2, h=o.h;
      const A=[a[0]-nx,a[1]-nz],B=[b[0]-nx,b[1]-nz],C=[b[0]+nx,b[1]+nz],D=[a[0]+nx,a[1]+nz];
      this.face([[A[0],h,A[1]],[D[0],h,D[1]],[C[0],h,C[1]],[B[0],h,B[1]]],o.c,items);
      this.face([[A[0],0,A[1]],[A[0],h,A[1]],[B[0],h,B[1]],[B[0],0,B[1]]],o.c,items);
      this.face([[C[0],0,C[1]],[C[0],h,C[1]],[D[0],h,D[1]],[D[0],0,D[1]]],o.c,items); } }
  crowdPos(o,t){ if(o.at) return kf(o.at,t); return [0,0]; }
  crowd(o,t,items){ const g=this.g; let [cx,cz]=this.crowdPos(o,t); const rise=o.rise?ez(prog(o.rise,t)):1, fade=o.fade?1-prog(o.fade,t):1;
    const jit=o.jit&&inR(o.jit,t)?1:0; const cheer=o.cheer&&inR(o.cheer,t)?1:0; let spread=1; if(o.spread&&t>o.spread[0]) spread=lerp(1,o.spread[1],prog([o.spread[0],o.spread[0]+1],t));
    let tagSet=false;
    for(let i=0;i<o._p.length;i++){ const pt=o._p[i]; let x,z;
      if(o.line){ const q=pathAt(o.line,o._L,pt[0]); x=q[0]-Math.sin(q[2])*o.lineOff; z=q[1]+Math.cos(q[2])*o.lineOff; }
      else { x=cx+pt[0]*spread; z=cz+pt[1]*spread; }
      if(jit){ x+=Math.sin(t*9+pt[2]*40)*o.h*0.25; z+=Math.cos(t*7+pt[2]*31)*o.h*0.25; }
      const hop=cheer?Math.abs(Math.sin(t*12+pt[2]*6))*o.h*0.35:0;
      const ry=-(1-rise)*o.h*1.2*(0.6+pt[2]*0.8);
      const f=this.P(x,Math.max(ry,ry)+hop,z); if(!f) continue;
      const hpx=o.h*this.F/f[2]; if(hpx<0.6) continue;
      if(o.tag&&!tagSet){ o._tagxy=[f[0],f[1]-hpx]; tagSet=true; }
      const vis=rise<1?cl((rise-pt[2]*0.4)/0.6,0,1):1;
      items.push({z:f[2],d:()=>person(g,f[0],f[1],hpx,o.c,o.flag,fade*vis)}); }
  }
  fleet(o,t,items){ const g=this.g; let u=prog(o.move,t);
    if(o.hold){ const T0=o.move[0],T1=o.move[1],h0=o.hold[0],h1=o.hold[1], run=(T1-T0)-(h1-h0); const el=t<h0?t-T0:t<h1?h0-T0:t-T0-(h1-h0); u=cl(el/run,0,1); u=ez(u); }
    else u=ez(u);
    const sink=o.sink?prog(o.sink,t):0, leave=o.leave?ez(prog(o.leave,t)):0;
    const q=pathAt(o.path,o._L,u);
    let cx=q[0], cz=q[1]; if(leave>0){ cx=lerp(cx,o.leaveTo[0],leave); cz=lerp(cz,o.leaveTo[1],leave); }
    for(let i=0;i<o._p.length;i++){ const pt=o._p[i]; const lag=(pt[2]-0.5)*o.r*0.6;
      const x=cx+pt[0]+Math.cos(q[2])*lag, z=cz+pt[1]+Math.sin(q[2])*lag;
      const bob=Math.sin(t*3+pt[2]*20)*o.sz*0.04; const sk=sink>0?cl((sink-pt[2]*0.5)*2,0,1):0;
      const f=this.P(x,bob-sk*o.sz*0.5,z); if(!f) continue; const s=Math.min(o.max||30,o.sz*this.F/f[2]); if(s<0.8) continue;
      const fd=o.fade?1-prog(o.fade,t):1; items.push({z:f[2],d:()=>ship(g,f[0],f[1],s,o.c,o.sail,(1-sk)*fd,sk*(pt[2]>0.5?1:-1)*0.9)}); } }
  boom(o,t,items){ const R=rnd(o.seed||1); for(const t0 of o.ts){ const a=R()*Math.PI*2, d=R()*o.sp; if(t<t0||t>t0+0.7) continue; const u=(t-t0)/0.7;
      const f=this.P(o.at[0]+Math.cos(a)*d,o.r*0.4,o.at[1]+Math.sin(a)*d); if(!f) continue; const s=o.r*this.F/f[2];
      items.push({z:f[2]-1,d:()=>{ const g=this.g; g.globalAlpha=1-u; g.fillStyle="#fff2c0"; g.beginPath(); g.arc(f[0],f[1],s*(0.3+u*0.9),0,7); g.fill();
        g.fillStyle="#f08a3a"; g.beginPath(); g.arc(f[0],f[1],s*(0.18+u*0.5),0,7); g.fill(); g.fillStyle="rgba(120,120,120,.6)"; g.beginPath(); g.arc(f[0]+s*0.3,f[1]-s*u,s*(0.3+u*0.6),0,7); g.fill(); g.globalAlpha=1; }}); } }
  fx(t){ const g=this.g, W=this.W, H=this.H; let badge=false;
    for(const f of this.S.fx){
      if(f.k==="speed"&&inR(f.on,t)){ badge=true; g.strokeStyle="rgba(255,255,255,.35)"; g.lineWidth=1.2; const R=rnd(Math.floor(t*20)); for(let i=0;i<26;i++){ const a=R()*Math.PI*2, r0=W*0.25+R()*W*0.2, r1=r0+W*0.4; g.beginPath(); g.moveTo(W/2+Math.cos(a)*r0,H/2+Math.sin(a)*r0); g.lineTo(W/2+Math.cos(a)*r1,H/2+Math.sin(a)*r1); g.stroke(); } }
      if(f.k==="flash"&&t>=f.t&&t<f.t+0.45){ g.fillStyle=`rgba(255,250,235,${(1-(t-f.t)/0.45)*0.9})`; g.fillRect(0,0,W,H); }
      if(f.k==="storm"&&inR(f.on,t)){ const a=Math.min(1,(t-f.on[0])/0.6,(f.on[1]-t)/0.6); g.fillStyle=`rgba(8,12,24,${0.5*a})`; g.fillRect(0,0,W,H);
        g.strokeStyle=`rgba(200,215,240,${0.55*a})`; g.lineWidth=1; const R=rnd(Math.floor(t*30)); g.beginPath(); for(let i=0;i<90;i++){ const x=R()*W*1.3-W*0.15, y=R()*H; g.moveTo(x,y); g.lineTo(x-7,y+18); } g.stroke();
        if(Math.sin(t*5.3)>0.97||Math.sin(t*3.1+1)>0.985){ g.fillStyle=`rgba(230,235,255,${0.35*a})`; g.fillRect(0,0,W,H); } } }
    this.q(".an3-badge").classList.toggle("on",badge); }
  texts(t){ const S=this.S; let cap=null,year=null,card=null;
    for(const x of S.text){ if(t<x.t||t>x.t+x.d) continue; if(x.k==="cap") cap=x; else if(x.k==="year") year=x; else if(x.k==="card") card=x; }
    const set=(sel,x,fill)=>{ const el=this.q(sel); const key=x?x.t+":"+x.s:""; if(el.dataset.k!==key){ el.dataset.k=key; if(x) fill(el,x); el.classList.remove("on"); void el.offsetWidth; if(x) el.classList.add("on"); } };
    set(".an3-cap",cap,(el,x)=>{ el.textContent=x.s; });
    set(".an3-year",year,(el,x)=>{ el.querySelector("b").textContent=x.s; el.querySelector("span").textContent=x.sub||""; });
    set(".an3-card",card,(el,x)=>{ el.textContent=x.s; }); }
}
function shade(hex,L){ const n=parseInt(hex.slice(1),16); const r=Math.min(255,Math.round(((n>>16)&255)*L)), g=Math.min(255,Math.round(((n>>8)&255)*L)), b=Math.min(255,Math.round((n&255)*L)); return `rgb(${r},${g},${b})`; }
// 人：胴は台形、頭は丸。旗を背負わせることもできる
function person(g,x,y,h,col,flag,a){ if(a<=0) return; g.globalAlpha=a; const w=h*0.46;
  g.fillStyle="rgba(0,0,0,.22)"; g.beginPath(); g.ellipse(x,y,w*0.55,w*0.18,0,0,7); g.fill();
  g.fillStyle=col; g.beginPath(); g.moveTo(x-w/2,y); g.lineTo(x-w*0.3,y-h*0.66); g.lineTo(x+w*0.3,y-h*0.66); g.lineTo(x+w/2,y); g.closePath(); g.fill();
  g.fillStyle=shade(col,0.75); g.beginPath(); g.moveTo(x+w*0.05,y); g.lineTo(x+w*0.08,y-h*0.66); g.lineTo(x+w*0.3,y-h*0.66); g.lineTo(x+w/2,y); g.closePath(); g.fill();
  g.fillStyle=shade(col,1.25); g.beginPath(); g.arc(x,y-h*0.8,h*0.15,0,7); g.fill();
  if(flag&&h>4){ g.strokeStyle="#2a2a2a"; g.lineWidth=Math.max(0.6,h*0.04); g.beginPath(); g.moveTo(x+w*0.2,y-h*0.5); g.lineTo(x+w*0.2,y-h*1.3); g.stroke(); g.fillStyle=flag; g.fillRect(x+w*0.2,y-h*1.3,h*0.28,h*0.36); }
  g.globalAlpha=1; }
// 船：船体と帆
function ship(g,x,y,s,col,sail,a,tilt){ if(a<=0) return; g.save(); g.globalAlpha=a; g.translate(x,y); g.rotate(tilt||0);
  g.fillStyle="rgba(0,0,0,.25)"; g.beginPath(); g.ellipse(0,0,s*0.55,s*0.12,0,0,7); g.fill();
  g.fillStyle=col; g.beginPath(); g.moveTo(-s*0.5,-s*0.16); g.lineTo(s*0.5,-s*0.2); g.lineTo(s*0.36,0); g.lineTo(-s*0.38,0); g.closePath(); g.fill();
  g.fillStyle=sail; g.fillRect(-s*0.16,-s*0.62,s*0.3,s*0.4); g.fillStyle=shade(sail,0.8); g.fillRect(-s*0.16,-s*0.62,s*0.3,s*0.06);
  g.restore(); g.globalAlpha=1; }

A3.font="'Hiragino Sans','Noto Sans JP',system-ui,sans-serif";
window.an3Mount=function(root){ A3.list.forEach(p=>p.stop()); A3.list=[];
  (root||document).querySelectorAll(".an3[data-an3]").forEach(el=>{ try{ A3.list.push(new Player(el,JSON.parse(el.getAttribute("data-an3")))); }catch(e){ console.error(e); } }); };
window.an3Debug=A3;
})();
/*AN3-END*/
