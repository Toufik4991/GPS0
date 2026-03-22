content = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover">
<title>GPS0 N7</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:#000;font-family:system-ui,sans-serif;color:#fff;touch-action:none;user-select:none}
#hud{position:relative;z-index:20;display:flex;align-items:center;gap:10px;padding:6px 52px 6px 10px;background:rgba(0,0,0,.78);backdrop-filter:blur(6px);flex-shrink:0}
#lives{font-size:1.1rem;letter-spacing:2px;min-width:54px}
#timer{flex:1;text-align:center;font-size:.95rem;font-weight:bold;color:#ffaa55}
#score-hud{font-size:.9rem;color:#FFD700;font-weight:bold;min-width:52px;text-align:right}
#game-container{position:relative;z-index:1;flex:1;overflow:hidden;display:flex;flex-direction:column}
canvas{display:block;width:100%;height:100%}
body{display:flex;flex-direction:column;height:100dvh}
</style>
</head>
<body>
<div id="hud">
  <span id="lives">&#10084;&#10084;&#10084;</span>
  <span id="timer">2:30</span>
  <span id="score-hud">0 &#10024;</span>
</div>
<div id="game-container">
  <canvas id="cv"></canvas>
</div>
<script src="shared.js"></script>
<script>
window.NIVEAU = 7;
window.TUTO_TEXT = "Lune de Temp\u00eate \u2014 Maintien = monte \u00b7 Rel\u00e2che = tombe \u00b7 \u00c9vite les lasers \u00b7 \u2726 cristaux bonus";

const GRAV = 0.38, THRUST = -0.80, MAX_VY = 8.5;
const FLOOR_GFX = 55, CEIL_GFX = 45;
const LASER_W = 12, LASER_DELAY = 70, GAP_RATIO = 0.44;
const CRYSTAL_SPAWN_FRAMES = [1500, 3000, 4800, 6500, 8000];
const PLAYER_X = 100;

let player, lasers, crystals, sand, fxParticles;
let frame, bgT, invTimer, currentSpeed, laserTimer;
let bgScrollA, bgScrollB, holding, rafId;

function _getTargetSpeed() {
  if (frame < 3600) return 3.5;
  if (frame < 7200) return 5.2;
  return 7.0;
}
function _getLaserInterval() {
  if (frame < 3600) return 290;
  if (frame < 7200) return 215;
  return 162;
}

function gameReset() {
  cancelAnimationFrame(rafId);
  player = { y: 0, vy: 0, r: 18 };
  lasers = []; crystals = []; sand = []; fxParticles = [];
  frame = 0; bgT = 0; invTimer = 0; currentSpeed = 3.5;
  laserTimer = 120; bgScrollA = 0; bgScrollB = 0; holding = false;
}
window.gameReset = gameReset;

function _initSand(W, ceilY, floorY) {
  sand = [];
  const ph = floorY - ceilY;
  for (let i = 0; i < 38; i++) sand.push({
    x: Math.random() * W,
    y: ceilY + Math.random() * ph,
    vy: (Math.random() - .5) * .55,
    size: .8 + Math.random() * 2.2,
    alpha: .12 + Math.random() * .28,
    spd: .45 + Math.random() * .9
  });
}

