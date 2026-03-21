
# -*- coding: utf-8 -*-
import os

BASE = r"C:\Users\Jules\Desktop\GPS0\minijeux"

COMMON_CSS = """*{margin:0;padding:0;box-sizing:border-box;user-select:none;-webkit-user-select:none;touch-action:none}
body{overflow:hidden;width:100vw;height:100vh;font-family:system-ui,sans-serif}
canvas{position:fixed;inset:0;width:100%;height:100%}
#hud{position:fixed;top:0;left:0;right:0;height:50px;display:flex;align-items:center;justify-content:space-between;padding:0 14px;z-index:10;border-bottom:1px solid rgba(255,255,255,.12)}
#htimer{font-weight:bold;font-size:.92rem}
#btn-q{background:none;border:1px solid rgba(255,255,255,.2);border-radius:8px;color:rgba(255,255,255,.5);padding:4px 10px;font-size:.76rem;cursor:pointer}
#overlay,#results{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;z-index:20;padding:24px;text-align:center}
#results{display:none;z-index:30}
h2{font-size:1.35rem}p{font-size:.88rem;max-width:290px;line-height:1.5;opacity:.85}
.ti{display:flex;align-items:center;gap:8px;font-size:.82rem;opacity:.65}
.btn-go{border:none;border-radius:14px;color:#0A0A1A;font-weight:bold;font-size:1rem;padding:13px 30px;cursor:pointer;margin-top:6px}"""

SELFIE_JS = """const selfieImg=new Image();const sd=localStorage.getItem('gps0_avatar_selfie_base64');if(sd)selfieImg.src=sd;"""

MM_JS = """function mm(s){return String(Math.floor(s/60)).padStart(2,'0')+':'+String(Math.floor(s%60)).padStart(2,'0');}"""

