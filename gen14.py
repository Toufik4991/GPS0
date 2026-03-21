#!/usr/bin/env python3
# GPS0 Bug 14 — Générateur des 9 mini-jeux avec shared.js
import os, sys

OUT = os.path.join(os.path.dirname(__file__), 'minijeux')

def html(niveau, bg_css, game_js):
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover">
<title>GPS0 N{niveau}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%;overflow:hidden;background:#0A0A1A;font-family:system-ui,sans-serif;color:#fff;touch-action:none;user-select:none}}
#bg{{position:fixed;inset:0;z-index:0;{bg_css}}}
#hud{{position:relative;z-index:20;display:flex;align-items:center;gap:10px;padding:6px 52px 6px 10px;background:rgba(0,0,0,.65);backdrop-filter:blur(6px);flex-shrink:0}}
#lives{{font-size:1.1rem;letter-spacing:2px;min-width:54px}}
#timer{{flex:1;text-align:center;font-size:.95rem;font-weight:bold;color:#4FC3F7}}
#score-hud{{font-size:.9rem;color:#FFD700;font-weight:bold;min-width:52px;text-align:right}}
#game-container{{position:relative;z-index:1;flex:1;overflow:hidden;display:flex;flex-direction:column}}
canvas{{display:block;width:100%;height:100%}}
body{{display:flex;flex-direction:column;height:100dvh}}
</style>
</head>
<body>
<div id="bg"></div>
<div id="hud">
  <span id="lives">❤❤❤</span>
  <span id="timer">2:30</span>
  <span id="score-hud">0 ✨</span>
</div>
<div id="game-container">
  <canvas id="cv"></canvas>
</div>
<script src="shared.js"></script>
<script>
window.NIVEAU = {niveau};
{game_js}
</script>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════════
# NIVEAU 1 — Lune de Verre (Lance-pierre / Angry Birds)
# ═══════════════════════════════════════════════════════════════════
N1_JS = r"""
window.TUTO_TEXT = "Glisse depuis la fronde pour viser.<br>Relâche pour tirer — tirs illimités !<br>Détruis un maximum de météorites.<br><small>Ta récompense dépend de ta précision · Évite qu'elles te touchent !</small>";

// ── CONSTANTES ────────────────────────────────────────────────────────────────
// Score interne par taille (non affiché — calcul d'efficacité final)
const KILL_TARGET = 20; // kills pour récompense maximale

// ── ÉTAT ──────────────────────────────────────────────────────────────────────
let slingX,slingY,cosX,cosY,bgT,rafId;
let orbs,meteors,particles;
let dragging,dragCX,dragCY;
let shotsFired,meteorsKilled;

function gameReset(){
  cancelAnimationFrame(rafId);
  bgT=0; shotsFired=0; meteorsKilled=0;
  orbs=[]; meteors=[]; particles=[];
  dragging=false; dragCX=dragCY=0;
}
window.gameReset=gameReset;


function gameStart(){
  const cv=document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  const W=cv.width,H=cv.height;
  slingX=W*.18; slingY=H*.63;
  cosX=slingX+26; cosY=slingY-26;

  // Récompense à la fin du timer : calcul d'efficacité → 5 à 50 ✨
  window.GPS0_onTimerExpired = function(){
    const killScore = Math.min(meteorsKilled / KILL_TARGET, 1);
    const precScore = shotsFired === 0 ? 0 : Math.min(meteorsKilled / shotsFired, 1);
    const eff = killScore * .6 + precScore * .4;
    window.GPS0_rewardOverride = Math.round(5 + eff * 45); // [5 → 50]
    endGame(true);
  };

  // Météorites initiales
  for(let i=0;i<4;i++) _spawn(W+i*220,H);

  cv.addEventListener('pointerdown',e=>{
    if(!GPS0_running())return;
    dragging=true;
    dragCX=e.offsetX; dragCY=e.offsetY;
  });
  cv.addEventListener('pointermove',e=>{if(!dragging)return;dragCX=e.offsetX;dragCY=e.offsetY;});
  cv.addEventListener('pointerup',()=>{
    if(!dragging)return; dragging=false;
    const dx=slingX-dragCX,dy=slingY-dragCY;
    const dist=Math.sqrt(dx*dx+dy*dy);
    if(dist<14)return;
    const spd=Math.min(15,dist*.1);
    orbs.push({x:slingX,y:slingY,vx:dx/dist*spd,vy:dy/dist*spd,r:9,life:220,trail:[]});
    shotsFired++;
    navigator.vibrate&&navigator.vibrate(25);
  });

  const ctx=cv.getContext('2d');
  const loop=()=>{
    rafId=requestAnimationFrame(loop);
    if(!GPS0_running())return;
    const W=cv.width,H=cv.height;
    bgT++;
    // Spawn nouveaux météores
    if(bgT%80===0) _spawn(W+40+Math.random()*100,H);
    // Mise à jour orbes
    orbs=orbs.filter(o=>{
      o.trail.push({x:o.x,y:o.y}); if(o.trail.length>12)o.trail.shift();
      o.vy+=.06; o.x+=o.vx; o.y+=o.vy; o.life--;
      for(let i=meteors.length-1;i>=0;i--){
        const m=meteors[i]; if(m.hp<=0)continue;
        const dx=o.x-m.x,dy=o.y-m.y;
        if(Math.sqrt(dx*dx+dy*dy)<o.r+m.r){
          _hit(m,o.vx,o.vy);
          navigator.vibrate&&navigator.vibrate([35,15,35]);
          o.life=0; break;
        }
      }
      return o.life>0&&o.x<W+80&&o.y<H+80&&o.x>-80;
    });
    // Mise à jour météorites
    meteors.forEach(m=>{
      if(m.hp<=0){m.explT--;return;}
      if(m.bouncing){m.vx*=.96;m.vy*=.96;m.rotSpd*=1.04;}
      m.x+=m.vx; m.y+=m.vy;
      if(!m.bouncing) m.y+=Math.sin(bgT*.025+m.phase)*m.drift;
      m.rot+=m.rotSpd;
      // Bords haut/bas (rebond doux)
      if(m.bouncing){
        if(m.y<m.r+6){m.y=m.r+6;m.vy=Math.abs(m.vy)*.45;}
        if(m.y>H-m.r-6){m.y=H-m.r-6;m.vy=-Math.abs(m.vy)*.45;}
      }
      // Collision cosmonaute → perte de vie
      const dc=Math.sqrt((m.x-cosX)*(m.x-cosX)+(m.y-cosY)*(m.y-cosY));
      if(m.hp>0&&dc<m.r+24){
        m.hp=-1; m.explT=18;
        for(let j=0;j<10;j++) particles.push({x:cosX,y:cosY,vx:(Math.random()-.5)*6,vy:-2.5-Math.random()*3,life:24,col:'#ff6060'});
        loseLife();
        return;
      }
      // Bord gauche → disparaît sans vie perdue
      if(m.x+m.r<-5) m.hp=-1;
    });
    meteors=meteors.filter(m=>m.hp>0||m.explT>0);
    // Particules
    particles=particles.filter(p=>p.life>0);
    particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.09;p.life--;});
    // Dessin
    ctx.clearRect(0,0,W,H);
    _drawBg(ctx,W,H);
    _drawMeteors(ctx,W,H);
    _drawOrbs(ctx,W,H);
    _drawSling(ctx,W,H);
    _drawParticles(ctx);
    _drawHUD(ctx,W,H);
  };
  loop();
}

function _spawn(x,H){
  const r=16+Math.random()*28;
  const hp=r>36?3:r>25?2:1;
  meteors.push({
    x,y:H*.1+Math.random()*H*.76,
    r,hp,maxHp:hp,
    vx:-(0.7+Math.random()*.9), vy:0,
    phase:Math.random()*Math.PI*2,
    drift:.22+Math.random()*.32,
    rot:Math.random()*Math.PI*2,
    rotSpd:(Math.random()-.5)*.022,
    hue:195+Math.random()*32,
    bouncing:false,explT:0
  });
}

function _hit(m,ovx,ovy){
  m.hp--;
  // Particules impact
  for(let j=0;j<8;j++) particles.push({x:m.x,y:m.y,vx:(Math.random()-.5)*5.5,vy:-2-Math.random()*3,life:22,col:m.hp<=0?'#4FC3F7':'#9ab0c4'});
  if(m.hp<=0){
    // Explosion finale
    for(let j=0;j<16;j++) particles.push({x:m.x,y:m.y,vx:(Math.random()-.5)*8,vy:(Math.random()-.5)*8,life:30,col:j%2===0?'#4FC3F7':'#C8A2C8'});
    m.explT=22;
    meteorsKilled++;
    // Screen shake
    document.body.style.transform='translateX(4px)';
    setTimeout(()=>document.body.style.transform='translateX(-3px)',55);
    setTimeout(()=>document.body.style.transform='',110);
  } else {
    // Ricochet : direction basée sur l'orbe + aléatoire
    m.bouncing=true;
    const ang=Math.atan2(ovy,ovx)+.3*(Math.random()-.5);
    const spd=.7+Math.random()*.6;
    m.vx=Math.cos(ang)*spd; m.vy=Math.sin(ang)*spd-.7;
    m.rotSpd=(Math.random()-.5)*.065;
  }
}

function _drawBg(ctx,W,H){
  // Étoiles parallaxe animées
  for(let i=0;i<55;i++){
    const sx=((i*137+bgT*.09)%W+W)%W;
    const sy=(i*71+17)%H;
    const fl=.42+.55*(Math.sin(i*2.4+bgT*.046)*.5+.5);
    ctx.fillStyle=`rgba(255,255,255,${fl.toFixed(2)})`;
    ctx.fillRect(sx,sy,i%9===0?2:1.5,i%9===0?2:1.5);
  }
  // Surface lunaire animée (bas)
  const sf=ctx.createLinearGradient(0,H*.82,0,H);
  sf.addColorStop(0,'rgba(38,44,68,.96)'); sf.addColorStop(1,'rgba(15,18,32,1)');
  ctx.fillStyle=sf;
  ctx.beginPath(); ctx.moveTo(0,H);
  for(let x=0;x<=W;x+=28){
    const bx=(x+bgT*.2)%(W*2+100);
    ctx.lineTo(x,H*.86+Math.sin(bx*.018)*11+Math.sin(bx*.04)*5);
  }
  ctx.lineTo(W,H); ctx.closePath(); ctx.fill();
  // Cratères mouvants
  for(let i=0;i<4;i++){
    const cx=(((i*.28+.06)*W*1.8-bgT*.18)%(W*1.8)+W*1.8)%(W*1.8)-W*.05;
    if(cx<-20||cx>W+20)continue;
    ctx.strokeStyle='rgba(60,70,105,.5)'; ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.ellipse(cx,H*.895,12+i*4,3+i,0,0,Math.PI*2); ctx.stroke();
  }
}

function _drawMeteors(ctx,W,H){
  meteors.forEach(m=>{
    if(m.hp<=0&&m.explT<=0)return;
    ctx.save(); ctx.translate(m.x,m.y);
    if(m.hp<=0){
      ctx.scale(1+(22-m.explT)*.05,1+(22-m.explT)*.05);
      ctx.globalAlpha=m.explT/22;
    }
    ctx.rotate(m.rot);
    // Halo extérieur
    const glow=ctx.createRadialGradient(0,0,m.r*.4,0,0,m.r*1.6);
    glow.addColorStop(0,`hsla(${m.hue},35%,55%,.13)`); glow.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=glow; ctx.beginPath(); ctx.arc(0,0,m.r*1.6,0,Math.PI*2); ctx.fill();
    // Corps irrégulier
    ctx.fillStyle=`hsl(${m.hue},22%,35%)`;
    ctx.beginPath();
    for(let k=0;k<8;k++){
      const a=(k/8)*Math.PI*2;
      const ir=m.r*(.72+Math.sin(k*1.85+m.phase)*.28);
      k===0?ctx.moveTo(Math.cos(a)*ir,Math.sin(a)*ir):ctx.lineTo(Math.cos(a)*ir,Math.sin(a)*ir);
    }
    ctx.closePath(); ctx.fill();
    // Surface intérieure (texture)
    ctx.fillStyle=`hsl(${m.hue},18%,47%)`;
    ctx.beginPath();
    for(let k=0;k<8;k++){
      const a=(k/8)*Math.PI*2+.2;
      const ir=m.r*(.45+Math.sin(k*1.85+m.phase)*.18);
      k===0?ctx.moveTo(Math.cos(a)*ir,Math.sin(a)*ir):ctx.lineTo(Math.cos(a)*ir,Math.sin(a)*ir);
    }
    ctx.closePath(); ctx.fill();
    // Fissures de dégâts
    if(m.hp<m.maxHp){
      ctx.strokeStyle='rgba(79,195,247,.72)'; ctx.lineWidth=1.5;
      for(let c=0;c<m.maxHp-m.hp;c++){
        const ca=Math.PI*.22+c*Math.PI*.52;
        ctx.beginPath(); ctx.moveTo(Math.cos(ca)*m.r*.15,Math.sin(ca)*m.r*.15);
        ctx.lineTo(Math.cos(ca)*m.r*.9,Math.sin(ca)*m.r*.9); ctx.stroke();
      }
    }
    // Reflet
    ctx.fillStyle='rgba(255,255,255,.12)';
    ctx.beginPath(); ctx.arc(-m.r*.28,-m.r*.28,m.r*.3,0,Math.PI*2); ctx.fill();
    ctx.restore();
    // Indicateur HP (points au-dessus)
    if(m.maxHp>=2&&m.hp>0){
      for(let h=0;h<m.maxHp;h++){
        ctx.fillStyle=h<m.hp?'#4FC3F7':'rgba(45,50,75,.85)';
        ctx.beginPath(); ctx.arc(m.x-(m.maxHp-1)*5+h*10,m.y-m.r-7,4,0,Math.PI*2); ctx.fill();
      }
    }
  });
}

function _drawOrbs(ctx,W,H){
  // Ligne de visée + élastique
  if(dragging){
    const dx=slingX-dragCX,dy=slingY-dragCY;
    const dist=Math.sqrt(dx*dx+dy*dy);
    if(dist>14){
      const spd=Math.min(15,dist*.1),nx=dx/dist,ny=dy/dist;
      // Élastique
      ctx.strokeStyle='rgba(185,150,68,.88)'; ctx.lineWidth=2.5; ctx.lineCap='round';
      ctx.beginPath(); ctx.moveTo(slingX-14,slingY-7); ctx.lineTo(dragCX,dragCY); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(slingX+14,slingY-7); ctx.lineTo(dragCX,dragCY); ctx.stroke();
      // Orbe en preview
      ctx.fillStyle='rgba(79,195,247,.6)';
      ctx.beginPath(); ctx.arc(dragCX,dragCY,9,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle='rgba(150,230,255,.8)'; ctx.lineWidth=1.5; ctx.stroke();
      // Trajectoire prédictive
      let px=slingX,py=slingY,pvx=nx*spd,pvy=ny*spd;
      for(let i=0;i<24;i++){
        px+=pvx; py+=pvy; pvy+=.06;
        ctx.fillStyle=`rgba(79,195,247,${(.42-i*.016).toFixed(2)})`;
        ctx.beginPath(); ctx.arc(px,py,2.5,0,Math.PI*2); ctx.fill();
      }
    }
  }
  // Orbes en vol
  orbs.forEach(o=>{
    o.trail.forEach((t,i)=>{
      ctx.fillStyle=`rgba(79,195,247,${(i/o.trail.length*.34).toFixed(2)})`;
      ctx.beginPath(); ctx.arc(t.x,t.y,o.r*(i/o.trail.length*.5+.15),0,Math.PI*2); ctx.fill();
    });
    const og=ctx.createRadialGradient(o.x-3,o.y-3,1,o.x,o.y,o.r);
    og.addColorStop(0,'rgba(220,245,255,.96)'); og.addColorStop(.5,'rgba(100,195,255,.85)'); og.addColorStop(1,'rgba(30,90,210,.5)');
    ctx.fillStyle=og; ctx.beginPath(); ctx.arc(o.x,o.y,o.r,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle='rgba(79,195,247,.85)'; ctx.lineWidth=1.5; ctx.stroke();
    const gp=(.12+Math.sin(bgT*.3)*.06).toFixed(2);
    ctx.fillStyle=`rgba(79,195,247,${gp})`;
    ctx.beginPath(); ctx.arc(o.x,o.y,o.r*2,0,Math.PI*2); ctx.fill();
  });
}

function _drawSling(ctx,W,H){
  // Fourche
  ctx.strokeStyle='#7a5f32'; ctx.lineWidth=5; ctx.lineCap='round';
  ctx.beginPath(); ctx.moveTo(slingX,slingY+48); ctx.lineTo(slingX-14,slingY); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(slingX,slingY+48); ctx.lineTo(slingX+14,slingY); ctx.stroke();
  // Élastique au repos
  if(!dragging){
    ctx.strokeStyle='rgba(172,145,68,.62)'; ctx.lineWidth=2;
    ctx.beginPath(); ctx.moveTo(slingX-14,slingY); ctx.lineTo(slingX,slingY-5); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(slingX+14,slingY); ctx.lineTo(slingX,slingY-5); ctx.stroke();
  }
  // Cosmonaute à côté
  drawCosmonaut(ctx,cosX,cosY,22,0,dragging?'jump':'idle');
}

function _drawParticles(ctx){
  particles.forEach(p=>{
    ctx.globalAlpha=p.life/32; ctx.fillStyle=p.col;
    ctx.beginPath(); ctx.arc(p.x,p.y,3,0,Math.PI*2); ctx.fill();
  });
  ctx.globalAlpha=1;
}

function _drawHUD(ctx,W,H){
  const prec = shotsFired===0 ? 0 : Math.round(meteorsKilled/shotsFired*100);
  // Panel bas gauche : kills + précision
  ctx.fillStyle='rgba(0,0,0,.52)';
  ctx.beginPath(); ctx.roundRect(6,H-50,130,44,8); ctx.fill();
  ctx.fillStyle='#4FC3F7'; ctx.font='bold 13px system-ui'; ctx.textAlign='left';
  ctx.fillText('\u{1F4A5} '+meteorsKilled+' d\u00e9truits',12,H-31);
  const col=prec>=60?'#7CFC00':prec>=35?'#FFD700':'#ff8080';
  ctx.fillStyle=col; ctx.font='12px system-ui';
  ctx.fillText('\u{1F3AF} '+prec+'% pr\u00e9cision',12,H-13);
  // Hint droite : tirs illimités
  ctx.fillStyle='rgba(255,255,255,.32)'; ctx.font='11px system-ui'; ctx.textAlign='right';
  ctx.fillText('Tirs illimit\u00e9s \u221e',W-8,H-8);
}
"""

