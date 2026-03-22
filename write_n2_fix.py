content = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover">
<title>GPS0 N2</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:#0d0608;font-family:system-ui,sans-serif;color:#fff;touch-action:none;user-select:none}
#hud{position:relative;z-index:20;display:flex;align-items:center;gap:10px;padding:6px 52px 6px 10px;background:rgba(0,0,0,.65);backdrop-filter:blur(6px);flex-shrink:0}
#lives{font-size:1.1rem;letter-spacing:2px;min-width:54px}
#timer{flex:1;text-align:center;font-size:.95rem;font-weight:bold;color:#FF7030}
#score-hud{font-size:.9rem;color:#FFD700;font-weight:bold;min-width:52px;text-align:right}
#game-container{position:relative;z-index:1;flex:1;overflow:hidden;display:flex;flex-direction:column}
canvas{display:block;width:100%;height:100%}
body{display:flex;flex-direction:column;height:100dvh}
</style>
</head>
<body>
<div id="hud">
  <span id="lives">\\u2764\\u2764\\u2764</span>
  <span id="timer">2:30</span>
  <span id="score-hud">0 \\u2728</span>
</div>
<div id="game-container">
  <canvas id="cv"></canvas>
</div>
<script src="shared.js"></script>
<script>
window.NIVEAU = 2;
window.TUTO_TEXT = "Lune Phobos \\u2014 Tape pour sauter \\xb7 \\xc9vite les colonnes \\xb7 3 vies<br><small>Les bords ne te tuent pas \\xb7 Cristaux \\u2726 = +1 poussi\\xe8re</small>";

// ── CONSTANTES ──────────────────────────────────────────────────────────────
const GRAV = 0.45, JUMP = -9.5, WALL_W = 44;
const SPEED_START = 2.4, SPEED_MAX = 5.8;
const CRYSTAL_MAX = 5;

// ── ÉTAT ──────────────────────────────────────────────────────────────────
let bird, walls, ashParts, parts, crystals;
let speed, frame, invincible, rafId, bgT, crystalCount;

function gameReset() {
  cancelAnimationFrame(rafId);
  bird = { x: 0, y: 0, vy: 0, r: 22 };
  walls = []; ashParts = []; parts = []; crystals = [];
  speed = SPEED_START; frame = 0; invincible = 0; bgT = 0; crystalCount = 0;
}
window.gameReset = gameReset;