# =============================================================================
# NIVEAU 5 — LUNE D'OMBRE (Ghost mode)
# =============================================================================
n5 = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover"><title>GPS0 - Lune d'Ombre</title><style>
""" + COMMON_CSS + r"""
body{background:#0a0014}#hud{background:rgba(10,0,20,.92);color:#C8A2C8}#htimer{color:#C8A2C8}
h2{color:#C8A2C8}p{color:rgba(220,180,255,.85)}.ti{color:rgba(200,162,200,.6)}.btn-go{background:linear-gradient(135deg,#C8A2C8,#9a72c8)}
#ghost-info{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);z-index:15;display:flex;flex-direction:column;align-items:center;gap:4px}
#ghost-label{color:rgba(200,162,200,.65);font-size:.78rem}
#ghost-bar-w{width:160px;height:8px;background:rgba(255,255,255,.1);border-radius:4px;overflow:hidden}
#ghost-bar{height:100%;background:linear-gradient(90deg,#C8A2C8,#aa44ff);border-radius:4px;transition:width .1s}
</style></head><body>
<canvas id="c"></canvas>
<div id="hud"><span id="htimer">3:00</span><span>&#x1F47B; Lune d'Ombre</span><button id="btn-q">Quitter</button></div>
<div id="ghost-info"><div id="ghost-label">MAINTENIR = Fant&#xF4;me (3s)</div><div id="ghost-bar-w"><div id="ghost-bar" style="width:100%"></div></div></div>
<div id="overlay" style="background:rgba(10,0,20,.93)">
  <h2>&#x1F47B; Lune d'Ombre</h2>
  <p>Des pi&#xe8;ges t'attendent ! Deviens fant&#xF4;me pour les traverser.</p>
  <div class="ti">&#x1F446; <span>MAINTENIR appuy&#xe9; = mode fant&#xF4;me (3 secondes)</span></div>
  <div class="ti">&#x23F1;&#xFE0F; <span>Cooldown 4s, 3 vies</span></div>
  <div class="ti">&#x2B50; <span>Zone secr&#xe8;te derri&#xe8;re un faux mur</span></div>
  <button class="btn-go" id="btn-start">Commencer !</button>
</div>
<div id="results" style="background:rgba(10,0,20,.95)"></div>
<script>
'use strict';
const C=document.getElementById('c'),X=C.getContext('2d');
let W=window.innerWidth,H=window.innerHeight;C.width=W;C.height=H;
""" + SELFIE_JS + r"""
const TOTAL=180,GHOST_MAX=3,GHOST_CD=4;
let started=false,done=false,poussieres=0,raf=null,elapsed=0,startTs=0,lastTs=0;
let lives=3,trapsHit=0,secretFound=false,touching=false;
let isGhost=false,ghostT=0,ghostCdT=0;
let px=80,py=0,vx=3,vy=0,camX=0;
const G=0.4,FLOOR=H-80;
function genTraps(){
  const t=[],types=['spike','laser','wall','spike','laser','wall','spike','wall'];
  let x=350;
  types.forEach((tp)=>{
    x+=190+Math.random()*130;
    if(tp==='spike')t.push({x,y:FLOOR-28,w:38,h:28,type:'spike'});
    else if(tp==='laser')t.push({x,y:H*0.15,w:12,h:FLOOR-H*0.15,type:'laser'});
    else t.push({x,y:FLOOR-H*0.4,w:26,h:H*0.4,type:'wall'});
  });
  t.push({x:1400,y:FLOOR-100,w:90,h:100,type:'secret'});
  return t;
}
const traps=genTraps();
const WORLD_END=traps[traps.length-2].x+280;
function draw(){
  X.clearRect(0,0,W,H);
  const bg=X.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,'#0a0014');bg.addColorStop(1,'#180030');
  X.fillStyle=bg;X.fillRect(0,0,W,H);
  for(let i=0;i<50;i++){X.fillStyle='rgba(200,162,200,.18)';X.beginPath();X.arc((i*137)%W,(i*89)%H,.7,0,Math.PI*2);X.fill();}
  X.fillStyle='#1a0030';X.fillRect(0,FLOOR,W,H-FLOOR);
  X.fillStyle='rgba(200,162,200,.3)';X.fillRect(0,FLOOR,W,2);
  traps.forEach(t=>{
    const sx=t.x-camX;if(sx>W+60||sx+t.w<-60)return;
    if(t.type==='secret'){X.fillStyle='rgba(180,0,255,.05)';X.fillRect(sx,t.y,t.w,t.h);return;}
    const col={spike:'#FF2244',laser:'rgba(200,0,255,.65)',wall:'#441a66'};
    X.fillStyle=col[t.type]||'#666';X.fillRect(sx,t.y,t.w,t.h);
    X.fillStyle='rgba(255,100,255,.4)';X.fillRect(sx,t.y,t.w,2);
  });
  const fx=WORLD_END-camX;
  X.strokeStyle='rgba(200,162,200,.7)';X.lineWidth=3;X.setLineDash([8,8]);
  X.beginPath();X.moveTo(fx,0);X.lineTo(fx,H);X.stroke();X.setLineDash([]);
  X.font='22px serif';X.textAlign='center';X.textBaseline='middle';X.fillText('\uD83D\uDE80',fx,H*0.25);
  const alp=isGhost?0.3:1;
  X.globalAlpha=alp;
  if(isGhost){X.shadowColor='rgba(200,162,200,.9)';X.shadowBlur=18;}
  X.fillStyle='#aaa';X.beginPath();X.ellipse(px,py+14,12,9,0,0,Math.PI*2);X.fill();
  X.fillStyle='rgba(200,162,200,.2)';X.beginPath();X.arc(px,py,15,0,Math.PI*2);X.fill();
  if(sd&&selfieImg.complete){X.save();X.beginPath();X.arc(px,py,13,0,Math.PI*2);X.clip();X.drawImage(selfieImg,px-13,py-13,26,26);X.restore();}
  else{X.font='17px serif';X.textAlign='center';X.textBaseline='middle';X.fillText('\uD83E\uDDD1\u200D\uD83D\uDE80',px,py);}
  X.globalAlpha=1;X.shadowBlur=0;
  const gbar=document.getElementById('ghost-bar'),glbl=document.getElementById('ghost-label');
  if(isGhost){gbar.style.width=(100*(1-ghostT/GHOST_MAX))+'%';gbar.style.background='linear-gradient(90deg,#C8A2C8,#aa44ff)';glbl.textContent='\uD83D\uDC7B Fant\xF4me actif !';}
  else if(ghostCdT>0){gbar.style.width=(100*(1-ghostCdT/GHOST_CD))+'%';gbar.style.background='rgba(100,100,100,.5)';glbl.textContent='\u23F3 Rechargement...';}
  else{gbar.style.width='100%';gbar.style.background='linear-gradient(90deg,#C8A2C8,#aa44ff)';glbl.textContent='MAINTENIR = Fant\xF4me (3s)';}
  X.font='15px serif';X.textAlign='left';X.textBaseline='middle';
  for(let i=0;i<lives;i++)X.fillText('\uD83D\uDC9C',8+i*26,H/2);
}
function tick(ts){
  if(!started||done)return;
  if(!startTs)startTs=ts;
  const dt=Math.min((ts-lastTs)/1000,0.05);lastTs=ts;
  elapsed=(ts-startTs)/1000;
  const rem=Math.max(0,TOTAL-elapsed);
  document.getElementById('htimer').textContent=mm(rem);
  if(rem<=0&&!done){done=true;_end(false);return;}
  if(touching&&ghostCdT<=0){isGhost=true;ghostT=Math.min(GHOST_MAX,ghostT+dt);if(ghostT>=GHOST_MAX){isGhost=false;ghostT=0;ghostCdT=GHOST_CD;}}
  else{isGhost=false;if(!touching)ghostT=Math.max(0,ghostT);}
  if(ghostCdT>0)ghostCdT=Math.max(0,ghostCdT-dt);
  vy+=G;py+=vy;
  if(py+18>=FLOOR){py=FLOOR-18;vy=0;}
  camX=Math.max(0,camX+vx);
  const wpx=px+camX;
  if(!isGhost){
    for(const t of traps){
      if(t.type==='secret'){if(wpx+12>t.x&&wpx-12<t.x+t.w&&py+18>t.y)secretFound=true;continue;}
      if(wpx+12>t.x&&wpx-12<t.x+t.w&&py+18>t.y&&py-18<t.y+t.h){
        trapsHit++;lives--;
        if(lives<=0){done=true;_end(false);return;}
        camX=Math.max(0,camX-200);break;
      }
    }
  }
  if(camX>=WORLD_END-px){done=true;_end(true);return;}
  draw();raf=requestAnimationFrame(tick);
}
""" + MM_JS + r"""
function _end(ok){
  done=true;cancelAnimationFrame(raf);
  const r=document.getElementById('results');r.style.display='flex';
  const noHit=trapsHit===0;
  poussieres=ok&&noHit&&secretFound?50:ok&&noHit?25:5;
  r.innerHTML=ok
    ?'<h2 style="color:#C8A2C8">\uD83D\uDE80 Sorti de l\'Ombre !</h2><p>'+(noHit?'\u2728 Sans toucher de pi\xe8ge ! ':'')+( secretFound?'\uD83C\uDF1F Zone secr\xe8te !':'')+'</p><p style="color:#C8A2C8;font-size:1.2rem">+'+poussieres+' \u2728 poussi\xe8res</p>'
    :'<h2 style="color:#FF6B6B">\uD83D\uDC80 Pi\xe9g\xe9 !</h2><p style="color:#C8A2C8">+5 \u2728 poussi\xe8res</p>';
  if(!ok)poussieres=5;
  setTimeout(()=>window.parent.postMessage({source:'gps0_minijeu',success:ok,niveau:5,poussieres},'*'),2200);
}
C.addEventListener('touchstart',e=>{e.preventDefault();touching=true;},{passive:false});
C.addEventListener('touchend',e=>{e.preventDefault();touching=false;if(isGhost){isGhost=false;ghostCdT=GHOST_CD;ghostT=0;}},{passive:false});
document.getElementById('btn-start').addEventListener('click',()=>{
  document.getElementById('overlay').style.display='none';
  py=FLOOR-18;started=true;lastTs=performance.now();raf=requestAnimationFrame(tick);
});
document.getElementById('btn-q').addEventListener('click',()=>{
  done=true;cancelAnimationFrame(raf);
  window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:5,poussieres:0},'*');
});
draw();
</script></body></html>"""

# =============================================================================
# NIVEAU 6 — LUNE DE FER (Magnet)
# =============================================================================
n6 = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover"><title>GPS0 - Lune de Fer</title><style>
""" + COMMON_CSS + r"""
body{background:#0a0a0a}#hud{background:rgba(10,10,10,.92);color:#aaa}#htimer{color:#ccc}
h2{color:#aaa}p{color:rgba(220,220,220,.85)}.ti{color:rgba(200,200,200,.6)}.btn-go{background:linear-gradient(135deg,#888,#444)}
#info-bar{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);color:rgba(200,200,200,.65);font-size:.8rem;z-index:15;background:rgba(0,0,0,.6);padding:4px 12px;border-radius:10px}
</style></head><body>
<canvas id="c"></canvas>
<div id="hud"><span id="htimer">3:00</span><span>&#x1F9F2; Lune de Fer</span><button id="btn-q">Quitter</button></div>
<div id="info-bar">TAP sur un bloc = l'attirer</div>
<div id="overlay" style="background:rgba(10,10,10,.93)">
  <h2>&#x1F9F2; Lune de Fer</h2>
  <p>Des blocs m&#xe9;talliques flottent dans l'espace. Utilise ton aimant !</p>
  <div class="ti">&#x1F446; <span>TAP sur un bloc = l'attirer vers toi</span></div>
  <div class="ti">&#x1F4A5; <span>Blocs ROUGES = pi&#xe9;g&#xe9;s ! Ils explosent !</span></div>
  <div class="ti">&#x2B50; <span>Attire TOUS les blocs bleus pour gagner</span></div>
  <button class="btn-go" id="btn-start">Commencer !</button>
</div>
<div id="results" style="background:rgba(10,10,10,.95)"></div>
<script>
'use strict';
const C=document.getElementById('c'),X=C.getContext('2d');
let W=window.innerWidth,H=window.innerHeight;C.width=W;C.height=H;
""" + SELFIE_JS + r"""
const TOTAL=180;
let started=false,done=false,poussieres=0,raf=null,elapsed=0,startTs=0,lastTs=0;
let lives=3,blueCollected=0,secretFound=false;
const PLAYER_X=W/2,PLAYER_Y=H*0.8;
const ATTRACT_SPEED=2.5, COLLECT_DIST=40;
function genBlocks(){
  const bs=[];
  const positions=[
    {x:W*0.15,y:H*0.15},{x:W*0.45,y:H*0.12},{x:W*0.75,y:H*0.18},
    {x:W*0.1,y:H*0.38},{x:W*0.5,y:H*0.33},{x:W*0.85,y:H*0.4},
    {x:W*0.25,y:H*0.58},{x:W*0.6,y:H*0.55},{x:W*0.9,y:H*0.22},
  ];
  positions.forEach((p,i)=>{
    bs.push({x:p.x,y:p.y,vx:(Math.random()-.5)*0.5,vy:(Math.random()-.5)*0.5,
      trapped:i===3||i===6,collected:false,attracting:false,size:28,secret:i===8});
  });
  return bs;
}
let blocks=genBlocks();
const BLUE_TOTAL=blocks.filter(b=>!b.trapped).length;
let magnetBeam=null,beamT=0;

function draw(){
  X.clearRect(0,0,W,H);
  X.fillStyle='#050508';X.fillRect(0,0,W,H);
  for(let i=0;i<60;i++){X.fillStyle='rgba(180,180,220,.2)';X.beginPath();X.arc((i*173)%W,(i*97)%H,.8,0,Math.PI*2);X.fill();}
  // Magnet beam
  if(magnetBeam){
    const t=Date.now()/200;
    X.strokeStyle='rgba(100,200,255,'+(0.5+Math.sin(t)*0.3)+')';
    X.lineWidth=3;X.setLineDash([8,6]);
    X.beginPath();X.moveTo(PLAYER_X,PLAYER_Y);X.lineTo(magnetBeam.x,magnetBeam.y);X.stroke();
    X.setLineDash([]);
  }
  // Blocks
  blocks.forEach(b=>{
    if(b.collected)return;
    const col=b.trapped?'#cc1122':b.secret?'#FFD700':'#4488cc';
    const glow=X.createRadialGradient(b.x,b.y,2,b.x,b.y,b.size+8);
    glow.addColorStop(0,b.trapped?'rgba(255,50,0,.3)':b.secret?'rgba(255,220,0,.4)':'rgba(80,160,255,.3)');
    glow.addColorStop(1,'transparent');
    X.fillStyle=glow;X.beginPath();X.arc(b.x,b.y,b.size+8,0,Math.PI*2);X.fill();
    X.fillStyle=col;X.beginPath();X.roundRect(b.x-b.size/2,b.y-b.size/2,b.size,b.size,5);X.fill();
    if(b.attracting){X.strokeStyle='rgba(255,255,100,.8)';X.lineWidth=2;X.beginPath();X.arc(b.x,b.y,b.size/2+6,0,Math.PI*2);X.stroke();}
    if(b.trapped){X.font='14px serif';X.textAlign='center';X.textBaseline='middle';X.fillText('\uD83D\uDCA5',b.x,b.y-b.size/2-10);}
    if(b.secret){X.font='11px serif';X.fillText('\u2B50',b.x,b.y-b.size/2-10);}
  });
  // Player (cosmonaute with magnet)
  X.fillStyle='#888';X.beginPath();X.ellipse(PLAYER_X,PLAYER_Y+14,13,10,0,0,Math.PI*2);X.fill();
  if(sd&&selfieImg.complete){X.save();X.beginPath();X.arc(PLAYER_X,PLAYER_Y,13,0,Math.PI*2);X.clip();X.drawImage(selfieImg,PLAYER_X-13,PLAYER_Y-13,26,26);X.restore();}
  else{X.font='18px serif';X.textAlign='center';X.textBaseline='middle';X.fillText('\uD83E\uDDD1\u200D\uD83D\uDE80',PLAYER_X,PLAYER_Y);}
  // Magnet icon
  X.font='24px serif';X.textAlign='center';X.textBaseline='middle';X.fillText('\uD83E\uDDF2',PLAYER_X+20,PLAYER_Y-20);
  // Progress
  X.fillStyle='rgba(255,255,255,.7)';X.font='bold 14px system-ui';X.textAlign='left';X.textBaseline='top';
  X.fillText(blueCollected+'/'+BLUE_TOTAL+' blocs',10,60);
  for(let i=0;i<lives;i++){X.font='14px serif';X.fillText('\uD83E\uDE9B',8+i*22,H/2);}
}
function tick(ts){
  if(!started||done)return;
  if(!startTs)startTs=ts;
  const dt=Math.min((ts-lastTs)/1000,0.05);lastTs=ts;
  elapsed=(ts-startTs)/1000;
  const rem=Math.max(0,TOTAL-elapsed);
  document.getElementById('htimer').textContent=mm(rem);
  if(rem<=0&&!done){done=true;_end(blueCollected===BLUE_TOTAL);return;}
  // Move blocks (float)
  blocks.forEach(b=>{
    if(b.collected)return;
    if(b.attracting){
      const dx=PLAYER_X-b.x,dy=PLAYER_Y-b.y,d=Math.sqrt(dx*dx+dy*dy);
      if(d<COLLECT_DIST){
        b.collected=true;b.attracting=false;magnetBeam=null;
        if(b.trapped){lives--;if(lives<=0){done=true;_end(false);return;}}
        else{blueCollected++;if(b.secret)secretFound=true;}
        if(blueCollected===BLUE_TOTAL){done=true;_end(true);return;}
      }else{b.x+=dx/d*ATTRACT_SPEED;b.y+=dy/d*ATTRACT_SPEED;}
    }else{
      b.x+=b.vx;b.y+=b.vy;
      if(b.x<20||b.x>W-20)b.vx*=-1;
      if(b.y<60||b.y>H*0.72)b.vy*=-1;
    }
  });
  draw();raf=requestAnimationFrame(tick);
}
""" + MM_JS + r"""
function _end(ok){
  done=true;cancelAnimationFrame(raf);
  const r=document.getElementById('results');r.style.display='flex';
  const all=blueCollected===BLUE_TOTAL;
  poussieres=all&&secretFound?50:all?25:blueCollected>0?10:5;
  r.innerHTML=ok
    ?'<h2 style="color:#4488cc">\uD83E\uDDF2 Tout attir\xe9 !</h2><p>'+(secretFound?'\uD83C\uDF1F Bloc secret !':'')+'</p><p style="color:#4FC3F7;font-size:1.2rem">+'+poussieres+' \u2728 poussi\xe8res</p>'
    :'<h2 style="color:#FF6B6B">\uD83D\uDCA5 '+(lives<=0?'Blocs pi\xe9g\xe9s !':'Temps!')+'</h2><p style="color:#4FC3F7">+'+poussieres+' \u2728</p>';
  setTimeout(()=>window.parent.postMessage({source:'gps0_minijeu',success:ok||blueCollected>0,niveau:6,poussieres},'*'),2200);
}
C.addEventListener('touchstart',e=>{
  e.preventDefault();if(!started)return;
  const tx=e.touches[0].clientX,ty=e.touches[0].clientY;
  let best=null,bestD=80;
  blocks.forEach(b=>{if(b.collected||b.attracting)return;const d=Math.sqrt((tx-b.x)**2+(ty-b.y)**2);if(d<bestD){bestD=d;best=b;}});
  if(best){blocks.forEach(b=>b.attracting=false);best.attracting=true;magnetBeam=best;}
},{passive:false});
document.getElementById('btn-start').addEventListener('click',()=>{
  document.getElementById('overlay').style.display='none';started=true;lastTs=performance.now();raf=requestAnimationFrame(tick);
});
document.getElementById('btn-q').addEventListener('click',()=>{
  done=true;cancelAnimationFrame(raf);window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:6,poussieres:0},'*');
});
draw();
</script></body></html>"""