# ═══════════════════════════════════════════════════════════════════
# NIVEAU 2 — Lune de Cendre (Flappy Bird)
# ═══════════════════════════════════════════════════════════════════
N2_JS = r"""
window.TUTO_TEXT = "Tape pour faire battre les ailes !<br>Passe entre les colonnes de lave.<br>Évite les parois et ne t'écrase pas.";

const GRAV_B=0.38, JUMP=-6;
let bird, pipes, dustItems, particles, speed, frame, rafId, ashParts, _pipeCount;

function gameReset(){
  cancelAnimationFrame(rafId);
  bird={x:0,y:0,vy:0,r:22};
  pipes=[]; dustItems=[]; particles=[]; ashParts=[];
  speed=2.2; frame=0; _pipeCount=0;
}
window.gameReset=gameReset;

function gameStart(){
  const cv=document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  bird.x=cv.width*.22; bird.y=cv.height*.45;
  cv.addEventListener('pointerdown',_jump);
  // Cendres décoratives
  for(let i=0;i<20;i++) ashParts.push({x:Math.random()*cv.width,y:Math.random()*cv.height,vx:-.3-Math.random()*.4,vy:.2+Math.random()*.3,r:1+Math.random()*2,a:.2+Math.random()*.3});
  _spawnPipe();
  const ctx=cv.getContext('2d');
  const loop=()=>{
    rafId=requestAnimationFrame(loop);
    if(!GPS0_running())return;
    const W=cv.width,H=cv.height;
    frame++;
    if(frame%280===0)speed=Math.min(5.5,speed+.35);
    bird.vy+=GRAV_B; bird.y+=bird.vy;
    // Spawn
    const gap=Math.max(140,210-frame*.06);
    if(frame%Math.floor(gap)===0)_spawnPipe();
    // Cendres
    ashParts.forEach(a=>{a.x+=a.vx;a.y+=a.vy;if(a.x<-5)a.x=W+5;if(a.y>H+5){a.y=-5;a.x=Math.random()*W;}});
    // Pipes
    let alive=true;
    pipes=pipes.filter(p=>p.x+p.w>-10);
    pipes.forEach(p=>{
      p.x-=speed;
      if(!p.passed&&p.x+p.w<bird.x){p.passed=true;}
      if(bird.x+bird.r>p.x&&bird.x-bird.r<p.x+p.w){
        if(bird.y-bird.r<p.top||bird.y+bird.r>p.bot)alive=false;
      }
    });
    // Dust
    dustItems.forEach(d=>{
      d.x-=speed; if(d.col)return;
      if(Math.sqrt((bird.x-d.x)**2+(bird.y-d.y)**2)<bird.r+d.r){d.col=true;addDust(5);for(let i=0;i<6;i++)particles.push({x:d.x,y:d.y,vx:(Math.random()-.5)*4,vy:-2,life:22});}
    });
    dustItems=dustItems.filter(d=>d.x>-30);
    if(bird.y-bird.r<0||bird.y+bird.r>H-48)alive=false;
    if(!alive){loseLife();if(GPS0_lives()>0){bird.vy=JUMP;bird.y=Math.min(bird.y,H*.5);}}
    // Draw
    ctx.clearRect(0,0,W,H);
    // Sol lave animé
    const lavaG=ctx.createLinearGradient(0,H-48,0,H);
    lavaG.addColorStop(0,'rgba(255,80,0,.95)'); lavaG.addColorStop(.5,'rgba(200,40,0,.9)'); lavaG.addColorStop(1,'rgba(100,10,0,1)');
    ctx.fillStyle=lavaG; ctx.fillRect(0,H-48,W,48);
    // Ondulation lave
    ctx.fillStyle='rgba(255,150,0,.4)';
    for(let x=0;x<W;x+=30){const off=Math.sin((x+frame*2)*.04)*4;ctx.fillRect(x,H-50+off,26,4);}
    // Brume volcanique haut
    ctx.fillStyle='rgba(80,50,30,.25)';
    ctx.fillRect(0,0,W,32);
    // Cendres
    ashParts.forEach(a=>{ctx.fillStyle=`rgba(120,100,80,${a.a})`;ctx.beginPath();ctx.arc(a.x,a.y,a.r,0,Math.PI*2);ctx.fill();});
    // Tuyaux volcaniques
    pipes.forEach(p=>{
      _drawLavaPipe(ctx,p.x,0,p.w,p.top,false);
      _drawLavaPipe(ctx,p.x,p.bot,p.w,H-p.bot,true);
    });
    dustItems.forEach(d=>{if(!d.col){ctx.fillStyle='#FFD700';ctx.font='bold 17px system-ui';ctx.textAlign='center';ctx.fillText('✨',d.x,d.y+6);}});
    particles=particles.filter(p=>p.life>0);
    particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;ctx.fillStyle=`rgba(255,215,0,${p.life/22})`;ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();});
    // Halo orange cosmonaute
    ctx.fillStyle='rgba(255,100,0,.18)'; ctx.beginPath();ctx.arc(bird.x,bird.y,bird.r+10,0,Math.PI*2);ctx.fill();
    drawCosmonaut(ctx,bird.x,bird.y,bird.r,bird.vy*.05,'fly');
  };
  loop();
}
function _jump(){if(!GPS0_running())return;bird.vy=JUMP;}
function _spawnPipe(){
  const H=document.getElementById('cv').clientHeight, W=document.getElementById('cv').clientWidth;
  const gap=H*.32; const topH=H*.08+Math.random()*(H*.55);
  _pipeCount++;
  pipes.push({x:W+60,top:topH,bot:topH+gap,w:50,passed:false});
  if(_pipeCount%3===0) dustItems.push({x:W+85,y:topH+gap/2+(Math.random()-.5)*50,r:14,col:false});
}
function _drawLavaPipe(ctx,x,y,w,h,flip){
  if(h<=0)return;
  const g=ctx.createLinearGradient(x,0,x+w,0);
  g.addColorStop(0,'rgba(80,50,40,.95)'); g.addColorStop(.4,'rgba(140,80,50,.95)'); g.addColorStop(1,'rgba(60,35,25,.95)');
  ctx.fillStyle=g; ctx.fillRect(x,y,w,h);
  // Bords irréguliers (dents)
  ctx.fillStyle='rgba(255,80,0,.25)';
  const edgeY=flip?y:y+h-12;
  for(let i=0;i<w;i+=14){const jag=flip?-Math.random()*8:Math.random()*8;ctx.fillRect(x+i,edgeY+jag,10,12);}
  ctx.strokeStyle='rgba(255,100,0,.5)';ctx.lineWidth=2;
  ctx.strokeRect(x,y,w,h);
}
"""