function gameStart() {
  const cv = document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  const W = cv.width, H = cv.height;
  bird.x = W * .22; bird.y = H * .45;

  for (let i = 0; i < 32; i++) ashParts.push({
    x: Math.random() * W, y: Math.random() * H,
    vx: -0.1 - Math.random() * .22, vy: -0.04 + Math.random() * .14,
    r: 0.8 + Math.random() * 2, a: 0.08 + Math.random() * .28
  });

  _spawnWall(W, H);
  cv.addEventListener('pointerdown', _tap);
  const ctx = cv.getContext('2d');

  const loop = () => {
    rafId = requestAnimationFrame(loop);
    if (!GPS0_running()) return;
    const W = cv.width, H = cv.height;
    frame++; bgT++;

    // Vitesse progressive : 2.4 → 5.8 sur 150s à 60fps
    speed = Math.min(SPEED_MAX, SPEED_START + (frame / (150 * 60)) * (SPEED_MAX - SPEED_START));

    bird.vy += GRAV; bird.y += bird.vy;
    if (bird.y < bird.r + 2) { bird.y = bird.r + 2; bird.vy = Math.abs(bird.vy) * .25; }
    if (bird.y > H - bird.r - 2) { bird.y = H - bird.r - 2; bird.vy = -Math.abs(bird.vy) * .25; }
    if (invincible > 0) invincible--;

    const spacing = Math.max(200, 370 - frame * .06);
    if (!walls.length || walls[walls.length - 1].x < W - spacing) _spawnWall(W, H);
    walls = walls.filter(w => w.x + WALL_W > -10);

    walls.forEach(w => {
      w.x -= speed;
      if (invincible > 0) return;
      if (bird.x + bird.r > w.x && bird.x - bird.r < w.x + WALL_W) {
        const inGap = bird.y - bird.r > w.gapTop && bird.y + bird.r < w.gapTop + w.gapH;
        if (!inGap) {
          invincible = 90; bird.vy = JUMP * .5;
          for (let j = 0; j < 12; j++) parts.push({ x: bird.x, y: bird.y, vx: (Math.random() - .5) * 5, vy: -2 - Math.random() * 3, life: 28, col: '#ff7040' });
          loseLife();
        }
      }
    });

    crystals = crystals.filter(c => {
      c.x -= speed * .72; c.rot += .045;
      if (Math.hypot(bird.x - c.x, bird.y - c.y) < bird.r + 13) {
        crystalCount++;
        addDust(1);
        for (let j = 0; j < 10; j++) parts.push({ x: c.x, y: c.y, vx: (Math.random() - .5) * 7, vy: -3 - Math.random() * 3, life: 24, col: '#88EEFF' });
        navigator.vibrate && navigator.vibrate([15, 8, 30]);
        return false;
      }
      return c.x > -30;
    });

    ashParts.forEach(a => {
      a.x += a.vx; a.y += a.vy;
      if (a.x < -4) a.x = W + 4;
      if (a.y < -4) a.y = H + 4;
      if (a.y > H + 4) a.y = -4;
    });

    parts = parts.filter(p => p.life > 0);
    parts.forEach(p => { p.x += p.vx; p.y += p.vy; p.vy += .09; p.life--; });

    ctx.clearRect(0, 0, W, H);
    _drawBg(ctx, W, H);
    _drawWalls(ctx, H);
    _drawCrystals(ctx);
    parts.forEach(p => {
      ctx.globalAlpha = p.life / 28; ctx.fillStyle = p.col;
      ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, Math.PI * 2); ctx.fill();
    });
    ctx.globalAlpha = 1;
    if (invincible > 0 && Math.floor(invincible / 6) % 2 === 0) {
      ctx.fillStyle = 'rgba(255,100,0,.22)';
      ctx.beginPath(); ctx.arc(bird.x, bird.y, bird.r + 14, 0, Math.PI * 2); ctx.fill();
    }
    _drawBird(ctx);
    _drawHUD(ctx, W, H);
  };
  loop();
}
window.gameStart = gameStart;

function _tap() {
  if (!GPS0_running()) return;
  bird.vy = JUMP;
  navigator.vibrate && navigator.vibrate(18);
}

function _spawnWall(W, H) {
  // Gap se rétrécit légèrement avec le temps
  const gapH = Math.max(130, 225 - frame * .038);
  const gapTop = H * .07 + Math.random() * (H * .8 - gapH);
  const teeth = Array.from({ length: 6 }, () => (Math.random() - .5) * 18);
  const mkCrk = () => Array.from({ length: 4 }, () => ({
    x1: 4 + Math.random() * WALL_W * .7, x2: 4 + Math.random() * WALL_W * .7,
    y1: .05 + Math.random() * .28, y2: .4 + Math.random() * .35
  }));
  const mkDrips = () => Array.from({ length: 3 }, () => ({
    x: 5 + Math.random() * (WALL_W - 10),
    phase: Math.random() * Math.PI * 2
  }));
  walls.push({ x: W + 50, gapTop, gapH, teeth, crksTop: mkCrk(), crksBot: mkCrk(), dripsTop: mkDrips(), dripsBot: mkDrips() });
  if (crystalCount < CRYSTAL_MAX && Math.random() < .38) {
    crystals.push({ x: W + 85, y: gapTop + gapH / 2, rot: 0 });
  }
}

// ── DESSIN ─────────────────────────────────────────────────────────────────