# =============================================================================
# NIVEAU 7 — LUNE DE TEMPÊTE (Wind runner)
# =============================================================================
n7 = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover"><title>GPS0 - Lune de Tempête</title><style>
""" + COMMON_CSS + r"""
body{background:#080818}#hud{background:rgba(8,8,24,.92);color:#4FC3F7}#htimer{color:#4FC3F7}
h2{color:#4FC3F7}p{color:rgba(180,220,255,.85)}.ti{color:rgba(100,180,255,.65)}.btn-go{background:linear-gradient(135deg,#4FC3F7,#1a6fa0)}
#wind-alert{position:fixed;top:60px;left:0;right:0;text-align:center;font-size:1.1rem;font-weight:bold;color:#FF6B6B;z-index:15;opacity:0;transition:opacity .3s;pointer-events:none}
</style></head><body>
<canvas id="c"></canvas>
<div id="hud"><span id="htimer">3:00</span><span>&#x1F32A;&#xFE0F; Lune de Temp&#xEA;te</span><button id="btn-q">Quitter</button></div>
<div id="wind-alert">&#x1F4A8; RAFALE ! Contr&#xF4;les invers&#xe9;s !</div>
<div id="overlay" style="background:rgba(8,8,24,.93)">
  <h2>&#x1F32A;&#xFE0F; Lune de Temp&#xEA;te</h2>
  <p>Le vent souffle de partout ! Course contre la temp&#xEA;te !</p>
  <div class="ti">&#x1F446; <span>TAP = sauter (attention aux rafales !)</span></div>
  <div class="ti">&#x1F4A8; <span>Rafale = le saut va dans l'autre sens !</span></div>
  <div class="ti">&#x1F90F; <span>Ne tombe pas dans les pr&#xe9;cipices</span></div>
  <button class="btn-go" id="btn-start">Commencer !</button>
</div>
<div id="results" style="background:rgba(8,8,24,.95)"></div>
<script>
'use strict';
const C=document.getElementById('c'),X=C.getContext('2d');
let W=window.innerWidth,H=window.innerHeight;C.width=W;C.height=H;
""" + SELFIE_JS + r"""
const TOTAL=180,VX=3;
let started=false,done=false,poussieres=0,raf=null,elapsed=0,startTs=0,lastTs=0;
let lives=3,fell=0,secretFound=false;
let px=80,py=0,vy=0,camX=0;
const G=0.42,JUMP=-11,FLOOR=H-75;
let windActive=false,windT=0,windInterval=7,windDur=0;
let particles=[];
// Platforms
function genPlatforms(){
  const ps=[];
  ps.push({x:0,y:FLOOR,w:300});
  let x=330;
  const gaps=[360,700,1100,1550,2080,2690,3390,4180];
  let last=300;
  gaps.forEach(g=>{
    ps.push({x:last+36,y:FLOOR,w:g-last-36+Math.round(Math.random()*60-30)});
    last=g+100+Math.round(Math.random()*60);
  });
  ps.push({x:last+36,y:FLOOR,w:600});
  // secret elevated platform
  ps.push({x:1300,y:FLOOR-90,w:70,secret:true});
  return ps;
}
const plats=genPlatforms();
const WORLD_END=plats[plats.length-2].x+plats[plats.length-2].w;
function onPlat(){
  const wx=px+camX;
  return plats.some(p=>wx>p.x&&wx<p.x+p.w&&Math.abs(py-(p.y-18))<8);
}
function landY(){
  const wx=px+camX;
  for(const p of plats)if(wx>p.x&&wx<p.x+p.w)return p.y;
  return null;
}
const windAlert=document.getElementById('wind-alert');
function draw(){
  X.clearRect(0,0,W,H);
  const bg=X.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,'#080818');bg.addColorStop(1,'#0c1030');
  X.fillStyle=bg;X.fillRect(0,0,W,H);
  for(let i=0;i<50;i++){X.fillStyle='rgba(150,200,255,.18)';X.beginPath();X.arc((i*173)%W,(i*89)%H,.8,0,Math.PI*2);X.fill();}
  // Wind particles
  if(windActive){
    particles.forEach(p=>{X.fillStyle='rgba(100,200,255,'+(p.a*.5)+')';X.beginPath();X.arc(p.x,p.y,p.s,0,Math.PI*2);X.fill();});
  }
  // Platforms
  plats.forEach(p=>{
    const sx=p.x-camX;if(sx>W+60||sx+p.w<-60)return;
    if(p.secret){X.fillStyle=secretFound?'rgba(255,220,100,.4)':'rgba(100,180,255,.07)';X.fillRect(sx,p.y-10,p.w,10);return;}
    const pg=X.createLinearGradient(0,p.y-10,0,p.y+6);
    pg.addColorStop(0,'rgba(80,130,180,.7)');pg.addColorStop(1,'rgba(40,80,130,.4)');
    X.fillStyle=pg;X.fillRect(sx,p.y-10,p.w,10);
    X.fillStyle='rgba(150,200,255,.8)';X.fillRect(sx,p.y-10,p.w,2);
  });
  // Finish
  const fx=WORLD_END-camX;
  X.strokeStyle='rgba(100,255,100,.7)';X.lineWidth=3;X.setLineDash([8,6]);
  X.beginPath();X.moveTo(fx,0);X.lineTo(fx,H);X.stroke();X.setLineDash([]);
  X.font='22px serif';X.textAlign='center';X.textBaseline='middle';X.fillText('\uD83C\uDFC1',fx,H*0.25);
  // Wind direction arrow
  if(windActive){
    X.font='bold 28px serif';X.fillStyle='rgba(255,150,0,.8)';X.textAlign='center';X.fillText('\uD83D\uDCA8',W/2,H*0.18);
  }
  // Cosmonaute (tilt in wind)
  X.save();
  if(windActive){X.translate(px,py);X.rotate(windActive?(-0.25):0);X.translate(-px,-py);}
  X.fillStyle='#7ab';X.beginPath();X.ellipse(px,py+14,12,9,0,0,Math.PI*2);X.fill();
  if(sd&&selfieImg.complete){X.save();X.beginPath();X.arc(px,py,13,0,Math.PI*2);X.clip();X.drawImage(selfieImg,px-13,py-13,26,26);X.restore();}
  else{X.font='17px serif';X.textAlign='center';X.textBaseline='middle';X.fillText('\uD83E\uDDD1\u200D\uD83D\uDE80',px,py);}
  X.restore();
  for(let i=0;i<lives;i++){X.font='14px serif';X.textAlign='left';X.textBaseline='middle';X.fillText('\u2764\uFE0F',8+i*24,H/2);}
}
function tick(ts){
  if(!started||done)return;
  if(!startTs)startTs=ts;
  const dt=Math.min((ts-lastTs)/1000,0.05);lastTs=ts;
  elapsed=(ts-startTs)/1000;
  const rem=Math.max(0,TOTAL-elapsed);
  document.getElementById('htimer').textContent=mm(rem);
  if(rem<=0&&!done){done=true;_end(fell===0);return;}
  // Wind
  windT+=dt;
  if(!windActive&&windT>windInterval){windActive=true;windT=0;windDur=3+Math.random()*2;
    windAlert.style.opacity='1';particles=Array.from({length:20},()=>({x:Math.random()*W,y:Math.random()*H,s:2+Math.random()*2,a:0.5+Math.random()*0.5,vx:-3-Math.random()*2,vy:(Math.random()-.5)*2}));}
  if(windActive){
    windDur-=dt;particles.forEach(p=>{p.x+=p.vx;if(p.x<-10)p.x=W+10;p.y+=p.vy;});
    if(windDur<0){windActive=false;windT=0;windInterval=6+Math.random()*4;windAlert.style.opacity='0';}
  }
  vy+=G;py+=vy;
  const ly=landY();
  if(ly!=null&&py+18>=ly-8&&vy>=0){
    py=ly-18;vy=0;
    const wx=px+camX;if(plats.some(p=>p.secret&&wx>p.x&&wx<p.x+p.w))secretFound=true;
  }else if(ly===null&&py>H+60){
    fell++;lives--;
    if(lives<=0){done=true;_end(false);return;}
    px=80;py=FLOOR-18;vy=0;camX=Math.max(0,camX-300);
  }
  camX=Math.max(0,camX+VX);
  if(camX>=WORLD_END-px){done=true;_end(true);return;}
  draw();raf=requestAnimationFrame(tick);
}
""" + MM_JS + r"""
function _end(ok){
  done=true;cancelAnimationFrame(raf);
  const r=document.getElementById('results');r.style.display='flex';
  const noFall=fell===0;
  poussieres=ok&&noFall&&secretFound?50:ok&&noFall?25:5;
  r.innerHTML=ok
    ?'<h2 style="color:#4FC3F7">\uD83C\uDFC1 Arriv\xe9e !</h2><p>'+(noFall?'\u2728 Sans tomber ! ':'')+( secretFound?'\uD83C\uDF1F Zone cach\xe9e !':'')+'</p><p style="color:#4FC3F7;font-size:1.2rem">+'+poussieres+' \u2728</p>'
    :'<h2 style="color:#FF6B6B">\uD83D\uDCA8 Emport\xe9 par le vent !</h2><p style="color:#4FC3F7">+5 \u2728</p>';
  if(!ok)poussieres=5;
  setTimeout(()=>window.parent.postMessage({source:'gps0_minijeu',success:ok,niveau:7,poussieres},'*'),2200);
}
C.addEventListener('touchstart',e=>{
  e.preventDefault();if(!started)return;
  // Jump (inverted if wind)
  if(onPlat()||Math.abs(py-(landY()||FLOOR)+18)<20)vy=windActive?Math.abs(JUMP):JUMP;
},{passive:false});
document.getElementById('btn-start').addEventListener('click',()=>{
  document.getElementById('overlay').style.display='none';
  py=FLOOR-18;started=true;lastTs=performance.now();raf=requestAnimationFrame(tick);
});
document.getElementById('btn-q').addEventListener('click',()=>{
  done=true;cancelAnimationFrame(raf);window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:7,poussieres:0},'*');
});
draw();
</script></body></html>"""

# =============================================================================
# NIVEAU 8 — LUNE DE CRISTAL (Crystals)
# =============================================================================
n8 = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover"><title>GPS0 - Lune de Cristal</title><style>
""" + COMMON_CSS + r"""
body{background:#02040e}#hud{background:rgba(2,4,14,.92);color:#69CCFF}#htimer{color:#69CCFF}
h2{color:#69CCFF}p{color:rgba(180,240,255,.85)}.ti{color:rgba(100,200,255,.65)}.btn-go{background:linear-gradient(135deg,#69CCFF,#2266aa);color:#02040e}
#crystal-info{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);font-size:.82rem;color:rgba(100,200,255,.7);z-index:15;background:rgba(2,4,14,.75);padding:4px 12px;border-radius:10px}
</style></head><body>
<canvas id="c"></canvas>
<div id="hud"><span id="htimer">3:00</span><span>&#x1F48E; Lune de Cristal</span><button id="btn-q">Quitter</button></div>
<div id="crystal-info">TAP rapide pour casser les cristaux !</div>
<div id="overlay" style="background:rgba(2,4,14,.93)">
  <h2>&#x1F48E; Lune de Cristal</h2>
  <p>Casse les cristaux pour activer les plateformes — dans le bon ordre !</p>
  <div class="ti">&#x1F446; <span>TAP rapide sur un cristal = l'endommager</span></div>
  <div class="ti">&#x1F525; <span>Cristaux ROUGES = pi&#xe9;g&#xe9;s, explosent !</span></div>
  <div class="ti">&#x2B50; <span>Cristal dor&#xe9; secret quelque part</span></div>
  <button class="btn-go" id="btn-start">Commencer !</button>
</div>
<div id="results" style="background:rgba(2,4,14,.95)"></div>
<script>
'use strict';
const C=document.getElementById('c'),X=C.getContext('2d');
let W=window.innerWidth,H=window.innerHeight;C.width=W;C.height=H;
""" + SELFIE_JS + r"""
const TOTAL=180;
let started=false,done=false,poussieres=0,raf=null,elapsed=0,startTs=0,lastTs=0;
let lives=3,broken=0,secretFound=false;
let lastTap=0,combo=0;
// Crystals grid
function genCrystals(){
  const cs=[];
  const COLS=3,ROWS=3;
  for(let r=0;r<ROWS;r++){
    for(let c=0;c<COLS;c++){
      const i=r*COLS+c;
      const cx=W*(0.2+c*0.28),cy=H*(0.2+r*0.22);
      cs.push({x:cx,y:cy,hp:i===4?8:5,maxHp:i===4?8:5,broken:false,
        trapped:i===1||i===7,gold:i===8,order:i+1,
        flash:0,shake:0});
    }
  }
  return cs;
}
const crystals=genCrystals();
const TOTAL_BREAKABLE=crystals.filter(c=>!c.trapped).length-1; // not counting secret gold
const PLATFORM_Y=H*0.85;
let platforms=[];
function draw(){
  X.clearRect(0,0,W,H);
  const bg=X.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,'#02040e');bg.addColorStop(1,'#040820');
  X.fillStyle=bg;X.fillRect(0,0,W,H);
  for(let i=0;i<60;i++){X.fillStyle='rgba(100,200,255,.15)';X.beginPath();X.arc((i*173)%W,(i*89)%H,.8,0,Math.PI*2);X.fill();}
  // Platforms activated by crystals
  for(let i=0;i<broken;i++){
    const px2=W*(0.1+i*0.08),py2=PLATFORM_Y;
    X.fillStyle='rgba(100,200,255,.5)';X.fillRect(px2,py2,60,8);
  }
  // Exit platform
  if(broken>=TOTAL_BREAKABLE){
    X.fillStyle='rgba(100,255,100,.7)';X.fillRect(W*0.75,PLATFORM_Y-80,80,10);
    X.font='18px serif';X.textAlign='center';X.textBaseline='bottom';X.fillText('\uD83D\uDE80',W*0.75+40,PLATFORM_Y-82);
  }
  // Crystals
  crystals.forEach(cr=>{
    if(cr.broken)return;
    const ox=cr.shake?(Math.random()*6-3):0,oy=cr.shake?(Math.random()*6-3):0;
    // Glow
    const col=cr.trapped?'#FF2244':cr.gold?'#FFD700':'#4488FF';
    const gc=X.createRadialGradient(cr.x+ox,cr.y+oy,4,cr.x+ox,cr.y+oy,32);
    gc.addColorStop(0,cr.trapped?'rgba(255,50,50,.35)':cr.gold?'rgba(255,200,0,.4)':'rgba(80,160,255,.35)');
    gc.addColorStop(1,'transparent');
    X.fillStyle=gc;X.beginPath();X.arc(cr.x+ox,cr.y+oy,32,0,Math.PI*2);X.fill();
    // Crystal body (hexagon)
    X.fillStyle=cr.flash>0?(cr.trapped?'#ff8888':cr.gold?'#fff':'#aaddff'):col;
    const sz=24*(cr.hp/cr.maxHp);
    X.save();X.translate(cr.x+ox,cr.y+oy);
    X.beginPath();
    for(let a=0;a<6;a++){X.lineTo(Math.cos(a*Math.PI/3)*sz,Math.sin(a*Math.PI/3)*sz);}
    X.closePath();X.fill();
    // HP bar
    X.fillStyle='rgba(0,0,0,.4)';X.fillRect(-sz,-sz-12,sz*2,6);
    X.fillStyle=cr.trapped?'#FF2244':cr.gold?'#FFD700':'#69CCFF';
    X.fillRect(-sz,-sz-12,sz*2*(cr.hp/cr.maxHp),6);
    X.restore();
    // Label
    X.fillStyle='rgba(255,255,255,.5)';X.font='11px system-ui';X.textAlign='center';X.textBaseline='top';
    X.fillText(cr.trapped?'PIEGE':cr.gold?'\u2B50 SECRET':'#'+cr.order,cr.x,cr.y+sz+6);
    // Tap hint
    X.fillStyle='rgba(150,220,255,.4)';X.font='10px system-ui';X.fillText('TAP',cr.x,cr.y+sz+20);
    if(cr.flash>0)cr.flash--;if(cr.shake>0)cr.shake--;
  });
  // Player
  const ppx=W*0.5,ppy=PLATFORM_Y-30;
  if(sd&&selfieImg.complete){X.save();X.beginPath();X.arc(ppx,ppy,13,0,Math.PI*2);X.clip();X.drawImage(selfieImg,ppx-13,ppy-13,26,26);X.restore();}
  else{X.font='18px serif';X.textAlign='center';X.textBaseline='middle';X.fillText('\uD83E\uDDD1\u200D\uD83D\uDE80',ppx,ppy);}
  // Score
  X.fillStyle='rgba(100,200,255,.8)';X.font='bold 13px system-ui';X.textAlign='left';X.textBaseline='top';
  X.fillText(broken+'/'+TOTAL_BREAKABLE+' cristaux bris\xe9s',10,60);
  for(let i=0;i<lives;i++){X.font='14px serif';X.fillText('\uD83D\uDC99',8+i*24,H/2);}
}
function tick(ts){
  if(!started||done)return;
  if(!startTs)startTs=ts;
  const dt=Math.min((ts-lastTs)/1000,0.05);lastTs=ts;
  elapsed=(ts-startTs)/1000;
  const rem=Math.max(0,TOTAL-elapsed);
  document.getElementById('htimer').textContent=mm(rem);
  if(rem<=0&&!done){done=true;_end(broken>=TOTAL_BREAKABLE);return;}
  draw();raf=requestAnimationFrame(tick);
}
""" + MM_JS + r"""
function _end(ok){
  done=true;cancelAnimationFrame(raf);
  const r=document.getElementById('results');r.style.display='flex';
  const all=broken>=TOTAL_BREAKABLE;
  poussieres=all&&secretFound?50:all?25:broken>=3?10:5;
  r.innerHTML=(ok||all)
    ?'<h2 style="color:#69CCFF">\uD83D\uDC8E Tous bris\xe9s !</h2><p>'+(secretFound?'\uD83C\uDF1F Cristal dor\xe9 !':'')+'</p><p style="color:#69CCFF;font-size:1.2rem">+'+poussieres+' \u2728</p>'
    :'<h2 style="color:#FF6B6B">&#x1F4A5; '+broken+' cristaux bris\xe9s</h2><p style="color:#69CCFF">+'+poussieres+' \u2728</p>';
  setTimeout(()=>window.parent.postMessage({source:'gps0_minijeu',success:ok||broken>=3,niveau:8,poussieres},'*'),2200);
}
C.addEventListener('touchstart',e=>{
  e.preventDefault();if(!started)return;
  const tx=e.touches[0].clientX,ty=e.touches[0].clientY;
  let best=null,bestD=60;
  crystals.forEach(cr=>{if(cr.broken)return;const d=Math.sqrt((tx-cr.x)**2+(ty-cr.y)**2);if(d<bestD){bestD=d;best=cr;}});
  if(!best)return;
  best.hp--;best.flash=4;best.shake=2;
  if(best.hp<=0){
    best.broken=true;
    if(best.trapped){lives--;if(lives<=0){done=true;_end(false);return;}}
    else{broken++;if(best.gold)secretFound=true;}
    if(broken>=TOTAL_BREAKABLE)setTimeout(()=>{if(!done){done=true;_end(true);}},600);
  }
  document.getElementById('crystal-info').textContent=best.trapped?'&#x1F4A5; PI\xC8GE !':best.hp<=0?'&#x1F48E; Bris\xe9 !':'HP: '+best.hp+'/'+best.maxHp;
},{passive:false});
document.getElementById('btn-start').addEventListener('click',()=>{
  document.getElementById('overlay').style.display='none';started=true;lastTs=performance.now();raf=requestAnimationFrame(tick);
});
document.getElementById('btn-q').addEventListener('click',()=>{
  done=true;cancelAnimationFrame(raf);window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:8,poussieres:0},'*');
});
draw();
</script></body></html>"""