# ═══════════════════════════════════════════════════════════════════
# NIVEAU 3 — Lune de Lierre (Doodle Jump)
# ═══════════════════════════════════════════════════════════════════
N3_JS = r"""
window.TUTO_TEXT = "Penche ton téléphone ou glisse gauche/droite pour te déplacer.<br>Le cosmonaute rebondit sur les plateformes.<br>Monte le plus haut possible !";

const JUMP_V=-13.5;
let cosmo,platforms,dustItems,particles,worldY,rafId;
let tiltX=0,touchDx=0,lastTx=null;

window.addEventListener('deviceorientation',e=>{if(!GPS0_running())return;tiltX=Math.max(-1,Math.min(1,(e.gamma||0)/30));},{passive:true});

function gameReset(){
  cancelAnimationFrame(rafId);
  cosmo={x:0,y:0,vx:0,vy:0,r:22};
  platforms=[]; dustItems=[]; particles=[]; worldY=0; tiltX=0; touchDx=0;
}
window.gameReset=gameReset;

function gameStart(){
  const cv=document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  const W=cv.width,H=cv.height;
  cosmo.x=W/2; cosmo.y=H*.68;
  // Plateformes initiales
  platforms.push({x:W/2-50,y:H*.74,w:100,h:14,type:'normal',broken:false,bounce:false});
  for(let i=1;i<28;i++) _mkPlat(-(i*78));
  worldY=0;
  // Swipe
  cv.addEventListener('touchstart',e=>{lastTx=e.touches[0].clientX;},{passive:true});
  cv.addEventListener('touchmove',e=>{if(!GPS0_running()||!lastTx)return;touchDx=(e.touches[0].clientX-lastTx)/40;lastTx=e.touches[0].clientX;},{passive:true});
  cv.addEventListener('touchend',()=>{touchDx=0;lastTx=null;});
  const ctx=cv.getContext('2d');
  const loop=()=>{
    rafId=requestAnimationFrame(loop);
    if(!GPS0_running())return;
    const W=cv.width,H=cv.height;
    cosmo.vx+=(tiltX+touchDx)*.7; cosmo.vx*=.82;
    cosmo.vy+=.43; cosmo.x+=cosmo.vx; cosmo.y+=cosmo.vy;
    if(cosmo.x<-cosmo.r)cosmo.x=W+cosmo.r;
    if(cosmo.x>W+cosmo.r)cosmo.x=-cosmo.r;
    // Caméra
    if(cosmo.y<H*.42+worldY){
      const diff=(H*.42+worldY)-cosmo.y; worldY-=diff; cosmo.y+=diff;
      const topP=platforms.reduce((m,p)=>Math.min(m,p.y),9999);
      while(topP+worldY>-H*.5)_mkPlat(topP-78);
      platforms=platforms.filter(p=>p.y+worldY<H+50);
    }
    // Mort bas
    if(cosmo.y-worldY>H+60){loseLife();if(GPS0_lives()>0){cosmo.y=H*.6-worldY;cosmo.vy=-9;}return;}
    // Collisions plateformes
    if(cosmo.vy>0){
      platforms.forEach(p=>{
        const py=p.y-worldY;
        if(!p.broken&&cosmo.x>p.x&&cosmo.x<p.x+p.w&&cosmo.y+cosmo.r>py&&cosmo.y+cosmo.r<py+p.h+16){
          if(p.type==='toxic'){loseLife();return;}
          if(p.type==='break'){p.broken=true;}
          cosmo.vy=p.type==='spring'?JUMP_V*1.55:JUMP_V;
          for(let i=0;i<5;i++)particles.push({x:cosmo.x,y:py,vx:(Math.random()-.5)*4,vy:-2,life:18,col:p.type==='spring'?'#00ff88':'#a0c840'});
        }
      });
    }
    // Dust aléatoires
    if(Math.random()<.001&&dustItems.filter(d=>!d.col).length<4)
      dustItems.push({x:20+Math.random()*(cv.width-40),y:worldY-cv.height*.3-Math.random()*cv.height*2,col:false});
    dustItems.forEach(d=>{if(d.col)return;const dy=d.y-worldY;if(Math.sqrt((cosmo.x-d.x)**2+(cosmo.y-dy-worldY+d.y)**2)<cosmo.r+13){d.col=true;addDust(4);for(let i=0;i<5;i++)particles.push({x:d.x,y:dy,vx:(Math.random()-.5)*4,vy:-2.5,life:20,col:'#FFD700'});}});
    ctx.clearRect(0,0,W,H);
    // BG jungle spatiale
    ctx.fillStyle='rgba(20,50,20,.15)';
    for(let i=0;i<5;i++){const vx=(i*W/5+worldY*.08)%W;ctx.beginPath();ctx.moveTo(vx,0);ctx.bezierCurveTo(vx+25,H/3,vx-20,H*2/3,vx,H);ctx.strokeStyle='rgba(40,120,40,.2)';ctx.lineWidth=2;ctx.stroke();}
    // Plateformes
    platforms.forEach(p=>{
      if(p.broken)return;
      const py=p.y-worldY;
      const cs={normal:'#4a9a3a',spring:'#3af070',break:'#c8c040',toxic:'#e05050'};
      ctx.fillStyle=cs[p.type]||'#4a9a3a';
      ctx.beginPath();ctx.ellipse(p.x+p.w/2,py+p.h/2,p.w/2,p.h/2,0,0,Math.PI*2);ctx.fill();
      ctx.strokeStyle='rgba(255,255,255,.25)';ctx.lineWidth=1.5;ctx.stroke();
      if(p.type==='spring'){ctx.fillStyle='rgba(0,255,136,.5)';ctx.font='14px system-ui';ctx.textAlign='center';ctx.fillText('🌿',p.x+p.w/2,py+p.h/2+5);}
    });
    dustItems.forEach(d=>{if(d.col)return;const dy=d.y-worldY;if(dy<-20||dy>H+20)return;ctx.fillStyle='#FFD700';ctx.font='17px system-ui';ctx.textAlign='center';ctx.fillText('✨',d.x,dy+6);});
    particles=particles.filter(p=>p.life>0);
    particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;ctx.fillStyle=p.col;ctx.globalAlpha=p.life/20;ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});
    drawCosmonaut(ctx,cosmo.x,cosmo.y,cosmo.r,0);
  };
  loop();
}
function _mkPlat(y){
  const types=['normal','normal','normal','normal','spring','break','toxic'];
  const t=types[Math.floor(Math.random()*types.length)];
  platforms.push({x:20+Math.random()*(document.getElementById('cv').width-120),y,w:80+Math.random()*30,h:14,type:t,broken:false});
}
"""