function _drawBg(ctx, W, H) {
  const sky = ctx.createLinearGradient(0, 0, 0, H);
  sky.addColorStop(0, '#0d0608');
  sky.addColorStop(.45, '#1c0a08');
  sky.addColorStop(1, '#2e1005');
  ctx.fillStyle = sky; ctx.fillRect(0, 0, W, H);

  for (let i = 0; i < 5; i++) {
    const cx = ((i * W * .22 - bgT * .3) % (W * 1.3) + W * 1.3) % (W * 1.3) - W * .05;
    const cy = H * (.05 + i * .06);
    ctx.fillStyle = 'rgba(90,60,50,' + (.06 + i * .018).toFixed(3) + ')';
    ctx.beginPath(); ctx.ellipse(cx, cy, 55 + i * 20, 14 + i * 4, 0, 0, Math.PI * 2); ctx.fill();
  }

  _drawVolcans(ctx, W, H);

  ashParts.forEach(a => {
    ctx.fillStyle = 'rgba(130,95,75,' + a.a.toFixed(2) + ')';
    ctx.beginPath(); ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2); ctx.fill();
  });

  _drawLavaSol(ctx, W, H);
}

function _drawVolcans(ctx, W, H) {
  [
    { cx: W * .12, h: H * .38, r: W * .09 },
    { cx: W * .56, h: H * .28, r: W * .08 },
    { cx: W * .88, h: H * .42, r: W * .10 },
  ].forEach(v => {
    const vg = ctx.createLinearGradient(v.cx - v.r, H, v.cx, H - v.h);
    vg.addColorStop(0, '#1a0d0a'); vg.addColorStop(1, '#2e1610');
    ctx.fillStyle = vg;
    ctx.beginPath();
    ctx.moveTo(v.cx - v.r, H);
    ctx.lineTo(v.cx - v.r * .12, H - v.h);
    ctx.lineTo(v.cx + v.r * .12, H - v.h);
    ctx.lineTo(v.cx + v.r, H);
    ctx.closePath(); ctx.fill();
    const intensity = .18 + .13 * Math.sin(bgT * .03 + v.cx * .01);
    const cg = ctx.createRadialGradient(v.cx, H - v.h, 2, v.cx, H - v.h, v.r * .42);
    cg.addColorStop(0, 'rgba(255,90,10,' + intensity.toFixed(2) + ')');
    cg.addColorStop(1, 'rgba(255,40,0,0)');
    ctx.fillStyle = cg;
    ctx.beginPath(); ctx.arc(v.cx, H - v.h, v.r * .42, 0, Math.PI * 2); ctx.fill();
  });
}

function _drawLavaSol(ctx, W, H) {
  const yB = H - H * .082;
  const lava = ctx.createLinearGradient(0, yB, 0, H);
  lava.addColorStop(0, 'rgba(255,85,5,.94)');
  lava.addColorStop(.35, 'rgba(220,52,0,.97)');
  lava.addColorStop(1, 'rgba(140,22,0,1)');
  ctx.fillStyle = lava;
  ctx.beginPath(); ctx.moveTo(0, H);
  for (let x = 0; x <= W; x += 16) {
    ctx.lineTo(x, yB + Math.sin(x * .02 + bgT * .04) * 7 + Math.sin(x * .038 + bgT * .025) * 4);
  }
  ctx.lineTo(W, H); ctx.closePath(); ctx.fill();
  const gl = ctx.createLinearGradient(0, yB - 36, 0, yB);
  gl.addColorStop(0, 'rgba(255,80,0,0)');
  gl.addColorStop(1, 'rgba(255,80,0,.22)');
  ctx.fillStyle = gl; ctx.fillRect(0, yB - 36, W, 36);
}