# =============================================================================
# NIVEAU 9 — LUNE D'ÉCLIPSE (Boss 3 phases)
# =============================================================================
n9 = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover"><title>GPS0 - Lune d'Eclipse</title><style>
""" + COMMON_CSS + r"""
body{background:#020008}#hud{background:rgba(2,0,8,.92)}#htimer{color:#C8A2C8}
h2{color:#C8A2C8}p{color:rgba(220,180,255,.85)}.ti{color:rgba(200,162,200,.65)}
.btn-go{background:linear-gradient(135deg,#C8A2C8,#9a72c8)}
#boss-hp-wrap{flex:1;height:12px;background:rgba(255,255,255,.1);border-radius:6px;overflow:hidden;min-width:80px}
#boss-hp-bar{height:100%;background:linear-gradient(90deg,#ff1744,#ff6d00);border-radius:6px;transition:width .3s}
#phase-label{position:fixed;top:60px;left:50%;transform:translateX(-50%);color:#FFD700;font-size:.9rem;font-weight:bold;z-index:15;background:rgba(2,0,8,.75);padding:4px 14px;border-radius:10px}
#mechanic-label{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);color:rgba(200,162,200,.65);font-size:.8rem;z-index:15;background:rgba(2,0,8,.7);padding:4px 12px;border-radius:10px}
</style></head><body>
<canvas id="c"></canvas>
<div id="hud">
  <span id="htimer">3:00</span>
  <span>&#x1F311; Lune d'Eclipse</span>
  <div id="boss-hp-wrap"><div id="boss-hp-bar" style="width:100%"></div></div>
  <button id="btn-q">Quitter</button>
</div>
<div id="phase-label">BOSS — Phase 1/3</div>
<div id="mechanic-label">TAP = Inverser la gravit\xe9</div>
<div id="overlay" style="background:rgba(2,0,8,.93)">
  <h2>&#x1F311; Lune d'Eclipse</h2>
  <p>Le Boss Final t'attend ! 3 phases, 3 m\xe9caniques combinees.</p>
  <div class="ti">&#x1FA90; <span>Phase 1 : gravit\xe9 invers\xe9e — \xe9vite les attaques</span></div>
  <div class="ti">&#x1F50E; <span>Phase 2 : miroirs — redirige les lasers vers le boss</span></div>
  <div class="ti">&#x1F47B; <span>Phase 3 : fant\xF4me — traverse les ultimes attaques</span></div>
  <button class="btn-go" id="btn-start">Affronter le Boss !</button>
</div>
<div id="results" style="background:rgba(2,0,8,.95)"></div>
<script>
'use strict';
const C=document.getElementById('c'),X=C.getContext('2d');
let W=window.innerWidth,H=window.innerHeight;C.width=W;C.height=H;
""" + SELFIE_JS + r"""
const TOTAL=180,BOSS_HP_MAX=9;
let started=false,done=false,poussieres=0,raf=null,elapsed=0,startTs=0,lastTs=0,winTime=0;
let lives=3,bossHp=BOSS_HP_MAX,phase=0,secretFound=false;
// Phase 1 state (gravity)
let py=0,vy=0,gravDir=1,gravFlipped=false,gravT=0;
const G=0.45,GRAV_MAX=5,FLOOR=H-80,CEIL=55,PX=W*0.25;
// Phase 2 state (mirrors)
let mirrors=[
  {x:W*0.3,y:H*0.3,type:'/'},
  {x:W*0.5,y:H*0.6,type:'\\'},
  {x:W*0.65,y:H*0.25,type:'/'},
];
// Phase 3 state (ghost)
let ghostT=0,ghostCdT=0,touching=false,isGhost=false;
const GHOST_MAX=3,GHOST_CD=4;
// Boss
let bossX=W*0.72,bossY=H*0.35,bossVx=1.8,bossVy=0.5;
// Projectiles
let projs=[];let projTimer=0,projInterval=3;
function addProj(){
  const angle=Math.atan2(py-bossY,PX-bossX);
  projs.push({x:bossX,y:bossY,vx:Math.cos(angle)*4,vy:Math.sin(angle)*4,w:20,h:8,reflected:false});
}
function bossColor(){return phase===0?'#7700aa':phase===1?'#FF6600':'#FF0000';}
function bossSize(){return 60+phase*12;}
const SRC2={x:40,y:H/2};
function traceRay2(){
  let pts=[{x:SRC2.x,y:SRC2.y}],dx=1,dy=0,cx=SRC2.x,cy=SRC2.y,hit=false;
  for(let b=0;b<6;b++){
    let bt=1e9,bm=null;
    for(const m of mirrors){
      const fx=m.x-cx,fy=m.y-cy,A=1,B=-2*(fx*dx+fy*dy),CC=fx*fx+fy*fy-22*22,D=B*B-4*A*CC;
      if(D<0)continue;const t=(-B-Math.sqrt(D))/(2*A);if(t>2&&t<bt){bt=t;bm=m;}
    }
    const tbx=(bossX-cx)*dx+(bossY-cy)*dy;
    const nx=cx+dx*tbx-bossX,ny=cy+dy*tbx-bossY;
    if(tbx>0&&tbx<(bm?bt:1e9)&&Math.sqrt(nx*nx+ny*ny)<bossSize()/2){
      pts.push({x:bossX,y:bossY});hit=true;break;
    }
    let wt=1e9;
    if(dx>0)wt=Math.min(wt,(W+50-cx)/dx);else if(dx<0)wt=Math.min(wt,(-50-cx)/dx);
    if(dy>0)wt=Math.min(wt,(H+50-cy)/dy);else if(dy<0)wt=Math.min(wt,(-50-cy)/dy);
    if(bm&&bt<wt){cx+=dx*bt;cy+=dy*bt;pts.push({x:cx,y:cy});if(bm.type=='/'){const t=dx;dx=-dy;dy=-t;}else{const t=dx;dx=dy;dy=t;}}
    else{pts.push({x:cx+dx*wt,y:cy+dy*wt});break;}
  }
  return{pts,hit};
}
function draw(){
  X.clearRect(0,0,W,H);
  const bg=X.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,'#020008');bg.addColorStop(1,'#0a0020');
  X.fillStyle=bg;X.fillRect(0,0,W,H);
  for(let i=0;i<50;i++){X.fillStyle='rgba(200,162,200,.15)';X.beginPath();X.arc((i*137)%W,(i*89)%H,.8,0,Math.PI*2);X.fill();}
  // Boss
  const bs2=bossSize();
  const gbo=X.createRadialGradient(bossX,bossY,bs2*0.2,bossX,bossY,bs2+20);
  gbo.addColorStop(0,'rgba(200,0,255,.5)');gbo.addColorStop(1,'transparent');
  X.fillStyle=gbo;X.beginPath();X.arc(bossX,bossY,bs2+20,0,Math.PI*2);X.fill();
  X.fillStyle=bossColor();X.beginPath();X.arc(bossX,bossY,bs2,0,Math.PI*2);X.fill();
  X.font=(bs2*0.7)+'px serif';X.textAlign='center';X.textBaseline='middle';
  X.fillText('\uD83D\uDC7E',bossX,bossY);
  // Phase-specific rendering
  if(phase===0){
    // Floor/ceiling indicator
    X.fillStyle='#FF3300';X.fillRect(0,FLOOR,W,H-FLOOR);
    X.fillStyle='rgba(255,100,0,.2)';X.fillRect(0,CEIL,W,3);
    // Gravity arrow
    X.font='bold 20px serif';X.textAlign='center';X.fillStyle='rgba(255,200,100,.7)';X.fillText(gravDir>0?'\uD83D\uDC47':'\uD83D\uDC46',PX,H*0.5);
  }
  if(phase===1){
    // Ray source
    const gs=X.createRadialGradient(SRC2.x,SRC2.y,2,SRC2.x,SRC2.y,28);
    gs.addColorStop(0,'rgba(255,255,180,.8)');gs.addColorStop(1,'transparent');
    X.fillStyle=gs;X.beginPath();X.arc(SRC2.x,SRC2.y,28,0,Math.PI*2);X.fill();
    X.font='18px serif';X.textAlign='center';X.textBaseline='middle';X.fillText('\uD83D\uDCA1',SRC2.x,SRC2.y);
    // Mirrors
    mirrors.forEach(m=>{
      X.strokeStyle='rgba(150,230,255,.75)';X.lineWidth=3;X.lineCap='round';
      const angle=m.type==='/'?-Math.PI/4:Math.PI/4;
      X.save();X.translate(m.x,m.y);X.rotate(angle);X.beginPath();X.moveTo(-22,0);X.lineTo(22,0);X.stroke();X.restore();
      X.fillStyle='rgba(200,162,200,.4)';X.font='10px system-ui';X.textAlign='center';X.textBaseline='top';X.fillText('TAP',m.x,m.y+26);
    });
    // Ray
    const {pts,hit}=traceRay2();
    if(pts.length>1){
      X.strokeStyle='rgba(255,255,80,.85)';X.lineWidth=3;X.shadowColor='rgba(255,255,0,.6)';X.shadowBlur=10;
      X.beginPath();X.moveTo(pts[0].x,pts[0].y);for(let i=1;i<pts.length;i++)X.lineTo(pts[i].x,pts[i].y);X.stroke();X.shadowBlur=0;
      if(hit&&!done){bossHp--;updateBossHp();if(bossHp<=3&&phase<2){phase=2;phaseTransition();}}
    }
  }
  if(phase===2){
    // Ghost bar
    const pct=isGhost?1-ghostT/GHOST_MAX:ghostCdT>0?1-ghostCdT/GHOST_CD:1;
    document.getElementById('mechanic-label').textContent=isGhost?'\uD83D\uDC7B FANT\xD4ME !':ghostCdT>0?'\u23F3 Rechargement...':'MAINTENIR = Fant\xF4me';
  }
  // Projectiles
  projs.forEach(p=>{
    X.fillStyle=p.reflected?'rgba(255,255,0,.8)':'rgba(255,50,200,.7)';
    X.fillRect(p.x-p.w/2,p.y-p.h/2,p.w,p.h);
  });
  // Player
  const alpha=isGhost?0.3:1;X.globalAlpha=alpha;
  if(isGhost){X.shadowColor='rgba(200,162,200,.9)';X.shadowBlur=18;}
  X.fillStyle='#888';X.beginPath();X.ellipse(PX,py+14,12,9,0,0,Math.PI*2);X.fill();
  if(sd&&selfieImg.complete){X.save();X.beginPath();X.arc(PX,py,13,0,Math.PI*2);X.clip();X.drawImage(selfieImg,PX-13,py-13,26,26);X.restore();}
  else{X.font='17px serif';X.textAlign='center';X.textBaseline='middle';X.fillText('\uD83E\uDDD1\u200D\uD83D\uDE80',PX,py);}
  X.globalAlpha=1;X.shadowBlur=0;
  for(let i=0;i<lives;i++){X.font='14px serif';X.textAlign='left';X.textBaseline='middle';X.fillText('\uD83D\uDC9C',8+i*24,H/2);}
}
function phaseTransition(){
  const pl=document.getElementById('phase-label');
  const ml=document.getElementById('mechanic-label');
  if(phase===1){pl.textContent='Phase 2/3 — MIROIRS';ml.textContent='TAP miroir = pivoter 45\xB0';}
  if(phase===2){pl.textContent='Phase 3/3 — FANT\xD4ME';ml.textContent='MAINTENIR = Fant\xF4me (3s)';}
  bossVx*=1.5;projInterval=Math.max(1.5,projInterval-0.7);
}
function updateBossHp(){
  const pct=Math.max(0,bossHp/BOSS_HP_MAX)*100;
  document.getElementById('boss-hp-bar').style.width=pct+'%';
  if(bossHp<=6&&phase<1){phase=1;phaseTransition();}
  if(bossHp<=0){done=true;winTime=elapsed;_end(true);}
}
function tick(ts){
  if(!started||done)return;
  if(!startTs)startTs=ts;
  const dt=Math.min((ts-lastTs)/1000,0.05);lastTs=ts;
  elapsed=(ts-startTs)/1000;
  const rem=Math.max(0,TOTAL-elapsed);
  document.getElementById('htimer').textContent=mm(rem);
  if(rem<=0&&!done){done=true;_end(false);return;}
  // Boss movement
  bossX+=bossVx;bossY+=bossVy;
  if(bossX<W*0.5||bossX>W-40)bossVx*=-1;
  if(bossY<70||bossY>H*0.65)bossVy*=-1;
  // Projectiles
  projTimer+=dt;
  if(projTimer>=projInterval){projTimer=0;addProj();}
  for(let i=projs.length-1;i>=0;i--){
    const p=projs[i];p.x+=p.vx;p.y+=p.vy;
    if(p.x<-40||p.x>W+40||p.y<-40||p.y>H+40){projs.splice(i,1);continue;}
    if(!isGhost&&Math.abs(p.x-PX)<20&&Math.abs(p.y-py)<20){
      projs.splice(i,1);lives--;
      if(lives<=0){done=true;_end(false);return;}
    }
    if(phase===1&&p.reflected&&Math.sqrt((p.x-bossX)**2+(p.y-bossY)**2)<bossSize()){
      projs.splice(i,1);bossHp--;updateBossHp();
    }
  }
  // Phase 0: gravity
  if(phase===0){
    if(gravFlipped){gravT+=dt;if(gravT>=GRAV_MAX){gravDir=1;gravFlipped=false;gravT=0;}}
    vy+=G*gravDir;py+=vy;
    if(gravDir===1&&py+22>=FLOOR){py=FLOOR-22;vy=0;}
    if(gravDir===-1&&py-16<=CEIL){py=CEIL+16;vy=0;}
  }
  // Phase 3: ghost
  if(phase===2){
    if(py+18<FLOOR)vy+=G,py+=vy;else{py=FLOOR-18;vy=0;}
    if(touching&&ghostCdT<=0){isGhost=true;ghostT=Math.min(GHOST_MAX,ghostT+dt);if(ghostT>=GHOST_MAX){isGhost=false;ghostT=0;ghostCdT=GHOST_CD;}}
    else isGhost=false;
    if(ghostCdT>0)ghostCdT=Math.max(0,ghostCdT-dt);
    // Check secret finding
    if(Math.abs(PX-bossX)<bossSize()+20&&Math.abs(py-bossY)<bossSize()+20&&isGhost&&!secretFound)secretFound=true;
  }
  draw();raf=requestAnimationFrame(tick);
}
""" + MM_JS + r"""
function _end(ok){
  done=true;cancelAnimationFrame(raf);
  const r=document.getElementById('results');r.style.display='flex';
  if(ok){
    poussieres=winTime<30&&secretFound?50:winTime<60?25:5;
    r.innerHTML='<h2 style="color:#FFD700">\uD83C\uDF1F Boss vaincu !</h2><p>'+(secretFound?'\uD83D\uDC7B Attaque cach\xe9e d\xe9couverte !':'')+'</p><p style="color:#C8A2C8;font-size:1.2rem">+'+poussieres+' \u2728 poussi\xe8res</p>';
  }else{
    poussieres=5;r.innerHTML='<h2 style="color:#FF6B6B">\uD83D\uDE22 Vaincu par le Boss...</h2><p style="color:#C8A2C8">+5 \u2728 poussi\xe8res</p>';
  }
  setTimeout(()=>window.parent.postMessage({source:'gps0_minijeu',success:ok,niveau:9,poussieres},'*'),2200);
}
C.addEventListener('touchstart',e=>{
  e.preventDefault();if(!started)return;
  const tx=e.touches[0].clientX-50,ty=e.touches[0].clientY;
  if(phase===0){
    if(!gravFlipped){gravDir*=-1;gravFlipped=true;gravT=0;vy=0;}
    else if(gravT>1){gravDir*=-1;gravFlipped=true;gravT=0;vy=0;}
  }else if(phase===1){
    for(const m of mirrors){
      if(Math.sqrt((tx-m.x)**2+(ty+50-m.y)**2)<30){m.type=m.type==='/'?'\\':'/';break;}
    }
  }
  touching=true;
},{passive:false});
C.addEventListener('touchend',e=>{e.preventDefault();touching=false;if(phase===2&&isGhost){isGhost=false;ghostCdT=GHOST_CD;ghostT=0;}},{passive:false});
document.getElementById('btn-start').addEventListener('click',()=>{
  document.getElementById('overlay').style.display='none';
  py=FLOOR-22;document.getElementById('phase-label').textContent='Phase 1/3 — GRAVIT\xC9';
  document.getElementById('mechanic-label').textContent='TAP = Inverser la gravit\xe9';
  started=true;lastTs=performance.now();raf=requestAnimationFrame(tick);
});
document.getElementById('btn-q').addEventListener('click',()=>{
  done=true;cancelAnimationFrame(raf);window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:9,poussieres:0},'*');
});
draw();
</script></body></html>"""

# Write all files
files = {
    'niveau5.html': n5,
    'niveau6.html': n6,
    'niveau7.html': n7,
    'niveau8.html': n8,
    'niveau9.html': n9,
}

for fname, content in files.items():
    path = os.path.join(BASE, fname)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    size = os.path.getsize(path)
    print(f"{fname}: {size} bytes OK")

print("Tous les fichiers ecrits!")
