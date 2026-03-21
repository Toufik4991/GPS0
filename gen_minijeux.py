#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate all 9 GPS0 mini-jeux HTML files"""
import os

MINIJEUX_DIR = os.path.join(os.path.dirname(__file__), 'minijeux')

# Shared head & common JS (selfie, postMessage, timer, lives)
def make_html(niveau, titre, emoji, description, game_js, game_html='', extra_css=''):
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover">
<title>GPS0 — {titre}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0A0A1A;color:#fff;font-family:system-ui,sans-serif;overflow:hidden;height:100dvh;display:flex;flex-direction:column;touch-action:none;user-select:none}}
#hud{{display:flex;align-items:center;gap:10px;padding:8px 12px;background:rgba(0,0,0,.5);flex-shrink:0;z-index:10}}
#lives{{font-size:1.3rem;letter-spacing:2px}}
#timer{{flex:1;text-align:center;font-size:1rem;font-weight:bold;color:#4FC3F7}}
#score-hud{{font-size:.9rem;color:#FFD700}}
#game-container{{flex:1;position:relative;overflow:hidden}}
canvas{{display:block;width:100%;height:100%}}
#overlay{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(10,10,26,.88);z-index:20;gap:14px;text-align:center;padding:24px}}
#overlay h2{{font-size:1.8rem;color:var(--accent,#C8A2C8)}}
#overlay p{{font-size:.9rem;color:rgba(255,255,255,.8);max-width:280px}}
#overlay .btn{{padding:12px 32px;border:none;border-radius:14px;font-size:1rem;font-weight:bold;cursor:pointer;background:linear-gradient(135deg,#C8A2C8,#8860a8);color:#fff}}
#selfie-anchor{{position:absolute;z-index:5;pointer-events:none}}
{extra_css}
:root{{--accent:#C8A2C8;--gold:#FFD700;--blue:#4FC3F7}}
</style>
</head>
<body>
<div id="hud">
  <span id="lives">&#10084;&#10084;&#10084;</span>
  <span id="timer">3:00</span>
  <span id="score-hud">0 &#10024;</span>
</div>
<div id="game-container">
  <canvas id="cv"></canvas>
  {game_html}
  <div id="overlay">
    <div style="font-size:3rem">{emoji}</div>
    <h2>{titre}</h2>
    <p>{description}</p>
    <button class="btn" id="btn-start">C&#8217;est parti !</button>
  </div>
  <canvas id="selfie-cv" width="48" height="48" style="display:none" aria-hidden="true"></canvas>
</div>
<script>
// === COMMON ENGINE ===
const NIVEAU = {niveau};
const DUST_REWARD = ({niveau} === 9) ? 50 : (5 + {niveau} * 5);
let lives = 3, dust = 0, running = false, gameover = false;
let timerSec = 180, timerInterval = null;
const livesEl = document.getElementById('lives');
const timerEl = document.getElementById('timer');
const scoreEl = document.getElementById('score-hud');
const overlay = document.getElementById('overlay');
const btnStart = document.getElementById('btn-start');

function updateLivesHUD() {{
  livesEl.textContent = '\\u2764'.repeat(lives) + '\\u2661'.repeat(Math.max(0, 3 - lives));
}}

function updateTimer() {{
  const m = Math.floor(timerSec / 60), s = timerSec % 60;
  timerEl.textContent = m + ':' + String(s).padStart(2,'0');
}}

function addDust(n) {{
  dust += n;
  scoreEl.textContent = dust + ' \\u2728';
}}

function loseLife() {{
  if (!running) return;
  lives--;
  updateLivesHUD();
  if (lives <= 0) endGame(false);
}}

function endGame(success) {{
  if (gameover) return;
  gameover = true;
  running = false;
  clearInterval(timerInterval);
  const finalDust = success ? dust + DUST_REWARD : Math.floor(dust * 0.5);
  setTimeout(() => {{
    window.parent.postMessage({{
      source: 'gps0_minijeu',
      success: success,
      niveau: NIVEAU,
      poussieres: finalDust
    }}, '*');
  }}, 800);
}}

function startTimer() {{
  updateTimer();
  timerInterval = setInterval(() => {{
    if (!running) return;
    timerSec--;
    updateTimer();
    if (timerSec <= 0) endGame(false);
  }}, 1000);
}}

// Load selfie
const selfieCanvas = document.getElementById('selfie-cv');
const selfieCtx = selfieCanvas.getContext('2d');
(function loadSelfie() {{
  const data = localStorage.getItem('gps0_avatar_selfie_base64');
  if (!data) return;
  const img = new Image();
  img.onload = () => {{
    selfieCtx.save();
    selfieCtx.beginPath();
    selfieCtx.arc(24, 24, 24, 0, Math.PI * 2);
    selfieCtx.clip();
    selfieCtx.drawImage(img, 0, 0, 48, 48);
    selfieCtx.restore();
  }};
  img.src = data;
}})();

// Tuto overlay auto-dismiss after 5s
let tutoDismissed = false;
btnStart.addEventListener('click', startGame);
setTimeout(() => {{ if (!tutoDismissed) startGame(); }}, 5000);

function startGame() {{
  if (tutoDismissed) return;
  tutoDismissed = true;
  overlay.style.display = 'none';
  running = true;
  startTimer();
  initGame();
}}

// === GAME LOGIC ===
{game_js}
</script>
</body>
</html>'''

# ==================== NIVEAU 1 — Slingshot (Angry Birds) ====================
N1_JS = r"""
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W, H;
function resize() {
  W = cv.width = cv.offsetWidth;
  H = cv.height = cv.offsetHeight;
}
window.addEventListener('resize', () => { resize(); if(running) drawAll(); });

// Slingshot physics
const GRAV = 0.45;
const SLING_X_RATIO = 0.2;
const SLING_Y_RATIO = 0.65;

let sling, ball, targets, particles, shots, maxShots;
let dragging = false, dragX = 0, dragY = 0;
let launched = false, ballVx = 0, ballVy = 0;
const BALL_R = 18;
const SLING_MAX = 80;

function initGame() {
  resize();
  shots = 0;
  maxShots = 7;
  ball = null;
  targets = [];
  particles = [];
  spawnTargets();
  resetBall();
  loop();
}

function spawnTargets() {
  targets = [];
  const cols = 4;
  for (let i = 0; i < cols; i++) {
    const x = W * 0.55 + i * (W * 0.1);
    const ht = 2 + Math.floor(Math.random() * 3);
    for (let j = 0; j < ht; j++) {
      targets.push({ x, y: H * 0.75 - j * 36, r: 16, alive: true, dust: 5 + Math.floor(Math.random() * 10) });
    }
  }
}

function resetBall() {
  sling = { x: W * SLING_X_RATIO, y: H * SLING_Y_RATIO };
  ball = { x: sling.x, y: sling.y - BALL_R, vx: 0, vy: 0 };
  launched = false;
  dragging = false;
}

function loop() {
  if (!running) return;
  update();
  drawAll();
  requestAnimationFrame(loop);
}

function update() {
  if (!launched) return;
  ball.x += ball.vx;
  ball.y += ball.vy;
  ball.vy += GRAV;

  // Collide with targets
  for (const t of targets) {
    if (!t.alive) continue;
    const dx = ball.x - t.x, dy = ball.y - t.y;
    if (Math.sqrt(dx*dx + dy*dy) < BALL_R + t.r) {
      t.alive = false;
      addDust(t.dust);
      for (let i = 0; i < 8; i++) particles.push({ x: t.x, y: t.y, vx: (Math.random()-0.5)*5, vy: (Math.random()-0.5)*5, life: 40, color: '#FFD700' });
    }
  }

  // Update particles
  particles = particles.filter(p => { p.x += p.vx; p.y += p.vy; p.vy += 0.1; p.life--; return p.life > 0; });

  // Out of bounds
  if (ball.y > H + 50 || ball.x > W + 50 || ball.x < -50) {
    shots++;
    if (shots >= maxShots) {
      const alive = targets.filter(t => t.alive).length;
      endGame(alive === 0);
    } else {
      resetBall();
    }
  }

  // All targets destroyed
  if (targets.every(t => !t.alive)) endGame(true);
}

function drawAll() {
  ctx.clearRect(0, 0, W, H);
  // Ground
  ctx.fillStyle = '#1a1a3a';
  ctx.fillRect(0, H * 0.8, W, H * 0.2);
  ctx.fillStyle = '#2a2a5a';
  ctx.fillRect(0, H * 0.78, W, 8);

  // Slingshot
  ctx.strokeStyle = '#8B6914';
  ctx.lineWidth = 6;
  ctx.beginPath(); ctx.moveTo(sling.x - 15, H * 0.8); ctx.lineTo(sling.x - 8, sling.y - 5); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(sling.x + 15, H * 0.8); ctx.lineTo(sling.x + 8, sling.y - 5); ctx.stroke();

  // Rubber band
  if (!launched) {
    const bx = ball.x, by = ball.y;
    ctx.strokeStyle = 'rgba(180,120,60,.8)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(sling.x - 8, sling.y - 5); ctx.lineTo(bx, by); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(sling.x + 8, sling.y - 5); ctx.lineTo(bx, by); ctx.stroke();
  }

  // Ball (selfie or emoji)
  if (selfieCanvas.width > 0 && selfieCtx.getImageData(0,0,1,1).data[3] > 0) {
    ctx.save();
    ctx.beginPath(); ctx.arc(ball.x, ball.y, BALL_R, 0, Math.PI*2); ctx.clip();
    ctx.drawImage(selfieCanvas, ball.x - BALL_R, ball.y - BALL_R, BALL_R*2, BALL_R*2);
    ctx.restore();
  } else {
    ctx.font = `${BALL_R*2}px serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('👨‍🚀', ball.x, ball.y);
  }

  // Targets
  for (const t of targets) {
    if (!t.alive) continue;
    ctx.fillStyle = '#4FC3F7';
    ctx.beginPath(); ctx.arc(t.x, t.y, t.r, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = '#0097d6'; ctx.lineWidth = 2; ctx.stroke();
    ctx.fillStyle = '#fff'; ctx.font = '10px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('✨', t.x, t.y);
  }

  // Particles
  for (const p of particles) {
    ctx.globalAlpha = p.life / 40;
    ctx.fillStyle = p.color;
    ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI*2); ctx.fill();
  }
  ctx.globalAlpha = 1;

  // Shots left
  ctx.fillStyle = 'rgba(255,255,255,.6)'; ctx.font = '14px sans-serif'; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  ctx.fillText(`Tirs: ${maxShots - shots}`, 10, 10);
}

// Touch/mouse
function getPos(e) {
  const r = cv.getBoundingClientRect();
  const src = e.touches ? e.touches[0] : e;
  return { x: src.clientX - r.left, y: src.clientY - r.top };
}
function onDown(e) {
  if (!running || launched) return;
  e.preventDefault();
  const p = getPos(e);
  const dx = p.x - ball.x, dy = p.y - ball.y;
  if (Math.sqrt(dx*dx+dy*dy) < BALL_R + 20) dragging = true;
}
function onMove(e) {
  if (!dragging || !running) return;
  e.preventDefault();
  const p = getPos(e);
  const dx = p.x - sling.x, dy = p.y - sling.y;
  const dist = Math.sqrt(dx*dx+dy*dy);
  const clamped = Math.min(dist, SLING_MAX);
  const ang = Math.atan2(dy, dx);
  ball.x = sling.x + Math.cos(ang) * clamped;
  ball.y = sling.y + Math.sin(ang) * clamped;
}
function onUp(e) {
  if (!dragging || !running) return;
  e.preventDefault();
  dragging = false;
  const power = 0.22;
  ball.vx = -(ball.x - sling.x) * power;
  ball.vy = -(ball.y - sling.y) * power;
  launched = true;
  shots++;
}
cv.addEventListener('touchstart', onDown, { passive: false });
cv.addEventListener('touchmove', onMove, { passive: false });
cv.addEventListener('touchend', onUp, { passive: false });
cv.addEventListener('mousedown', onDown);
window.addEventListener('mousemove', onMove);
window.addEventListener('mouseup', onUp);
"""

# ==================== NIVEAU 2 — Flappy Bird ====================
N2_JS = r"""
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W, H;
function resize() { W = cv.width = cv.offsetWidth; H = cv.height = cv.offsetHeight; }
window.addEventListener('resize', () => { resize(); });

const GRAV = 0.5, JUMP = -9, PIPE_W = 60, GAP = H * 0.38 || 160, PIPE_SPEED_INIT = 3;
let playerY, playerVy, pipes, dustItems, frameCount, score, pipeSpeed, lastPipe;

function initGame() {
  resize();
  playerY = H * 0.4;
  playerVy = 0;
  pipes = [];
  dustItems = [];
  frameCount = 0;
  score = 0;
  pipeSpeed = PIPE_SPEED_INIT;
  lastPipe = 0;
  loop();
}

function spawnPipe() {
  const gapY = H * 0.2 + Math.random() * (H * 0.4);
  const gap = H * 0.36;
  pipes.push({ x: W + PIPE_W, topH: gapY, botY: gapY + gap, passed: false });
  if (Math.random() < 0.6) {
    dustItems.push({ x: W + PIPE_W + PIPE_W / 2, y: gapY + gap / 2, alive: true });
  }
}

const PLAYER_R = 20;
function loop() {
  if (!running) return;
  frameCount++;
  update();
  drawAll();
  requestAnimationFrame(loop);
}

function update() {
  playerVy += GRAV;
  playerY += playerVy;
  // Increase speed over time
  pipeSpeed = PIPE_SPEED_INIT + Math.floor(frameCount / 400) * 0.5;

  // Spawn pipes
  if (frameCount - lastPipe > 90) {
    spawnPipe();
    lastPipe = frameCount;
  }

  // Move pipes
  for (const p of pipes) {
    p.x -= pipeSpeed;
    if (!p.passed && p.x + PIPE_W < W * 0.2) { p.passed = true; score++; }
  }
  pipes = pipes.filter(p => p.x > -PIPE_W - 10);

  // Move dust
  for (const d of dustItems) { d.x -= pipeSpeed; }
  dustItems = dustItems.filter(d => d.x > -30);

  // Collect dust
  for (const d of dustItems) {
    if (d.alive && Math.abs(d.x - W * 0.2) < PLAYER_R + 12 && Math.abs(d.y - playerY) < PLAYER_R + 12) {
      d.alive = false;
      addDust(8);
    }
  }

  // Collide ceiling/floor
  if (playerY - PLAYER_R < 0 || playerY + PLAYER_R > H) { loseLife(); if (lives > 0) { playerY = H * 0.4; playerVy = 0; } return; }

  // Collide pipes
  const px = W * 0.2;
  for (const p of pipes) {
    if (px + PLAYER_R > p.x && px - PLAYER_R < p.x + PIPE_W) {
      if (playerY - PLAYER_R < p.topH || playerY + PLAYER_R > p.botY) {
        loseLife();
        if (lives > 0) { playerY = H * 0.4; playerVy = 0; }
        return;
      }
    }
  }
}

function drawAll() {
  // BG
  ctx.fillStyle = '#0d1b2a';
  ctx.fillRect(0, 0, W, H);

  // Stars
  ctx.fillStyle = 'rgba(255,255,255,.4)';
  for (let i = 0; i < 30; i++) {
    const sx = (i * 67 + frameCount * 0.3) % W;
    const sy = (i * 43) % H;
    ctx.fillRect(sx, sy, 2, 2);
  }

  // Pipes (as lava columns)
  for (const p of pipes) {
    const grad1 = ctx.createLinearGradient(p.x, 0, p.x + PIPE_W, 0);
    grad1.addColorStop(0, '#ff4444'); grad1.addColorStop(1, '#882222');
    ctx.fillStyle = grad1;
    ctx.fillRect(p.x, 0, PIPE_W, p.topH);
    ctx.fillRect(p.x, p.botY, PIPE_W, H - p.botY);
    // caps
    ctx.fillStyle = '#ff6666';
    ctx.fillRect(p.x - 5, p.topH - 18, PIPE_W + 10, 18);
    ctx.fillRect(p.x - 5, p.botY, PIPE_W + 10, 18);
  }

  // Dust items
  for (const d of dustItems) {
    if (!d.alive) continue;
    ctx.font = '20px serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('✨', d.x, d.y);
  }

  // Player
  if (selfieCanvas.width > 0 && selfieCtx.getImageData(0,0,1,1).data[3] > 0) {
    ctx.save();
    ctx.translate(W * 0.2, playerY);
    ctx.rotate(Math.min(Math.max(playerVy * 0.05, -0.5), 0.8));
    ctx.beginPath(); ctx.arc(0, 0, PLAYER_R, 0, Math.PI*2); ctx.clip();
    ctx.drawImage(selfieCanvas, -PLAYER_R, -PLAYER_R, PLAYER_R*2, PLAYER_R*2);
    ctx.restore();
  } else {
    ctx.save();
    ctx.translate(W * 0.2, playerY);
    ctx.rotate(Math.min(Math.max(playerVy * 0.05, -0.5), 0.8));
    ctx.font = `${PLAYER_R * 2.2}px serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('🚀', 0, 0);
    ctx.restore();
  }
}

// Tap to jump
function doJump(e) { if (!running) return; e.preventDefault(); playerVy = JUMP; }
cv.addEventListener('touchstart', doJump, { passive: false });
cv.addEventListener('mousedown', doJump);
"""

# ==================== NIVEAU 3 — Doodle Jump ====================
N3_JS = r"""
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W, H;
function resize() { W = cv.width = cv.offsetWidth; H = cv.height = cv.offsetHeight; }
window.addEventListener('resize', () => { resize(); });

const PLAT_W = 80, PLAT_H = 12, JUMP_V = -14, P_R = 18;
let px, py, pvx, pvy, platforms, dustItems, camY, maxH, touchStartX, touchStartY;

function initGame() {
  resize();
  camY = 0;
  maxH = 0;
  px = W / 2;
  py = H * 0.6;
  pvx = 0;
  pvy = JUMP_V;
  platforms = [];
  dustItems = [];
  // Generate initial platforms
  platforms.push({ x: W / 2 - PLAT_W / 2, y: H * 0.65, type: 'normal' });
  for (let i = 0; i < 25; i++) generatePlatform(-i * 90);
  loop();
}

function generatePlatform(y) {
  const x = Math.random() * (W - PLAT_W);
  const type = Math.random() < 0.15 ? 'break' : 'normal';
  platforms.push({ x, y, type, broken: false });
  if (Math.random() < 0.4) {
    dustItems.push({ x: x + PLAT_W / 2, y: y - 30, alive: true });
  }
}

function loop() {
  if (!running) return;
  update();
  drawAll();
  requestAnimationFrame(loop);
}

function update() {
  // Horizontal control via device tilt or touch left/right
  // Using touch swipe direction
  if (touchDir !== 0) pvx += touchDir * 0.8;
  pvx *= 0.85;
  pvx = Math.max(-8, Math.min(8, pvx));

  px += pvx;
  // Wrap
  if (px < -P_R) px = W + P_R;
  if (px > W + P_R) px = -P_R;

  pvy += 0.6; // gravity
  py += pvy;

  // Camera follows upward
  const screenY = py - camY;
  if (screenY < H * 0.4) {
    const diff = H * 0.4 - screenY;
    camY -= diff;
  }
  const height = -camY;
  if (height > maxH) { maxH = height; }

  // Platform collisions (only when falling)
  if (pvy > 0) {
    for (const p of platforms) {
      const scrPy = p.y - camY;
      if (py - camY >= scrPy - PLAT_H / 2 && py - camY <= scrPy + PLAT_H &&
          px >= p.x - P_R && px <= p.x + PLAT_W + P_R) {
        if (p.type === 'break') {
          if (!p.broken) { p.broken = true; addDust(5); }
          continue;
        }
        pvy = JUMP_V;
        break;
      }
    }
  }

  // Collect dust
  for (const d of dustItems) {
    if (!d.alive) continue;
    const dx = px - d.x, dy = (py - camY) - (d.y - camY);
    if (Math.sqrt(dx*dx + dy*dy) < P_R + 12) { d.alive = false; addDust(10); }
  }

  // Fall below screen = lose life
  if (py - camY > H + 100) {
    loseLife();
    if (lives > 0) { pvy = JUMP_V; py = camY + H * 0.6; pvx = 0; }
  }

  // Generate new platforms
  const topPlatY = platforms.reduce((m, p) => Math.min(m, p.y), 0);
  while (topPlatY - camY > -200) generatePlatform(topPlatY - 90);
  // Remove old platforms
  platforms = platforms.filter(p => p.y - camY < H + 100);
  dustItems = dustItems.filter(d => d.y - camY < H + 100);
}

let touchDir = 0;
function handleTouchStart(e) {
  e.preventDefault();
  if (!running) return;
  const t = e.touches[0];
  touchStartX = t.clientX;
}
function handleTouchMove(e) {
  e.preventDefault();
  if (!running) return;
  const t = e.touches[0];
  const dx = t.clientX - touchStartX;
  touchDir = dx > 20 ? 1 : dx < -20 ? -1 : 0;
}
function handleTouchEnd(e) { e.preventDefault(); touchDir = 0; }
cv.addEventListener('touchstart', handleTouchStart, { passive: false });
cv.addEventListener('touchmove', handleTouchMove, { passive: false });
cv.addEventListener('touchend', handleTouchEnd, { passive: false });
window.addEventListener('keydown', e => {
  if (e.key === 'ArrowLeft') touchDir = -1;
  if (e.key === 'ArrowRight') touchDir = 1;
});
window.addEventListener('keyup', () => touchDir = 0);

function drawAll() {
  ctx.fillStyle = '#080820'; ctx.fillRect(0, 0, W, H);
  // Stars
  for (let i = 0; i < 40; i++) {
    const sx = (i * 79 + Math.abs(camY) * 0.05) % W;
    const sy = (i * 53 + Math.abs(camY) * 0.02) % H;
    ctx.fillStyle = `rgba(255,255,255,${0.2 + (i % 3) * 0.2})`;
    ctx.fillRect(sx, sy, 2, 2);
  }

  // Platforms
  for (const p of platforms) {
    const sy = p.y - camY;
    if (sy > H + 20 || sy < -20) continue;
    if (p.broken) { ctx.fillStyle = 'rgba(200,100,100,.3)'; }
    else if (p.type === 'break') { ctx.fillStyle = '#cc4444'; }
    else { ctx.fillStyle = '#4FC3F7'; }
    ctx.beginPath();
    ctx.roundRect(p.x, sy, PLAT_W, PLAT_H, 6);
    ctx.fill();
    if (p.type !== 'break' && !p.broken) {
      ctx.fillStyle = 'rgba(255,255,255,.3)';
      ctx.beginPath(); ctx.roundRect(p.x + 4, sy + 2, PLAT_W - 8, 4, 3); ctx.fill();
    }
  }

  // Dust
  for (const d of dustItems) {
    if (!d.alive) continue;
    const sy = d.y - camY;
    if (sy < -20 || sy > H + 20) continue;
    ctx.font = '18px serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('✨', d.x, sy);
  }

  // Player
  const spy = py - camY;
  if (selfieCanvas.width > 0 && selfieCtx.getImageData(0,0,1,1).data[3] > 0) {
    ctx.save(); ctx.beginPath(); ctx.arc(px, spy, P_R, 0, Math.PI*2); ctx.clip();
    ctx.drawImage(selfieCanvas, px - P_R, spy - P_R, P_R*2, P_R*2); ctx.restore();
  } else {
    ctx.font = `${P_R*2}px serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('👨‍🚀', px, spy);
  }

  // Height indicator
  ctx.fillStyle = 'rgba(255,255,255,.5)'; ctx.font = '13px sans-serif'; ctx.textAlign = 'right'; ctx.textBaseline = 'top';
  ctx.fillText(`+${Math.floor(maxH / 10)}m`, W - 10, 10);
}
"""

# ==================== NIVEAU 4 — Swing / Rope ====================
N4_JS = r"""
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W, H;
function resize() { W = cv.width = cv.offsetWidth; H = cv.height = cv.offsetHeight; }
window.addEventListener('resize', () => { resize(); drawAll(); });

const GRAV = 0.5, P_R = 18, ROPE_LEN = 110;
let px, py, pvx, pvy, attached, anchorX, anchorY, angle, avel, ropeLen;
let anchors, dustItems, camX, scrolled, nextAnchorX;

function initGame() {
  resize();
  camX = 0;
  scrolled = 0;
  px = W * 0.15;
  py = H * 0.5;
  pvx = 4;
  pvy = 0;
  attached = false;
  anchors = [];
  dustItems = [];
  nextAnchorX = W * 0.3;
  for (let i = 0; i < 8; i++) spawnAnchor();
  loop();
}

function spawnAnchor() {
  anchors.push({
    x: nextAnchorX,
    y: H * (0.1 + Math.random() * 0.3),
    r: 8
  });
  if (Math.random() < 0.7) {
    dustItems.push({ x: nextAnchorX, y: H * 0.6 + Math.random() * H * 0.15, alive: true });
  }
  nextAnchorX += W * 0.25 + Math.random() * W * 0.15;
}

function loop() {
  if (!running) return;
  update();
  drawAll();
  requestAnimationFrame(loop);
}

function update() {
  if (attached) {
    // Pendulum physics
    const dx = px - anchorX, dy = py - anchorY;
    const ang = Math.atan2(dx, -dy);
    avel += -0.002 * Math.sin(ang);
    avel *= 0.99;
    angle += avel;
    px = anchorX + Math.sin(angle) * ropeLen;
    py = anchorY - Math.cos(angle) * ropeLen;
    pvx = avel * ropeLen * Math.cos(angle);
    pvy = avel * ropeLen * Math.sin(angle);
  } else {
    pvx *= 0.99;
    pvy += GRAV;
    px += pvx;
    py += pvy;
  }

  // Camera follows player
  const screenX = px - camX;
  if (screenX > W * 0.6) { camX += screenX - W * 0.6; scrolled += screenX - W * 0.6; }

  // Collect dust
  for (const d of dustItems) {
    if (!d.alive) continue;
    const dx = (px - camX) - (d.x - camX), dy = py - d.y;
    if (Math.abs(d.x - px) < P_R + 16 && Math.abs(d.y - py) < P_R + 16) {
      d.alive = false; addDust(12);
    }
  }

  // Generate new anchors
  while (nextAnchorX - camX < W * 2) spawnAnchor();

  // Fall = lose life
  if (py - 0 > H + 60) {
    loseLife();
    if (lives > 0) { py = H * 0.3; pvy = 0; pvx = 4; attached = false; }
  }

  // Win: scrolled far enough
  if (scrolled > W * 8) endGame(true);
}

function grabNearest() {
  if (attached) {
    // Release
    attached = false;
    return;
  }
  // Find nearest anchor on screen
  let best = null, bestDist = 200;
  for (const a of anchors) {
    const ax = a.x - camX, ay = a.y;
    const dist = Math.sqrt((px - camX - ax)**2 + (py - ay)**2);
    if (dist < bestDist && ay < py - 20) { best = a; bestDist = dist; }
  }
  if (best) {
    attached = true;
    anchorX = best.x;
    anchorY = best.y;
    ropeLen = Math.max(60, Math.min(ROPE_LEN, Math.sqrt((px - anchorX)**2 + (py - anchorY)**2)));
    angle = Math.atan2(px - anchorX, -(py - anchorY));
    avel = pvx / ropeLen;
  }
}

cv.addEventListener('touchstart', e => { e.preventDefault(); if (running) grabNearest(); }, { passive: false });
cv.addEventListener('mousedown', e => { e.preventDefault(); if (running) grabNearest(); });

function drawAll() {
  // BG gradient
  const bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#050515'); bg.addColorStop(1, '#1a0030');
  ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

  // Stalactites
  for (const a of anchors) {
    const ax = a.x - camX;
    if (ax < -20 || ax > W + 20) continue;
    ctx.fillStyle = '#333355';
    ctx.beginPath();
    ctx.moveTo(ax - 12, 0); ctx.lineTo(ax + 12, 0); ctx.lineTo(ax, a.y - P_R); ctx.closePath(); ctx.fill();
    ctx.fillStyle = '#C8A2C8';
    ctx.beginPath(); ctx.arc(ax, a.y, a.r, 0, Math.PI*2); ctx.fill();
  }

  // Rope
  if (attached) {
    ctx.strokeStyle = '#C8A2C8'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(anchorX - camX, anchorY); ctx.lineTo(px - camX, py); ctx.stroke();
  }

  // Dust
  for (const d of dustItems) {
    if (!d.alive) continue;
    const dx = d.x - camX;
    if (dx < -20 || dx > W + 20) continue;
    ctx.font = '20px serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('✨', dx, d.y);
  }

  // Spikes at bottom
  ctx.fillStyle = '#cc4444';
  for (let i = 0; i < Math.ceil(W / 30); i++) {
    ctx.beginPath(); ctx.moveTo(i*30, H); ctx.lineTo(i*30+15, H-20); ctx.lineTo(i*30+30, H); ctx.fill();
  }

  // Player
  const spx = px - camX;
  if (selfieCanvas.width > 0 && selfieCtx.getImageData(0,0,1,1).data[3] > 0) {
    ctx.save(); ctx.beginPath(); ctx.arc(spx, py, P_R, 0, Math.PI*2); ctx.clip();
    ctx.drawImage(selfieCanvas, spx - P_R, py - P_R, P_R*2, P_R*2); ctx.restore();
  } else {
    ctx.font = `${P_R*2}px serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('🧑‍🚀', spx, py);
  }

  // Progress
  const prog = Math.min(100, Math.floor(scrolled / (W * 8) * 100));
  ctx.fillStyle = 'rgba(255,255,255,.4)'; ctx.font = '13px sans-serif'; ctx.textAlign = 'right'; ctx.textBaseline = 'top';
  ctx.fillText(`${prog}%`, W - 10, 10);
}
"""

# ==================== NIVEAU 5 — Dark Maze ====================
N5_JS = r"""
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W, H;
function resize() { W = cv.width = cv.offsetWidth; H = cv.height = cv.offsetHeight; }
window.addEventListener('resize', () => { resize(); if(running) drawAll(); });

const CELL = 56, LIGHT_R = 90;
let maze, cols, rows, px, py, ex, ey, dustItems, mx, my;

function initGame() {
  resize();
  cols = Math.floor(W / CELL); rows = Math.floor(H / CELL);
  if (cols % 2 === 0) cols--;
  if (rows % 2 === 0) rows--;
  maze = generateMaze(cols, rows);
  px = CELL * 1 + CELL / 2; py = CELL * 1 + CELL / 2;
  ex = CELL * (cols - 2) + CELL / 2; ey = CELL * (rows - 2) + CELL / 2;
  mx = px; my = py;
  dustItems = [];
  // Scatter dust in open cells
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (maze[r][c] === 0 && Math.random() < 0.12) {
        dustItems.push({ x: c * CELL + CELL / 2, y: r * CELL + CELL / 2, alive: true });
      }
    }
  }
  loop();
}

function generateMaze(cols, rows) {
  const g = Array.from({ length: rows }, () => Array(cols).fill(1));
  function carve(c, r) {
    g[r][c] = 0;
    const dirs = [[0,-2],[0,2],[-2,0],[2,0]].sort(() => Math.random() - 0.5);
    for (const [dc, dr] of dirs) {
      const nc = c + dc, nr = r + dr;
      if (nr > 0 && nr < rows && nc > 0 && nc < cols && g[nr][nc] === 1) {
        g[r + dr/2][c + dc/2] = 0;
        carve(nc, nr);
      }
    }
  }
  carve(1, 1);
  g[rows-2][cols-2] = 0;
  return g;
}

function loop() {
  if (!running) return;
  update();
  drawAll();
  requestAnimationFrame(loop);
}

const SPEED = 3;
let moveDir = { x: 0, y: 0 };

function update() {
  let nx = px + moveDir.x * SPEED;
  let ny = py + moveDir.y * SPEED;
  const r = 14;

  // Wall collision
  if (!isWall(nx, py, r)) px = nx;
  if (!isWall(px, ny, r)) py = ny;

  mx = px; my = py;

  // Collect dust
  for (const d of dustItems) {
    if (!d.alive) continue;
    if (Math.abs(d.x - px) < 22 && Math.abs(d.y - py) < 22) { d.alive = false; addDust(10); }
  }

  // Reach exit
  if (Math.abs(px - ex) < 24 && Math.abs(py - ey) < 24) endGame(true);
}

function isWall(x, y, r) {
  const corners = [[x-r, y-r],[x+r, y-r],[x-r, y+r],[x+r, y+r],[x, y-r],[x, y+r],[x-r, y],[x+r, y]];
  for (const [cx, cy] of corners) {
    const gc = Math.floor(cx / CELL), gr = Math.floor(cy / CELL);
    if (gr < 0 || gr >= rows || gc < 0 || gc >= cols) return true;
    if (maze[gr][gc] === 1) return true;
  }
  return false;
}

function drawAll() {
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);

  // Draw maze under light
  ctx.save();
  // Clip to light circle
  ctx.beginPath(); ctx.arc(mx, my, LIGHT_R, 0, Math.PI*2); ctx.clip();

  // Draw walls
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (maze[r][c] === 1) {
        ctx.fillStyle = '#1a1a4a';
        ctx.fillRect(c * CELL, r * CELL, CELL, CELL);
        ctx.strokeStyle = '#2a2a6a'; ctx.lineWidth = 1;
        ctx.strokeRect(c * CELL, r * CELL, CELL, CELL);
      } else {
        ctx.fillStyle = '#0a0820';
        ctx.fillRect(c * CELL, r * CELL, CELL, CELL);
      }
    }
  }

  // Exit marker
  ctx.font = '28px serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('🚀', ex, ey);

  // Dust
  for (const d of dustItems) {
    if (!d.alive) continue;
    ctx.font = '18px serif'; ctx.fillText('✨', d.x, d.y);
  }

  ctx.restore();

  // Vignette around light
  const grad = ctx.createRadialGradient(mx, my, LIGHT_R * 0.7, mx, my, LIGHT_R);
  grad.addColorStop(0, 'rgba(0,0,0,0)'); grad.addColorStop(1, 'rgba(0,0,0,0.98)');
  ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);

  // Player glyph above vignette
  if (selfieCanvas.width > 0 && selfieCtx.getImageData(0,0,1,1).data[3] > 0) {
    ctx.save(); ctx.beginPath(); ctx.arc(mx, my, 18, 0, Math.PI*2); ctx.clip();
    ctx.drawImage(selfieCanvas, mx - 18, my - 18, 36, 36); ctx.restore();
  } else {
    ctx.font = '30px serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('🔦', mx, my);
  }
}

// Controls: swipe on canvas
let t0x, t0y;
cv.addEventListener('touchstart', e => { e.preventDefault(); const t = e.touches[0]; t0x = t.clientX; t0y = t.clientY; }, { passive: false });
cv.addEventListener('touchmove', e => {
  e.preventDefault();
  const t = e.touches[0];
  const dx = t.clientX - t0x, dy = t.clientY - t0y;
  if (Math.abs(dx) > Math.abs(dy)) moveDir = { x: dx > 0 ? 1 : -1, y: 0 };
  else moveDir = { x: 0, y: dy > 0 ? 1 : -1 };
}, { passive: false });
cv.addEventListener('touchend', e => { e.preventDefault(); moveDir = { x: 0, y: 0 }; }, { passive: false });
window.addEventListener('keydown', e => {
  if (e.key === 'ArrowLeft') moveDir = { x: -1, y: 0 };
  if (e.key === 'ArrowRight') moveDir = { x: 1, y: 0 };
  if (e.key === 'ArrowUp') moveDir = { x: 0, y: -1 };
  if (e.key === 'ArrowDown') moveDir = { x: 0, y: 1 };
});
window.addEventListener('keyup', () => moveDir = { x: 0, y: 0 });
"""

# ==================== NIVEAU 6 — Agar.io ====================
N6_JS = r"""
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W, H;
function resize() { W = cv.width = cv.offsetWidth; H = cv.height = cv.offsetHeight; }
window.addEventListener('resize', () => { resize(); });

const WORLD = 1200;
let player, particles, enemies, camX, camY, frameCount;

function initGame() {
  resize();
  player = { x: WORLD/2, y: WORLD/2, r: 22, score: 0 };
  particles = [];
  enemies = [];
  camX = 0; camY = 0; frameCount = 0;
  for (let i = 0; i < 80; i++) spawnParticle();
  for (let i = 0; i < 6; i++) spawnEnemy();
  loop();
}

function spawnParticle() {
  particles.push({ x: Math.random() * WORLD, y: Math.random() * WORLD, r: 6 + Math.random() * 8, dust: Math.random() < 0.3, color: randomColor() });
}

function spawnEnemy() {
  const minR = 10, maxR = 35;
  let x, y;
  do { x = Math.random() * WORLD; y = Math.random() * WORLD; }
  while (Math.sqrt((x - player.x)**2 + (y - player.y)**2) < 200);
  enemies.push({ x, y, r: minR + Math.random() * (maxR - minR), vx: (Math.random()-0.5)*2, vy: (Math.random()-0.5)*2, color: randomColor() });
}

function randomColor() {
  const hues = [200, 280, 320, 40, 160, 0];
  const h = hues[Math.floor(Math.random() * hues.length)];
  return `hsl(${h},70%,55%)`;
}

let touchX = null, touchY = null;

function loop() {
  if (!running) return;
  frameCount++;
  update();
  drawAll();
  requestAnimationFrame(loop);
}

function update() {
  // Move player toward touch/mouse
  if (touchX !== null) {
    const scrX = player.x - camX, scrY = player.y - camY;
    const dx = touchX - scrX, dy = touchY - scrY;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist > 5) {
      const speed = Math.max(1.5, 6 - player.r * 0.12);
      player.x += dx / dist * speed;
      player.y += dy / dist * speed;
    }
  }
  player.x = Math.max(player.r, Math.min(WORLD - player.r, player.x));
  player.y = Math.max(player.r, Math.min(WORLD - player.r, player.y));

  // Camera
  camX = player.x - W / 2; camY = player.y - H / 2;

  // Absorb particles
  for (const p of particles) {
    const dx = player.x - p.x, dy = player.y - p.y;
    if (Math.sqrt(dx*dx+dy*dy) < player.r) {
      p.dead = true;
      player.r += 0.5;
      if (p.dust) addDust(8);
      else addDust(2);
    }
  }
  particles = particles.filter(p => !p.dead);
  while (particles.length < 50) spawnParticle();

  // Move enemies
  for (const e of enemies) {
    e.x += e.vx; e.y += e.vy;
    if (e.x < e.r || e.x > WORLD - e.r) e.vx *= -1;
    if (e.y < e.r || e.y > WORLD - e.r) e.vy *= -1;
    // Enemy absorbs particles
    for (const p of particles) {
      const dx = e.x - p.x, dy = e.y - p.y;
      if (Math.sqrt(dx*dx+dy*dy) < e.r) { p.dead = true; e.r = Math.min(e.r + 0.3, 50); }
    }
    // Interact with player
    const dx = player.x - e.x, dy = player.y - e.y;
    const dist = Math.sqrt(dx*dx+dy*dy);
    if (dist < player.r + e.r) {
      if (player.r > e.r * 1.1) {
        e.dead = true; player.r += e.r * 0.3; addDust(15);
      } else if (e.r > player.r * 1.1) {
        loseLife();
        if (lives > 0) { player.r = Math.max(22, player.r * 0.7); }
      }
    }
  }
  enemies = enemies.filter(e => !e.dead);
  while (enemies.length < 4) spawnEnemy();
  particles = particles.filter(p => !p.dead);

  // Win: player is very large
  if (player.r > 90) endGame(true);
}

function drawAll() {
  ctx.fillStyle = '#0a0820'; ctx.fillRect(0, 0, W, H);

  // Grid
  ctx.strokeStyle = 'rgba(255,255,255,.05)'; ctx.lineWidth = 1;
  const gs = 80;
  for (let x = -camX % gs; x < W; x += gs) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = -camY % gs; y < H; y += gs) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

  // World border
  ctx.strokeStyle = 'rgba(200,162,200,.3)'; ctx.lineWidth = 4;
  ctx.strokeRect(-camX, -camY, WORLD, WORLD);

  // Particles
  for (const p of particles) {
    const sx = p.x - camX, sy = p.y - camY;
    if (sx < -50 || sx > W + 50 || sy < -50 || sy > H + 50) continue;
    ctx.fillStyle = p.dust ? '#FFD700' : p.color;
    ctx.beginPath(); ctx.arc(sx, sy, p.r, 0, Math.PI*2); ctx.fill();
    if (p.dust) { ctx.font = `${p.r}px serif`; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText('✨', sx, sy); }
  }

  // Enemies
  for (const e of enemies) {
    const sx = e.x - camX, sy = e.y - camY;
    if (sx < -100 || sx > W + 100) continue;
    ctx.fillStyle = e.color; ctx.globalAlpha = 0.85;
    ctx.beginPath(); ctx.arc(sx, sy, e.r, 0, Math.PI*2); ctx.fill(); ctx.globalAlpha = 1;
    ctx.strokeStyle = 'rgba(255,255,255,.3)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(sx, sy, e.r, 0, Math.PI*2); ctx.stroke();
  }

  // Player
  const spx = player.x - camX, spy = player.y - camY;
  if (selfieCanvas.width > 0 && selfieCtx.getImageData(0,0,1,1).data[3] > 0) {
    ctx.save(); ctx.beginPath(); ctx.arc(spx, spy, player.r, 0, Math.PI*2); ctx.clip();
    ctx.drawImage(selfieCanvas, spx - player.r, spy - player.r, player.r*2, player.r*2); ctx.restore();
  } else {
    ctx.font = `${player.r * 1.8}px serif`; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText('🌕', spx, spy);
  }
  ctx.strokeStyle = '#C8A2C8'; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.arc(spx, spy, player.r, 0, Math.PI*2); ctx.stroke();
}

cv.addEventListener('touchmove', e => { e.preventDefault(); const r = cv.getBoundingClientRect(); touchX = e.touches[0].clientX - r.left; touchY = e.touches[0].clientY - r.top; }, { passive: false });
cv.addEventListener('touchstart', e => { e.preventDefault(); const r = cv.getBoundingClientRect(); touchX = e.touches[0].clientX - r.left; touchY = e.touches[0].clientY - r.top; }, { passive: false });
cv.addEventListener('touchend', e => { e.preventDefault(); touchX = null; }, { passive: false });
cv.addEventListener('mousemove', e => { const r = cv.getBoundingClientRect(); touchX = e.clientX - r.left; touchY = e.clientY - r.top; });
cv.addEventListener('mouseleave', () => { touchX = null; });
"""

# ==================== NIVEAU 7 — Jetpack Joyride ====================
N7_JS = r"""
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W, H;
function resize() { W = cv.width = cv.offsetWidth; H = cv.height = cv.offsetHeight; }
window.addEventListener('resize', () => { resize(); });

const GRAV = 0.4, JETPACK = -0.8, SPEED = 3.5, P_R = 20;
let py, pvy, obstacles, dustItems, particles, distance, pressing, frameCount;

function initGame() {
  resize();
  py = H * 0.5; pvy = 0; pressing = false;
  obstacles = []; dustItems = []; particles = [];
  distance = 0; frameCount = 0;
  loop();
}

function loop() {
  if (!running) return;
  frameCount++;
  update();
  drawAll();
  requestAnimationFrame(loop);
}

function update() {
  // Physics
  pvy += pressing ? JETPACK : GRAV * 0.6;
  pvy = Math.max(-8, Math.min(8, pvy));
  py += pvy;
  distance += SPEED;

  // Clamp
  if (py < P_R) { py = P_R; pvy = 0; }
  if (py > H - P_R) { py = H - P_R; pvy = 0; loseLife(); if(lives>0){py=H*0.5;pvy=0;} }

  // Obstacles (missile rows)
  if (frameCount % 80 === 0) {
    const gapY = H * 0.2 + Math.random() * H * 0.5;
    const gapH = H * 0.3;
    obstacles.push({ x: W + 40, topH: gapY, botY: gapY + gapH, speed: SPEED });
    if (Math.random() < 0.7)
      dustItems.push({ x: W + 40, y: gapY + gapH / 2, alive: true });
  }

  // Move obstacles
  for (const o of obstacles) o.x -= SPEED * 1.1;
  obstacles = obstacles.filter(o => o.x > -60);
  for (const d of dustItems) d.x -= SPEED * 1.1;
  dustItems = dustItems.filter(d => d.x > -30);

  // Collision with obstacles
  const px = W * 0.2;
  for (const o of obstacles) {
    if (Math.abs(o.x - px) < P_R + 18) {
      if (py - P_R < o.topH || py + P_R > o.botY) { loseLife(); if(lives>0){py=H*0.5;pvy=0;} break; }
    }
  }

  // Collect dust
  for (const d of dustItems) {
    if (!d.alive) continue;
    if (Math.abs(d.x - px) < P_R + 16 && Math.abs(d.y - py) < P_R + 16) { d.alive=false; addDust(10); }
  }

  // Particle trail
  if (pressing) particles.push({ x: px - P_R, y: py + P_R, vx: -3 + Math.random(), vy: (Math.random()-0.5)*3, life: 20, color: Math.random()<0.5?'#FF8C00':'#FFD700' });
  particles = particles.filter(p => { p.x+=p.vx; p.y+=p.vy; p.life--; return p.life>0; });

  if (distance > 5000) endGame(true);
}

function drawAll() {
  // BG
  const bg = ctx.createLinearGradient(0, 0, W, 0);
  bg.addColorStop(0, '#050520'); bg.addColorStop(1, '#0a1030');
  ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

  // moving bg lines
  ctx.strokeStyle = 'rgba(255,255,255,.04)'; ctx.lineWidth = 1;
  for (let i = 0; i < 8; i++) {
    const lx = W - ((distance * 2 + i * (W/8)) % W);
    ctx.beginPath(); ctx.moveTo(lx, 0); ctx.lineTo(lx, H); ctx.stroke();
  }

  // Floor/ceiling
  ctx.fillStyle = '#1a1a4a';
  ctx.fillRect(0, 0, W, 6); ctx.fillRect(0, H - 6, W, 6);

  // Obstacles (electric walls)
  for (const o of obstacles) {
    const grad = ctx.createLinearGradient(o.x, 0, o.x + 36, 0);
    grad.addColorStop(0, '#ff8800'); grad.addColorStop(1, '#ffcc00');
    ctx.fillStyle = grad;
    ctx.fillRect(o.x - 18, 0, 36, o.topH);
    ctx.fillRect(o.x - 18, o.botY, 36, H - o.botY);
    // Electric arc effect
    ctx.strokeStyle = '#ffff00'; ctx.lineWidth = 2; ctx.globalAlpha = 0.6;
    ctx.beginPath(); ctx.moveTo(o.x, o.topH);
    for (let i = 1; i <= 5; i++) ctx.lineTo(o.x + (Math.random()-0.5)*10, o.topH + (o.botY - o.topH) * i/5);
    ctx.stroke(); ctx.globalAlpha = 1;
  }

  // Dust
  for (const d of dustItems) {
    if (!d.alive) continue;
    ctx.font = '20px serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText('✨', d.x, d.y);
  }

  // Jetpack particles
  for (const p of particles) {
    ctx.globalAlpha = p.life / 20;
    ctx.fillStyle = p.color; ctx.beginPath(); ctx.arc(p.x, p.y, 5, 0, Math.PI*2); ctx.fill();
  }
  ctx.globalAlpha = 1;

  // Player
  const px = W * 0.2;
  if (selfieCanvas.width > 0 && selfieCtx.getImageData(0,0,1,1).data[3] > 0) {
    ctx.save(); ctx.beginPath(); ctx.arc(px, py, P_R, 0, Math.PI*2); ctx.clip();
    ctx.drawImage(selfieCanvas, px-P_R, py-P_R, P_R*2, P_R*2); ctx.restore();
  } else {
    ctx.font = `${P_R*2.2}px serif`; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText('🚀', px, py);
  }

  // Distance
  ctx.fillStyle = 'rgba(255,255,255,.5)'; ctx.font = '13px sans-serif'; ctx.textAlign='right'; ctx.textBaseline='top';
  ctx.fillText(`${Math.floor(distance)}m`, W-10, 10);
}

function press(e) { e.preventDefault(); pressing = true; }
function release(e) { e.preventDefault(); pressing = false; }
cv.addEventListener('touchstart', press, { passive: false });
cv.addEventListener('touchend', release, { passive: false });
cv.addEventListener('mousedown', press);
window.addEventListener('mouseup', release);
"""

# ==================== NIVEAU 8 — Crossy Road ====================
N8_JS = r"""
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W, H;
function resize() { W = cv.width = cv.offsetWidth; H = cv.height = cv.offsetHeight; }
window.addEventListener('resize', () => { resize(); if(running) drawAll(); });

const CELL_SIZE = 60, ROWS_VISIBLE = 10;
let px, py, targetPx, targetPy, moving, lanes, dustItems, camOffsetY, stepCount;
let swipeStart = null;

function initGame() {
  resize();
  px = Math.floor(W / CELL_SIZE / 2);
  py = ROWS_VISIBLE - 2;
  targetPx = px; targetPy = py;
  moving = false;
  camOffsetY = 0;
  stepCount = 0;
  lanes = [];
  dustItems = [];
  for (let r = 0; r < ROWS_VISIBLE + 5; r++) generateLane(r);
  loop();
}

function generateLane(row) {
  const types = ['safe', 'safe', 'road', 'road', 'road', 'water'];
  const type = row < 2 ? 'safe' : types[Math.floor(Math.random() * types.length)];
  const cars = [];
  const logs = [];
  if (type === 'road') {
    const dir = Math.random() < 0.5 ? 1 : -1;
    const count = 1 + Math.floor(Math.random() * 3);
    const speed = 1 + Math.random() * 2;
    for (let i = 0; i < count; i++) cars.push({ x: Math.random() * (W / CELL_SIZE), dir, speed });
  }
  if (type === 'water') {
    const dir = Math.random() < 0.5 ? 1 : -1;
    const count = 2 + Math.floor(Math.random() * 3);
    const speed = 0.8 + Math.random();
    for (let i = 0; i < count; i++) logs.push({ x: i * 5 * Math.random() * (W / CELL_SIZE), dir, speed, w: 2 + Math.floor(Math.random() * 2) });
  }
  const hasDust = type === 'safe' && Math.random() < 0.3;
  if (hasDust) dustItems.push({ col: Math.floor(Math.random() * Math.floor(W / CELL_SIZE)), row, alive: true });
  lanes.push({ type, cars, logs, row });
}

function loop() {
  if (!running) return;
  updateLane();
  drawAll();
  requestAnimationFrame(loop);
}

let interp = 0;
let fromPx, fromPy;

function move(dc, dr) {
  if (moving) return;
  const nx = px + dc, ny = py + dr;
  const cols = Math.floor(W / CELL_SIZE);
  if (nx < 0 || nx >= cols) return;
  fromPx = px; fromPy = py;
  targetPx = nx; targetPy = ny;
  moving = true; interp = 0;
  stepCount++;
}

function updateLane() {
  // Interpolate movement
  if (moving) {
    interp += 0.15;
    if (interp >= 1) { px = targetPx; py = targetPy; moving = false; interp = 1; }
  }

  // Camera: follow player forward
  const realRow = py + camOffsetY;
  if (targetPy < 2) {
    camOffsetY++;
    // Generate new lane at top
    const topRow = lanes[0].row - 1;
    generateLane(topRow);
    lanes.sort((a, b) => a.row - b.row);
    // Add dust check
    if (camOffsetY > 100) { endGame(true); return; }
  }

  // Move cars and logs
  const cols = Math.floor(W / CELL_SIZE);
  for (const lane of lanes) {
    for (const c of lane.cars) {
      c.x += c.dir * c.speed * 0.03;
      if (c.x > cols + 2) c.x = -2;
      if (c.x < -2) c.x = cols + 2;
    }
    for (const l of lane.logs) {
      l.x += l.dir * l.speed * 0.025;
      if (l.x > cols + 4) l.x = -4;
      if (l.x < -4) l.x = cols + 4;
    }
  }

  // Collision
  const effPx = moving ? fromPx + (targetPx - fromPx) * interp : px;
  const effPy = moving ? fromPy + (targetPy - fromPy) * interp : py;
  const lane = lanes.find(l => l.row === Math.round(effPy));
  if (lane) {
    if (lane.type === 'road') {
      for (const c of lane.cars) {
        if (Math.abs(c.x - effPx) < 1.2) { loseLife(); if(lives>0){px=Math.floor(W/CELL_SIZE/2);py=ROWS_VISIBLE-2;targetPx=px;targetPy=py;camOffsetY=0;} return; }
      }
    }
    if (lane.type === 'water') {
      let onLog = false;
      for (const l of lane.logs) { if (effPx >= l.x - 0.5 && effPx <= l.x + l.w + 0.5) { onLog = true; break; } }
      if (!onLog) { loseLife(); if(lives>0){px=Math.floor(W/CELL_SIZE/2);py=ROWS_VISIBLE-2;targetPx=px;targetPy=py;camOffsetY=0;} return; }
    }
  }

  // Collect dust
  for (const d of dustItems) {
    if (!d.alive) continue;
    if (d.col === Math.round(effPx) && d.row === Math.round(effPy)) { d.alive = false; addDust(12); }
  }
}

function drawAll() {
  ctx.fillStyle = '#0a1a0a'; ctx.fillRect(0, 0, W, H);
  const cols = Math.floor(W / CELL_SIZE);
  const effPx = moving ? fromPx + (targetPx - fromPx) * interp : px;
  const effPy = moving ? fromPy + (targetPy - fromPy) * interp : py;

  for (const lane of lanes) {
    const screenRow = lane.row - effPy + ROWS_VISIBLE * 0.7;
    const sy = screenRow * CELL_SIZE;
    if (sy < -CELL_SIZE || sy > H + CELL_SIZE) continue;

    // Lane BG
    if (lane.type === 'road') ctx.fillStyle = '#1a1a1a';
    else if (lane.type === 'water') ctx.fillStyle = '#0a2a4a';
    else ctx.fillStyle = '#0a2a0a';
    ctx.fillRect(0, sy, W, CELL_SIZE);

    // Lane details
    if (lane.type === 'road') {
      ctx.strokeStyle = 'rgba(255,255,100,.15)'; ctx.lineWidth = 2; ctx.setLineDash([20,20]);
      ctx.beginPath(); ctx.moveTo(0, sy + CELL_SIZE/2); ctx.lineTo(W, sy + CELL_SIZE/2); ctx.stroke(); ctx.setLineDash([]);
      for (const c of lane.cars) {
        const cx = c.x * CELL_SIZE;
        ctx.fillStyle = c.dir > 0 ? '#ff4444' : '#4444ff';
        ctx.fillRect(cx, sy + 8, CELL_SIZE * 1.5, CELL_SIZE - 16);
        ctx.font = '22px serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
        ctx.fillText(c.dir > 0 ? '🚗' : '🚕', cx + CELL_SIZE * 0.75, sy + CELL_SIZE/2);
      }
    } else if (lane.type === 'water') {
      for (const l of lane.logs) {
        ctx.fillStyle = '#8B5E3C';
        ctx.fillRect(l.x * CELL_SIZE, sy + 10, l.w * CELL_SIZE, CELL_SIZE - 20);
      }
    } else {
      // Trees on sides
    }

    // Dust
    for (const d of dustItems) {
      if (!d.alive || d.row !== lane.row) continue;
      ctx.font = '22px serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
      ctx.fillText('✨', d.col * CELL_SIZE + CELL_SIZE/2, sy + CELL_SIZE/2);
    }
  }

  // Player
  const spx = effPx * CELL_SIZE + CELL_SIZE/2;
  const spy = ROWS_VISIBLE * 0.7 * CELL_SIZE + CELL_SIZE/2;
  if (selfieCanvas.width > 0 && selfieCtx.getImageData(0,0,1,1).data[3] > 0) {
    ctx.save(); ctx.beginPath(); ctx.arc(spx, spy, 24, 0, Math.PI*2); ctx.clip();
    ctx.drawImage(selfieCanvas, spx-24, spy-24, 48, 48); ctx.restore();
  } else {
    ctx.font = '40px serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText('🐸', spx, spy);
  }

  // Step counter
  ctx.fillStyle = 'rgba(255,255,255,.5)'; ctx.font = '13px sans-serif'; ctx.textAlign='right'; ctx.textBaseline='top';
  ctx.fillText(`${stepCount} pas`, W-10, 10);
}

// Swipe controls
cv.addEventListener('touchstart', e => { e.preventDefault(); const t = e.touches[0]; swipeStart = { x: t.clientX, y: t.clientY }; }, { passive: false });
cv.addEventListener('touchend', e => {
  e.preventDefault();
  if (!swipeStart || !running) return;
  const t = e.changedTouches[0];
  const dx = t.clientX - swipeStart.x, dy = t.clientY - swipeStart.y;
  if (Math.abs(dx) > Math.abs(dy)) { if (dx > 20) move(1, 0); else if (dx < -20) move(-1, 0); }
  else { if (dy < -20) move(0, -1); else if (dy > 20) move(0, 1); }
  swipeStart = null;
}, { passive: false });
window.addEventListener('keydown', e => {
  if (!running) return;
  if (e.key === 'ArrowLeft') move(-1, 0);
  if (e.key === 'ArrowRight') move(1, 0);
  if (e.key === 'ArrowUp') move(0, -1);
  if (e.key === 'ArrowDown') move(0, 1);
});
"""

# ==================== NIVEAU 9 — Duel Réflexe ====================
N9_JS = r"""
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W, H;
function resize() { W = cv.width = cv.offsetWidth; H = cv.height = cv.offsetHeight; }
window.addEventListener('resize', () => { resize(); if(running) drawAll(); });

const ROUNDS = 5;
let round, playerWins, enemyWins, phase, countdown, signal, tStart, tEnd;
let reactionTimes, pressed, enemyTime;
let particles;

function initGame() {
  resize();
  round = 0;
  playerWins = 0; enemyWins = 0;
  reactionTimes = [];
  particles = [];
  nextRound();
  loop();
}

function nextRound() {
  round++;
  phase = 'waiting'; // waiting -> ready -> FIRE! -> result
  countdown = 2 + Math.random() * 3; // seconds before FIRE
  pressed = false;
  signal = false;
  tStart = null; tEnd = null;
  enemyTime = null;
  setTimeout(() => {
    if (!running || gameover) return;
    phase = 'ready';
    tStart = Date.now();
    signal = true;
    // Enemy reacts in 200-700ms (fair challenge)
    enemyTime = 200 + Math.random() * 500;
    setTimeout(() => {
      if (!running || gameover || pressed) return;
      // Enemy fires
      if (!pressed) {
        enemyWins++;
        for (let i=0;i<12;i++) particles.push({x:W*0.75,y:H*0.5,vx:(Math.random()-0.5)*8,vy:(Math.random()-0.5)*8,life:40,color:'#ff4444'});
        phase = 'result_enemy';
        if (enemyWins >= 3) { endGame(false); return; }
        if (round < ROUNDS) setTimeout(nextRound, 1500); else endGame(playerWins >= 3);
      }
    }, enemyTime);
  }, countdown * 1000);
}

function playerFire(e) {
  if (e) e.preventDefault();
  if (!running || gameover) return;
  if (phase === 'waiting') {
    // Too early! Penalize
    enemyWins++;
    phase = 'result_early';
    if (enemyWins >= 3) { endGame(false); return; }
    if (round < ROUNDS) setTimeout(nextRound, 1500); else endGame(playerWins >= 3);
    return;
  }
  if (phase !== 'ready' || pressed) return;
  pressed = true;
  tEnd = Date.now();
  const rt = tEnd - tStart;
  reactionTimes.push(rt);
  if (rt < enemyTime) {
    playerWins++;
    for (let i=0;i<12;i++) particles.push({x:W*0.25,y:H*0.5,vx:(Math.random()-0.5)*8,vy:(Math.random()-0.5)*8,life:40,color:'#FFD700'});
    addDust(10);
    phase = 'result_player';
  } else {
    enemyWins++;
    phase = 'result_enemy';
  }
  if (phase === 'result_player' || phase === 'result_enemy') {
    if (playerWins >= 3 || enemyWins >= 3) { endGame(playerWins >= 3); return; }
    if (round < ROUNDS) setTimeout(nextRound, 1500); else endGame(playerWins >= 3);
  }
}

function loop() {
  if (!running) return;
  particles = particles.filter(p => { p.x+=p.vx; p.y+=p.vy; p.life--; return p.life>0; });
  drawAll();
  requestAnimationFrame(loop);
}

function drawAll() {
  // BG color based on phase
  let bgColor = signal ? '#0a2a0a' : '#0a0a1a';
  if (phase === 'result_early') bgColor = '#2a0a0a';
  ctx.fillStyle = bgColor; ctx.fillRect(0, 0, W, H);

  // FIRE signal
  if (signal && (phase === 'ready' || phase === 'result_player' || phase === 'result_enemy')) {
    ctx.fillStyle = signal ? '#00ff44' : '#1a1a1a';
    ctx.fillRect(W*0.3, H*0.35, W*0.4, H*0.15);
    ctx.fillStyle = '#000'; ctx.font = 'bold 28px sans-serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText('FEU !', W/2, H*0.425);
  }

  if (phase === 'waiting') {
    ctx.fillStyle = '#ff4444';
    ctx.fillRect(W*0.3, H*0.35, W*0.4, H*0.15);
    ctx.fillStyle = '#fff'; ctx.font = 'bold 24px sans-serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText('ATTENDS...', W/2, H*0.425);
  }

  if (phase === 'result_early') {
    ctx.fillStyle = '#ff2222'; ctx.font = 'bold 22px sans-serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText('Trop tôt ! -1', W/2, H*0.58);
  }

  // Player avatar
  if (selfieCanvas.width > 0 && selfieCtx.getImageData(0,0,1,1).data[3] > 0) {
    ctx.save(); ctx.beginPath(); ctx.arc(W*0.22, H*0.5, 36, 0, Math.PI*2); ctx.clip();
    ctx.drawImage(selfieCanvas, W*0.22-36, H*0.5-36, 72, 72); ctx.restore();
  } else {
    ctx.font = '64px serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText('🧑‍🚀', W*0.22, H*0.5);
  }

  // Enemy avatar
  ctx.font = '64px serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText('👾', W*0.78, H*0.5);

  // VS
  ctx.fillStyle = 'rgba(255,255,255,.4)'; ctx.font = 'bold 20px sans-serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText('VS', W/2, H*0.5);

  // Score
  ctx.fillStyle = '#FFD700'; ctx.font = 'bold 28px sans-serif'; ctx.textAlign='center';
  ctx.textBaseline = 'middle';
  ctx.fillText(playerWins + ' — ' + enemyWins, W/2, H * 0.25);
  ctx.fillStyle = 'rgba(255,255,255,.5)'; ctx.font = '14px sans-serif';
  ctx.fillText('Round ' + round + '/' + ROUNDS, W/2, H * 0.16);

  // Reaction time
  if (reactionTimes.length > 0) {
    const last = reactionTimes[reactionTimes.length - 1];
    ctx.fillStyle = 'rgba(255,255,255,.5)'; ctx.font = '13px sans-serif'; ctx.textAlign='center';
    ctx.fillText('Réflexe: ' + last + 'ms', W/2, H * 0.72);
  }

  // Particles
  for (const p of particles) {
    ctx.globalAlpha = p.life / 40;
    ctx.fillStyle = p.color; ctx.beginPath(); ctx.arc(p.x, p.y, 6, 0, Math.PI*2); ctx.fill();
  }
  ctx.globalAlpha = 1;

  // Instruction
  ctx.fillStyle = 'rgba(255,255,255,.3)'; ctx.font = '14px sans-serif'; ctx.textAlign='center'; ctx.textBaseline='bottom';
  ctx.fillText('Appuie quand "FEU !" s\'allume en vert', W/2, H - 16);
}

cv.addEventListener('touchstart', playerFire, { passive: false });
cv.addEventListener('mousedown', playerFire);
"""

games = [
    (1, 'Lune de Verre', '🌑', 'Lance des cosmonautes avec ta fronde !<br>Vise les cristaux pour les faire exploser.', N1_JS),
    (2, 'Lune de Cendre', '🌒', 'Tap pour voler ! Évite les colonnes de lave.', N2_JS),
    (3, 'Lune de Lierre', '🌓', 'Rebondis sur les plateformes pour monter le plus haut possible !<br>Touche gauche/droite pour te diriger.', N3_JS),
    (4, 'Lune de Givre', '🌔', 'Tap pour agripper une stalactite.<br>Balance-toi et traverse l\'abîme !', N4_JS),
    (5, 'Lune d\'Ombre', '🌕', 'Tu ne vois que ce que ta lampe éclaire.<br>Trouve la sortie dans le labyrinthe !', N5_JS),
    (6, 'Lune de Fer', '🌖', 'Absorbe les particules plus petites que toi.<br>Grossis pour dominer l\'espace !', N6_JS),
    (7, 'Lune de Tempête', '🌗', 'Maintiens appuyé pour monter.<br>Relâche pour descendre. Évite les obstacles !', N7_JS),
    (8, 'Lune de Cristal', '🌘', 'Swipe ou utilise les flèches pour traverser.<br>Évite les voitures et l\'eau !', N8_JS),
    (9, 'Lune d\'Éclipse', '🌑', 'Duel de réflexes !<br>Appuie UNIQUEMENT quand le signal devient vert.', N9_JS),
]

for niveau, titre, emoji, desc, js in games:
    html = make_html(niveau, titre, emoji, desc, js)
    path = os.path.join(MINIJEUX_DIR, f'niveau{niveau}.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written: niveau{niveau}.html ({len(html)} chars)')

print('All 9 mini-jeux written!')