function _drawWalls(ctx, H) {
  walls.forEach(w => {
    const { x, gapTop, gapH } = w;
    _drawBlock(ctx, x, 0, gapTop, w, false);
    _drawBlock(ctx, x, gapTop + gapH, H - (gapTop + gapH), w, true);
    const gl = ctx.createRadialGradient(x + WALL_W / 2, gapTop + gapH / 2, 4, x + WALL_W / 2, gapTop + gapH / 2, gapH * .6);
    gl.addColorStop(0, 'rgba(255,120,30,.13)');
    gl.addColorStop(1, 'rgba(255,60,0,0)');
    ctx.fillStyle = gl;
    ctx.beginPath(); ctx.ellipse(x + WALL_W / 2, gapTop + gapH / 2, WALL_W + 22, gapH * .52, 0, 0, Math.PI * 2); ctx.fill();
  });
}

function _drawBlock(ctx, x, y, h, wall, isBot) {
  if (h < 2) return;
  const cracks = isBot ? wall.crksBot : wall.crksTop;
  const drips = isBot ? wall.dripsBot : wall.dripsTop;

  const g = ctx.createLinearGradient(x, 0, x + WALL_W, 0);
  g.addColorStop(0, '#1a1525'); g.addColorStop(.38, '#2e2840');
  g.addColorStop(.68, '#3d3655'); g.addColorStop(1, '#1e182c');
  ctx.fillStyle = g; ctx.fillRect(x, y, WALL_W, h);

  ctx.fillStyle = 'rgba(255,70,10,.38)';
  for (let i = 0; i < Math.ceil(WALL_W / 9); i++) {
    const jag = Math.abs(wall.teeth[i % wall.teeth.length] || 8);
    ctx.fillRect(x + i * 9, isBot ? y : y + h - jag, 8, jag + 2);
  }

  ctx.lineWidth = 1.2;
  cracks.forEach(c => {
    ctx.strokeStyle = 'rgba(255,100,30,.24)';
    ctx.beginPath(); ctx.moveTo(x + c.x1, y + h * c.y1); ctx.lineTo(x + c.x2, y + h * c.y2); ctx.stroke();
  });

  const faceY = isBot ? y : y + h;
  const dir = isBot ? -1 : 1;
  drips.forEach(d => {
    const prog = Math.sin(bgT * .025 + d.phase) * .5 + .5;
    const dripLen = 8 + prog * 20;
    const endY = faceY + dir * dripLen;
    ctx.strokeStyle = 'rgba(255,' + Math.round(70 + prog * 50) + ',0,' + (.72 - prog * .22).toFixed(2) + ')';
    ctx.lineWidth = 1.6;
    ctx.beginPath(); ctx.moveTo(x + d.x, faceY); ctx.lineTo(x + d.x, endY); ctx.stroke();
    const dropR = 2.2 + prog * 1.8;
    const dropG = ctx.createRadialGradient(x + d.x, endY, 0, x + d.x, endY, dropR * 2);
    dropG.addColorStop(0, 'rgba(255,220,60,.95)');
    dropG.addColorStop(.4, 'rgba(255,80,0,.8)');
    dropG.addColorStop(1, 'rgba(255,40,0,0)');
    ctx.fillStyle = dropG;
    ctx.beginPath(); ctx.arc(x + d.x, endY, dropR, 0, Math.PI * 2); ctx.fill();
  });

  ctx.fillStyle = 'rgba(255,255,255,.03)'; ctx.fillRect(x, y, 3, h);
  const eg = ctx.createLinearGradient(x, isBot ? y : y + h - 16, x, isBot ? y + 16 : y + h);
  eg.addColorStop(0, 'rgba(255,80,15,.42)');
  eg.addColorStop(1, 'rgba(255,80,15,0)');
  ctx.fillStyle = eg; ctx.fillRect(x, isBot ? y : y + h - 16, WALL_W, 16);
}