# ═══════════════════════════════════════════════════════════════════
# NIVEAU 4 — Lune de Givre (Swing / Pendule)
# ═══════════════════════════════════════════════════════════════════
N4_JS = r"""
window.TUTO_TEXT = "Tape pour t'accrocher à une stalactite.<br>Swipe haut/bas pour changer la longueur de la corde.<br>Retape pour te lâcher et voler !";

let cosmo,anchors,attached,rope,dustItems,particles,spikes,rafId,swStart;

function gameReset(){
  cancelAnimationFrame(rafId);
  cosmo={x:0,y:0,vx:2.5,vy:0,r:22};
  attached=null; rope={len:0,angle:0,angVel:0};
  dustItems=[]; particles=[]; spikes=[];
}
window.gameReset=gameReset;

function gameStart(){
  const cv=document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  const W=cv.width,H=cv.height;
  cosmo.x=W*.1; cosmo.y=H*.38;
  anchors=[];
  for(let i=0;i<13;i++) anchors.push({x:W*.04+i*(W*.08),y:H*.07+Math.random()*H*.12,r:10});
  for(let i=0;i<Math.floor(W/28);i++) spikes.push({x:i*28+14,y:H-26});
  for(let i=0;i<8;i++) dustItems.push({x:W*.1+i*(W*.12),y:H*.2+Math.random()*H*.55,r:12,col:false});
  cv.addEventListener('pointerdown',_tap);
  cv.addEventListener('touchstart',e=>{swStart={y:e.touches[0].clientY};},{passive:true});
  cv.addEventListener('touchmove',e=>{
    if(!swStart||attached===null)return;
    const dy=e.touches[0].clientY-swStart.y;
    rope.len=Math.max(40,Math.min(220,rope.len+dy*.35));
    swStart={y:e.touches[0].clientY};
  },{passive:true});
  const ctx=cv.getContext('2d');
  const loop=()=>{
    rafId=requestAnimationFrame(loop);
    if(!GPS0_running())return;
    if(attached){
      const G=.38,gc=G*Math.cos(rope.angle)/rope.len;
      rope.angVel-=gc; rope.angVel*=.998; rope.angle+=rope.angVel;
      cosmo.x=attached.x+Math.sin(rope.angle)*rope.len;
      cosmo.y=attached.y+Math.cos(rope.angle)*rope.len;
      cosmo.vx=rope.angVel*rope.len*Math.cos(rope.angle);
      cosmo.vy=rope.angVel*rope.len*Math.sin(rope.angle);
    } else {
      cosmo.vx*=.99; cosmo.vy+=.38; cosmo.x+=cosmo.vx; cosmo.y+=cosmo.vy;
    }
    if(cosmo.x<cosmo.r){cosmo.x=cosmo.r;cosmo.vx=Math.abs(cosmo.vx)*.6;}
    if(cosmo.x>cv.width-cosmo.r){cosmo.x=cv.width-cosmo.r;cosmo.vx=-Math.abs(cosmo.vx)*.6;}
    if(cosmo.y<cosmo.r){cosmo.y=cosmo.r;cosmo.vy=Math.abs(cosmo.vy)*.5;}
    if(cosmo.y>cv.height-55){loseLife();if(GPS0_lives()>0){cosmo.y=cv.height*.38;cosmo.x=cv.width*.1;cosmo.vx=2.5;cosmo.vy=0;attached=null;}return;}
    dustItems.forEach(d=>{if(d.col)return;if(Math.sqrt((cosmo.x-d.x)**2+(cosmo.y-d.y)**2)<cosmo.r+d.r){d.col=true;addDust(4);for(let i=0;i<6;i++)particles.push({x:d.x,y:d.y,vx:(Math.random()-.5)*5,vy:-3,life:22,col:'#FFD700'});}});
    ctx.clearRect(0,0,cv.width,cv.height);
    // Glace fond
    ctx.strokeStyle='rgba(160,210,240,.08)';ctx.lineWidth=2;
    for(let i=0;i<8;i++){const x=i*cv.width/8;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,cv.height);ctx.stroke();}
    // Stalactites + anchors
    anchors.forEach(a=>{
      ctx.fillStyle='rgba(150,220,255,.65)';
      ctx.beginPath();ctx.moveTo(a.x-a.r,0);ctx.lineTo(a.x+a.r,0);ctx.lineTo(a.x,a.y+30);ctx.closePath();ctx.fill();
      ctx.beginPath();ctx.arc(a.x,a.y,a.r,0,Math.PI*2);ctx.fill();
      if(attached===a){
        ctx.strokeStyle='rgba(79,195,247,.9)';ctx.lineWidth=3;ctx.beginPath();ctx.arc(a.x,a.y,a.r+5,0,Math.PI*2);ctx.stroke();
        ctx.strokeStyle='rgba(200,235,255,.7)';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(cosmo.x,cosmo.y);ctx.stroke();
      }
    });
    // Pics
    ctx.fillStyle='rgba(150,200,230,.8)';
    spikes.forEach(s=>{ctx.beginPath();ctx.moveTo(s.x-13,cv.height);ctx.lineTo(s.x,s.y);ctx.lineTo(s.x+13,cv.height);ctx.closePath();ctx.fill();});
    dustItems.forEach(d=>{if(!d.col){ctx.fillStyle='#FFD700';ctx.font='17px system-ui';ctx.textAlign='center';ctx.fillText('✨',d.x,d.y+6);}});
    particles=particles.filter(p=>p.life>0);
    particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;ctx.fillStyle=p.col;ctx.globalAlpha=p.life/22;ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});
    drawCosmonaut(ctx,cosmo.x,cosmo.y,cosmo.r,0);
    ctx.fillStyle='rgba(255,255,255,.4)';ctx.font='12px system-ui';ctx.textAlign='center';
    ctx.fillText(attached?'TAP pour lâcher':'TAP pour s\'accrocher',cv.width/2,cv.height-8);
  };
  loop();
}
function _tap(){
  if(!GPS0_running())return;
  if(attached){
    cosmo.vx=-Math.sin(rope.angle)*rope.angVel*rope.len*.7;
    cosmo.vy=Math.cos(rope.angle)*rope.angVel*rope.len*.7;
    attached=null;return;
  }
  let best=null,bestD=150;
  anchors.forEach(a=>{const d=Math.sqrt((cosmo.x-a.x)**2+(cosmo.y-a.y)**2);if(d<bestD){bestD=d;best=a;}});
  if(best){
    attached=best;
    rope.len=Math.max(40,Math.sqrt((cosmo.x-best.x)**2+(cosmo.y-best.y)**2));
    rope.angle=Math.atan2(cosmo.x-best.x,cosmo.y-best.y);
    rope.angVel=(cosmo.vx*Math.cos(rope.angle)+cosmo.vy*Math.sin(rope.angle))/rope.len;
  }
}
"""

# ═══════════════════════════════════════════════════════════════════
# NIVEAU 5 — Lune d'Ombre (Labyrinthe, D-pad, lampes)
# ═══════════════════════════════════════════════════════════════════
N5_JS = r"""
window.TUTO_TEXT = "Utilise le D-pad pour explorer le labyrinthe.<br>Ramasse les 🔦 lampes pour agrandir ta lumière.<br>Trouve la 🚪 sortie dorée !";

const CELL=30,ROWS=33,COLS=33;
let maze,cosmo,exitPos,lamps,particles,lightR,blindT,moved,hold,holdInt,rafId;

function gameReset(){
  cancelAnimationFrame(rafId); clearInterval(holdInt);
  maze=_genMaze(COLS,ROWS);
  cosmo={cx:1,cy:1};
  exitPos={cx:COLS-2,cy:ROWS-2};
  lamps=[]; lightR=70; blindT=0; moved=false; hold=null; holdInt=null;
  particles=[];
  // Lampes normales
  for(let y=1;y<ROWS-1;y+=2) for(let x=1;x<COLS-1;x+=2){
    if(maze[y][x]===0&&Math.random()<.14&&!(x===1&&y===1)&&!(x===COLS-2&&y===ROWS-2))
      lamps.push({cx:x,cy:y,gold:Math.random()<.18,col:false});
  }
}
window.gameReset=gameReset;

function _genMaze(C,R){
  const m=Array.from({length:R},()=>Array(C).fill(1));
  function carve(x,y){m[y][x]=0;const d=[[0,-2],[2,0],[0,2],[-2,0]].sort(()=>Math.random()-.5);d.forEach(([dx,dy])=>{const nx=x+dx,ny=y+dy;if(nx>=0&&nx<C&&ny>=0&&ny<R&&m[ny][nx]===1){m[y+dy/2][x+dx/2]=0;carve(nx,ny);}});}
  carve(1,1);m[ROWS-2][COLS-2]=0;return m;
}

function gameStart(){
  const cv=document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  _buildDpad(cv);
  document.addEventListener('keydown',e=>{const m={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};if(m[e.key])_move(...m[e.key]);});
  const ctx=cv.getContext('2d');
  const loop=()=>{
    rafId=requestAnimationFrame(loop);
    if(!GPS0_running())return;
    if(blindT>0)blindT--;
    const W=cv.width,H=cv.height;
    const camPxX=cosmo.cx*CELL+CELL/2, camPxY=cosmo.cy*CELL+CELL/2;
    const offX=W/2-camPxX, offY=H/2-camPxY;
    const LR=blindT>0?24:lightR;
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#000';ctx.fillRect(0,0,W,H);
    ctx.save();
    ctx.beginPath();ctx.arc(W/2,H/2,LR,0,Math.PI*2);ctx.clip();
    for(let y=0;y<ROWS;y++) for(let x=0;x<COLS;x++){
      const px=x*CELL+offX,py=y*CELL+offY;
      if(px<-CELL||px>W||py<-CELL||py>H)continue;
      ctx.fillStyle=maze[y][x]===1?'rgba(25,15,50,.98)':'rgba(6,3,16,.92)';
      ctx.fillRect(px,py,CELL,CELL);
      if(maze[y][x]===1){ctx.strokeStyle='rgba(70,50,110,.3)';ctx.lineWidth=.5;ctx.strokeRect(px,py,CELL,CELL);}
    }
    // Sortie
    const ex=exitPos.cx*CELL+offX,ey=exitPos.cy*CELL+offY;
    const eg=ctx.createRadialGradient(ex+CELL/2,ey+CELL/2,2,ex+CELL/2,ey+CELL/2,CELL);
    eg.addColorStop(0,'rgba(255,215,0,.9)');eg.addColorStop(1,'rgba(255,215,0,0)');
    ctx.fillStyle=eg;ctx.fillRect(ex,ey,CELL,CELL);
    ctx.font='16px system-ui';ctx.textAlign='center';ctx.fillText('🚪',ex+CELL/2,ey+CELL/2+6);
    // Lampes
    lamps.forEach(l=>{
      if(l.col)return;
      const px=l.cx*CELL+offX+CELL/2,py=l.cy*CELL+offY+CELL/2;
      if(Math.abs(px-W/2)>LR+20||Math.abs(py-H/2)>LR+20)return;
      ctx.fillStyle=l.gold?'#FFD700':'rgba(200,200,100,.9)';
      ctx.font='16px system-ui';ctx.textAlign='center';ctx.fillText(l.gold?'🔆':'🔦',px,py+6);
    });
    ctx.restore();
    // Vignette
    const rg=ctx.createRadialGradient(W/2,H/2,LR*.75,W/2,H/2,LR*1.15+20);
    rg.addColorStop(0,'rgba(0,0,0,0)');rg.addColorStop(1,'rgba(0,0,0,1)');
    ctx.fillStyle=rg;ctx.fillRect(0,0,W,H);
    // Particles
    particles=particles.filter(p=>p.life>0);
    particles.forEach(p=>{
      const px=(p.x*CELL+offX-camPxX+W/2),py=(p.y*CELL+offY-camPxY+H/2);
      p.x+=p.vx*.016;p.y+=p.vy*.016;p.life--;
      ctx.fillStyle=p.col;ctx.globalAlpha=p.life/20;ctx.beginPath();ctx.arc(px,py,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;
    });
    drawCosmonaut(ctx,W/2,H/2,14,0);
    if(blindT>0){ctx.fillStyle='rgba(80,0,180,.4)';ctx.fillRect(0,0,W,H);ctx.fillStyle='rgba(255,255,255,.6)';ctx.font='12px system-ui';ctx.textAlign='center';ctx.fillText('⚫ Piège !',W/2,H*.88);}
  };
  loop();
}
function _move(dx,dy){
  if(!GPS0_running())return;
  const nx=cosmo.cx+dx,ny=cosmo.cy+dy;
  if(nx<0||nx>=COLS||ny<0||ny>=ROWS||maze[ny][nx]===1)return;
  cosmo.cx=nx;cosmo.cy=ny;
  // Lampe
  lamps.forEach(l=>{
    if(l.col||l.cx!==cosmo.cx||l.cy!==cosmo.cy)return;
    l.col=true;
    if(l.gold){lightR=Math.min(lightR+12,130);addDust(5);}
    else{lightR=Math.min(lightR+20,130);addDust(2);setTimeout(()=>{lightR=Math.max(70,lightR-20);},15000);}
    for(let i=0;i<8;i++)particles.push({x:cosmo.cx,y:cosmo.cy,vx:(Math.random()-.5)*2,vy:-1.5+Math.random(),life:20,col:l.gold?'#FFD700':'#ffffaa'});
  });
  if(cosmo.cx===exitPos.cx&&cosmo.cy===exitPos.cy)endGame(true);
}
function _buildDpad(cv){
  const gc=document.getElementById('game-container');
  const dpad=document.createElement('div');
  dpad.style.cssText='position:absolute;bottom:12px;left:50%;transform:translateX(-50%);z-index:50;display:grid;grid-template-columns:repeat(3,68px);grid-template-rows:repeat(3,68px);gap:4px';
  const dirs=[['','↑',''],['←','','→'],['','↓','']];
  const acts=[[null,()=>_move(0,-1),null],[()=>_move(-1,0),null,()=>_move(1,0)],[null,()=>_move(0,1),null]];
  dirs.forEach((row,ri)=>row.forEach((lbl,ci)=>{
    const btn=document.createElement('div');
    if(!lbl){btn.style.cssText='width:68px;height:68px';dpad.appendChild(btn);return;}
    btn.textContent=lbl;
    btn.style.cssText='width:68px;height:68px;display:flex;align-items:center;justify-content:center;font-size:1.6rem;background:rgba(255,255,255,.14);border-radius:12px;cursor:pointer;border:1px solid rgba(255,255,255,.2);active:scale(.9);touch-action:none';
    const fn=acts[ri][ci];
    // Maintien continu
    let hInt=null;
    btn.addEventListener('pointerdown',e=>{e.preventDefault();fn&&fn();hInt=setInterval(()=>{if(GPS0_running()&&fn)fn();},160);});
    btn.addEventListener('pointerup',()=>{clearInterval(hInt);});
    btn.addEventListener('pointerleave',()=>{clearInterval(hInt);});
    dpad.appendChild(btn);
  }));
  gc.appendChild(dpad);
}
"""

