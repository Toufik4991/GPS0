content = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover">
<title>GPS0 N5</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:#000;font-family:system-ui,sans-serif;color:#fff;touch-action:none;user-select:none}
#hud{position:relative;z-index:20;display:flex;align-items:center;gap:10px;padding:6px 52px 6px 10px;background:rgba(0,0,0,.78);backdrop-filter:blur(6px);flex-shrink:0}
#lives{font-size:1.1rem;letter-spacing:2px;min-width:54px}
#timer{flex:1;text-align:center;font-size:.95rem;font-weight:bold;color:#cc88ff}
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
window.NIVEAU = 5;
window.TUTO_TEXT = "Lune d'Ombre \u2014 D-pad ou swipe \u00b7 \uD83D\uDD26 agrandit ta lumi\u00e8re \u00b7 \u2726 = +1 poussi\u00e8re<br><small>\uD83D\uDEAA Sortie = +10 bonus \u00b7 \u00c9vite les entit\u00e9s sombres \u2014 le maze s\u2019agrandit !</small>";

const CELL = 30, CRYSTAL_MAX = 50, UPGRADE_AT = 4500;
let ROWS = 21, COLS = 21;
let maze, cosmo, exitPos, lamps, crystals, particles, shadows;
let lightR, dirAngle, targetDirAngle, dustCount, frame, bgT, mazeUpgraded, bonusFlash, rafId;

function gameReset() {
  cancelAnimationFrame(rafId);
  ROWS = 21; COLS = 21;
  particles = []; dustCount = 0; frame = 0; bgT = 0; mazeUpgraded = false; bonusFlash = 0;
  lightR = 75; dirAngle = -Math.PI / 2; targetDirAngle = -Math.PI / 2;
  _buildMaze();
  cosmo = { cx: 1, cy: 1 };
}
window.gameReset = gameReset;

function _buildMaze() {
  exitPos = { cx: COLS - 2, cy: ROWS - 2 };
  maze = _genMaze(COLS, ROWS);
  lamps = []; crystals = []; shadows = [];
  let cCount = 0;
  for (let y = 1; y < ROWS - 1; y++) for (let x = 1; x < COLS - 1; x++) {
    if (maze[y][x] !== 0) continue;
    if (x === 1 && y === 1) continue;
    if (x === COLS - 2 && y === ROWS - 2) continue;
    const r = Math.random();
    if (r < .055) lamps.push({ cx: x, cy: y, col: false });
    else if (cCount < CRYSTAL_MAX && r < .20) { crystals.push({ cx: x, cy: y, col: false }); cCount++; }
  }
  for (let i = 0; i < 2; i++) {
    let attempts = 0, sx = COLS - 3 - i * 4, sy = ROWS - 3 - i * 2;
    while (maze[sy]?.[sx] !== 0 && attempts < 30) {
      sx = COLS - 2 - Math.floor(Math.random() * 8);
      sy = ROWS - 2 - Math.floor(Math.random() * 8);
      attempts++;
    }
    shadows.push({ cx: sx, cy: sy, t: 0, interval: 52 + i * 28, flash: 0 });
  }
}

function _genMaze(C, R) {
  const m = Array.from({ length: R }, () => Array(C).fill(1));
  function carve(x, y) {
    m[y][x] = 0;
    [[0,-2],[2,0],[0,2],[-2,0]].sort(() => Math.random() - .5).forEach(([dx, dy]) => {
      const nx = x + dx, ny = y + dy;
      if (nx >= 0 && nx < C && ny >= 0 && ny < R && m[ny][nx] === 1) {
        m[y + dy/2][x + dx/2] = 0; carve(nx, ny);
      }
    });
  }
  carve(1, 1); m[R-2][C-2] = 0; return m;
}