function _drawCrystals(ctx) {
  crystals.forEach(c => {
    ctx.save(); ctx.translate(c.x, c.y); ctx.rotate(c.rot);
    const hg = ctx.createRadialGradient(0, 0, 3, 0, 0, 22);
    hg.addColorStop(0, 'rgba(136,238,255,.42)');
    hg.addColorStop(1, 'rgba(136,238,255,0)');
    ctx.fillStyle = hg; ctx.beginPath(); ctx.arc(0, 0, 22, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#88EEFF';
    ctx.beginPath(); ctx.moveTo(0, -13); ctx.lineTo(7, 0); ctx.lineTo(0, 13); ctx.lineTo(-7, 0); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = 'rgba(200,255,255,.7)'; ctx.lineWidth = 1.2; ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,.5)';
    ctx.beginPath(); ctx.moveTo(0, -11); ctx.lineTo(3, -4); ctx.lineTo(0, -2); ctx.closePath(); ctx.fill();
    ctx.restore();
  });
}

function _drawBird(ctx) {
  const tilt = Math.max(-1.1, Math.min(1.1, bird.vy * .08));
  const rising = bird.vy < -2;
  const fH = rising ? 28 : 16;
  const fX = bird.x, fY = bird.y + bird.r * .75;
  const fg = ctx.createRadialGradient(fX, fY, 2, fX, fY + fH * .5, fH);
  fg.addColorStop(0, 'rgba(255,210,60,.97)');
  fg.addColorStop(.4, 'rgba(255,80,0,.78)');
  fg.addColorStop(1, 'rgba(255,30,0,0)');
  ctx.fillStyle = fg;
  ctx.beginPath(); ctx.ellipse(fX, fY + fH * .35, bird.r * .38, fH * .52, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = 'rgba(180,220,255,' + (rising ? .68 : .38) + ')';
  ctx.beginPath(); ctx.ellipse(fX, fY + 5, bird.r * .16, rising ? 10 : 6, 0, 0, Math.PI * 2); ctx.fill();
  drawCosmonaut(ctx, bird.x, bird.y, bird.r, tilt, 'fly');
}

function _drawHUD(ctx, W, H) {
  ctx.fillStyle = 'rgba(0,0,0,.52)';
  ctx.beginPath(); ctx.roundRect(W - 90, H - 46, 84, 40, 8); ctx.fill();
  ctx.fillStyle = '#88EEFF'; ctx.font = 'bold 13px system-ui'; ctx.textAlign = 'center';
  ctx.fillText('\\u2726 ' + crystalCount + '/' + CRYSTAL_MAX, W - 48, H - 21);
  ctx.fillStyle = 'rgba(136,238,255,.55)'; ctx.font = '10px system-ui';
  ctx.fillText('cristaux', W - 48, H - 9);
  ctx.fillStyle = 'rgba(255,120,30,.75)'; ctx.font = '11px system-ui'; ctx.textAlign = 'left';
  ctx.fillText('\\u26a1 x' + speed.toFixed(1), 8, H - 8);
}
</script>
</body>
</html>"""

with open(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau2.html", "w", encoding="utf-8") as f:
    f.write(content)

import os
print("OK:", os.path.getsize(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau2.html"), "bytes")

# Verify
with open(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau2.html", encoding="utf-8") as f:
    t = f.read()

checks = {
    "UTF8 correct lives": "\u2764\u2764\u2764" in t,
    "UTF8 score":         "\u2728" in t,
    "TUTO_TEXT":          "Lune Phobos" in t,
    "crystal HUD":        "\u2726" in t and "crystalCount" in t,
    "speed HUD":          "\u26a1" in t and "speed.toFixed" in t,
    "drawCosmonaut":      "drawCosmonaut" in t,
    "loseLife":           "loseLife()" in t,
    "GPS0_running":       "GPS0_running()" in t,
    "no mojibake lives":  "â¤" not in t,
    "no mojibake tick":   "âœ¨" not in t,
}
for k, v in checks.items():
    print(f"  {'OK' if v else 'FAIL'}: {k}")