# ═══════════════════════════════════════════════════════════════════
# NIVEAU 6 — Lune de Fer (Agar.io++)
# ═══════════════════════════════════════════════════════════════════
N6_JS = r"""
window.TUTO_TEXT = "Drag le doigt pour déplacer ta lune.<br>Absorbe les plus petites boules, fuis les grandes.<br>Grossis jusqu'à la taille maximum !";

const WORLD=1400;
let player,enemies,dustBlobs,particles,camX,camY,ptarget,rafId,aiInt;

function gameReset(){
  cancelAnimationFrame(rafId); clearInterval(aiInt);
  player={x:WORLD/2,y:WORLD/2,r:20,vx:0,vy:0};
  enemies=[]; dustBlobs=[]; particles=[]; camX=0; camY=0;
  ptarget={x:WORLD/2,y:WORLD/2};
}
window.gameReset=gameReset;

function _spd(){return Math.max(1.3,5/(1+((player.r-20)/18)*.5));}

function gameStart(){
  const cv=document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  camX=player.x-cv.width/2; camY=player.y-cv.height/2;
  ptarget={x:player.x,y:player.y};
  // Ennemis (25)
  for(let i=0;i<25;i++){const r=8+Math.random()*50;enemies.push({x:Math.random()*WORLD,y:Math.random()*WORLD,r,vx:(Math.random()-.5)*1.6,vy:(Math.random()-.5)*1.6,col:`hsl(${Math.random()*360},55%,55%)`});}
  // Dust
  for(let i=0;i<20;i++) dustBlobs.push({x:Math.random()*WORLD,y:Math.random()*WORLD,col:false});
  cv.addEventListener('pointermove',e=>{ptarget={x:e.offsetX+camX,y:e.offsetY+camY};});
  cv.addEventListener('pointerdown',e=>{ptarget={x:e.offsetX+camX,y:e.offsetY+camY};});
  // Respawn dust
  setInterval(()=>{const alive=dustBlobs.filter(d=>!d.col).length;for(let i=alive;i<20;i++)dustBlobs.push({x:Math.random()*WORLD,y:Math.random()*WORLD,col:false});},8000);
  // IA ennemis
  aiInt=setInterval(()=>{
    enemies.forEach(en=>{
      const dx=player.x-en.x,dy=player.y-en.y,d=Math.sqrt(dx*dx+dy*dy);
      if(d<250){if(en.r<player.r-5){en.vx+=(en.x-player.x)/d*.2;en.vy+=(en.y-player.y)/d*.2;}else if(en.r>player.r+5){en.vx+=(player.x-en.x)/d*.12;en.vy+=(player.y-en.y)/d*.12;}}
      en.vx+=(Math.random()-.5)*.12;en.vy+=(Math.random()-.5)*.12;
      const sp=Math.sqrt(en.vx**2+en.vy**2);if(sp>2.2){en.vx=en.vx/sp*2.2;en.vy=en.vy/sp*2.2;}
      en.x=Math.max(en.r,Math.min(WORLD-en.r,en.x+en.vx));
      en.y=Math.max(en.r,Math.min(WORLD-en.r,en.y+en.vy));
    });
  },50);
  const ctx=cv.getContext('2d');
  const loop=()=>{
    rafId=requestAnimationFrame(loop);
    if(!GPS0_running())return;
    const dx=ptarget.x-player.x,dy=ptarget.y-player.y,d=Math.sqrt(dx*dx+dy*dy);
    if(d>5){player.vx=dx/d*_spd();player.vy=dy/d*_spd();}
    player.x=Math.max(player.r,Math.min(WORLD-player.r,player.x+player.vx));
    player.y=Math.max(player.r,Math.min(WORLD-player.r,player.y+player.vy));
    camX+=(player.x-cv.width/2-camX)*.09;camY+=(player.y-cv.height/2-camY)*.09;
    camX=Math.max(0,Math.min(WORLD-cv.width,camX));camY=Math.max(0,Math.min(WORLD-cv.height,camY));
    // Absorb dust
    dustBlobs.forEach(d=>{if(d.col)return;const dd=Math.sqrt((player.x-d.x)**2+(player.y-d.y)**2);if(dd<player.r+7){d.col=true;player.r=Math.min(100,player.r+2);addDust(3);for(let i=0;i<4;i++)particles.push({x:d.x,y:d.y,vx:(Math.random()-.5)*3,vy:-2,life:16,col:'#FFD700'});}});
    // Enemy interactions
    for(let i=enemies.length-1;i>=0;i--){
      const en=enemies[i],dd=Math.sqrt((player.x-en.x)**2+(player.y-en.y)**2);
      if(dd<player.r+en.r){
        if(player.r>en.r+5){player.r=Math.min(100,player.r+en.r*.3);addDust(4);for(let j=0;j<8;j++)particles.push({x:en.x,y:en.y,vx:(Math.random()-.5)*5,vy:-3,life:20,col:en.col});enemies.splice(i,1);setTimeout(()=>{const r=8+Math.random()*50;enemies.push({x:Math.random()*WORLD,y:Math.random()*WORLD,r,vx:(Math.random()-.5)*1.6,vy:(Math.random()-.5)*1.6,col:`hsl(${Math.random()*360},55%,55%)`});},4000);}
        else if(en.r>player.r+5&&dd<(player.r+en.r)*.5){player.r=Math.max(14,player.r*.72);loseLife();}
      }
    }
    if(player.r>=99)endGame(true);
    const W=cv.width,H=cv.height;
    ctx.clearRect(0,0,W,H);
    ctx.strokeStyle='rgba(100,80,60,.18)';ctx.lineWidth=1;
    for(let x=((-camX)%60);x<W;x+=60){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
    for(let y=((-camY)%60);y<H;y+=60){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
    ctx.strokeStyle='rgba(200,160,80,.5)';ctx.lineWidth=4;ctx.strokeRect(-camX,-camY,WORLD,WORLD);
    dustBlobs.forEach(d=>{if(d.col)return;const px=d.x-camX,py=d.y-camY;if(px<-15||px>W+15||py<-15||py>H+15)return;ctx.fillStyle='#FFD700';ctx.font='13px system-ui';ctx.textAlign='center';ctx.fillText('✨',px,py+5);});
    enemies.forEach(en=>{const px=en.x-camX,py=en.y-camY;if(px<-en.r-10||px>W+en.r+10||py<-en.r-10||py>H+en.r+10)return;ctx.fillStyle=en.col;ctx.beginPath();ctx.arc(px,py,en.r,0,Math.PI*2);ctx.fill();ctx.strokeStyle='rgba(255,255,255,.25)';ctx.lineWidth=2;ctx.stroke();});
    particles=particles.filter(p=>p.life>0);
    particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.05;p.life--;ctx.fillStyle=p.col;ctx.globalAlpha=p.life/20;ctx.beginPath();ctx.arc(p.x-camX,p.y-camY,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});
    const px=player.x-camX,py=player.y-camY;
    // Boule joueur sans halo
    ctx.fillStyle='rgba(200,220,255,.12)';ctx.beginPath();ctx.arc(px,py,player.r,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle='rgba(79,195,247,.5)';ctx.lineWidth=2;ctx.stroke();
    drawCosmonaut(ctx,px,py,Math.min(player.r*.78,38),0);
    ctx.fillStyle='rgba(255,255,255,.45)';ctx.font='11px system-ui';ctx.textAlign='left';
    ctx.fillText('Taille: '+Math.round(player.r)+'/100',8,cv.height-8);
  };
  loop();
}
"""