function gameStart() {
  const cv = document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();
  _buildDpad(cv);

  let swX = null, swY = null;
  cv.addEventListener('touchstart', e => { swX = e.touches[0].clientX; swY = e.touches[0].clientY; }, { passive: true });
  cv.addEventListener('touchend', e => {
    if (swX === null) return;
    const dx = e.changedTouches[0].clientX - swX, dy = e.changedTouches[0].clientY - swY;
    if (Math.max(Math.abs(dx), Math.abs(dy)) < 28) { swX = null; swY = null; return; }
    if (Math.abs(dx) > Math.abs(dy)) _move(dx > 0 ? 1 : -1, 0); else _move(0, dy > 0 ? 1 : -1);
    swX = null; swY = null;
  }, { passive: true });
  document.addEventListener('keydown', e => {
    const m = { ArrowLeft:[-1,0], ArrowRight:[1,0], ArrowUp:[0,-1], ArrowDown:[0,1] };
    if (m[e.key]) _move(...m[e.key]);
  });

  const ctx = cv.getContext('2d');
  const loop = () => {
    rafId = requestAnimationFrame(loop);
    if (!GPS0_running()) return;
    const W = cv.width, H = cv.height;
    frame++; bgT++;

    if (!mazeUpgraded && frame >= UPGRADE_AT) {
      mazeUpgraded = true; ROWS = 33; COLS = 33; _buildMaze(); cosmo.cx = 1; cosmo.cy = 1;
    }

    shadows.forEach(s => {
      s.t++; if (s.flash > 0) s.flash--;
      if (s.t >= s.interval) {
        s.t = 0;
        const dirs = [[-1,0],[1,0],[0,-1],[0,1]].sort(() => Math.random() - .5);
        for (const [dx, dy] of dirs) {
          const nx = s.cx + dx, ny = s.cy + dy;
          if (nx >= 0 && nx < COLS && ny >= 0 && ny < ROWS && maze[ny]?.[nx] === 0) { s.cx = nx; s.cy = ny; break; }
        }
      }
      if (s.cx === cosmo.cx && s.cy === cosmo.cy && s.flash === 0) {
        s.flash = 70; s.cx = COLS - 2; s.cy = ROWS - 3; loseLife();
      }
    });

    if (bonusFlash > 0) bonusFlash--;
    dirAngle = _lerpAngle(dirAngle, targetDirAngle, .13);

    const camPxX = cosmo.cx * CELL + CELL / 2, camPxY = cosmo.cy * CELL + CELL / 2;
    const offX = W / 2 - camPxX, offY = H / 2 - camPxY;

    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);

    ctx.save();
    ctx.beginPath();
    ctx.arc(W / 2, H / 2, 42, 0, Math.PI * 2);
    const HALF = Math.PI * .55;
    ctx.moveTo(W / 2, H / 2);
    ctx.arc(W / 2, H / 2, lightR, dirAngle - HALF, dirAngle + HALF);
    ctx.closePath(); ctx.clip();

    for (let y = 0; y < ROWS; y++) for (let x = 0; x < COLS; x++) {
      const px = x * CELL + offX, py = y * CELL + offY;
      if (px < -CELL || px > W + CELL || py < -CELL || py > H + CELL) continue;
      if (maze[y][x] === 1) {
        ctx.fillStyle = 'rgba(8,4,22,.98)'; ctx.fillRect(px, py, CELL, CELL);
        _drawRune(ctx, px, py, x, y);
      } else {
        ctx.fillStyle = 'rgba(3,1,10,.92)'; ctx.fillRect(px, py, CELL, CELL);
      }
    }

    const ex = exitPos.cx * CELL + offX, ey = exitPos.cy * CELL + offY;
    const eg = ctx.createRadialGradient(ex + CELL/2, ey + CELL/2, 2, ex + CELL/2, ey + CELL/2, CELL * .85);
    eg.addColorStop(0, 'rgba(255,215,0,.95)'); eg.addColorStop(1, 'rgba(255,215,0,0)');
    ctx.fillStyle = eg; ctx.fillRect(ex, ey, CELL, CELL);
    ctx.font = '18px system-ui'; ctx.textAlign = 'center'; ctx.fillText('\uD83D\uDEAA', ex + CELL/2, ey + CELL/2 + 6);

    lamps.forEach(l => {
      if (l.col) return;
      const px = l.cx * CELL + offX + CELL/2, py = l.cy * CELL + offY + CELL/2;
      ctx.font = '18px system-ui'; ctx.textAlign = 'center'; ctx.fillText('\uD83D\uDD26', px, py + 6);
    });

    crystals.forEach(c => {
      if (c.col) return;
      const px = c.cx * CELL + offX + CELL/2, py = c.cy * CELL + offY + CELL/2;
      ctx.save(); ctx.translate(px, py); ctx.rotate(bgT * .025);
      const hg = ctx.createRadialGradient(0, 0, 2, 0, 0, 15);
      hg.addColorStop(0, 'rgba(200,136,255,.45)'); hg.addColorStop(1, 'rgba(200,136,255,0)');
      ctx.fillStyle = hg; ctx.beginPath(); ctx.arc(0, 0, 15, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#cc88ff';
      ctx.beginPath(); ctx.moveTo(0, -9); ctx.lineTo(5, 0); ctx.lineTo(0, 9); ctx.lineTo(-5, 0); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(220,180,255,.55)'; ctx.lineWidth = 1.2; ctx.stroke();
      ctx.restore();
    });

    shadows.forEach(s => {
      const px = s.cx * CELL + offX + CELL/2, py = s.cy * CELL + offY + CELL/2;
      const pulse = .5 + .5 * Math.sin(bgT * .09 + s.cx * .4);
      ctx.globalAlpha = s.flash > 0 ? .92 : .55 + .35 * pulse;
      const r = 13 + pulse * 4;
      const sg = ctx.createRadialGradient(px, py, 2, px, py, r);
      sg.addColorStop(0, s.flash > 0 ? 'rgba(255,60,60,.95)' : 'rgba(110,0,190,.92)');
      sg.addColorStop(1, s.flash > 0 ? 'rgba(255,0,0,0)' : 'rgba(50,0,90,0)');
      ctx.fillStyle = sg; ctx.beginPath(); ctx.arc(px, py, r, 0, Math.PI * 2); ctx.fill();
      ctx.globalAlpha = .88;
      ctx.fillStyle = s.flash > 0 ? '#ff8888' : '#ff6644';
      ctx.beginPath(); ctx.arc(px - 3.5, py - 2, 2.5, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(px + 3.5, py - 2, 2.5, 0, Math.PI * 2); ctx.fill();
      ctx.globalAlpha = 1;
    });

    particles = particles.filter(p => p.life > 0);
    particles.forEach(p => {
      p.wx += p.vx; p.wy += p.vy; p.vy += .06; p.life--;
      ctx.globalAlpha = p.life / 24; ctx.fillStyle = p.col;
      ctx.beginPath(); ctx.arc(p.wx + offX, p.wy + offY, 3, 0, Math.PI * 2); ctx.fill();
    });
    ctx.globalAlpha = 1;
    ctx.restore();

    const vg = ctx.createRadialGradient(W/2, H/2, lightR * .68, W/2, H/2, lightR * 1.22 + 24);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,1)');
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);

    drawCosmonaut(ctx, W / 2, H / 2, 14, 0);

    if (bonusFlash > 0) {
      ctx.fillStyle = 'rgba(255,215,0,' + (bonusFlash / 90 * .35).toFixed(2) + ')';
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = '#FFD700'; ctx.font = 'bold 20px system-ui'; ctx.textAlign = 'center';
      ctx.globalAlpha = Math.min(1, bonusFlash / 45);
      ctx.fillText('+10 \uD83D\uDCA8 Sortie !', W/2, H/2 - 60);
      ctx.globalAlpha = 1;
    }

    _drawHUD(ctx, W, H);
  };
  loop();
}
window.gameStart = gameStart;