function gameStart() {
  const cv = document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  player.y = cv.height / 2;
  const floorY0 = cv.height - FLOOR_GFX, ceilY0 = CEIL_GFX;
  _initSand(cv.width, ceilY0, floorY0);

  // Controles
  cv.addEventListener('touchstart', e => { e.preventDefault(); holding = true; }, { passive: false });
  cv.addEventListener('touchend', () => { holding = false; }, { passive: true });
  cv.addEventListener('touchcancel', () => { holding = false; }, { passive: true });
  document.addEventListener('keydown', e => { if (e.code === 'Space' || e.key === 'ArrowUp') { e.preventDefault(); holding = true; } });
  document.addEventListener('keyup', e => { if (e.code === 'Space' || e.key === 'ArrowUp') holding = false; });

  const ctx = cv.getContext('2d');
  const loop = () => {
    rafId = requestAnimationFrame(loop);
    if (!GPS0_running()) return;
    const W = cv.width, H = cv.height;
    const floorY = H - FLOOR_GFX, ceilY = CEIL_GFX;
    const playableH = floorY - ceilY;
    frame++; bgT++;

    // Speed lerp
    currentSpeed += (_getTargetSpeed() - currentSpeed) * .008;

    // Physique
    if (holding) player.vy += THRUST;
    player.vy += GRAV;
    player.vy = Math.max(-MAX_VY, Math.min(MAX_VY, player.vy));
    player.y += player.vy;

    // Sol / plafond rebond
    if (player.y > floorY - player.r) { player.y = floorY - player.r; player.vy = -Math.abs(player.vy) * .42; }
    if (player.y < ceilY + player.r) { player.y = ceilY + player.r; player.vy = Math.abs(player.vy) * .42; }

    if (invTimer > 0) invTimer--;
    const visible = invTimer === 0 || Math.floor(bgT / 6) % 2 === 0;

    // Spawn lasers
    laserTimer--;
    if (laserTimer <= 0) {
      laserTimer = _getLaserInterval();
      const gapH = playableH * GAP_RATIO;
      const gapY = ceilY + (playableH - gapH) * (.1 + Math.random() * .8);
      lasers.push({ x: W + 20, gapY, gapH, delay: LASER_DELAY });
    }

    // Spawn cristaux bonus
    CRYSTAL_SPAWN_FRAMES.forEach(sf => {
      if (frame === sf) {
        const cy = ceilY + playableH * (.2 + Math.random() * .6);
        crystals.push({ x: W + 40, y: cy, col: false });
      }
    });

    // Update lasers
    lasers.forEach(l => {
      if (l.delay > 0) { l.delay--; return; }
      l.x -= currentSpeed;
      if (invTimer === 0) {
        const lx = l.x;
        if (lx - LASER_W/2 < PLAYER_X + player.r && lx + LASER_W/2 > PLAYER_X - player.r) {
          const inGap = (player.y - player.r) > l.gapY && (player.y + player.r) < (l.gapY + l.gapH);
          if (!inGap) {
            invTimer = 90;
            _spawnFx(PLAYER_X, player.y, '#ff5500', 12);
            loseLife();
            navigator.vibrate && navigator.vibrate([30, 10, 60]);
          }
        }
      }
    });
    lasers = lasers.filter(l => l.x > -20);

    // Update cristaux
    crystals.forEach(c => {
      if (c.col) return;
      c.x -= currentSpeed;
      if (Math.hypot(PLAYER_X - c.x, player.y - c.y) < player.r + 14) {
        c.col = true; addDust(1);
        _spawnFx(c.x, c.y, '#cc88ff', 8);
        navigator.vibrate && navigator.vibrate([8, 4, 15]);
      }
    });
    crystals = crystals.filter(c => c.x > -20 && !c.col);

    // Sand drift
    sand.forEach(s => {
      s.x -= currentSpeed * s.spd * .42;
      s.y += s.vy;
      if (s.x < -4) { s.x = W + 4; s.y = ceilY + Math.random() * playableH; }
      if (s.y < ceilY + 2 || s.y > floorY - 2) s.vy *= -1;
    });

    // BG scroll
    bgScrollA += currentSpeed * .28;
    bgScrollB += currentSpeed * .55;

    // FX
    fxParticles = fxParticles.filter(p => p.life > 0);
    fxParticles.forEach(p => { p.x += p.vx; p.y += p.vy; p.vy += .06; p.life--; });

    // ========= DESSIN =========
    // Ciel desert alien
    const sky = ctx.createLinearGradient(0, 0, 0, floorY);
    sky.addColorStop(0, '#0d0020');
    sky.addColorStop(.42, '#6b1560');
    sky.addColorStop(.85, '#c84818');
    sky.addColorStop(1, '#e06820');
    ctx.fillStyle = sky; ctx.fillRect(0, 0, W, floorY);

    // Planete BG decorative
    const pg = ctx.createRadialGradient(W*.72, H*.2, 4, W*.72, H*.2, 46);
    pg.addColorStop(0, 'rgba(185,165,80,.52)'); pg.addColorStop(1, 'rgba(120,80,20,0)');
    ctx.fillStyle = pg; ctx.beginPath(); ctx.arc(W*.72, H*.2, 46, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = 'rgba(200,180,100,.18)'; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(W*.72, H*.2, 46, 0, Math.PI*2); ctx.stroke();

    // Etoiles
    ctx.fillStyle = 'rgba(255,225,185,.52)';
    for (let i = 0; i < 20; i++) {
      const sx = ((i * 139 + bgScrollA * .04) % W + W) % W;
      const sy = (i * 47 + 18) % (floorY * .48);
      ctx.beginPath(); ctx.arc(sx, sy, .6 + (i%3)*.5, 0, Math.PI*2); ctx.fill();
    }

    // Dune couche fond lente
    ctx.fillStyle = 'rgba(108,58,12,.58)';
    ctx.beginPath(); ctx.moveTo(-2, floorY);
    for (let x = 0; x <= W + 52; x += 9) {
      const dy = Math.sin((x + bgScrollA) * .012) * 26 + Math.sin((x + bgScrollA) * .007) * 13;
      ctx.lineTo(x, floorY - 18 - dy);
    }
    ctx.lineTo(W + 2, floorY); ctx.closePath(); ctx.fill();

    // Dune couche avant rapide
    ctx.fillStyle = 'rgba(168,102,28,.72)';
    ctx.beginPath(); ctx.moveTo(-2, floorY);
    for (let x = 0; x <= W + 52; x += 7) {
      const dy = Math.sin((x + bgScrollB) * .019) * 15 + Math.cos((x + bgScrollB) * .011) * 8;
      ctx.lineTo(x, floorY - 9 - dy);
    }
    ctx.lineTo(W + 2, floorY); ctx.closePath(); ctx.fill();

    // Sol alien
    const floorGrad = ctx.createLinearGradient(0, floorY, 0, H);
    floorGrad.addColorStop(0, '#b87830'); floorGrad.addColorStop(1, '#6a4010');
    ctx.fillStyle = floorGrad; ctx.fillRect(0, floorY, W, H - floorY);

    // Plafond alien (roche sombre)
    const ceilGrad = ctx.createLinearGradient(0, 0, 0, ceilY);
    ceilGrad.addColorStop(0, '#1a0535'); ceilGrad.addColorStop(1, '#4a1065');
    ctx.fillStyle = ceilGrad; ctx.fillRect(0, 0, W, ceilY);
    // Stalactites decoratifs
    ctx.fillStyle = '#280840';
    for (let i = 0; i < 7; i++) {
      const stx = ((i * 87 + bgScrollB * .62) % (W + 50) + W + 50) % (W + 50) - 25;
      const sth = 7 + (i % 3) * 5;
      ctx.beginPath(); ctx.moveTo(stx - 6, ceilY); ctx.lineTo(stx, ceilY - sth); ctx.lineTo(stx + 6, ceilY); ctx.closePath(); ctx.fill();
    }

    // Particules sable
    sand.forEach(s => {
      ctx.globalAlpha = s.alpha;
      ctx.fillStyle = '#d4a050';
      ctx.beginPath(); ctx.arc(s.x, s.y, s.size, 0, Math.PI*2); ctx.fill();
    });
    ctx.globalAlpha = 1;

    // Warnings lasers (blink pendant delay)
    lasers.filter(l => l.delay > 0).forEach(l => {
      const blink = Math.floor(bgT / 7) % 2;
      if (!blink) return;
      ctx.fillStyle = 'rgba(255,48,48,.78)';
      ctx.fillRect(W - 18, ceilY, 18, l.gapY - ceilY);
      ctx.fillRect(W - 18, l.gapY + l.gapH, 18, floorY - (l.gapY + l.gapH));
      ctx.fillStyle = 'rgba(255,255,60,.92)';
      ctx.font = 'bold 15px system-ui'; ctx.textAlign = 'right';
      ctx.fillText('\u25ba', W - 2, l.gapY + l.gapH / 2 + 5);
    });

    // Lasers actifs
    lasers.filter(l => l.delay <= 0).forEach(l => {
      const lx = l.x;
      const pulse = .7 + .3 * Math.sin(bgT * .18);
      // Glow lateral
      const lg = ctx.createRadialGradient(lx, H / 2, 0, lx, H / 2, 30);
      lg.addColorStop(0, `rgba(255,60,0,${(.28 * pulse).toFixed(2)})`); lg.addColorStop(1, 'rgba(255,60,0,0)');
      ctx.fillStyle = lg; ctx.fillRect(lx - 30, ceilY, 60, playableH);
      // Barre haute
      ctx.fillStyle = `rgba(255,${Math.floor(85 + 35 * pulse)},0,.94)`;
      ctx.fillRect(lx - LASER_W / 2, ceilY, LASER_W, l.gapY - ceilY);
      // Barre basse
      ctx.fillRect(lx - LASER_W / 2, l.gapY + l.gapH, LASER_W, floorY - (l.gapY + l.gapH));
      // Ligne brillante centrale
      ctx.strokeStyle = `rgba(255,225,185,${(.58 + .38 * pulse).toFixed(2)})`;
      ctx.lineWidth = 1.8;
      ctx.beginPath(); ctx.moveTo(lx, ceilY); ctx.lineTo(lx, l.gapY - 2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(lx, l.gapY + l.gapH + 2); ctx.lineTo(lx, floorY); ctx.stroke();
    });

    // Cristaux bonus
    crystals.forEach(c => {
      ctx.save(); ctx.translate(c.x, c.y); ctx.rotate(bgT * .03);
      const hg = ctx.createRadialGradient(0, 0, 2, 0, 0, 16);
      hg.addColorStop(0, 'rgba(200,136,255,.55)'); hg.addColorStop(1, 'rgba(200,136,255,0)');
      ctx.fillStyle = hg; ctx.beginPath(); ctx.arc(0, 0, 16, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#cc88ff';
      ctx.beginPath(); ctx.moveTo(0,-9); ctx.lineTo(5,0); ctx.lineTo(0,9); ctx.lineTo(-5,0); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(220,180,255,.6)'; ctx.lineWidth = 1.2; ctx.stroke();
      ctx.restore();
    });

    // FX particules
    fxParticles.forEach(p => {
      ctx.globalAlpha = p.life / 24; ctx.fillStyle = p.col;
      ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, Math.PI*2); ctx.fill();
    });
    ctx.globalAlpha = 1;

    // Joueur + jetpack
    if (visible) {
      if (holding) {
        // Flamme jetpack
        const flen = 18 + Math.random() * 12;
        const fg = ctx.createLinearGradient(PLAYER_X, player.y + player.r, PLAYER_X, player.y + player.r + flen);
        fg.addColorStop(0, 'rgba(80,180,255,.9)'); fg.addColorStop(1, 'rgba(80,180,255,0)');
        ctx.fillStyle = fg;
        ctx.beginPath(); ctx.ellipse(PLAYER_X, player.y + player.r + flen/2, 7, flen/2, 0, 0, Math.PI*2); ctx.fill();
        // Particules jetpack
        if (frame % 3 === 0) fxParticles.push({
          x: PLAYER_X + (Math.random() - .5) * 8, y: player.y + player.r + 4,
          vx: (Math.random() - .5) * 1.5, vy: 1.8 + Math.random(), life: 12, col: '#55aaff'
        });
      }
      drawCosmonaut(ctx, PLAYER_X, player.y, Math.max(10, player.r * .78), 0);
    }

    _drawHUD(ctx, W, H);
  };
  loop();
}
window.gameStart = gameStart;

function _spawnFx(x, y, col, n) {
  for (let i = 0; i < n; i++) fxParticles.push({
    x: x + (Math.random() - .5) * 6, y: y + (Math.random() - .5) * 6,
    vx: (Math.random() - .5) * 3, vy: -2 + Math.random() * 1.5, life: 24, col
  });
}

function _drawHUD(ctx, W, H) {
  const phase = frame < 3600 ? 1 : frame < 7200 ? 2 : 3;
  const cols = ['#aaffcc', '#ffcc44', '#ff6644'];
  ctx.fillStyle = 'rgba(0,0,0,.52)';
  ctx.beginPath(); ctx.roundRect(W - 98, H - 130, 92, 48, 8); ctx.fill();
  ctx.fillStyle = cols[phase - 1]; ctx.font = 'bold 13px system-ui'; ctx.textAlign = 'center';
  ctx.fillText('Phase ' + phase + '/3', W - 52, H - 108);
  ctx.fillStyle = 'rgba(255,185,80,.58)'; ctx.font = '10px system-ui';
  ctx.fillText('\u00d7' + currentSpeed.toFixed(1) + ' vitesse', W - 52, H - 94);
  // Mini cristaux collectes
  const colCount = CRYSTAL_SPAWN_FRAMES.filter(sf => frame > sf).length - crystals.length;
  ctx.fillStyle = '#cc88ff'; ctx.font = '10px system-ui';
  ctx.fillText('\u2726 ' + Math.max(0, colCount) + '/5', W - 52, H - 80);
}
</script>
</body>
</html>"""

with open(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau7.html", "w", encoding="utf-8") as f:
    f.write(content)

import os
size = os.path.getsize(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau7.html")
print(f"OK: {size} bytes")

with open(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau7.html", encoding="utf-8") as f:
    txt = f.read()

checks = {
    "gameStart":        "gameStart" in txt,
    "holding/thrust":   "THRUST" in txt,
    "gravity":          "GRAV" in txt,
    "lasers":           "LASER_DELAY" in txt,
    "gap_ratio":        "GAP_RATIO" in txt,
    "warning_blink":    "blink" in txt,
    "loseLife":         "loseLife()" in txt,
    "addDust":          "addDust(1)" in txt,
    "5cristaux":        "CRYSTAL_SPAWN_FRAMES" in txt,
    "rebond_sol":       "floorY - player.r" in txt,
    "rebond_plafond":   "ceilY + player.r" in txt,
    "3paliers vitesse": "_getLaserInterval" in txt,
    "desert_alien":     "bgScrollA" in txt,
    "drawCosmonaut":    "drawCosmonaut" in txt,
    "jetpack_flames":   "flen" in txt,
}
for k, v in checks.items():
    print(f"  {'OK' if v else 'MISSING'}: {k}")