# ═══════════════════════════════════════════════════════════════════
# NIVEAU 7 — Lune de Tempête (Jetpack Joyride)
# ═══════════════════════════════════════════════════════════════════
N7_JS = r"""
window.TUTO_TEXT = "Maintiens appuyé pour monter avec le jetpack.<br>Relâche pour descendre doucement.<br>Évite les éclairs et les météores !";

let cosmo,obstacles,dustItems,particles,powerups;
let scrollSpd,frame,thrust,shield,magnet,magnetT,rafId;

function gameReset(){
  cancelAnimationFrame(rafId);
  cosmo={x:0,y:0,vy:0,r:22}; obstacles=[]; dustItems=[]; particles=[]; powerups=[];
  scrollSpd=2.2; frame=0; thrust=false; shield=false; magnet=false; magnetT=0;
}
window.gameReset=gameReset;

function gameStart(){
  const cv=document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  cosmo.x=cv.width*.18; cosmo.y=cv.height*.5;
  cv.addEventListener('pointerdown',()=>{thrust=true;});
  cv.addEventListener('pointerup',()=>{thrust=false;});
  _spawnObs();
  const ctx=cv.getContext('2d');
  const loop=()=>{
    rafId=requestAnimationFrame(loop);
    if(!GPS0_running())return;
    const W=cv.width,H=cv.height;
    frame++;
    if(frame%550===0)scrollSpd=Math.min(5.5,scrollSpd+.4);
    // Physique — poussée réduite de 40%, gravité +20%
    const PUSH=thrust?-0.34:0, GRAV=0.42;
    cosmo.vy+=GRAV+PUSH; cosmo.vy=Math.max(-5.5,Math.min(5,cosmo.vy)); cosmo.y+=cosmo.vy;
    // Rebond doux sol/plafond (pas mort)
    const safeTop=30+cosmo.r, safeBot=H-30-cosmo.r;
    if(cosmo.y<safeTop){cosmo.y=safeTop;cosmo.vy=Math.abs(cosmo.vy)*.4;}
    if(cosmo.y>safeBot){cosmo.y=safeBot;cosmo.vy=-Math.abs(cosmo.vy)*.4;}
    // Spawn
    if(frame%Math.max(160-Math.floor(frame/400),70)===0)_spawnObs();
    if(frame%280===0&&dustItems.filter(d=>!d.col).length<3){const y=H*.12+Math.random()*H*.72;dustItems.push({x:W+30,y,r:11,col:false});}
    if(frame%320===0&&Math.random()<.5)powerups.push({x:W+10,y:H*.15+Math.random()*H*.65,type:Math.random()<.5?'shield':'magnet',r:18,col:false});
    // Move
    obstacles=obstacles.filter(o=>{
      if(o.type==='lightning'){o.x-=scrollSpd;return o.x>-15;}
      if(o.type==='meteor'){o.x-=scrollSpd*.55;o.y+=o.vy;return o.x>-45&&o.y<H+50;}
      if(o.type==='wind'){o.x-=scrollSpd;o.life--;return o.life>0&&o.x>-90;}
      return false;
    });
    // Collisions obstacles
    obstacles.forEach(o=>{
      let hit=false;
      // Obstacles réduits de 30%
      if(o.type==='lightning'&&Math.abs(cosmo.x-o.x)<o.w/2+cosmo.r&&cosmo.y>o.y&&cosmo.y<o.y+o.h)hit=true;
      if(o.type==='meteor'&&Math.sqrt((cosmo.x-o.x)**2+(cosmo.y-o.y)**2)<o.r*.7+cosmo.r)hit=true;
      if(hit){if(!shield){loseLife();cosmo.vy=-4;}else{shield=false;for(let i=0;i<8;i++)particles.push({x:cosmo.x,y:cosmo.y,vx:(Math.random()-.5)*5,vy:-3,life:20,col:'#5af0ff'});}}
      if(o.type==='wind'&&Math.abs(cosmo.x-o.x)<o.w/2+cosmo.r&&Math.abs(cosmo.y-o.y)<o.h/2+cosmo.r)cosmo.vy+=o.dir*.35;
    });
    // Dust
    dustItems.forEach(d=>{d.x-=scrollSpd;if(magnet){const dx=cosmo.x-d.x,dy=cosmo.y-d.y;const dd=Math.sqrt(dx*dx+dy*dy);if(dd<150){d.x+=dx/dd*4.5;d.y+=dy/dd*4.5;}}});
    dustItems=dustItems.filter(d=>d.x>-25);
    dustItems.forEach(d=>{if(d.col)return;if(Math.sqrt((cosmo.x-d.x)**2+(cosmo.y-d.y)**2)<cosmo.r+d.r){d.col=true;addDust(3);for(let i=0;i<4;i++)particles.push({x:d.x,y:d.y,vx:(Math.random()-.5)*4,vy:-2,life:16,col:'#FFD700'});}});
    powerups.forEach(p=>{p.x-=scrollSpd;if(p.col)return;if(Math.sqrt((cosmo.x-p.x)**2+(cosmo.y-p.y)**2)<cosmo.r+p.r){p.col=true;if(p.type==='shield')shield=true;else{magnet=true;magnetT=320;}}});
    powerups=powerups.filter(p=>p.x>-35&&!p.col);
    if(magnet){magnetT--;if(magnetT<=0)magnet=false;}
    ctx.clearRect(0,0,W,H);
    // BG orageux
    if(frame%85<6){ctx.fillStyle='rgba(140,120,255,.05)';ctx.fillRect(0,0,W,H);}
    ctx.fillStyle='rgba(60,40,100,.4)';
    for(let i=0;i<4;i++){const cx=((i*230-frame*scrollSpd*.15+W*2)%W)*1.05;ctx.beginPath();ctx.ellipse(cx,60+i*28,110,32,0,0,Math.PI*2);ctx.fill();}
    // Lignes sol/plafond
    ctx.strokeStyle='rgba(120,80,200,.3)';ctx.lineWidth=3;
    ctx.beginPath();ctx.moveTo(0,safeBot+cosmo.r);ctx.lineTo(W,safeBot+cosmo.r);ctx.stroke();
    ctx.beginPath();ctx.moveTo(0,safeTop-cosmo.r);ctx.lineTo(W,safeTop-cosmo.r);ctx.stroke();
    // Obstacles
    obstacles.forEach(o=>{
      if(o.type==='lightning'){
        ctx.strokeStyle='rgba(200,180,255,.9)';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(o.x,o.y);ctx.lineTo(o.x,o.y+o.h);ctx.stroke();
        ctx.strokeStyle='rgba(255,255,255,.3)';ctx.lineWidth=7;ctx.stroke();
      }
      if(o.type==='meteor'){ctx.fillStyle='rgba(200,80,40,.85)';ctx.beginPath();ctx.arc(o.x,o.y,o.r*.7,0,Math.PI*2);ctx.fill();ctx.fillStyle='rgba(255,150,50,.3)';ctx.beginPath();ctx.arc(o.x,o.y,o.r,0,Math.PI*2);ctx.fill();}
      if(o.type==='wind'){const a=o.life/200*.45;ctx.fillStyle=`rgba(100,150,255,${a})`;ctx.fillRect(o.x-o.w/2,o.y-o.h/2,o.w,o.h);ctx.font='22px system-ui';ctx.textAlign='center';ctx.fillStyle=`rgba(255,255,255,${a*.6})`;ctx.fillText(o.dir>0?'→':'←',o.x,o.y+8);}
    });
    dustItems.forEach(d=>{if(!d.col){ctx.fillStyle='#FFD700';ctx.font='15px system-ui';ctx.textAlign='center';ctx.fillText('✨',d.x,d.y+5);}});
    powerups.forEach(p=>{if(p.col)return;ctx.font='22px system-ui';ctx.textAlign='center';ctx.fillText(p.type==='shield'?'🛡️':'🧲',p.x,p.y+7);});
    if(shield){ctx.strokeStyle='rgba(79,195,247,.7)';ctx.lineWidth=3;ctx.beginPath();ctx.arc(cosmo.x,cosmo.y,cosmo.r+9,0,Math.PI*2);ctx.stroke();}
    particles=particles.filter(p=>p.life>0);
    particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.08;p.life--;ctx.fillStyle=p.col;ctx.globalAlpha=p.life/20;ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});
    drawCosmonaut(ctx,cosmo.x,cosmo.y,cosmo.r,thrust?-.3:.08,thrust?'fly':'run');
  };
  loop();
}
function _spawnObs(){
  const cv=document.getElementById('cv'),H=cv.clientHeight,W=cv.clientWidth;
  const t=['lightning','meteor','wind'][Math.floor(Math.random()*3)];
  if(t==='lightning'){const y=H*.08+Math.random()*H*.68;obstacles.push({type:'lightning',x:W+55,y,w:7,h:H*.5,vy:0});}
  else if(t==='meteor'){obstacles.push({type:'meteor',x:W+30+Math.random()*80,y:-30,r:22,vy:2.5+Math.random()*2});}
  else{obstacles.push({type:'wind',x:W,y:H*.25+Math.random()*H*.45,w:55,h:38,dir:Math.random()<.5?1:-1,life:200});}
}
"""

# ═══════════════════════════════════════════════════════════════════
# NIVEAU 8 — Lune de Cristal (Course de Cristal)
# ═══════════════════════════════════════════════════════════════════
N8_JS = r"""
window.TUTO_TEXT = "La piste avance automatiquement.<br>Tape vite sur les cristaux pour les casser !<br>Évite les rouges 🔴 — vise les dorés 🟡 !";

let crystals,particles,powerups,speed,frame,combo,shield,magnet,magnetT,score,rafId,piste;

function gameReset(){
  cancelAnimationFrame(rafId);
  crystals=[]; particles=[]; powerups=[]; piste=[];
  speed=1.8; frame=0; combo=0; shield=false; magnet=false; magnetT=0; score=0;
}
window.gameReset=gameReset;

function gameStart(){
  const cv=document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  const W=cv.width,H=cv.height;
  // Piste de base
  for(let i=0;i<18;i++) piste.push({x:W/2+(Math.random()-.5)*60,y:H*.85-i*44,w:70,h:20});
  cv.addEventListener('pointerdown',e=>{
    if(!GPS0_running())return;
    const tx=e.offsetX,ty=e.offsetY;
    let hit=false;
    crystals.forEach((c,i)=>{
      if(c.col)return;
      const dx=tx-c.x,dy=ty-c.y;
      if(Math.sqrt(dx*dx+dy*dy)<c.r+18){
        c.col=true; hit=true;
        if(c.type==='red'){combo=0;loseLife();for(let j=0;j<5;j++)particles.push({x:c.x,y:c.y,vx:(Math.random()-.5)*5,vy:-3,life:20,col:'rgba(255,60,60,.8)'});}
        else{
          const pts=c.type==='gold'?8:c.type==='blue'?5:3;
          combo++; const bonus=combo>=5?2:1;
          addDust(pts*bonus); score+=pts*bonus;
          for(let j=0;j<7;j++)particles.push({x:c.x,y:c.y,vx:(Math.random()-.5)*5,vy:-3,life:22,col:c.type==='gold'?'#FFD700':c.type==='blue'?'#5af0ff':'rgba(180,255,180,.9)'});
          if(combo>=5){const el=document.createElement('div');el.style.cssText='position:fixed;top:35%;left:50%;transform:translateX(-50%);z-index:100;font-size:1.6rem;font-weight:900;color:#FFD700;text-shadow:0 0 20px gold;pointer-events:none';el.textContent='COMBO x'+combo+' !';document.body.appendChild(el);setTimeout(()=>el.remove(),900);}
        }
      }
    });
    // Powerups
    powerups.forEach(p=>{if(p.col)return;const dx=tx-p.x,dy=ty-p.y;if(Math.sqrt(dx*dx+dy*dy)<p.r+20){p.col=true;if(p.type==='shield')shield=true;else if(p.type==='magnet'){magnet=true;magnetT=300;}else{speed=Math.max(1,speed*.55);setTimeout(()=>{speed+=.9;},8000);}}});
  });
  const ctx=cv.getContext('2d');
  const loop=()=>{
    rafId=requestAnimationFrame(loop);
    if(!GPS0_running())return;
    const W=cv.width,H=cv.height;
    frame++;
    if(frame%500===0)speed=Math.min(5,speed+.35);
    // Scroll piste
    piste.forEach(p=>{p.y+=speed;});
    piste=piste.filter(p=>p.y<H+30);
    while(piste.length<20){const last=piste.reduce((a,b)=>a.y<b.y?a:b);piste.push({x:W/2+(Math.random()-.5)*80,y:last.y-44,w:70,h:20});}
    // Spawn cristaux
    if(frame%55===0){
      const pt=piste[Math.floor(piste.length*.3)];
      const types=['normal','normal','normal','normal','red','gold','blue'];
      const t=types[Math.floor(Math.random()*types.length)];
      crystals.push({x:pt.x+(Math.random()-.5)*50,y:pt.y-10,r:18,type:t,col:false,bounce:0});
    }
    // Spawn powerups
    if(frame%380===0&&Math.random()<.55){
      const pt=piste[Math.floor(piste.length*.3)];
      powerups.push({x:pt.x+(Math.random()-.5)*40,y:pt.y-10,type:['shield','magnet','slow'][Math.floor(Math.random()*3)],r:16,col:false});
    }
    // Move
    crystals.forEach(c=>{c.y+=speed;c.bounce=(c.bounce||0)+.15;});
    crystals=crystals.filter(c=>{
      if(!c.col&&c.y>H+20){combo=0;return false;}
      return c.y<H+30;
    });
    powerups.forEach(p=>p.y+=speed);
    powerups=powerups.filter(p=>p.y<H+30&&!p.col);
    if(magnetT>0){magnetT--;if(magnetT<=0)magnet=false;}
    if(magnet){
      crystals.forEach(c=>{if(c.col||c.type==='red')return;const cx=W*.5,cy=H*.75;const dx=cx-c.x,dy=cy-c.y;const d=Math.sqrt(dx*dx+dy*dy);if(d<160){c.x+=dx/d*3.5;c.y+=dy/d*3.5;}});
    }
    ctx.clearRect(0,0,W,H);
    // Piste prismatique
    piste.forEach((p,i)=>{
      const g=ctx.createLinearGradient(p.x-p.w/2,p.y,p.x+p.w/2,p.y+p.h);
      g.addColorStop(0,`hsl(${(i*20+frame*.5)%360},60%,55%)`); g.addColorStop(1,'rgba(255,255,255,.15)');
      ctx.fillStyle=g; ctx.beginPath();
      ctx.ellipse(p.x,p.y+p.h/2,p.w/2,p.h/2,0,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle='rgba(255,255,255,.3)';ctx.lineWidth=1;ctx.stroke();
    });
    // Cristaux
    crystals.forEach(c=>{
      if(c.col)return;
      const bob=Math.sin(c.bounce)*4;
      const cols={normal:'rgba(180,255,180,.9)',red:'rgba(255,60,60,.9)',gold:'#FFD700',blue:'rgba(100,220,255,.9)'};
      const glow=ctx.createRadialGradient(c.x,c.y+bob,2,c.x,c.y+bob,c.r);
      glow.addColorStop(0,cols[c.type]);glow.addColorStop(1,'rgba(0,0,0,0)');
      ctx.fillStyle=glow;ctx.beginPath();ctx.arc(c.x,c.y+bob,c.r*1.4,0,Math.PI*2);ctx.fill();
      ctx.fillStyle=cols[c.type];ctx.beginPath();ctx.arc(c.x,c.y+bob,c.r,0,Math.PI*2);ctx.fill();
      ctx.fillStyle='rgba(255,255,255,.6)';ctx.beginPath();ctx.arc(c.x-c.r*.25,c.y+bob-c.r*.25,c.r*.3,0,Math.PI*2);ctx.fill();
      if(c.type==='red'){ctx.fillStyle='rgba(0,0,0,.4)';ctx.font='bold 12px system-ui';ctx.textAlign='center';ctx.fillText('✗',c.x,c.y+bob+5);}
      if(c.type==='gold'){ctx.fillStyle='rgba(0,0,0,.4)';ctx.font='bold 10px system-ui';ctx.textAlign='center';ctx.fillText('×5',c.x,c.y+bob+4);}
    });
    // Powerups
    powerups.forEach(p=>{if(p.col)return;ctx.font='22px system-ui';ctx.textAlign='center';ctx.fillText(p.type==='shield'?'🛡️':p.type==='magnet'?'🧲':'⏱️',p.x,p.y+8);});
    // Cosmonaute (bas-centre, glisse sur la piste)
    const cosmoX=W*.5, cosmoY=H*.75;
    if(shield){ctx.strokeStyle='rgba(79,195,247,.7)';ctx.lineWidth=3;ctx.beginPath();ctx.arc(cosmoX,cosmoY,30,0,Math.PI*2);ctx.stroke();}
    if(magnet){ctx.strokeStyle='rgba(255,215,0,.5)';ctx.lineWidth=2;ctx.beginPath();ctx.arc(cosmoX,cosmoY,160,0,Math.PI*2);ctx.stroke();}
    drawCosmonaut(ctx,cosmoX,cosmoY,22,0);
    particles=particles.filter(p=>p.life>0);
    particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;ctx.fillStyle=p.col;ctx.globalAlpha=p.life/22;ctx.beginPath();ctx.arc(p.x,p.y,4,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});
    // Combo indicator
    if(combo>=2){ctx.fillStyle='rgba(255,215,0,.7)';ctx.font='bold 13px system-ui';ctx.textAlign='left';ctx.fillText('COMBO x'+combo,8,cv.height-8);}
  };
  loop();
}
"""

