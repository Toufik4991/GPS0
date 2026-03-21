#!/usr/bin/env python3
"""GPS0 Bug 13 — Générateur des 9 mini-jeux complets (refonte totale)"""
import os

OUTDIR = os.path.join(os.path.dirname(__file__), 'minijeux')

LUNE_NAMES = ['','Lune de Verre','Lune de Cendre','Lune de Lierre','Lune de Givre',
              "Lune d'Ombre","Lune de Fer","Lune de Tempête","Lune de Cristal","Lune d'Éclipse"]
LUNE_EMOJIS = ['','🌑','🌒','🌓','🌔','🌕','🌖','🌗','🌘','🌑']

# ── SHARED TEMPLATE ────────────────────────────────────────────────────────────
def make_html(niveau, extra_style, extra_html, extra_js, tuto_text, bg_css):
    name = LUNE_NAMES[niveau]
    emoji = LUNE_EMOJIS[niveau]
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover">
<title>GPS0 — {name}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0A0A1A;color:#fff;font-family:system-ui,sans-serif;overflow:hidden;height:100dvh;display:flex;flex-direction:column;touch-action:none;user-select:none}}
#bg{{position:fixed;inset:0;z-index:0;{bg_css}}}
#hud{{position:relative;z-index:20;display:flex;align-items:center;gap:10px;padding:8px 12px;background:rgba(0,0,0,.65);flex-shrink:0;backdrop-filter:blur(6px)}}
#lives{{font-size:1.2rem;letter-spacing:2px}}
#timer{{flex:1;text-align:center;font-size:1rem;font-weight:bold;color:#4FC3F7}}
#score-hud{{font-size:.9rem;color:#FFD700;font-weight:bold}}
#game-container{{flex:1;position:relative;overflow:hidden;z-index:1}}
canvas{{display:block;width:100%;height:100%}}
#overlay{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(0,0,0,.88);z-index:20;gap:14px;text-align:center;padding:24px}}
#overlay h2{{font-size:1.8rem;color:#C8A2C8}}
#overlay p{{font-size:.9rem;color:rgba(255,255,255,.8);max-width:280px;line-height:1.5}}
#overlay .btn{{padding:12px 32px;border:none;border-radius:14px;font-size:1rem;font-weight:bold;cursor:pointer;background:linear-gradient(135deg,#C8A2C8,#8860a8);color:#fff}}
:root{{--accent:#C8A2C8;--gold:#FFD700;--blue:#4FC3F7}}
{extra_style}
</style>
</head>
<body>
<div id="bg"></div>
<div id="hud">
  <span id="lives">❤❤❤</span>
  <span id="timer">3:00</span>
  <span id="score-hud">0 ✨</span>
</div>
<div id="game-container">
  <canvas id="cv"></canvas>
{extra_html}
  <div id="overlay">
    <div style="font-size:3rem">{emoji}</div>
    <h2>{name}</h2>
    <p>{tuto_text}</p>
    <button class="btn" id="btn-start">C'est parti&nbsp;!</button>
  </div>
  <canvas id="selfie-cv" width="64" height="64" style="display:none" aria-hidden="true"></canvas>
</div>
<script>
// ── COMMON ENGINE ──
const NIVEAU = {niveau};
let lives = 3, dust = 0, running = false, gameover = false;
let timerSec = 180, timerInterval = null;
const livesEl = document.getElementById('lives');
const timerEl = document.getElementById('timer');
const scoreEl = document.getElementById('score-hud');
const overlay = document.getElementById('overlay');
const btnStart = document.getElementById('btn-start');
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');

function updateLivesHUD(){{livesEl.textContent='❤'.repeat(lives)+'♡'.repeat(Math.max(0,3-lives));}}
function updateTimer(){{const m=Math.floor(timerSec/60),s=timerSec%60;timerEl.textContent=m+':'+(s<10?'0':'')+s;}}
function addDust(n){{dust+=n;scoreEl.textContent=dust+' ✨';}}
function loseLife(){{if(!running)return;lives--;updateLivesHUD();if(lives<=0)endGame(false);}}

function calcDust(){{
  const played = 180 - timerSec;
  let base;
  if(played < 30) base = 1 + Math.floor(Math.random()*5);
  else if(played < 60) base = 5 + Math.floor(Math.random()*10);
  else if(played < 120) base = 15 + Math.floor(Math.random()*15);
  else if(played < 150) base = 30 + Math.floor(Math.random()*10);
  else base = 40 + Math.floor(Math.random()*10);
  return Math.min(50, base + dust);
}}

function endGame(success){{
  if(gameover)return;
  gameover=true; running=false;
  clearInterval(timerInterval);
  const finalDust = success ? Math.min(60, calcDust() + 10) : calcDust();
  setTimeout(()=>{{
    window.parent.postMessage({{source:'gps0_minijeu',success,niveau:NIVEAU,poussieres:finalDust}},'*');
  }}, 600);
}}

function startTimer(){{
  updateTimer();
  timerInterval=setInterval(()=>{{
    if(!running)return;
    timerSec--;updateTimer();
    if(timerSec<=0)endGame({{'9':true}}.hasOwnProperty(String(NIVEAU)) ? false : false);
  }},1000);
}}

// Selfie canvas
let selfieImg = null;
function loadSelfie(){{
  const b64 = localStorage.getItem('gps0_avatar_selfie_base64');
  if(!b64)return;
  const img = new Image();
  img.onload = ()=>{{ selfieImg = img; }};
  img.src = b64;
}}
loadSelfie();

function drawSelfie(x, y, r){{
  if(!selfieImg)return;
  ctx.save();
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI*2); ctx.clip();
  ctx.drawImage(selfieImg, x-r, y-r, r*2, r*2);
  ctx.restore();
}}

function drawCosmonaut(x, y, r, angle){{
  ctx.save();
  ctx.translate(x, y);
  if(angle)ctx.rotate(angle);
  // Body (suit)
  ctx.beginPath();
  ctx.ellipse(0, r*0.5, r*0.55, r*0.7, 0, 0, Math.PI*2);
  ctx.fillStyle='#dde4ee'; ctx.fill();
  // Helmet
  ctx.beginPath(); ctx.arc(0, -r*0.15, r*0.55, 0, Math.PI*2);
  ctx.fillStyle='rgba(60,120,200,0.3)'; ctx.fill();
  ctx.beginPath(); ctx.arc(0, -r*0.15, r*0.55, 0, Math.PI*2);
  ctx.strokeStyle='#8ab4d4'; ctx.lineWidth=2; ctx.stroke();
  // Selfie face
  if(selfieImg){{
    ctx.save(); ctx.beginPath(); ctx.arc(0,-r*0.15,r*0.45,0,Math.PI*2); ctx.clip();
    ctx.drawImage(selfieImg,-r*0.45,-r*0.6,r*0.9,r*0.9); ctx.restore();
  }} else {{
    ctx.fillStyle='rgba(79,195,247,.5)';
    ctx.beginPath(); ctx.arc(0,-r*0.15,r*0.4,0,Math.PI*2); ctx.fill();
  }}
  ctx.restore();
}}

function resizeCanvas(){{
  const gc = document.getElementById('game-container');
  cv.width = gc.clientWidth; cv.height = gc.clientHeight;
}}
resizeCanvas();
window.addEventListener('resize', ()=>{{resizeCanvas(); if(running) onResize && onResize();}});

btnStart.addEventListener('click', ()=>{{
  overlay.style.display='none';
  running=true;
  startTimer();
  gameStart();
}}, {{once:true}});

// ── GAME SPECIFIC ──
{extra_js}
</script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────────
# N1 : Angry Birds / Slingshot
# ─────────────────────────────────────────────────────────────────────────────
n1_js = r"""
const GRAV = 0.45, MAX_SHOTS = 15;
let shots_left = MAX_SHOTS, phase = 'idle'; // idle | aiming | flying
let sling = {x:0,y:0}, anchor = {x:0,y:0};
let ball = null, trail = [];
let targets = [], particles = [];
let camX = 0, WORLD_W = 0;

function onResize() {
  sling.x = cv.width * 0.18;
  sling.y = cv.height * 0.72;
  anchor.x = sling.x; anchor.y = sling.y;
  if(WORLD_W < cv.width * 3) WORLD_W = cv.width * 3;
}

function buildTargets() {
  targets = [];
  const cols = ['rgba(180,220,255,0.9)', 'rgba(140,200,255,0.8)', 'rgba(200,240,255,0.85)'];
  // Structures procedurales: colonnes de blocs
  for(let g = 0; g < 7; g++) {
    const bx = cv.width * 0.5 + g * (cv.width * 0.3);
    const rows = 2 + Math.floor(Math.random()*4);
    for(let r = 0; r < rows; r++) {
      targets.push({
        x: bx + (Math.random()-0.5)*60,
        y: cv.height*0.72 - 36*r - 18,
        w: 36, h: 36,
        hp: 2, hit: false, dy: 0,
        col: cols[Math.floor(Math.random()*cols.length)],
        hasDust: Math.random() < 0.4
      });
    }
  }
}

function gameStart() {
  onResize(); WORLD_W = cv.width * 3;
  buildTargets();
  requestAnimationFrame(loop);
}

let touchStart = null;
cv.addEventListener('pointerdown', e => {
  if(!running || phase !== 'idle') return;
  const dx = e.offsetX - sling.x, dy = e.offsetY - sling.y;
  if(Math.sqrt(dx*dx+dy*dy) < 60) { phase = 'aiming'; touchStart = {x: e.offsetX, y: e.offsetY}; }
});
cv.addEventListener('pointermove', e => {
  if(phase !== 'aiming') return;
  const dx = Math.min(80, Math.max(-80, e.offsetX - sling.x));
  const dy = Math.min(80, Math.max(-80, e.offsetY - sling.y));
  anchor = {x: sling.x + dx, y: sling.y + dy};
});
cv.addEventListener('pointerup', e => {
  if(phase !== 'aiming') return;
  const dx = sling.x - anchor.x, dy = sling.y - anchor.y;
  const spd = Math.sqrt(dx*dx+dy*dy);
  if(spd < 10) { phase = 'idle'; anchor = {...sling}; return; }
  ball = {x: anchor.x + camX, y: anchor.y, vx: dx*0.22, vy: dy*0.22, r: 20};
  trail = [];
  phase = 'flying'; anchor = {...sling};
  shots_left--;
  if(shots_left <= 0 && !ball) endGame(false);
});

function loop() {
  if(!running) return;
  requestAnimationFrame(loop);
  const W = cv.width, H = cv.height;
  ctx.clearRect(0,0,W,H);

  // BG stars
  ctx.fillStyle='rgba(0,0,0,0)';
  ctx.clearRect(0,0,W,H);

  // Camera follow ball
  if(ball) {
    const target = ball.x - camX - W*0.3;
    if(target > 0) camX += target * 0.08;
    camX = Math.max(0, Math.min(WORLD_W - W, camX));
  }

  // Draw targets
  targets.forEach(t => {
    if(t.hit) {
      t.y += t.dy; t.dy += 0.3;
      if(t.y > H+50) return;
    }
    ctx.save();
    ctx.fillStyle = t.col;
    ctx.strokeStyle = 'rgba(255,255,255,0.6)';
    ctx.lineWidth = 2;
    const tx = t.x - camX;
    ctx.beginPath();
    roundRect(ctx, tx-t.w/2, t.y-t.h/2, t.w, t.h, 6);
    ctx.fill(); ctx.stroke();
    if(t.hasDust && !t.hit) {
      ctx.fillStyle='#FFD700';
      ctx.font='14px system-ui'; ctx.textAlign='center';
      ctx.fillText('✨', tx, t.y+6);
    }
    ctx.restore();
  });

  // Draw ground
  ctx.fillStyle='rgba(40,60,100,0.6)';
  ctx.fillRect(0, H*0.72+20, W, H);

  // Draw sling
  ctx.strokeStyle='#8a6a40'; ctx.lineWidth=4;
  ctx.beginPath(); ctx.moveTo(sling.x-14, sling.y); ctx.lineTo(sling.x-14, sling.y+30); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(sling.x+14, sling.y); ctx.lineTo(sling.x+14, sling.y+30); ctx.stroke();

  if(phase === 'aiming') {
    // Rubber band
    ctx.strokeStyle='#c8a264'; ctx.lineWidth=3;
    ctx.beginPath(); ctx.moveTo(sling.x-14, sling.y); ctx.lineTo(anchor.x, anchor.y); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(sling.x+14, sling.y); ctx.lineTo(anchor.x, anchor.y); ctx.stroke();
    // Trajectory preview
    let px = anchor.x + camX, py = anchor.y;
    let pvx = (sling.x - anchor.x)*0.22, pvy = (sling.y - anchor.y)*0.22;
    ctx.fillStyle='rgba(255,255,255,0.4)';
    for(let i=0;i<18;i++) {
      px+=pvx; py+=pvy; pvy+=GRAV;
      ctx.beginPath(); ctx.arc(px-camX, py, 3, 0, Math.PI*2); ctx.fill();
    }
    // Cosmonaute visant
    drawCosmonaut(anchor.x, anchor.y, 20, 0);
  }

  // Ball in flight
  if(ball) {
    trail.push({x: ball.x - camX, y: ball.y});
    if(trail.length > 20) trail.shift();
    trail.forEach((p,i) => {
      const a = i/trail.length*0.5;
      ctx.fillStyle=`rgba(79,195,247,${a})`;
      ctx.beginPath(); ctx.arc(p.x, p.y, ball.r*(i/trail.length*0.6+0.2), 0, Math.PI*2);
      ctx.fill();
    });
    ball.vx *= 0.995; ball.vy += GRAV;
    ball.x += ball.vx; ball.y += ball.vy;
    const bsx = ball.x - camX;
    drawCosmonaut(bsx, ball.y, ball.r, Math.atan2(ball.vy, ball.vx));

    // Collision targets
    targets.forEach(t => {
      if(t.hit) return;
      const dx = (ball.x - t.x), dy = (ball.y - t.y);
      if(Math.abs(dx) < t.w/2 + ball.r && Math.abs(dy) < t.h/2 + ball.r) {
        t.hit = true; t.dy = -4 + Math.random()*2;
        t.hp--;
        // Particles
        for(let i=0;i<8;i++) particles.push({x:t.x-camX,y:t.y,vx:(Math.random()-.5)*5,vy:-3+Math.random()*2,life:30,col:t.col});
        if(t.hasDust) { addDust(3); t.hasDust = false; }
      }
    });

    // Hit ground
    if(ball.y > H*0.72 + 20) {
      ball = null; phase = 'idle';
      if(shots_left <= 0) {
        const alive = targets.filter(t=>!t.hit).length;
        endGame(alive === 0);
      }
    }
    // Out of world
    if(ball && ball.x > WORLD_W + 200) { ball = null; phase = 'idle'; }
  }

  // Particles
  particles = particles.filter(p => p.life > 0);
  particles.forEach(p => {
    p.x+=p.vx; p.y+=p.vy; p.vy+=0.15; p.life--;
    ctx.fillStyle = p.col; ctx.globalAlpha = p.life/30;
    ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI*2); ctx.fill();
    ctx.globalAlpha=1;
  });

  // Idle cosmonaute in sling
  if(phase === 'idle') {
    drawCosmonaut(sling.x, sling.y, 20, 0);
  }

  // HUD shots
  ctx.fillStyle='rgba(255,255,255,.8)';
  ctx.font='bold 13px system-ui'; ctx.textAlign='left';
  ctx.fillText('Tirs: ' + shots_left + '/' + MAX_SHOTS, 8, cv.height-10);

  // Check win
  if(targets.length > 0 && targets.every(t=>t.hit)) { setTimeout(()=>endGame(true), 500); }
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y); ctx.quadraticCurveTo(x+w,y,x+w,y+r);
  ctx.lineTo(x+w,y+h-r); ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
  ctx.lineTo(x+r,y+h); ctx.quadraticCurveTo(x,y+h,x,y+h-r);
  ctx.lineTo(x,y+r); ctx.quadraticCurveTo(x,y,x+r,y);
  ctx.closePath();
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# N2 : Flappy Bird / Lune de Cendre
# ─────────────────────────────────────────────────────────────────────────────
n2_js = r"""
const GRAV_BASE = 0.38, JUMP = -5.5;
let bird = {x:0,y:0,vy:0,r:22};
let pipes = [], dustItems = [], particles = [];
let speed = 2, frameCount = 0;

function gameStart() {
  bird.x = cv.width * 0.25;
  bird.y = cv.height * 0.45;
  bird.vy = 0;
  pipes = []; dustItems = []; particles = [];
  speed = 2; frameCount = 0;
  spawnPipe();
  cv.addEventListener('pointerdown', jump);
  requestAnimationFrame(loop);
}

function jump() { if(!running)return; bird.vy = JUMP; }

function spawnPipe() {
  const W = cv.width, H = cv.height;
  const gap = H * 0.34;
  const topH = H * 0.1 + Math.random() * (H * 0.55);
  pipes.push({x: W + 60, top: topH, bot: topH + gap, w: 48, passed: false});
  // Dust in gap
  dustItems.push({x: W + 60 + 24, y: topH + gap/2 + (Math.random()-0.5)*60, r: 14, collected: false});
}

function loop() {
  if(!running)return;
  requestAnimationFrame(loop);
  const W = cv.width, H = cv.height;
  frameCount++;

  // Accelerate
  if(frameCount % 300 === 0) speed = Math.min(5, speed + 0.3);

  // Physics
  bird.vy += GRAV_BASE;
  bird.y += bird.vy;

  // Spawn pipes
  const pipeGap = Math.max(160, 220 - frameCount*0.05);
  if(frameCount % Math.floor(pipeGap) === 0) spawnPipe();

  // Pipe collisions + move
  let alive = true;
  pipes = pipes.filter(p => p.x + p.w > -10);
  pipes.forEach(p => {
    p.x -= speed;
    if(!p.passed && p.x + p.w < bird.x) { p.passed = true; addDust(2); }
    // collision
    if(bird.x + bird.r > p.x && bird.x - bird.r < p.x + p.w) {
      if(bird.y - bird.r < p.top || bird.y + bird.r > p.bot) {
        alive = false;
      }
    }
  });

  // Dust collect
  dustItems.forEach(d => {
    if(d.collected) return;
    d.x -= speed;
    const dx = bird.x - d.x, dy = bird.y - d.y;
    if(Math.sqrt(dx*dx+dy*dy) < bird.r + d.r) { d.collected = true; addDust(5); for(let i=0;i<6;i++) particles.push({x:d.x,y:d.y,vx:(Math.random()-.5)*4,vy:-2+Math.random()*2,life:25}); }
  });
  dustItems = dustItems.filter(d => d.x > -30);

  // Walls
  if(bird.y - bird.r < 0 || bird.y + bird.r > H - 60) alive = false;

  if(!alive) { loseLife(); if(lives>0)bird.vy=JUMP; }

  // Draw
  ctx.clearRect(0,0,W,H);

  // Ground
  ctx.fillStyle='rgba(40,20,0,0.85)';
  ctx.fillRect(0, H-60, W, 60);
  ctx.fillStyle='rgba(255,100,0,0.5)';
  for(let x=0;x<W;x+=40) ctx.fillRect(x, H-62, 36, 4);

  // Pipes (lava columns)
  pipes.forEach(p => {
    const grad = ctx.createLinearGradient(p.x, 0, p.x+p.w, 0);
    grad.addColorStop(0,'rgba(200,50,0,0.9)');
    grad.addColorStop(0.5,'rgba(255,120,0,0.95)');
    grad.addColorStop(1,'rgba(180,40,0,0.9)');
    ctx.fillStyle = grad;
    ctx.fillRect(p.x, 0, p.w, p.top);
    ctx.fillRect(p.x, p.bot, p.w, H);
    // Glow edges
    ctx.fillStyle='rgba(255,70,0,0.4)';
    ctx.fillRect(p.x, p.top-4, p.w+4, 8);
    ctx.fillRect(p.x, p.bot-4, p.w+4, 8);
  });

  // Dust items
  dustItems.forEach(d => {
    if(d.collected) return;
    ctx.fillStyle='#FFD700';
    ctx.font='bold 18px system-ui'; ctx.textAlign='center';
    ctx.fillText('✨', d.x, d.y+6);
  });

  // Particles
  particles = particles.filter(p=>p.life>0);
  particles.forEach(p=>{ p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;
    ctx.fillStyle=`rgba(255,215,0,${p.life/25})`; ctx.beginPath(); ctx.arc(p.x,p.y,3,0,Math.PI*2); ctx.fill(); });

  // Bird / cosmonaut
  drawCosmonaut(bird.x, bird.y, bird.r, bird.vy * 0.05);

  // Ash particles (decorative)
  ctx.fillStyle='rgba(120,100,80,0.3)'; ctx.textAlign='left';
  for(let i=0;i<6;i++) {
    const ax = (frameCount*speed*0.7 + i*W/6) % W;
    ctx.fillRect(ax, (40+i*30+frameCount*0.5)%H, 2, 2);
  }
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# N3 : Doodle Jump / Lune de Lierre
# ─────────────────────────────────────────────────────────────────────────────
n3_js = r"""
const JUMP_SPND = -13, PLAT_MIN = 6, PLAT_MAX = 9, GRAVITY = 0.45;
let cosmo = {x:0,y:0,vx:0,vy:0,r:22,onGround:false};
let platforms = [], dustItems = [], particles = [], worldY = 0, highestY = 0;
let tiltX = 0;

window.addEventListener('deviceorientation', e => { if(!running)return; tiltX = Math.max(-1, Math.min(1, e.gamma/35)); });
let touchDx = 0, lastTx = null;
document.addEventListener('touchstart', e=>{ lastTx = e.touches[0].clientX; }, {passive:true});
document.addEventListener('touchmove', e=>{ if(!running||!lastTx)return; touchDx = (e.touches[0].clientX - lastTx)/50; lastTx = e.touches[0].clientX; }, {passive:true});
document.addEventListener('touchend', ()=>{ touchDx = 0; lastTx = null; });

function makePlatform(y) {
  const types = ['normal','normal','normal','spring','break','break','toxic'];
  const t = types[Math.floor(Math.random()*types.length)];
  return {x: 20 + Math.random()*(cv.width - 120), y, w: 80 + Math.random()*30, h:14, type:t, broken: false};
}

function gameStart() {
  const H = cv.height, W = cv.width;
  cosmo.x = W/2; cosmo.y = H*0.7; cosmo.vx=0; cosmo.vy=0;
  worldY = 0; highestY = cosmo.y;
  platforms = [];
  // Initial platforms
  platforms.push({x: W/2-50, y: H*0.75, w:100, h:14, type:'normal', broken:false});
  for(let i=1;i<24;i++) makePlatformAt(-i*85);
  requestAnimationFrame(loop);
}

function makePlatformAt(y) {
  platforms.push(makePlatform(y));
}

function loop() {
  if(!running)return;
  requestAnimationFrame(loop);
  const W=cv.width, H=cv.height;

  // Horizontal input
  const inputX = tiltX + touchDx;
  cosmo.vx += inputX * 0.8;
  cosmo.vx *= 0.85;

  // Physics
  cosmo.vy += GRAVITY;
  cosmo.x += cosmo.vx;
  cosmo.y += cosmo.vy;

  // Wrap horizontal
  if(cosmo.x < -cosmo.r) cosmo.x = W + cosmo.r;
  if(cosmo.x > W + cosmo.r) cosmo.x = -cosmo.r;

  // Camera: keep cosmo in middle-upper
  if(cosmo.y < H*0.45 + worldY) {
    const diff = (H*0.45 + worldY) - cosmo.y;
    worldY -= diff; cosmo.y += diff;
    // Spawn new platforms ahead
    const topP = platforms.reduce((mn,p)=>Math.min(mn,p.y), 9999);
    while(topP + worldY > -H*0.5) makePlatformAt(topP - 85);
    platforms = platforms.filter(p => p.y + worldY < H + 50);
  }

  // Floor death
  if(cosmo.y - worldY > H + 60) { loseLife(); if(lives>0){ cosmo.y=H*0.7-worldY; cosmo.vy=-8; } return; }

  // Platform collision (only when falling)
  if(cosmo.vy > 0) {
    platforms.forEach(p => {
      const py = p.y - worldY;
      if(cosmo.x > p.x && cosmo.x < p.x + p.w &&
         cosmo.y + cosmo.r > py && cosmo.y + cosmo.r < py + p.h + 14 &&
         !p.broken) {
        if(p.type === 'toxic') { loseLife(); return; }
        if(p.type === 'break') { p.broken = true; setTimeout(()=>{},200); }
        cosmo.vy = p.type === 'spring' ? JUMP_SPND * 1.5 : JUMP_SPND;
        addDust(1);
        for(let i=0;i<5;i++) particles.push({x:cosmo.x,y:py,vx:(Math.random()-.5)*4,vy:-2,life:20,col:p.type==='spring'?'#69FF47':'#a0c840'});
      }
    });
  }

  // Dust items
  dustItems = dustItems.filter(d=>!d.col);
  if(Math.random()<0.004 && dustItems.length < 5) {
    const y = worldY - H*0.3 - Math.random()*H*2;
    dustItems.push({x:20+Math.random()*(W-40), y, col:false});
  }

  // Draw
  ctx.clearRect(0,0,W,H);

  // BG vines decoration
  ctx.strokeStyle='rgba(40,100,40,0.25)'; ctx.lineWidth=2;
  for(let i=0;i<5;i++){
    const vx = (i*W/5+worldY*0.1)%W;
    ctx.beginPath(); ctx.moveTo(vx,0); ctx.bezierCurveTo(vx+20,H/3,vx-20,H*2/3,vx,H); ctx.stroke();
  }

  // Platforms
  platforms.forEach(p=>{
    if(p.broken)return;
    const py=p.y-worldY;
    const cols = {normal:'#4a9a3a', spring:'#3af070', break:'#c8c040', toxic:'#e05050'};
    ctx.fillStyle=cols[p.type]||'#4a9a3a';
    ctx.beginPath(); ctx.ellipse(p.x+p.w/2, py+p.h/2, p.w/2, p.h/2, 0, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle='rgba(255,255,255,0.3)'; ctx.lineWidth=1.5; ctx.stroke();
  });

  // Dust items
  dustItems.forEach(d=>{
    const dy=d.y-worldY;
    if(dy<-20||dy>H+20)return;
    const dx2=cosmo.x-d.x, dy2=cosmo.y-dy+worldY-d.y;
    const dd=Math.sqrt((cosmo.x-d.x)**2+(cosmo.y-(d.y-worldY))**2);
    if(dd<cosmo.r+14){d.col=true;addDust(4);for(let i=0;i<5;i++)particles.push({x:d.x,y:dy,vx:(Math.random()-.5)*4,vy:-2,life:20,col:'#FFD700'});}
    ctx.fillStyle='#FFD700'; ctx.font='18px system-ui'; ctx.textAlign='center';
    ctx.fillText('✨',d.x,dy+6);
  });

  // Particles
  particles=particles.filter(p=>p.life>0);
  particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;
    ctx.fillStyle=p.col||'#69FF47'; ctx.globalAlpha=p.life/20;
    ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});

  // Cosmonaut
  drawCosmonaut(cosmo.x, cosmo.y, cosmo.r, 0);
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# N4 : Lune de Givre — Swing / Stickman
# ─────────────────────────────────────────────────────────────────────────────
n4_js = r"""
let cosmo = {x:0,y:0,vx:0,vy:0,r:22};
let anchors = [], attached = null, rope = {len:0, angle:0, angVel:0};
let dustItems = [], particles = [], spikes = [];
let phase = 'free'; // free | swinging

function gameStart() {
  const W = cv.width, H = cv.height;
  cosmo.x = W*0.1; cosmo.y = H*0.4; cosmo.vx = 2; cosmo.vy = 0;

  // Build anchors (stalactites) across world
  anchors = [];
  for(let i=0; i<12; i++) {
    anchors.push({x: W*0.05 + i*(W*0.09), y: H*0.08 + Math.random()*H*0.12, r:10});
  }

  // Spikes at bottom
  spikes = [];
  for(let i=0; i<Math.floor(W/30); i++) {
    spikes.push({x: i*30 + 15, y: H - 28});
  }

  // Dust
  dustItems = [];
  for(let i=0; i<14; i++) {
    dustItems.push({x:W*0.1+i*(W*0.08), y:H*0.3+Math.random()*H*0.4, r:12, col:false});
  }

  cv.addEventListener('pointerdown', e => {
    if(!running)return;
    if(phase === 'swinging') {
      // Detach on tap: fling
      if(attached) {
        const velMag = rope.angVel * rope.len;
        cosmo.vx = -Math.sin(rope.angle) * velMag * 0.7;
        cosmo.vy = Math.cos(rope.angle) * velMag * 0.7;
      }
      phase = 'free'; attached = null;
    } else {
      // Attach to nearest anchor
      let best = null, bestD = 140;
      anchors.forEach(a => {
        const d = Math.sqrt((cosmo.x-a.x)**2+(cosmo.y-a.y)**2);
        if(d < bestD) { bestD=d; best=a; }
      });
      if(best) {
        attached = best;
        rope.len = Math.sqrt((cosmo.x-best.x)**2+(cosmo.y-best.y)**2);
        rope.angle = Math.atan2(cosmo.y - best.y, cosmo.x - best.x);
        rope.angVel = (cosmo.vx * Math.cos(rope.angle) + cosmo.vy * Math.sin(rope.angle)) / rope.len;
        phase = 'swinging';
      }
    }
  });

  // Swipe to control rope
  let swipeStart = null;
  cv.addEventListener('touchstart', e=>{swipeStart={x:e.touches[0].clientX,y:e.touches[0].clientY};},{passive:true});
  cv.addEventListener('touchmove', e=>{
    if(!swipeStart||phase!=='swinging')return;
    const dy = e.touches[0].clientY - swipeStart.y;
    rope.len = Math.max(40, Math.min(200, rope.len + dy*0.3));
    swipeStart={x:e.touches[0].clientX,y:e.touches[0].clientY};
  },{passive:true});

  requestAnimationFrame(loop);
}

function loop() {
  if(!running)return;
  requestAnimationFrame(loop);
  const W=cv.width, H=cv.height;
  const GRAV=0.4;

  if(phase==='swinging' && attached) {
    // Pendulum physics
    const gravComp = GRAV * Math.cos(rope.angle) / rope.len;
    rope.angVel -= gravComp;
    rope.angVel *= 0.998;
    rope.angle += rope.angVel;
    cosmo.x = attached.x + Math.sin(rope.angle)*rope.len;
    cosmo.y = attached.y + Math.cos(rope.angle)*rope.len;
    cosmo.vx = rope.angVel * rope.len * Math.cos(rope.angle);
    cosmo.vy = rope.angVel * rope.len * Math.sin(rope.angle);
  } else {
    cosmo.vx *= 0.99;
    cosmo.vy += GRAV;
    cosmo.x += cosmo.vx;
    cosmo.y += cosmo.vy;
  }

  // Walls
  if(cosmo.x < cosmo.r) { cosmo.x = cosmo.r; cosmo.vx = Math.abs(cosmo.vx)*0.6; }
  if(cosmo.x > W-cosmo.r) { cosmo.x = W-cosmo.r; cosmo.vx = -Math.abs(cosmo.vx)*0.6; }

  // Spikes
  if(cosmo.y > H - 60) { loseLife(); if(lives>0){cosmo.y=H*0.4;cosmo.x=W*0.1;cosmo.vx=2;cosmo.vy=0;phase='free';attached=null;} return; }

  // Ceiling
  if(cosmo.y < cosmo.r) { cosmo.y=cosmo.r; cosmo.vy=Math.abs(cosmo.vy)*0.5; }

  // Dust collect
  dustItems.forEach(d=>{
    if(d.col)return;
    if(Math.sqrt((cosmo.x-d.x)**2+(cosmo.y-d.y)**2)<cosmo.r+d.r){
      d.col=true; addDust(4);
      for(let i=0;i<6;i++) particles.push({x:d.x,y:d.y,vx:(Math.random()-.5)*5,vy:-3,life:22,col:'#FFD700'});
    }
  });

  ctx.clearRect(0,0,W,H);

  // BG ice effect
  ctx.fillStyle='rgba(160,210,240,0.07)';
  for(let i=0;i<8;i++) ctx.fillRect(i*W/8, 0, 2, H);

  // Stalactites (anchors)
  anchors.forEach(a=>{
    ctx.strokeStyle='rgba(150,220,255,0.8)'; ctx.lineWidth=2;
    ctx.fillStyle='rgba(150,220,255,0.6)';
    ctx.beginPath(); ctx.moveTo(a.x-a.r, 0); ctx.lineTo(a.x+a.r, 0); ctx.lineTo(a.x, a.y+30); ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.arc(a.x, a.y, a.r, 0, Math.PI*2); ctx.fill();
    if(attached===a) {
      ctx.strokeStyle='rgba(79,195,247,.9)'; ctx.lineWidth=3;
      ctx.beginPath(); ctx.arc(a.x, a.y, a.r+4, 0, Math.PI*2); ctx.stroke();
      // Draw rope
      ctx.strokeStyle='rgba(200,230,255,.7)'; ctx.lineWidth=2;
      ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(cosmo.x,cosmo.y); ctx.stroke();
    }
  });

  // Spikes
  ctx.fillStyle='rgba(150,200,230,0.8)';
  spikes.forEach(s=>{
    ctx.beginPath(); ctx.moveTo(s.x-12,H); ctx.lineTo(s.x,s.y); ctx.lineTo(s.x+12,H); ctx.closePath(); ctx.fill();
  });

  // Dust
  dustItems.forEach(d=>{if(!d.col){ctx.fillStyle='#FFD700';ctx.font='18px system-ui';ctx.textAlign='center';ctx.fillText('✨',d.x,d.y+6);}});

  // Particles
  particles=particles.filter(p=>p.life>0);
  particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;
    ctx.fillStyle=p.col;ctx.globalAlpha=p.life/22;ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});

  // Cosmonaut
  drawCosmonaut(cosmo.x, cosmo.y, cosmo.r, 0);

  // Hint
  if(phase==='free'){
    ctx.fillStyle='rgba(255,255,255,.5)';ctx.font='13px system-ui';ctx.textAlign='center';
    ctx.fillText('TAP pour s'accrocher', W/2, H*0.92);
  }
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# N5 : Labyrinthe / Lune d'Ombre — GRAND labyrinthe scrollant, caméra centré
# ─────────────────────────────────────────────────────────────────────────────
n5_js = r"""
const CELL = 28, ROWS = 31, COLS = 31, LIGHT_R = 90;
let maze = [], cosmo = {cx:1,cy:1}, exit_ = {cx:COLS-2,cy:ROWS-2};
let dustItems = [], traps = [], particles = [];
let blindTimer = 0;

// DFS maze generator
function genMaze(C, R) {
  const m = Array.from({length:R}, ()=>Array(C).fill(1));
  function carve(x,y) {
    m[y][x]=0;
    const dirs=[[0,-2],[2,0],[0,2],[-2,0]].sort(()=>Math.random()-.5);
    dirs.forEach(([dx,dy])=>{
      const nx=x+dx,ny=y+dy;
      if(nx>=0&&nx<C&&ny>=0&&ny<R&&m[ny][nx]===1){m[y+dy/2][x+dx/2]=0;carve(nx,ny);}
    });
  }
  carve(1,1); m[ROWS-2][COLS-2]=0; return m;
}

function gameStart() {
  maze = genMaze(COLS, ROWS);
  cosmo = {cx:1,cy:1};
  exit_ = {cx:COLS-2, cy:ROWS-2};
  dustItems=[];
  // Place dusts in dead-ends
  for(let y=1;y<ROWS-1;y+=2) for(let x=1;x<COLS-1;x+=2) {
    if(maze[y][x]===0&&Math.random()<0.12&&!(x===1&&y===1)&&!(x===COLS-2&&y===ROWS-2))
      dustItems.push({cx:x,cy:y,col:false});
  }
  traps=[];
  for(let i=0;i<8;i++) {
    let tx,ty;
    do{tx=1+Math.floor(Math.random()*(COLS-2));ty=1+Math.floor(Math.random()*(ROWS-2));}
    while(maze[ty][tx]!==0||Math.sqrt((tx-1)**2+(ty-1)**2)<5);
    traps.push({cx:tx,cy:ty,phase:0,timer:Math.random()*200});
  }
  blindTimer=0;
  particles=[];

  // Touch swipe
  let ts=null;
  cv.addEventListener('touchstart',e=>{ts={x:e.touches[0].clientX,y:e.touches[0].clientY};},{passive:true});
  cv.addEventListener('touchend',e=>{
    if(!ts||!running)return;
    const dx=e.changedTouches[0].clientX-ts.x, dy=e.changedTouches[0].clientY-ts.y;
    if(Math.abs(dx)>Math.abs(dy)){if(dx>20)move(1,0);else if(dx<-20)move(-1,0);}
    else{if(dy>20)move(0,1);else if(dy<-20)move(0,-1);}
    ts=null;
  },{passive:true});
  document.addEventListener('keydown',e=>{
    if(!running)return;
    if(e.key==='ArrowLeft')move(-1,0);
    if(e.key==='ArrowRight')move(1,0);
    if(e.key==='ArrowUp')move(0,-1);
    if(e.key==='ArrowDown')move(0,1);
  });

  requestAnimationFrame(loop);
}

function move(dx,dy) {
  const nx=cosmo.cx+dx, ny=cosmo.cy+dy;
  if(nx<0||nx>=COLS||ny<0||ny>=ROWS)return;
  if(maze[ny][nx]===1)return;
  cosmo.cx=nx; cosmo.cy=ny;
  addDust(1);
  // Check exit
  if(cosmo.cx===exit_.cx&&cosmo.cy===exit_.cy) endGame(true);
  // Check dust
  dustItems.forEach(d=>{if(!d.col&&d.cx===cosmo.cx&&d.cy===cosmo.cy){d.col=true;addDust(5);for(let i=0;i<8;i++)particles.push({x:cosmo.cx*CELL+CELL/2,y:cosmo.cy*CELL+CELL/2,vx:(Math.random()-.5)*4,vy:-3+Math.random()*2,life:25,col:'#FFD700'});}});
  // Check traps
  traps.forEach(t=>{if(t.phase===0&&t.cx===cosmo.cx&&t.cy===cosmo.cy){blindTimer=Math.max(blindTimer,100);}});
}

function loop() {
  if(!running)return;
  requestAnimationFrame(loop);
  const W=cv.width, H=cv.height;
  if(blindTimer>0)blindTimer--;

  // Traps animate
  traps.forEach(t=>{ t.timer--; if(t.timer<=0){t.phase=t.phase===0?1:0;t.timer=180+Math.random()*120;} });

  // Camera: center on cosmo
  const camPxX = cosmo.cx*CELL + CELL/2;
  const camPxY = cosmo.cy*CELL + CELL/2;
  const offX = W/2 - camPxX;
  const offY = H/2 - camPxY;

  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#000';
  ctx.fillRect(0,0,W,H);

  // Draw revealed cells (within light)
  const lightPx = {x: camPxX, y: camPxY};
  const LR = blindTimer>0 ? 28 : LIGHT_R;

  ctx.save();
  // Clip to circle of light
  ctx.beginPath(); ctx.arc(W/2, H/2, LR, 0, Math.PI*2); ctx.clip();

  // Walls & floor
  for(let y=0;y<ROWS;y++) {
    for(let x=0;x<COLS;x++) {
      const px=x*CELL+offX, py=y*CELL+offY;
      if(maze[y][x]===1) {
        ctx.fillStyle='rgba(30,20,60,0.98)';
        ctx.fillRect(px,py,CELL,CELL);
        ctx.strokeStyle='rgba(80,60,120,0.3)'; ctx.lineWidth=0.5;
        ctx.strokeRect(px,py,CELL,CELL);
      } else {
        ctx.fillStyle='rgba(8,4,20,0.9)';
        ctx.fillRect(px,py,CELL,CELL);
      }
    }
  }

  // Exit door
  const ex=exit_.cx*CELL+offX, ey=exit_.cy*CELL+offY;
  const egrd=ctx.createRadialGradient(ex+CELL/2,ey+CELL/2,2,ex+CELL/2,ey+CELL/2,CELL);
  egrd.addColorStop(0,'rgba(255,215,0,0.9)'); egrd.addColorStop(1,'rgba(255,215,0,0)');
  ctx.fillStyle=egrd; ctx.fillRect(ex,ey,CELL,CELL);
  ctx.font='16px system-ui'; ctx.textAlign='center';
  ctx.fillText('🚪',ex+CELL/2,ey+CELL/2+6);

  // Dust
  dustItems.forEach(d=>{
    if(d.col)return;
    const px=d.cx*CELL+offX+CELL/2, py=d.cy*CELL+offY+CELL/2;
    ctx.fillStyle='#FFD700'; ctx.font='14px system-ui'; ctx.textAlign='center';
    ctx.fillText('✨',px,py+5);
  });

  // Traps (visible only when active)
  traps.forEach(t=>{
    if(t.phase===0)return;
    const px=t.cx*CELL+offX+CELL/2, py=t.cy*CELL+offY+CELL/2;
    ctx.fillStyle='rgba(100,0,200,0.6)'; ctx.beginPath(); ctx.arc(px,py,CELL*0.4,0,Math.PI*2); ctx.fill();
  });

  // Cosmo
  drawCosmonaut(W/2, H/2, 14, 0);

  ctx.restore();

  // Vignette shadow beyond light
  const radGrd = ctx.createRadialGradient(W/2,H/2,LR*0.75,W/2,H/2,LR*1.1+30);
  radGrd.addColorStop(0,'rgba(0,0,0,0)');
  radGrd.addColorStop(1,'rgba(0,0,0,1)');
  ctx.fillStyle=radGrd; ctx.fillRect(0,0,W,H);

  // Particles
  particles=particles.filter(p=>p.life>0);
  particles.forEach(p=>{
    p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;
    const px2=p.x+offX-camPxX+W/2, py2=p.y+offY-camPxY+H/2;
    ctx.fillStyle=p.col; ctx.globalAlpha=p.life/25;
    ctx.beginPath(); ctx.arc(px2, py2,3,0,Math.PI*2); ctx.fill(); ctx.globalAlpha=1;
  });

  if(blindTimer>0) {
    ctx.fillStyle='rgba(80,0,180,0.35)';
    ctx.fillRect(0,0,W,H);
    ctx.fillStyle='rgba(255,255,255,.6)'; ctx.font='13px system-ui'; ctx.textAlign='center';
    ctx.fillText('⚫ Piège d\'ombre !', W/2, H*0.88);
  }

  // Mini map hint
  ctx.fillStyle='rgba(255,255,255,.3)'; ctx.font='11px system-ui'; ctx.textAlign='left';
  ctx.fillText('🚪 Trouve la sortie dorée !', 8, H-10);
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# N6 : Agar.io / Lune de Fer — grow by absorption
# ─────────────────────────────────────────────────────────────────────────────
n6_js = r"""
const WORLD = 1200, DUST_RESPAWN = 10000;
let player = {x:WORLD/2,y:WORLD/2,r:20,vx:0,vy:0};
let enemies = [], dustBlobs = [], particles = [];
let camX = 0, camY = 0;
let lastDust = 0;

function speed() { return Math.max(1.5, 5 - (player.r - 20)/10); }

function spawnEnemies() {
  enemies = [];
  for(let i=0;i<15;i++) {
    const r = 10 + Math.random()*40;
    enemies.push({
      x: Math.random()*WORLD, y: Math.random()*WORLD,
      r, vx: (Math.random()-.5)*1.5, vy: (Math.random()-.5)*1.5,
      col: `hsl(${Math.random()*360},60%,55%)`
    });
  }
}

function spawnDust() {
  dustBlobs = [];
  for(let i=0;i<60;i++) {
    dustBlobs.push({x:Math.random()*WORLD,y:Math.random()*WORLD,r:6,col:false});
  }
}

function gameStart() {
  player={x:WORLD/2,y:WORLD/2,r:20,vx:0,vy:0};
  spawnEnemies(); spawnDust();
  camX=player.x-cv.width/2; camY=player.y-cv.height/2;
  lastDust=Date.now();

  let ptarget={x:player.x,y:player.y};
  cv.addEventListener('pointermove',e=>{ ptarget={x:e.offsetX+camX,y:e.offsetY+camY}; });
  cv.addEventListener('pointerdown',e=>{ ptarget={x:e.offsetX+camX,y:e.offsetY+camY}; });

  function ai() {
    enemies.forEach(en=>{
      // Chase small players; flee from big ones
      const d=Math.sqrt((player.x-en.x)**2+(player.y-en.y)**2);
      if(en.r < player.r - 5 && d < 200) {
        en.vx += (en.x-player.x)/d*0.15;
        en.vy += (en.y-player.y)/d*0.15;
      } else if(en.r > player.r + 5 && d < 200) {
        en.vx += (player.x-en.x)/d*0.1;
        en.vy += (player.y-en.y)/d*0.1;
      }
      // Wander
      en.vx += (Math.random()-.5)*0.1;
      en.vy += (Math.random()-.5)*0.1;
      const spd=Math.sqrt(en.vx**2+en.vy**2);
      if(spd>2){en.vx=en.vx/spd*2;en.vy=en.vy/spd*2;}
      en.x=Math.max(en.r,Math.min(WORLD-en.r,en.x+en.vx));
      en.y=Math.max(en.r,Math.min(WORLD-en.r,en.y+en.vy));
    });
    setTimeout(ai, 50);
  }
  ai();

  setInterval(()=>{
    if(Date.now()-lastDust>DUST_RESPAWN){
      dustBlobs=dustBlobs.filter(d=>d.col===false?false:(d.col=false,true));
      for(let i=dustBlobs.filter(d=>!d.col).length;i<60;i++)
        dustBlobs.push({x:Math.random()*WORLD,y:Math.random()*WORLD,r:6,col:false});
      lastDust=Date.now();
    }
  },1000);

  function loop() {
    if(!running)return;
    requestAnimationFrame(loop);

    // Move player toward pointer
    const dx=ptarget.x-player.x, dy=ptarget.y-player.y;
    const d=Math.sqrt(dx*dx+dy*dy);
    if(d>4){player.vx=dx/d*speed();player.vy=dy/d*speed();}
    player.x=Math.max(player.r,Math.min(WORLD-player.r,player.x+player.vx));
    player.y=Math.max(player.r,Math.min(WORLD-player.r,player.y+player.vy));

    // Cam
    camX += (player.x - cv.width/2 - camX)*0.08;
    camY += (player.y - cv.height/2 - camY)*0.08;
    camX=Math.max(0,Math.min(WORLD-cv.width,camX));
    camY=Math.max(0,Math.min(WORLD-cv.height,camY));

    // Absorb dust
    dustBlobs.forEach(d=>{
      if(d.col)return;
      const dd=Math.sqrt((player.x-d.x)**2+(player.y-d.y)**2);
      if(dd<player.r+d.r){d.col=true;player.r=Math.min(100,player.r+2);addDust(2);
        for(let i=0;i<4;i++)particles.push({x:d.x,y:d.y,vx:(Math.random()-.5)*3,vy:-2,life:18,col:'#FFD700'});}
    });

    // Absorb/get eaten by enemies
    enemies.forEach((en,i)=>{
      const dd=Math.sqrt((player.x-en.x)**2+(player.y-en.y)**2);
      if(dd<player.r+en.r) {
        if(player.r > en.r + 5) {
          player.r=Math.min(100,player.r+en.r*0.3);
          addDust(3);
          for(let j=0;j<8;j++)particles.push({x:en.x,y:en.y,vx:(Math.random()-.5)*5,vy:-3,life:22,col:en.col});
          enemies.splice(i,1);
          // respawn enemy
          setTimeout(()=>{const r=10+Math.random()*40;enemies.push({x:Math.random()*WORLD,y:Math.random()*WORLD,r,vx:(Math.random()-.5)*1.5,vy:(Math.random()-.5)*1.5,col:`hsl(${Math.random()*360},60%,55%)`});},3000);
        } else if(en.r > player.r + 5 && dd < (player.r+en.r)*0.6) {
          player.r=Math.max(15,player.r*0.7);
          loseLife();
        }
      }
    });

    const W=cv.width,H=cv.height;
    ctx.clearRect(0,0,W,H);

    // Grid
    ctx.strokeStyle='rgba(100,80,60,0.2)'; ctx.lineWidth=1;
    for(let x=((- camX)%60);x<W;x+=60){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
    for(let y=((-camY)%60);y<H;y+=60){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}

    // Border
    ctx.strokeStyle='rgba(200,160,80,0.5)'; ctx.lineWidth=4;
    ctx.strokeRect(-camX,-camY,WORLD,WORLD);

    // Dust
    dustBlobs.forEach(d=>{
      if(d.col)return;
      const px=d.x-camX,py=d.y-camY;
      if(px<-20||px>W+20||py<-20||py>H+20)return;
      ctx.fillStyle='#FFD700'; ctx.font='14px system-ui'; ctx.textAlign='center';
      ctx.fillText('✨',px,py+5);
    });

    // Enemies
    enemies.forEach(en=>{
      const px=en.x-camX,py=en.y-camY;
      if(px<-en.r-10||px>W+en.r+10||py<-en.r-10||py>H+en.r+10)return;
      ctx.fillStyle=en.col;
      ctx.beginPath();ctx.arc(px,py,en.r,0,Math.PI*2);ctx.fill();
      ctx.strokeStyle='rgba(255,255,255,0.3)';ctx.lineWidth=2;ctx.stroke();
    });

    // Particles
    particles=particles.filter(p=>p.life>0);
    particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.05;p.life--;
      ctx.fillStyle=p.col;ctx.globalAlpha=p.life/22;ctx.beginPath();ctx.arc(p.x-camX,p.y-camY,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});

    // Player cosmonaut
    const px=player.x-camX,py=player.y-camY;
    ctx.fillStyle='rgba(79,195,247,0.15)';
    ctx.beginPath();ctx.arc(px,py,player.r,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle='rgba(79,195,247,0.6)';ctx.lineWidth=2;ctx.stroke();
    drawCosmonaut(px,py,Math.min(player.r*0.75,36),0);

    // Size indicator
    ctx.fillStyle='rgba(255,255,255,.5)'; ctx.font='12px system-ui'; ctx.textAlign='left';
    ctx.fillText('Taille: '+Math.round(player.r), 8, H-10);
  }
  loop();
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# N7 : Jetpack Joyride / Lune de Tempête
# ─────────────────────────────────────────────────────────────────────────────
n7_js = r"""
let cosmo = {x:0,y:0,vy:0,r:22};
let obstacles = [], dustItems = [], particles = [], powerups = [];
let scrollX = 0, speed = 2, frameCount = 0;
let thrust = false, shield = false, magnet = false, magnetTimer = 0;

function gameStart() {
  cosmo.x = cv.width*0.2; cosmo.y = cv.height*0.5; cosmo.vy=0;
  obstacles=[]; dustItems=[]; particles=[]; powerups=[];
  scrollX=0; speed=2; frameCount=0; shield=false; magnet=false;

  cv.addEventListener('pointerdown',()=>{ thrust=true; });
  cv.addEventListener('pointerup',()=>{ thrust=false; });
  requestAnimationFrame(loop);
}

function spawnObstacle() {
  const H=cv.height;
  const types=['lightning','meteor','wind'];
  const t=types[Math.floor(Math.random()*types.length)];
  if(t==='lightning') {
    const y=H*0.1+Math.random()*H*0.7;
    obstacles.push({type:'lightning',x:cv.width+60,y,w:8,h:H*0.55,vy:0});
  } else if(t==='meteor') {
    const x=cv.width+30+Math.random()*100;
    obstacles.push({type:'meteor',x,y:-30,w:28,h:28,vy:3+Math.random()*2});
  } else {
    obstacles.push({type:'wind',x:cv.width,y:H*0.3+Math.random()*H*0.3,w:60,h:40,dir:Math.random()<.5?1:-1,life:180});
  }
}

function loop() {
  if(!running)return;
  requestAnimationFrame(loop);
  const W=cv.width, H=cv.height;
  frameCount++;

  // Accelerate every 10s
  if(frameCount%600===0) speed=Math.min(5, speed+0.4);

  // Physics
  const GRAV=0.35;
  if(thrust) { cosmo.vy += -0.6; } else { cosmo.vy += GRAV; }
  cosmo.vy = Math.max(-6, Math.min(5, cosmo.vy));
  cosmo.y += cosmo.vy;
  cosmo.y = Math.max(cosmo.r, Math.min(H-cosmo.r, cosmo.y));
  if(cosmo.y<=cosmo.r||cosmo.y>=H-cosmo.r) { if(!shield)loseLife(); cosmo.vy=0; }

  scrollX += speed;

  // Spawn obstacles (easy first 30s)
  const minSpawn = frameCount < 1800 ? 120 : 60;
  if(frameCount%Math.max(minSpawn - Math.floor(frameCount/300),40) === 0) spawnObstacle();

  // Spawn dust (lines)
  if(frameCount%45===0) {
    const y=H*0.15+Math.random()*H*0.65;
    for(let i=0;i<4;i++) dustItems.push({x:W+i*40,y,r:10,col:false});
  }

  // Spawn powerups
  if(frameCount%300===0&&Math.random()<0.4) {
    powerups.push({x:W+10,y:H*0.2+Math.random()*H*0.6,type:Math.random()<.5?'shield':'magnet',r:16,col:false});
  }

  // Move obstacles
  obstacles=obstacles.filter(o=>{
    if(o.type==='lightning'){o.x-=speed;return o.x>-20;}
    if(o.type==='meteor'){o.x-=speed*0.5;o.y+=o.vy;return o.x>-40&&o.y<H+40;}
    if(o.type==='wind'){o.x-=speed;o.life--;return o.life>0&&o.x>-80;}
    return false;
  });

  // Obstacle collision
  obstacles.forEach(o=>{
    let hit=false;
    if(o.type==='lightning'){const dx=cosmo.x-o.x,dy=cosmo.y-o.y;if(Math.abs(dx)<o.w/2+cosmo.r&&dy>-o.h/2&&dy<o.h/2)hit=true;}
    if(o.type==='meteor'){const dx=cosmo.x-o.x,dy=cosmo.y-o.y;if(Math.sqrt(dx*dx+dy*dy)<o.w/2+cosmo.r)hit=true;}
    if(hit){if(!shield){loseLife();cosmo.vy=-4;}else{shield=false;for(let i=0;i<8;i++)particles.push({x:cosmo.x,y:cosmo.y,vx:(Math.random()-.5)*5,vy:-3,life:20,col:'#5af0ff'});}}
    if(o.type==='wind'){const dx=cosmo.x-o.x,dy=cosmo.y-o.y;if(Math.abs(dx)<o.w/2+cosmo.r&&Math.abs(dy)<o.h/2+cosmo.r)cosmo.vy+=o.dir*0.4;}
  });

  // Move dust
  dustItems.forEach(d=>{d.x-=speed;if(magnet){const dx=cosmo.x-d.x,dy=cosmo.y-d.y;const dd=Math.sqrt(dx*dx+dy*dy);if(dd<140){d.x+=dx/dd*4;d.y+=dy/dd*4;}}});
  dustItems=dustItems.filter(d=>d.x>-20);
  dustItems.forEach(d=>{
    if(d.col)return;
    const dx=cosmo.x-d.x,dy=cosmo.y-d.y;
    if(Math.sqrt(dx*dx+dy*dy)<cosmo.r+d.r){d.col=true;addDust(3);for(let i=0;i<4;i++)particles.push({x:d.x,y:d.y,vx:(Math.random()-.5)*4,vy:-2,life:16,col:'#FFD700'});}
  });

  // Powerups
  powerups.forEach(p=>{p.x-=speed;if(p.col)return;const dx=cosmo.x-p.x,dy=cosmo.y-p.y;if(Math.sqrt(dx*dx+dy*dy)<cosmo.r+p.r){p.col=true;if(p.type==='shield')shield=true;else{magnet=true;magnetTimer=300;}}});
  powerups=powerups.filter(p=>p.x>-30&&!p.col);
  if(magnet){magnetTimer--;if(magnetTimer<=0)magnet=false;}

  // Draw
  ctx.clearRect(0,0,W,H);

  // Storm BG layers
  const stormX=(scrollX*0.3)%W;
  ctx.fillStyle='rgba(40,30,80,0.5)';
  ctx.fillRect(0,0,W,H);
  // Lightning flashes (bg)
  if(frameCount%80<5){ctx.fillStyle='rgba(140,120,255,0.06)';ctx.fillRect(0,0,W,H);}
  // Clouds
  ctx.fillStyle='rgba(60,40,100,0.4)';
  for(let i=0;i<4;i++){const cx=((i*220-stormX+W*2)%W)*1.1;ctx.beginPath();ctx.ellipse(cx,60+i*30,100,35,0,0,Math.PI*2);ctx.fill();}

  // Ground + ceiling lines
  ctx.strokeStyle='rgba(120,80,200,0.4)'; ctx.lineWidth=3;
  ctx.beginPath();ctx.moveTo(0,H-cosmo.r+2);ctx.lineTo(W,H-cosmo.r+2);ctx.stroke();
  ctx.beginPath();ctx.moveTo(0,cosmo.r-2);ctx.lineTo(W,cosmo.r-2);ctx.stroke();

  // Obstacles
  obstacles.forEach(o=>{
    if(o.type==='lightning'){
      ctx.strokeStyle='rgba(200,180,255,0.9)';ctx.lineWidth=4;
      ctx.beginPath();ctx.moveTo(o.x,o.y);ctx.lineTo(o.x,o.y+o.h);ctx.stroke();
      ctx.strokeStyle='rgba(255,255,255,0.4)';ctx.lineWidth=8;ctx.stroke();
    }
    if(o.type==='meteor'){
      ctx.fillStyle='rgba(200,80,40,0.85)';ctx.beginPath();ctx.arc(o.x,o.y,o.w/2,0,Math.PI*2);ctx.fill();
      ctx.fillStyle='rgba(255,150,50,0.4)';ctx.beginPath();ctx.arc(o.x,o.y,o.w/2+8,0,Math.PI*2);ctx.fill();
    }
    if(o.type==='wind'){const a=o.life/180*0.5;ctx.fillStyle=`rgba(100,150,255,${a})`;ctx.fillRect(o.x-o.w/2,o.y-o.h/2,o.w,o.h);ctx.fillStyle=`rgba(255,255,255,${a*0.5})`;ctx.font='24px system-ui';ctx.textAlign='center';ctx.fillText(o.dir>0?'💨':'💨',o.x,o.y+8);}
  });

  // Dust
  dustItems.forEach(d=>{if(!d.col){ctx.fillStyle='#FFD700';ctx.font='16px system-ui';ctx.textAlign='center';ctx.fillText('✨',d.x,d.y+5);}});

  // Powerups
  powerups.forEach(p=>{if(p.col)return;ctx.font='22px system-ui';ctx.textAlign='center';ctx.fillText(p.type==='shield'?'🛡️':'🧲',p.x,p.y+7);});

  // Shield ring
  if(shield){ctx.strokeStyle='rgba(79,195,247,.7)';ctx.lineWidth=3;ctx.beginPath();ctx.arc(cosmo.x,cosmo.y,cosmo.r+8,0,Math.PI*2);ctx.stroke();}

  // Particles
  particles=particles.filter(p=>p.life>0);
  particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.08;p.life--;ctx.fillStyle=p.col;ctx.globalAlpha=p.life/20;ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});

  // Cosmonaut
  drawCosmonaut(cosmo.x, cosmo.y, cosmo.r, thrust ? -0.3 : 0.1);

  // Jetpack flame
  if(thrust){
    ctx.fillStyle='rgba(255,140,0,0.7)';
    ctx.beginPath();ctx.ellipse(cosmo.x-18,cosmo.y+14,6,10+Math.random()*6,Math.PI/4,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='rgba(255,215,0,0.5)';
    ctx.beginPath();ctx.ellipse(cosmo.x-18,cosmo.y+14,4,7,Math.PI/4,0,Math.PI*2);ctx.fill();
  }
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# N8 : Crossy Road / Lune de Cristal
# ─────────────────────────────────────────────────────────────────────────────
n8_js = r"""
const CELL_W=60, CELL_H=48;
let cosmo = {col:0, row:0};
let worldRow = 0; // how many rows scrolled
let lanes = []; // generated lanes
let dustItems = [], particles = [];
let idleTimer = 0, frameCount = 0;
let camOffY = 0;

function genLane(row) {
  if(row === 0) return {type:'safe',crystals:[]};
  const rng=Math.random();
  if(rng<0.15) return {type:'safe',crystals:[]};
  if(rng<0.5) {
    const dir=Math.random()<.5?1:-1;
    const spd=1+Math.random()*2.5;
    const crystals=[];
    const count=2+Math.floor(Math.random()*3);
    for(let i=0;i<count;i++) crystals.push({x:(i*4+Math.random()*3)*CELL_W,vx:spd*dir,w:CELL_W*0.7,h:CELL_H*0.6,col:`hsl(${170+Math.random()*80},80%,65%)`});
    return {type:'crystal',crystals};
  }
  // River
  const dir=Math.random()<.5?1:-1;
  const spd=0.8+Math.random()*1.2;
  const platforms=[];
  for(let i=0;i<3;i++) platforms.push({x:i*CELL_W*2.5+Math.random()*CELL_W,vx:spd*dir,w:CELL_W*1.2,h:CELL_H*0.5});
  return {type:'river',platforms};
}

function gameStart() {
  const W=cv.width, H=cv.height;
  const COLS=Math.ceil(W/CELL_W)+1;
  cosmo.col=Math.floor(COLS/2); cosmo.row=0; worldRow=0;
  lanes=[]; dustItems=[]; particles=[]; idleTimer=0; frameCount=0;
  // Generate initial lanes
  for(let r=-1;r<20;r++) lanes.push({row:r,...genLane(r)});

  let swipeStart=null;
  cv.addEventListener('pointerdown',e=>{swipeStart={x:e.clientX,y:e.clientY};idleTimer=0;});
  cv.addEventListener('pointerup',e=>{
    if(!swipeStart||!running)return;
    const dx=e.clientX-swipeStart.x, dy=e.clientY-swipeStart.y;
    if(Math.abs(dx)>Math.abs(dy)){
      if(dx>20)moveCosmo(1,0); else if(dx<-20)moveCosmo(-1,0);
    } else {
      if(dy<-20)moveCosmo(0,-1); else if(dy>20)moveCosmo(0,1);
    }
    swipeStart=null;
  });

  requestAnimationFrame(loop);
}

const COLS_GRID=()=>Math.ceil(cv.width/CELL_W)+1;

function moveCosmo(dc,dr) {
  const nc=cosmo.col+dc, nr=cosmo.row+dr;
  if(nc<0||nc>=COLS_GRID())return;
  cosmo.col=nc; cosmo.row=nr; idleTimer=0;
  addDust(1);
  // Advance world if player moves up
  if(nr < worldRow + 3) {
    // Scroll up
    worldRow = nr - 3;
    // Generate more lanes ahead
    const topRow=lanes.reduce((mn,l)=>Math.min(mn,l.row),999);
    while(topRow > worldRow - 8) lanes.push({row:topRow-1,...genLane(Math.abs(topRow-1))});
    lanes=lanes.filter(l=>l.row<worldRow+20);
  }
}

function loop() {
  if(!running)return;
  requestAnimationFrame(loop);
  const W=cv.width, H=cv.height;
  frameCount++; idleTimer++;

  // Idle push back
  if(idleTimer>180){cosmo.row++;idleTimer=0;}

  // Move crystals/platforms
  lanes.forEach(lane=>{
    if(lane.type==='crystal') lane.crystals.forEach(c=>{c.x+=c.vx;if(c.x>W+100)c.x=-c.w-50;if(c.x<-c.w-100)c.x=W+50;});
    if(lane.type==='river') lane.platforms.forEach(p=>{p.x+=p.vx;if(p.x>W+100)p.x=-p.w-50;if(p.x<-p.w-100)p.x=W+50;});
  });

  // Camera smooth scroll
  const targetCamY = H/2 - (cosmo.row - worldRow)*CELL_H;
  camOffY += (targetCamY - camOffY) * 0.12;

  // Check collision / death
  const playerX = cosmo.col*CELL_W + CELL_W/2;
  const lane = lanes.find(l=>l.row===cosmo.row);
  if(lane) {
    if(lane.type==='crystal') {
      lane.crystals.forEach(c=>{
        const cx=c.x+c.w/2, cy=0;
        const px=playerX;
        if(Math.abs(px-cx)<c.w/2+20){
          // Hit crystal → push back 3 rows
          cosmo.row+=3; idleTimer=0;
          for(let i=0;i<8;i++)particles.push({x:playerX,y:camOffY,vx:(Math.random()-.5)*5,vy:-3+Math.random()*2,life:24,col:'rgba(150,220,255,0.9)'});
        }
      });
    }
    if(lane.type==='river') {
      // Must be on a platform
      let onPlatform=false;
      lane.platforms.forEach(p=>{if(playerX>p.x&&playerX<p.x+p.w)onPlatform=true;});
      if(!onPlatform) loseLife();
    }
  }

  // Dust collection
  if(frameCount%90===0) {
    dustItems.push({x:cosmo.col*CELL_W+CELL_W/2+(Math.random()-.5)*CELL_W*3,row:cosmo.row-2-Math.floor(Math.random()*4),col:false});
  }
  dustItems.forEach(d=>{
    if(d.col)return;
    if(d.row===cosmo.row&&Math.abs(d.x-playerX)<CELL_W*0.7){d.col=true;addDust(5);for(let i=0;i<5;i++)particles.push({x:d.x,y:0,vx:(Math.random()-.5)*4,vy:-3,life:20,col:'#FFD700'});}
  });
  dustItems=dustItems.filter(d=>!d.col&&d.row>=worldRow-2);

  // Draw
  ctx.clearRect(0,0,W,H);

  // BG prismatic
  const bgGrd=ctx.createLinearGradient(0,0,W,H);
  bgGrd.addColorStop(0,'rgba(10,5,30,0.95)');
  bgGrd.addColorStop(1,'rgba(5,20,40,0.95)');
  ctx.fillStyle=bgGrd; ctx.fillRect(0,0,W,H);

  // Lanes
  lanes.forEach(lane=>{
    const laneY=(lane.row-worldRow)*CELL_H+camOffY;
    if(laneY<-CELL_H*2||laneY>H+CELL_H)return;
    // Lane BG
    if(lane.type==='safe'){ctx.fillStyle='rgba(30,50,80,0.6)';ctx.fillRect(0,laneY,W,CELL_H);}
    if(lane.type==='crystal'){ctx.fillStyle='rgba(10,20,40,0.7)';ctx.fillRect(0,laneY,W,CELL_H);
      lane.crystals.forEach(c=>{
        const grad=ctx.createLinearGradient(c.x,laneY,c.x+c.w,laneY+c.h);
        grad.addColorStop(0,c.col); grad.addColorStop(1,'rgba(255,255,255,0.3)');
        ctx.fillStyle=grad; ctx.fillRect(c.x,laneY+CELL_H*0.2,c.w,c.h);
        ctx.strokeStyle='rgba(255,255,255,0.5)';ctx.lineWidth=1;ctx.strokeRect(c.x,laneY+CELL_H*0.2,c.w,c.h);
      });
    }
    if(lane.type==='river'){
      ctx.fillStyle='rgba(20,60,120,0.7)';ctx.fillRect(0,laneY,W,CELL_H);
      lane.platforms.forEach(p=>{ctx.fillStyle='rgba(150,220,255,0.8)';ctx.fillRect(p.x,laneY+CELL_H*0.2,p.w,p.h);});
    }
  });

  // Grid lines
  ctx.strokeStyle='rgba(100,150,200,0.1)';ctx.lineWidth=1;
  for(let x=0;x<W;x+=CELL_W){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}

  // Dust
  dustItems.forEach(d=>{
    if(d.col)return;
    const dy2=(d.row-worldRow)*CELL_H+camOffY+CELL_H/2;
    ctx.fillStyle='#FFD700';ctx.font='16px system-ui';ctx.textAlign='center';ctx.fillText('✨',d.x,dy2+5);
  });

  // Particles
  particles=particles.filter(p=>p.life>0);
  particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;ctx.fillStyle=p.col;ctx.globalAlpha=p.life/24;ctx.beginPath();ctx.arc(p.x,p.y,4,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});

  // Cosmonaut
  const cosmoX=cosmo.col*CELL_W+CELL_W/2;
  const cosmoY=(cosmo.row-worldRow)*CELL_H+camOffY+CELL_H/2;
  drawCosmonaut(cosmoX,cosmoY,22,0);

  // Score (rows advanced)
  ctx.fillStyle='rgba(255,255,255,.5)';ctx.font='12px system-ui';ctx.textAlign='right';
  ctx.fillText('Avancée: '+Math.max(0,-cosmo.row),W-8,H-10);
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# N9 : Boss Fight / Lune d'Éclipse  
# ─────────────────────────────────────────────────────────────────────────────
n9_js = r"""
let cosmo = {x:0,y:0,vx:0,vy:0,r:22};
let boss = {x:0,y:0,r:0,hp:100,maxHp:100,phase:1,phaseTimer:0,shake:0};
let projectiles = [], goldProjectiles = [], minions = [], lasers = [], particles = [];
let frameCount = 0, phaseStartTime = 0;
let shield = false, superShot = false;

function gameStart() {
  const W=cv.width, H=cv.height;
  cosmo.x=W/2; cosmo.y=H*0.82; cosmo.vx=0; cosmo.vy=0;
  boss.x=W/2; boss.y=H*0.18; boss.r=W*0.12; boss.hp=100; boss.maxHp=100;
  boss.phase=1; boss.phaseTimer=0; boss.shake=0;
  projectiles=[]; goldProjectiles=[]; minions=[]; lasers=[]; particles=[];
  frameCount=0; phaseStartTime=Date.now();
  shield=false; superShot=false;

  // Drag cosmo left/right
  let dragging=false, dragStart=null, dragBase=null;
  cv.addEventListener('pointerdown',e=>{
    dragging=true; dragStart=e.clientX; dragBase=cosmo.x;
    // Tap gold projectile
    const tx=e.offsetX, ty=e.offsetY;
    goldProjectiles.forEach((p,i)=>{
      const dx=tx-p.x,dy=ty-p.y;
      if(Math.sqrt(dx*dx+dy*dy)<p.r+20){
        p.tapped=true;
        // Shoot back at boss
        const ang=Math.atan2(boss.y-p.y,boss.x-p.x);
        goldProjectiles.splice(i,1);
        projectiles.push({x:p.x,y:p.y,vx:Math.cos(ang)*9,vy:Math.sin(ang)*9,r:10,gold:true,toBoss:true});
        for(let j=0;j<6;j++)particles.push({x:p.x,y:p.y,vx:(Math.random()-.5)*5,vy:-3,life:20,col:'#FFD700'});
      }
    });
    // Tap minion
    minions.forEach((m,i)=>{
      const dx=tx-m.x,dy=ty-m.y;
      if(Math.sqrt(dx*dx+dy*dy)<m.r+16){
        m.dead=true; addDust(4);
        for(let j=0;j<6;j++)particles.push({x:m.x,y:m.y,vx:(Math.random()-.5)*5,vy:-3,life:20,col:'rgba(180,100,220,0.9)'});
      }
    });
    // Swipe UP → jump (avoid shockwave), swipe DOWN → duck (avoid high laser)
  });
  cv.addEventListener('pointermove',e=>{
    if(!dragging||!running)return;
    cosmo.x = dragBase + (e.clientX - dragStart);
    cosmo.x=Math.max(cosmo.r, Math.min(cv.width-cosmo.r, cosmo.x));
  });
  cv.addEventListener('pointerup',()=>{ dragging=false; });

  // Swipe up/down
  let swStart=null;
  cv.addEventListener('touchstart',e=>{swStart={x:e.touches[0].clientY};},{passive:true});
  cv.addEventListener('touchend',e=>{
    if(!swStart||!running)return;
    const dy=e.changedTouches[0].clientY-swStart.x;
    if(dy<-40&&cosmo.y>=cv.height*0.82)cosmo.vy=-10; // jump
    if(dy>40)cosmo.y=Math.min(cv.height*0.88,cosmo.y+20); // duck
    swStart=null;
  },{passive:true});

  requestAnimationFrame(loop);
}

function bossShoot() {
  const W=cv.width, ang=Math.atan2(cosmo.y-boss.y,cosmo.x-boss.x);
  const spd=boss.phase===1?3:boss.phase===2?5:7;
  const spread=boss.phase>=2?3:1;
  for(let i=0;i<spread;i++){
    const a=ang+(i-Math.floor(spread/2))*0.3;
    const isGold=Math.random()<(boss.phase===1?0.5:boss.phase===2?0.35:0.2);
    if(isGold) goldProjectiles.push({x:boss.x,y:boss.y,vx:Math.cos(a)*spd*0.8,vy:Math.sin(a)*spd*0.8,r:14,tapped:false});
    else projectiles.push({x:boss.x,y:boss.y,vx:Math.cos(a)*spd,vy:Math.sin(a)*spd,r:12,gold:false,toBoss:false});
  }
}

function loop() {
  if(!running)return;
  requestAnimationFrame(loop);
  const W=cv.width,H=cv.height;
  frameCount++;

  // Phase transitions
  const elapsed=(Date.now()-phaseStartTime)/1000;
  if(elapsed>=60&&boss.phase===1){boss.phase=2;phaseStartTime=Date.now();}
  if(elapsed>=60&&boss.phase===2){boss.phase=3;}

  // Screen darken phase 3
  const darkAlpha=boss.phase===3?Math.min(0.5,(elapsed/60)*0.5):0;

  // Boss physics (hover, shake)
  boss.y=H*0.18+Math.sin(frameCount*0.02)*12;
  if(boss.shake>0){boss.x=W/2+(Math.random()-.5)*boss.shake*8;boss.shake*=0.8;}

  // Cosmo physics
  cosmo.vy+=0.4; cosmo.y+=cosmo.vy;
  cosmo.y=Math.max(H*0.7,Math.min(H*0.88,cosmo.y));
  if(cosmo.y>=H*0.82)cosmo.vy=0;

  // Boss shoots
  const shootInterval=boss.phase===1?80:boss.phase===2?50:35;
  if(frameCount%shootInterval===0) bossShoot();

  // Minions phase 2+
  if(boss.phase>=2&&frameCount%90===0&&minions.length<5) {
    minions.push({x:boss.x+(Math.random()-.5)*boss.r*3,y:boss.y+boss.r,vx:(Math.random()-.5)*2,vy:2+Math.random(),r:14,dead:false});
  }

  // Lasers phase 2+ (horizontal sweep)
  if(boss.phase>=2&&frameCount%120===60) {
    const ly=H*0.5+Math.random()*H*0.25;
    lasers.push({y:ly,timer:60,warning:true});
  }

  // Power-ups phase 3
  if(boss.phase===3&&frameCount%180===0) {
    const type=Math.random()<.5?'shield':'super';
    projectiles.push({x:Math.random()*W*0.8+W*0.1,y:boss.y+boss.r,vx:0,vy:1.5,r:14,isPowerup:true,puType:type});
  }

  // Move projectiles
  projectiles=projectiles.filter(p=>{
    p.x+=p.vx;p.y+=p.vy;
    if(p.isPowerup){
      if(Math.sqrt((p.x-cosmo.x)**2+(p.y-cosmo.y)**2)<cosmo.r+p.r){
        if(p.puType==='shield')shield=true;
        else{superShot=true;setTimeout(()=>superShot=false,5000);}
        for(let i=0;i<6;i++)particles.push({x:p.x,y:p.y,vx:(Math.random()-.5)*4,vy:-3,life:20,col:p.puType==='shield'?'#5af0ff':'#FFD700'});
        return false;
      }
      return p.y<H+30;
    }
    if(p.toBoss){
      const dx=p.x-boss.x,dy=p.y-boss.y;
      if(Math.sqrt(dx*dx+dy*dy)<boss.r){
        const dmg=superShot?20:10; boss.hp=Math.max(0,boss.hp-dmg);
        boss.shake=2+dmg/5;
        addDust(superShot?15:8);
        for(let i=0;i<8;i++)particles.push({x:boss.x,y:boss.y,vx:(Math.random()-.5)*6,vy:-4+Math.random()*3,life:25,col:'rgba(255,100,100,0.9)'});
        if(boss.hp<=0){endGame(true);return false;}
        return false;
      }
      return p.y>-20&&p.y<H+20&&p.x>-20&&p.x<W+20;
    }
    // Shadow projectile hits cosmo
    if(!p.gold&&!p.toBoss){
      const dx=p.x-cosmo.x,dy=p.y-cosmo.y;
      if(Math.sqrt(dx*dx+dy*dy)<cosmo.r+p.r){
        if(!shield)loseLife();else{shield=false;for(let i=0;i<6;i++)particles.push({x:cosmo.x,y:cosmo.y,vx:(Math.random()-.5)*5,vy:-3,life:18,col:'#5af0ff'});}
        return false;
      }
    }
    return p.y<H+30&&p.y>-30&&p.x>-30&&p.x<W+30;
  });

  // Gold projs
  goldProjectiles=goldProjectiles.filter(p=>{p.x+=p.vx;p.y+=p.vy;return p.y<H+30&&!p.tapped;});

  // Minions
  minions=minions.filter(m=>{
    if(m.dead)return false;
    m.x+=m.vx;m.y+=m.vy;
    if(m.y>H+20)return false;
    // Hit cosmo
    const dx=m.x-cosmo.x,dy=m.y-cosmo.y;
    if(Math.sqrt(dx*dx+dy*dy)<cosmo.r+m.r){if(!shield)loseLife();return false;}
    return true;
  });

  // Lasers
  lasers=lasers.filter(l=>{
    l.timer--;
    if(l.timer<=0&&l.warning){l.warning=false;l.timer=20;}
    else if(l.timer<=0&&!l.warning){
      // Hit cosmo if in laser
      if(Math.abs(cosmo.y-l.y)<20){if(!shield)loseLife();}
      return false;
    }
    return true;
  });

  // Draw
  ctx.clearRect(0,0,W,H);

  // BG eclipse
  const eclGrd=ctx.createRadialGradient(W/2,0,0,W/2,0,H);
  eclGrd.addColorStop(0,'rgba(80,40,120,0.6)');
  eclGrd.addColorStop(1,'rgba(5,0,20,0.95)');
  ctx.fillStyle=eclGrd;ctx.fillRect(0,0,W,H);

  // Corona beams
  ctx.strokeStyle='rgba(255,200,50,0.2)';ctx.lineWidth=30;
  for(let i=0;i<8;i++){
    const a=(i/8)*Math.PI*2+frameCount*0.005;
    ctx.beginPath();ctx.moveTo(W/2,boss.y);ctx.lineTo(W/2+Math.cos(a)*H,boss.y+Math.sin(a)*H);ctx.stroke();
  }

  // Phase 3 darkness
  if(darkAlpha>0){ctx.fillStyle=`rgba(0,0,0,${darkAlpha})`;ctx.fillRect(0,0,W,H);}

  // Boss
  const bossX=boss.x, bossY=boss.y;
  // Shadow body
  ctx.fillStyle='rgba(20,10,40,0.95)';
  ctx.beginPath();ctx.arc(bossX,bossY,boss.r,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle='rgba(120,60,220,0.8)';ctx.lineWidth=4;ctx.stroke();
  // Eye
  const eyePulse=0.8+0.2*Math.sin(frameCount*0.08);
  const eyeCol=boss.phase===3?'rgba(255,80,80,0.95)':'rgba(220,100,255,0.95)';
  ctx.fillStyle=eyeCol;ctx.beginPath();ctx.arc(bossX,bossY-boss.r*0.1,boss.r*0.35*eyePulse,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='rgba(0,0,0,0.8)';ctx.beginPath();ctx.arc(bossX,bossY-boss.r*0.1,boss.r*0.18,0,Math.PI*2);ctx.fill();
  // Tentacles
  for(let i=0;i<5;i++){
    const a=(i/5)*Math.PI*2+frameCount*0.01;
    const tx=bossX+Math.cos(a)*boss.r*1.4;const ty=bossY+Math.sin(a)*boss.r*1.2;
    ctx.strokeStyle=`rgba(60,20,100,0.7)`;ctx.lineWidth=6;
    ctx.beginPath();ctx.moveTo(bossX+Math.cos(a)*boss.r*0.8,bossY+Math.sin(a)*boss.r*0.8);
    ctx.bezierCurveTo(tx-20,ty+20,tx+10,ty-10,tx,ty+boss.r*0.3);ctx.stroke();
  }

  // HP bar
  const bpw=W*0.6;const bpx=(W-bpw)/2;
  ctx.fillStyle='rgba(0,0,0,0.6)';ctx.fillRect(bpx,16,bpw,14);
  const col=boss.hp>50?'#a040ff':boss.hp>25?'#ff6020':'#ff2020';
  ctx.fillStyle=col;ctx.fillRect(bpx,16,bpw*(boss.hp/boss.maxHp),14);
  ctx.strokeStyle='rgba(255,255,255,0.3)';ctx.lineWidth=1;ctx.strokeRect(bpx,16,bpw,14);
  ctx.fillStyle='rgba(255,255,255,.8)';ctx.font='bold 10px system-ui';ctx.textAlign='center';
  ctx.fillText('BOSS',W/2,27);

  // Phase indicator
  ctx.fillStyle='rgba(200,100,255,.7)';ctx.font='11px system-ui';
  ctx.fillText('Phase '+boss.phase,W/2,42);

  // Lasers
  lasers.forEach(l=>{
    if(l.warning){ctx.strokeStyle='rgba(255,50,50,0.6)';ctx.lineWidth=3;ctx.setLineDash([10,10]);ctx.beginPath();ctx.moveTo(0,l.y);ctx.lineTo(W,l.y);ctx.stroke();ctx.setLineDash([]);
      ctx.fillStyle='rgba(255,50,50,.5)';ctx.font='12px system-ui';ctx.textAlign='left';ctx.fillText('LASER !',8,l.y-5);}
    else{ctx.strokeStyle='rgba(255,80,80,0.95)';ctx.lineWidth=8;ctx.beginPath();ctx.moveTo(0,l.y);ctx.lineTo(W,l.y);ctx.stroke();}
  });

  // Projectiles
  projectiles.forEach(p=>{
    if(p.isPowerup){ctx.font='20px system-ui';ctx.textAlign='center';ctx.fillText(p.puType==='shield'?'🛡️':'⚡',p.x,p.y+7);return;}
    if(p.toBoss){ctx.fillStyle='rgba(255,215,0,0.9)';ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();}
    else{ctx.fillStyle='rgba(60,20,100,0.85)';ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();ctx.strokeStyle='rgba(120,60,200,0.7)';ctx.lineWidth=2;ctx.stroke();}
  });
  goldProjectiles.forEach(p=>{
    const glow=ctx.createRadialGradient(p.x,p.y,2,p.x,p.y,p.r);
    glow.addColorStop(0,'rgba(255,215,0,0.95)');glow.addColorStop(1,'rgba(255,150,0,0)');
    ctx.fillStyle=glow;ctx.beginPath();ctx.arc(p.x,p.y,p.r*1.5,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='rgba(255,215,0,.9)';ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='rgba(0,0,0,.5)';ctx.font='bold 10px system-ui';ctx.textAlign='center';ctx.fillText('TAP',p.x,p.y+4);
  });
  minions.forEach(m=>{ctx.fillStyle='rgba(100,40,180,0.85)';ctx.beginPath();ctx.arc(m.x,m.y,m.r,0,Math.PI*2);ctx.fill();ctx.font='12px system-ui';ctx.textAlign='center';ctx.fillText('💥',m.x,m.y+5);});

  // Particles
  particles=particles.filter(p=>p.life>0);
  particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.vy+=.1;p.life--;ctx.fillStyle=p.col;ctx.globalAlpha=p.life/25;ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;});

  // Shield ring
  if(shield){ctx.strokeStyle='rgba(79,195,247,.7)';ctx.lineWidth=3;ctx.beginPath();ctx.arc(cosmo.x,cosmo.y,cosmo.r+8,0,Math.PI*2);ctx.stroke();}
  if(superShot){ctx.strokeStyle='rgba(255,215,0,.8)';ctx.lineWidth=3;ctx.beginPath();ctx.arc(cosmo.x,cosmo.y,cosmo.r+14,0,Math.PI*2);ctx.stroke();}

  // Cosmonaut
  drawCosmonaut(cosmo.x, cosmo.y, cosmo.r, 0);

  // Hints
  ctx.fillStyle='rgba(255,255,255,.45)';ctx.font='11px system-ui';ctx.textAlign='left';
  ctx.fillText('DRAG:déplacer  TAP doré:renvoyer  TAP ennemi:détruire',8,H-8);
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Backgrounds
# ─────────────────────────────────────────────────────────────────────────────
BG = [
    '',  # placeholder 0
    # N1 Verre: glass planet starfield
    "background:radial-gradient(ellipse at 60% 70%,rgba(100,180,255,0.14) 0%,transparent 60%),linear-gradient(135deg,#060818 0%,#0a1428 100%);",
    # N2 Cendre: lava red
    "background:radial-gradient(ellipse at 50% 90%,rgba(255,80,0,0.3) 0%,transparent 60%),linear-gradient(180deg,#1a0a00 0%,#0d0008 100%);",
    # N3 Lierre: jungle space
    "background:radial-gradient(ellipse at 30% 40%,rgba(30,120,20,0.2) 0%,transparent 60%),linear-gradient(160deg,#040c04 0%,#0a1408 100%);",
    # N4 Givre: ice cave
    "background:radial-gradient(ellipse at 50% 20%,rgba(100,200,255,0.15) 0%,transparent 60%),linear-gradient(180deg,#060e18 0%,#020810 100%);",
    # N5 Ombre: pure black + subtle purple
    "background:radial-gradient(ellipse at 50% 50%,rgba(60,0,100,0.12) 0%,transparent 70%),linear-gradient(180deg,#020004 0%,#000000 100%);",
    # N6 Fer: metallic grey
    "background:radial-gradient(ellipse at 40% 40%,rgba(140,140,160,0.12) 0%,transparent 60%),linear-gradient(135deg,#0a0a10 0%,#080810 100%);",
    # N7 Tempête: storm purple
    "background:radial-gradient(ellipse at 50% 20%,rgba(80,40,160,0.2) 0%,transparent 60%),linear-gradient(180deg,#080414 0%,#0a0820 100%);",
    # N8 Cristal: prismatic
    "background:radial-gradient(ellipse at 30% 60%,rgba(0,150,200,0.12) 0%,transparent 50%),radial-gradient(ellipse at 70% 30%,rgba(200,0,150,0.08) 0%,transparent 50%),linear-gradient(135deg,#050814 0%,#081020 100%);",
    # N9 Éclipse: eclipse corona
    "background:radial-gradient(ellipse at 50% 20%,rgba(200,150,0,0.18) 0%,rgba(100,0,150,0.1) 40%,transparent 70%),linear-gradient(180deg,#080010 0%,#040008 100%);",
]

TUTOS = [
    '',
    "Lance le cosmonaute avec ta fronde !<br>Fais glisser vers l'arrière &rarr; relâche.<br>Vise les cristaux pour récupérer les ✨.",
    "Tape pour faire battre les ailes !<br>Passe entre les colonnes de lave.<br>Ne touche ni les parois ni le sol.",
    "Le cosmonaute rebondit automatiquement.<br>Glisse gauche/droite pour se déplacer.<br>Monte le plus haut possible !",
    "Tape pour t&rsquo;accrocher à une stalactite.<br>Le cosmonaute fait un pendule.<br>Swipe haut/bas pour raccourcir/allonger la corde.",
    "Swipe ou flèches pour te déplacer.<br>Une lumière éclaire tes alentours.<br>Trouve la 🚪 sortie dorée !",
    "Drag le doigt pour déplacer ta lune.<br>Absorbe les plus petits, fuis les grands.<br>Grossis jusqu&rsquo;à la taille max !",
    "Maintiens appuyé pour monter.<br>Relâche pour descendre doucement.<br>Évite les éclairs et météores.",
    "Swipe haut pour avancer, gauche/droite pour bifurquer.<br>Évite les vagues de cristaux.<br>Saute sur les plateformes en zone rivière.",
    "Drag pour te déplacer.<br>TAP les projectiles dorés pour les renvoyer au boss.<br>TAP les ennemis pour les détruire.",
]

# ─────────────────────────────────────────────────────────────────────────────
GAME_JS = [None, n1_js, n2_js, n3_js, n4_js, n5_js, n6_js, n7_js, n8_js, n9_js]

for n in range(1, 10):
    html = make_html(
        niveau=n,
        extra_style="",
        extra_html="",
        extra_js=GAME_JS[n],
        tuto_text=TUTOS[n],
        bg_css=BG[n]
    )
    path = os.path.join(OUTDIR, f'niveau{n}.html')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print(f'  ✅ Written: niveau{n}.html ({len(html)} chars)')

print('\n🌙 All 9 mini-jeux written!')