function _move(dx, dy) {
  if (!GPS0_running()) return;
  if (dx !== 0 || dy !== 0) targetDirAngle = Math.atan2(dy, dx);
  const nx = cosmo.cx + dx, ny = cosmo.cy + dy;
  if (nx < 0 || nx >= COLS || ny < 0 || ny >= ROWS || maze[ny]?.[nx] === 1) return;
  cosmo.cx = nx; cosmo.cy = ny;
  const li = lamps.findIndex(l => !l.col && l.cx === cosmo.cx && l.cy === cosmo.cy);
  if (li >= 0) { lamps[li].col = true; lightR = Math.min(lightR + 22, 145); _spawnFx(cosmo.cx, cosmo.cy, '#ffffaa', 8); }
  const ci = crystals.findIndex(c => !c.col && c.cx === cosmo.cx && c.cy === cosmo.cy);
  if (ci >= 0) {
    crystals[ci].col = true; dustCount++; addDust(1);
    _spawnFx(cosmo.cx, cosmo.cy, '#cc88ff', 8);
    navigator.vibrate && navigator.vibrate([10, 5, 20]);
  }
  if (cosmo.cx === exitPos.cx && cosmo.cy === exitPos.cy) {
    addDust(10); bonusFlash = 90;
    navigator.vibrate && navigator.vibrate([20, 10, 40, 10, 60]);
    if (!mazeUpgraded) { ROWS = 33; COLS = 33; mazeUpgraded = true; }
    _buildMaze(); cosmo.cx = 1; cosmo.cy = 1; lightR = Math.max(75, lightR - 12);
  }
  shadows.forEach(s => {
    if (s.cx === cosmo.cx && s.cy === cosmo.cy && s.flash === 0) {
      s.flash = 70; s.cx = COLS - 2; s.cy = ROWS - 3; loseLife();
    }
  });
}

function _spawnFx(cx, cy, col, n) {
  const wx = cx * CELL + CELL/2, wy = cy * CELL + CELL/2;
  for (let i = 0; i < n; i++) particles.push({
    wx: wx + (Math.random() - .5) * 4, wy: wy + (Math.random() - .5) * 4,
    vx: (Math.random() - .5) * 2.5, vy: -1.8 + Math.random(), life: 24, col
  });
}