# ═══════════════════════════════════════════════════════════════════
# NIVEAU 9 — Lune d'Éclipse (Boss Fight par HP)
# ═══════════════════════════════════════════════════════════════════
N9_JS = r"""
window.TUTO_TEXT = "Drag pour te déplacer.<br>TAP les projectiles DORÉS pour les renvoyer au boss.<br>TAP les ennemis pour les détruire. Swipe haut pour sauter !";

let cosmo,boss,projs,goldProjs,minions,lasers,particles,rafId;
let shield,superShot,superShotT,frame,rageMode,rageT,bossPhase;

function gameReset(){
  cancelAnimationFrame(rafId);
  cosmo={x:0,y:0,vy:0,r:22};
  boss={x:0,y:0,r:0,hp:300,maxHp:300,phase:1,shake:0,regenT:0};
  projs=[]; goldProjs=[]; minions=[]; lasers=[]; particles=[];
  shield=false; superShot=false; superShotT=0; frame=0; rageMode=false; rageT=0; bossPhase=1;
}
window.gameReset=gameReset;

function gameStart(){
  const cv=document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  const W=cv.width,H=cv.height;
  cosmo.x=W/2; cosmo.y=H*.83;
  boss.x=W/2; boss.y=H*.2; boss.r=W*.11;
  // Rage mode si le timer expire (remplace l'accès direct à timerSec)
  window.GPS0_onTimerExpired = function(){ if(!rageMode){ rageMode=true; rageT=150; } };
  let dragging=false,dragBase=null,dragStartX=null;
  cv.addEventListener('pointerdown',e=>{
    dragging=true; dragBase=cosmo.x; dragStartX=e.clientX;
    // Tap gold / minion
    const tx=e.offsetX,ty=e.offsetY;
    goldProjs.forEach((p,i)=>{
      const dx=tx-p.x,dy=ty-p.y;
      if(Math.sqrt(dx*dx+dy*dy)<p.r+22){
        const ang=Math.atan2(boss.y-p.y,boss.x-p.x);
        const spd=superShot?16:10;
        projs.push({x:p.x,y:p.y,vx:Math.cos(ang)*spd,vy:Math.sin(ang)*spd,r:11,toBoss:true});
        goldProjs.splice(i,1);
        for(let j=0;j<6;j++)particles.push({x:p.x,y:p.y,vx:(Math.random()-.5)*5,vy:-3,life:20,col:'#FFD700'});
      }
    });
    minions.forEach((m,i)=>{const dx=tx-m.x,dy=ty-m.y;if(Math.sqrt(dx*dx+dy*dy)<m.r+18){m.hp--;if(m.hp<=0){for(let j=0;j<6;j++)particles.push({x:m.x,y:m.y,vx:(Math.random()-.5)*5,vy:-3,life:20,col:'rgba(180,100,220,.9)'});minions.splice(i,1);addDust(3);}}});
  });
  cv.addEventListener('pointermove',e=>{if(!dragging)return;cosmo.x=Math.max(cosmo.r,Math.min(W-cosmo.r,dragBase+(e.clientX-dragStartX)));});
  cv.addEventListener('pointerup',()=>{dragging=false;});
  let swStart=null;
  cv.addEventListener('touchstart',e=>{swStart=e.touches[0].clientY;},{passive:true});
  cv.addEventListener('touchend',e=>{if(!swStart)return;const dy=e.changedTouches[0].clientY-swStart;if(dy<-40&&cosmo.y>=H*.78)cosmo.vy=-10;swStart=null;});
  const ctx=cv.getContext('2d');
  const loop=()=>{
    rafId=requestAnimationFrame(loop);
    if(!GPS0_running())return;
    frame++;
    // Phase par HP
    const hpPct=boss.hp/boss.maxHp;
    if(hpPct<=.33&&bossPhase<3){bossPhase=3;boss.phase=3;_phaseFlash(ctx,'ÉCLIPSE !','#ff2020');}
    else if(hpPct<=.66&&bossPhase<2){bossPhase=2;boss.phase=2;_phaseFlash(ctx,'COLÈRE !','#ff8800');}
    // Rage mode (déclenché par GPS0_onTimerExpired)
    if(rageMode){rageT--;if(rageT<=0)endGame(false);}
    const spd=rageMode?2:1, fq=rageMode?18:(bossPhase===1?80:bossPhase===2?48:30);
    // Boss physique
    const W=cv.width,H=cv.height;
    boss.y=H*.2+Math.sin(frame*.02)*12;
    if(boss.shake>0){boss.x=W/2+(Math.random()-.5)*boss.shake*8;boss.shake*=.78;}
    // Cosmonaut physique
    cosmo.vy+=.4; cosmo.y+=cosmo.vy;
    cosmo.y=Math.max(H*.65,Math.min(H*.9,cosmo.y));
    if(cosmo.y>=H*.9)cosmo.vy=0;
    // Tir boss
    if(frame%Math.floor(fq/spd)===0)_bossShoot(W,H,spd);
    // Mini-ennemis
    const mInt=bossPhase===1?120:bossPhase===2?70:45;
    if(frame%Math.floor(mInt/spd)===0&&minions.length<8)minions.push({x:boss.x+(Math.random()-.5)*boss.r*3,y:boss.y+boss.r,vx:(Math.random()-.5)*2,vy:2+Math.random(),r:15,hp:bossPhase>=2?2:1});
    // Lasers phase 2+
    if(bossPhase>=2&&frame%Math.floor(110/spd)===60){const ly=H*.48+Math.random()*H*.3;lasers.push({y:ly,timer:bossPhase===2?42:28,firing:false});}
    // Charges boss phase 2+
    if(bossPhase>=2&&frame%Math.floor(260/spd)===0){const dir=Math.random()<.5?-1:1;projs.push({x:boss.x,y:boss.y+boss.r,vx:dir*2.5*spd,vy:3.5*spd,r:30,charge:true,toBoss:false});}
    // Régén HP phase 3
    if(bossPhase===3&&!rageMode){boss.regenT++;if(boss.regenT%90===0&&boss.hp<boss.maxHp)boss.hp=Math.min(boss.maxHp,boss.hp+2);}
    // Power-ups
    if(frame%280===0)projs.push({x:W*.15+Math.random()*W*.7,y:boss.y+boss.r,vx:0,vy:1.5*spd,r:14,isPu:true,puType:Math.random()<.5?'shield':'super',toBoss:false});
    // Move projs
    projs=projs.filter(p=>{
      p.x+=p.vx; p.y+=p.vy;
      if(p.isPu){if(Math.sqrt((p.x-cosmo.x)**2+(p.y-cosmo.y)**2)<cosmo.r+p.r){if(p.puType==='shield')shield=true;else{superShot=true;superShotT=320;}for(let i=0;i<5;i++)particles.push({x:p.x,y:p.y,vx:(Math.random()-.5)*4,vy:-3,life:18,col:p.puType==='shield'?'#5af0ff':'#FFD700'});return false;}return p.y<H+35;}
      if(p.toBoss){const dx=p.x-boss.x,dy=p.y-boss.y;if(Math.sqrt(dx*dx+dy*dy)<boss.r){const dmg=superShot?28:12;boss.hp=Math.max(0,boss.hp-dmg);boss.shake=3;addDust(superShot?8:5);for(let i=0;i<8;i++)particles.push({x:boss.x,y:boss.y,vx:(Math.random()-.5)*6,vy:-4+Math.random()*3,life:24,col:'rgba(255,80,80,.9)'});if(boss.hp<=0){const ph=bossPhase;addDust(ph===1?15:ph===2?12:rageMode?8:10);endGame(true);return false;}return false;}return p.y>-30&&p.y<H+30&&p.x>-30&&p.x<W+30;}
      if(p.charge){if(Math.sqrt((p.x-cosmo.x)**2+(p.y-cosmo.y)**2)<cosmo.r+p.r*.6){if(!shield)loseLife();else shield=false;return false;}return p.y<H+35;}
      if(!p.toBoss){const dx=p.x-cosmo.x,dy=p.y-cosmo.y;if(Math.sqrt(dx*dx+dy*dy)<cosmo.r+p.r){if(!shield)loseLife();else{shield=false;for(let i=0;i<5;i++)particles.push({x:cosmo.x,y:cosmo.y,vx:(Math.random()-.5)*5,vy:-3,life:18,col:'#5af0ff'});}return false;}}
      return p.y<H+35&&p.y>-35&&p.x>-35&&p.x<W+35;
    });
    goldProjs=goldProjs.filter(p=>{p.x+=p.vx;p.y+=p.vy;return p.y<H+35;});
    minions=minions.filter(m=>{m.x+=m.vx;m.y+=m.vy;if(m.y>H+25)return false;const dx=m.x-cosmo.x,dy=m.y-cosmo.y;if(Math.sqrt(dx*dx+dy*dy)<cosmo.r+m.r){if(!shield)loseLife();return false;}return true;});
    lasers=lasers.filter(l=>{l.timer--;if(l.timer===0&&!l.firing){l.firing=true;l.timer=22;}else if(l.timer===0&&l.firing){if(Math.abs(cosmo.y-l.y)<22){if(!shield)loseLife();}return false;}return true;});
    if(superShotT>0){superShotT--;if(superShotT<=0)superShot=false;}
    // Draw
    ctx.clearRect(0,0,W,H);
    const darkAlpha=bossPhase===3?.38:0;
    const eclG=ctx.createRadialGradient(W/2,0,0,W/2,0,H);
    eclG.addColorStop(0,'rgba(80,40,120,.55)');eclG.addColorStop(1,'rgba(5,0,20,.95)');
    ctx.fillStyle=eclG;ctx.fillRect(0,0,W,H);
    for(let i=0;i<8;i++){const a=(i/8)*Math.PI*2+frame*.005;ctx.strokeStyle='rgba(255,200,50,.15)';ctx.lineWidth=25;ctx.beginPath();ctx.moveTo(W/2,boss.y);ctx.lineTo(W/2+Math.cos(a)*H,boss.y+Math.sin(a)*H);ctx.stroke();}
    if(darkAlpha>0){ctx.fillStyle=`rgba(0,0,0,${darkAlpha})`;ctx.fillRect(0,0,W,H);}
    // Boss
    ctx.fillStyle='rgba(18,8,38,.97)';ctx.beginPath();ctx.arc(boss.x,boss.y,boss.r,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle=`rgba(${bossPhase===3?'255,30,30':bossPhase===2?'255,120,0':'120,60,220'},.8)`;ctx.lineWidth=4;ctx.stroke();
    const ep=.8+.2*Math.sin(frame*.08);
    ctx.fillStyle=bossPhase===3?'rgba(255,60,60,.95)':'rgba(220,100,255,.95)';
    ctx.beginPath();ctx.arc(boss.x,boss.y-boss.r*.1,boss.r*.35*ep,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='rgba(0,0,0,.8)';ctx.beginPath();ctx.arc(boss.x,boss.y-boss.r*.1,boss.r*.17,0,Math.PI*2);ctx.fill();
    // HP bar
    const bpw=W*.62,bpx=(W-bpw)/2;
    ctx.fillStyle='rgba(0,0,0,.6)';ctx.fillRect(bpx,15,bpw,15);
    const hcol=boss.hp/boss.maxHp>.5?'#a040ff':boss.hp/boss.maxHp>.25?'#ff7020':'#ff2020';
    ctx.fillStyle=hcol;ctx.fillRect(bpx,15,bpw*(boss.hp/boss.maxHp),15);
    if(rageMode){ctx.fillStyle='rgba(255,0,0,.5)';ctx.fillRect(bpx,15,bpw*(boss.hp/boss.maxHp),15);}
    ctx.strokeStyle='rgba(255,255,255,.25)';ctx.lineWidth=1;ctx.strokeRect(bpx,15,bpw,15);
    ctx.fillStyle='rgba(255,255,255,.7)';ctx.font='bold 9px system-ui';ctx.textAlign='center';
    ctx.fillText(rageMode?'⚡ RAGE MODE ⚡':'BOSS — Phase '+bossPhase,W/2,26);
    // Lasers
    lasers.forEach(l=>{if(!l.firing){ctx.strokeStyle='rgba(255,50,50,.55)';ctx.lineWidth=2;ctx.setLineDash([10,8]);ctx.beginPath();ctx.moveTo(0,l.y);ctx.lineTo(W,l.y);ctx.stroke();ctx.setLineDash([]);}else{ctx.strokeStyle='rgba(255,60,60,.95)';ctx.lineWidth=9;ctx.beginPath();ctx.moveTo(0,l.y);ctx.lineTo(W,l.y);ctx.stroke();}});
    projs.forEach(p=>{if(p.isPu){ctx.font='20px system-ui';ctx.textAlign='center';ctx.fillText(p.puType==='shield'?'🛡️':'⚡',p.x,p.y+7);return;}if(p.charge){ctx.fillStyle='rgba(120,50,220,.7)';ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();}else if(p.toBoss){ctx.fillStyle='rgba(255,215,0,.9)';ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();}else{ctx.fillStyle='rgba(50,15,90,.88)';ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();ctx.strokeStyle='rgba(120,60,200,.7)';ctx.lineWidth=2;ctx.stroke();}});
    goldProjs.forEach(p=>{const g=ctx.createRadialGradient(p.x,p.y,2,p.x,p.y,p.r);g.addColorStop(0,'rgba(255,215,0,.95)');g.addColorStop(1,'rgba(255,150,0,0)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(p.x,p.y,p.r*1.5,0,Math.PI*2);ctx.fill();ctx.fillStyle='rgba(255,215,0,.9)';ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();ctx.fillStyle='rgba(0,0,0,.4)';ctx.font='bold 9px system-ui';ctx.textAlign='center';ctx.fillText('TAP',p.x,p.y+4);});
    minions.forEach(m=>{ctx.fillStyle='rgba(100,40,180,.88)';ctx.beginPath();ctx.arc(m.x,m.y,m.r,0,Math.PI*2);ctx.fill();ctx.fillStyle='rgba(0,0,0,.4)';ctx.font='9px system-ui';ctx.textAlign='center';ctx.fillText(m.hp>1?'TAP×2':'TAP',m.x,m.y+4);});
    particles=particles.filter(p=>p.life>0);
    particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;ctx.fillStyle=p.col;ctx.globalAlpha=p.life/24;ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});
    if(shield){ctx.strokeStyle='rgba(79,195,247,.7)';ctx.lineWidth=3;ctx.beginPath();ctx.arc(cosmo.x,cosmo.y,cosmo.r+9,0,Math.PI*2);ctx.stroke();}
    if(superShot){ctx.strokeStyle='rgba(255,215,0,.7)';ctx.lineWidth=3;ctx.beginPath();ctx.arc(cosmo.x,cosmo.y,cosmo.r+16,0,Math.PI*2);ctx.stroke();}
    drawCosmonaut(ctx,cosmo.x,cosmo.y,cosmo.r,0);
    ctx.fillStyle='rgba(255,255,255,.4)';ctx.font='10px system-ui';ctx.textAlign='center';ctx.fillText('DRAG déplacer · TAP doré · TAP ennemi · Swipe↑ sauter',W/2,H-5);
  };
  loop();
}
function _bossShoot(W,H,spd){
  const ang=Math.atan2(cosmo.y-boss.y,cosmo.x-boss.x);
  const bspd=(bossPhase===1?3.5:bossPhase===2?5.5:7.5)*spd;
  const spread=bossPhase===1?1:bossPhase===2?2:3;
  for(let i=0;i<spread;i++){
    const a=ang+(i-Math.floor(spread/2))*.28;
    const isGold=Math.random()<(bossPhase===1?.5:bossPhase===2?.35:.22);
    if(isGold)goldProjs.push({x:boss.x,y:boss.y+boss.r*.8,vx:Math.cos(a)*bspd*.8,vy:Math.sin(a)*bspd*.8,r:15});
    else projs.push({x:boss.x,y:boss.y+boss.r*.8,vx:Math.cos(a)*bspd,vy:Math.sin(a)*bspd,r:12,toBoss:false});
  }
  // Spirale phase 3
  if(bossPhase===3&&frame%60===0){for(let i=0;i<6;i++){const a=(i/6)*Math.PI*2+frame*.03;projs.push({x:boss.x,y:boss.y,vx:Math.cos(a)*3.5,vy:Math.sin(a)*3.5,r:10,toBoss:false,spiral:true});}}
}
function _phaseFlash(ctx,txt,col){
  const el=document.createElement('div');
  el.style.cssText=`position:fixed;inset:0;z-index:200;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0);color:${col};font-size:3rem;font-weight:900;text-shadow:0 0 30px ${col};pointer-events:none`;
  el.textContent=txt; document.body.appendChild(el);
  setTimeout(()=>el.remove(),1400);
}
"""