function _drawRune(ctx, px, py, x, y) {
  const h = (x * 7 + y * 13) % 8;
  if (h >= 2) return;
  ctx.strokeStyle = 'rgba(110,55,185,.26)'; ctx.lineWidth = .8;
  const cx = px + CELL/2, cy = py + CELL/2, s = 5;
  ctx.beginPath();
  if (h === 0) {
    ctx.moveTo(cx - s, cy); ctx.lineTo(cx + s, cy);
    ctx.moveTo(cx, cy - s); ctx.lineTo(cx, cy + s);
    ctx.moveTo(cx - s * .6, cy - s * .4); ctx.lineTo(cx + s * .6, cy - s * .4);
  } else {
    ctx.moveTo(cx - s, cy - s * .6); ctx.lineTo(cx + s, cy + s * .6);
    ctx.moveTo(cx - s, cy + s * .6); ctx.lineTo(cx + s, cy - s * .6);
    ctx.moveTo(cx - s * .7, cy); ctx.lineTo(cx + s * .7, cy);
  }
  ctx.stroke();
}

function _lerpAngle(cur, tgt, t) {
  let d = tgt - cur;
  while (d > Math.PI) d -= 2 * Math.PI;
  while (d < -Math.PI) d += 2 * Math.PI;
  return cur + d * t;
}

function _drawHUD(ctx, W, H) {
  ctx.fillStyle = 'rgba(0,0,0,.58)';
  ctx.beginPath(); ctx.roundRect(W - 90, H - 128, 84, 40, 8); ctx.fill();
  ctx.fillStyle = '#cc88ff'; ctx.font = 'bold 13px system-ui'; ctx.textAlign = 'center';
  ctx.fillText('\u2726 ' + dustCount + '/' + CRYSTAL_MAX, W - 48, H - 103);
  ctx.fillStyle = 'rgba(200,136,255,.55)'; ctx.font = '10px system-ui';
  ctx.fillText('cristaux', W - 48, H - 91);
  if (!mazeUpgraded) {
    ctx.fillStyle = 'rgba(180,120,255,.48)'; ctx.font = '9px system-ui'; ctx.textAlign = 'left';
    ctx.fillText('21\u00d721 \u2192 33\u00d733 bient\u00f4t', 6, H - 116);
  }
}

function _buildDpad(cv) {
  const gc = document.getElementById('game-container');
  const dpad = document.createElement('div');
  dpad.style.cssText = 'position:absolute;bottom:10px;left:50%;transform:translateX(-50%);z-index:50;display:grid;grid-template-columns:repeat(3,64px);grid-template-rows:repeat(3,64px);gap:3px';
  const acts = [[null, () => _move(0, -1), null], [() => _move(-1, 0), null, () => _move(1, 0)], [null, () => _move(0, 1), null]];
  const lbls = [['', '\u2191', ''], ['\u2190', '', '\u2192'], ['', '\u2193', '']];
  lbls.forEach((row, ri) => row.forEach((lbl, ci) => {
    const btn = document.createElement('div');
    if (!lbl) { btn.style.cssText = 'width:64px;height:64px'; dpad.appendChild(btn); return; }
    btn.textContent = lbl;
    btn.style.cssText = 'width:64px;height:64px;display:flex;align-items:center;justify-content:center;font-size:1.4rem;background:rgba(180,100,255,.16);border-radius:12px;border:1px solid rgba(180,100,255,.28);cursor:pointer;touch-action:none';
    const fn = acts[ri][ci];
    let hi = null;
    btn.addEventListener('pointerdown', e => { e.preventDefault(); fn && fn(); hi = setInterval(() => { if (GPS0_running() && fn) fn(); }, 165); });
    btn.addEventListener('pointerup', () => clearInterval(hi));
    btn.addEventListener('pointerleave', () => clearInterval(hi));
    dpad.appendChild(btn);
  }));
  gc.appendChild(dpad);
}
</script>
</body>
</html>"""

with open(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau5.html", "w", encoding="utf-8") as f:
    f.write(content)

import os
size = os.path.getsize(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau5.html")
print(f"OK: {size} bytes")
with open(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau5.html", encoding="utf-8") as f:
    txt = f.read()
checks = {
    "gameStart": "gameStart" in txt,
    "_genMaze": "_genMaze" in txt,
    "shadows": "shadows" in txt,
    "cone/clip": "ctx.clip()" in txt,
    "swipe": "touchend" in txt,
    "CRYSTAL_MAX=50": "CRYSTAL_MAX = 50" in txt,
    "UPGRADE_AT": "UPGRADE_AT" in txt,
    "_drawRune": "_drawRune" in txt,
    "addDust(10)": "addDust(10)" in txt,
    "loseLife": "loseLife" in txt,
}
for k, v in checks.items():
    print(f"  {'OK' if v else 'MISSING'}: {k}")