# ─── BACKGROUNDS ───────────────────────────────────────────────────────────────
BG = [
    '',
    'background:url("../assets/backgrounds/bg-n1.svg") no-repeat center/cover;',
    'background:radial-gradient(ellipse at 50% 90%,rgba(255,80,0,.28) 0%,transparent 60%),linear-gradient(180deg,#1a0800 0%,#0d0008 100%);',
    'background:radial-gradient(ellipse at 30% 40%,rgba(30,120,20,.18) 0%,transparent 60%),linear-gradient(160deg,#040c04 0%,#0a1408 100%);',
    'background:radial-gradient(ellipse at 50% 20%,rgba(100,200,255,.14) 0%,transparent 60%),linear-gradient(180deg,#060e18 0%,#020810 100%);',
    'background:radial-gradient(ellipse at 50% 50%,rgba(60,0,100,.1) 0%,transparent 70%),linear-gradient(180deg,#020004 0%,#000 100%);',
    'background:radial-gradient(ellipse at 40% 40%,rgba(140,140,160,.1) 0%,transparent 60%),linear-gradient(135deg,#0a0a10 0%,#080810 100%);',
    'background:radial-gradient(ellipse at 50% 20%,rgba(80,40,160,.2) 0%,transparent 60%),linear-gradient(180deg,#080414 0%,#0a0820 100%);',
    'background:radial-gradient(ellipse at 40% 60%,rgba(0,150,200,.1) 0%,transparent 50%),radial-gradient(ellipse at 70% 30%,rgba(200,0,150,.07) 0%,transparent 50%),linear-gradient(135deg,#050814 0%,#081020 100%);',
    'background:radial-gradient(ellipse at 50% 20%,rgba(200,150,0,.16) 0%,rgba(100,0,150,.1) 40%,transparent 70%),linear-gradient(180deg,#080010 0%,#040008 100%);',
]

GAME_JS = [None, N1_JS, N2_JS, N3_JS, N4_JS, N5_JS, N6_JS, N7_JS, N8_JS, N9_JS]

for n in range(1, 10):
    path = os.path.join(OUT, f'niveau{n}.html')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html(n, BG[n], GAME_JS[n]))
    size = os.path.getsize(path)
    print(f'  ✅ niveau{n}.html — {size//1024}KB')

print('\n🌙 9 mini-jeux Bug 14 générés !')
