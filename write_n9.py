content = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover">
<title>GPS0 N9</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:#000;font-family:system-ui,sans-serif;color:#fff;touch-action:none;user-select:none}
#hud{position:relative;z-index:20;display:flex;align-items:center;gap:10px;padding:6px 52px 6px 10px;background:rgba(0,0,0,.78);backdrop-filter:blur(6px);flex-shrink:0}
#lives{font-size:1.1rem;letter-spacing:2px;min-width:54px}
#timer{flex:1;text-align:center;font-size:.95rem;font-weight:bold;color:#ffdd88}
#score-hud{font-size:.9rem;color:#FFD700;font-weight:bold;min-width:52px;text-align:right}
#game-container{position:relative;z-index:1;flex:1;overflow:hidden;display:flex;flex-direction:column}
canvas{display:block;width:100%;height:100%}
body{display:flex;flex-direction:column;height:100dvh}
</style>
</head>
<body>
<div id="hud">
  <span id="lives">&#10084;&#10084;&#10084;</span>
  <span id="timer">2:15</span>
  <span id="score-hud">0 &#10024;</span>
</div>
<div id="game-container">
  <canvas id="cv"></canvas>
</div>
<script src="shared.js"></script>
<script>
window.NIVEAU = 9;
window.GPS0_TIMER_SEC = 135;
window.TUTO_TEXT = "\u00c9clipse Boss \u2014 Esquive G/D \u00b7 Tape le boss quand il devient orange \u00b7 3 phases \u00d7 45s";

// Phases: 0=P1(projectiles), 1=P2(laser), 2=P3(rage), 3=victoire
const PHASE_DUR = 45 * 60; // 45s @ 60fps
const PLAYER_Y_PCT = 0.80;
const INV_FRAMES = 120; // 2s
const DODGE_RANGE = 0.38; // fraction of W

let phase, phaseTick, boss, player, projectiles, bombs, laserAngle, laserActive, laserTimer;
let invTimer, hitFlash, bgT, frame, vulnerable, vulnTimer, vulnWindow;
let particles, victoryAnim, victoryTick, rafId;
let swX = null;

// ---- BOSS STATE ----
function _resetBoss() {
  boss = {
    x: 0.5, // fraction of W
    t: 0,
    hue: 28, // corona color shifts per phase
    coronaAngles: Array.from({length:12}, (_,i) => i * Math.PI * 2 / 12),
    wobble: 0
  };
}

function gameReset() {
  cancelAnimationFrame(rafId);
  phase = 0; phaseTick = 0;
  _resetBoss();
  player = { x: 0.5, inv: 0, drawX: 0.5 };
  projectiles = []; bombs = []; particles = [];
  laserAngle = -Math.PI/2; laserActive = false; laserTimer = 0;
  invTimer = 0; hitFlash = 0; bgT = 0; frame = 0;
  vulnerable = false; vulnTimer = 0; vulnWindow = 0;
  victoryAnim = false; victoryTick = 0;
}
window.gameReset = gameReset;

function gameStart() {
  const cv = document.getElementById('cv');
  GPS0_resizeCanvas(cv);
  gameReset();

  // Swipe laterale
  cv.addEventListener('touchstart', e => {
    swX = e.touches[0].clientX;
    // Tap -> attaque si vulnerable
    if (vulnerable) _hitBoss(cv);
  }, { passive: true });
  cv.addEventListener('touchend', e => {
    if (swX === null) return;
    const dx = e.changedTouches[0].clientX - swX;
    if (Math.abs(dx) > 22) {
      player.x = Math.max(0.1, Math.min(0.9, player.x + (dx > 0 ? DODGE_RANGE : -DODGE_RANGE)));
    } else if (vulnerable) {
      _hitBoss(cv);
    }
    swX = null;
  }, { passive: true });

  // Clavier
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft')  player.x = Math.max(0.1, player.x - DODGE_RANGE);
    if (e.key === 'ArrowRight') player.x = Math.min(0.9, player.x + DODGE_RANGE);
    if (e.key === ' ' && vulnerable) _hitBoss(cv);
  });

  const ctx = cv.getContext('2d');
  const loop = () => {
    rafId = requestAnimationFrame(loop);
    if (!GPS0_running()) return;
    const W = cv.width, H = cv.height;
    const bx = boss.x * W, by = H * 0.24;
    const bR = Math.min(W, H) * 0.14;
    const px = player.x * W, py = H * PLAYER_Y_PCT;
    frame++; bgT++; phaseTick++;
    player.drawX += (player.x - player.drawX) * 0.18;

    // Phase transitions
    if (!victoryAnim && phaseTick >= PHASE_DUR) {
      phaseTick = 0;
      phase++;
      if (phase >= 3) {
        // Victoire
        victoryAnim = true;
        _boom(bx, by, 28);
        endGame(true);
        return;
      }
      projectiles = []; bombs = []; laserActive = false;
      _boom(bx, by, 18);
    }

    if (victoryAnim) { _drawVictory(ctx, W, H, bx, by); return; }

    if (invTimer > 0) invTimer--;
    if (hitFlash > 0) hitFlash--;
    if (vulnTimer > 0) {
      vulnTimer--; vulnerable = true;
      if (vulnTimer === 0) { vulnerable = false; vulnWindow = 0; }
    }

    // Boss animation
    boss.t += 0.018;
    boss.wobble = Math.sin(boss.t * 1.4) * 0.012;
    boss.x = 0.5 + boss.wobble;
    boss.coronaAngles = boss.coronaAngles.map((a, i) => a + 0.008 + i * 0.0012);

    // ---- PHASE LOGIC ----
    if (phase === 0) {
      // Phase 1: projectiles depuis boss
      if (frame % 70 === 0) {
        const count = 5 + Math.floor(phaseTick / (PHASE_DUR / 3));
        for (let i = 0; i < count; i++) {
          const ang = (Math.PI * 2 / count) * i + bgT * 0.04;
          projectiles.push({ x: bx, y: by, vx: Math.cos(ang) * 3.2, vy: Math.sin(ang) * 3.2, life: 120 });
        }
      }
      if (frame % 200 === 0) { vulnerable = true; vulnTimer = 60; }
    } else if (phase === 1) {
      // Phase 2: laser rotatif
      laserTimer++;
      if (laserTimer % 90 === 0) laserActive = !laserActive;
      if (laserActive) laserAngle += 0.038 + phaseTick * 0.000008;
      // + quelques projectiles
      if (frame % 55 === 0) {
        const ang = Math.atan2(py - by, px - bx) + (Math.random() - 0.5) * 0.8;
        projectiles.push({ x: bx, y: by, vx: Math.cos(ang) * 4.2, vy: Math.sin(ang) * 4.2, life: 100 });
      }
      if (frame % 180 === 0) { vulnerable = true; vulnTimer = 55; }
    } else if (phase === 2) {
      // Phase 3: rage — tout mix
      laserActive = true;
      laserAngle += 0.055 + phaseTick * 0.000012;
      if (frame % 40 === 0) {
        const count = 8;
        for (let i = 0; i < count; i++) {
          const ang = (Math.PI * 2 / count) * i + bgT * 0.07;
          projectiles.push({ x: bx, y: by, vx: Math.cos(ang) * 5.0, vy: Math.sin(ang) * 5.0, life: 90 });
        }
      }
      // Bombes tombantes
      if (frame % 55 === 0) {
        bombs.push({ x: 0.1 + Math.random() * 0.8, y: 0, vy: 3.5 + Math.random() * 2, r: 12 });
      }
      // Dash boss vers joueur (visual shake)
      if (frame % 150 === 0) {
        boss.wobble = (player.x - 0.5) * 0.25;
        if (invTimer === 0 && Math.abs(boss.x - player.x) < 0.22) {
          hitFlash = 30; invTimer = INV_FRAMES; loseLife();
          navigator.vibrate && navigator.vibrate([30, 10, 60]);
        }
      }
      if (frame % 130 === 0) { vulnerable = true; vulnTimer = 45; }
    }

    // Update projectiles
    projectiles.forEach(p => { p.x += p.vx; p.y += p.vy; p.life--; });
    projectiles = projectiles.filter(p => p.life > 0 && p.x > -20 && p.x < W + 20 && p.y < H + 20);

    // Update bombs
    bombs.forEach(b => { b.y += b.vy; });
    bombs = bombs.filter(b => b.y < H + 20);

    // Collision joueur - projectiles
    if (invTimer === 0) {
      for (const p of projectiles) {
        if (Math.hypot(p.x - px, p.y - py) < 18) {
          hitFlash = 25; invTimer = INV_FRAMES;
          _spawnFx(px, py, '#ff4444', 12);
          loseLife();
          navigator.vibrate && navigator.vibrate([25, 8, 50]);
          break;
        }
      }
      // Laser collision (rayon depuis boss)
      if (laserActive) {
        const lx2 = bx + Math.cos(laserAngle) * W;
        const ly2 = by + Math.sin(laserAngle) * W;
        if (_ptToSegDist(px, py, bx, by, lx2, ly2) < 22) {
          hitFlash = 25; invTimer = INV_FRAMES;
          _spawnFx(px, py, '#ffaa00', 12);
          loseLife();
          navigator.vibrate && navigator.vibrate([25, 8, 50]);
        }
      }
      // Bombs
      for (const b of bombs) {
        const bpx = b.x * W;
        if (Math.hypot(bpx - px, b.y - py) < b.r + 16) {
          hitFlash = 25; invTimer = INV_FRAMES;
          _spawnFx(px, py, '#ff8800', 12);
          loseLife();
          navigator.vibrate && navigator.vibrate([25, 8, 50]);
          bombs = bombs.filter(bb => bb !== b);
          break;
        }
      }
    }

    // Update particles
    particles = particles.filter(p => p.life > 0);
    particles.forEach(p => { p.x += p.vx; p.y += p.vy; p.vy += 0.05; p.life--; });

    // ===== DRAW =====
    // BG cosmos éclipse
    const sk = ctx.createRadialGradient(W/2, H*0.2, 20, W/2, H*0.2, H*0.9);
    const phase3pct = phase === 2 ? phaseTick / PHASE_DUR : 0;
    sk.addColorStop(0, '#000');
    sk.addColorStop(0.35, phase < 2 ? '#080210' : `rgba(${Math.floor(25+phase3pct*40)},5,0,1)`);
    sk.addColorStop(1, '#000');
    ctx.fillStyle = sk; ctx.fillRect(0, 0, W, H);

    // Couronne lumineuse (corona)
    const coronaHue = phase === 0 ? 38 : phase === 1 ? 195 : 14;
    boss.coronaAngles.forEach((ang, i) => {
      const r1 = bR * 1.12, r2 = bR * (1.55 + 0.28 * Math.sin(boss.t * 1.8 + i * 0.7));
      const grad = ctx.createLinearGradient(
        bx + Math.cos(ang) * r1, by + Math.sin(ang) * r1,
        bx + Math.cos(ang) * r2, by + Math.sin(ang) * r2
      );
      grad.addColorStop(0, `hsla(${coronaHue},100%,70%,.68)`);
      grad.addColorStop(1, `hsla(${coronaHue},100%,55%,0)`);
      ctx.strokeStyle = grad; ctx.lineWidth = 4 + 3 * Math.sin(boss.t + i);
      ctx.beginPath(); ctx.moveTo(bx + Math.cos(ang)*r1, by + Math.sin(ang)*r1);
      ctx.lineTo(bx + Math.cos(ang)*r2, by + Math.sin(ang)*r2); ctx.stroke();
    });

    // Glow autour du boss
    const bg2 = ctx.createRadialGradient(bx, by, bR*0.5, bx, by, bR*2.6);
    bg2.addColorStop(0, vulnerable ? 'rgba(255,140,0,.38)' : `hsla(${coronaHue},90%,55%,.18)`);
    bg2.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = bg2; ctx.beginPath(); ctx.arc(bx, by, bR*2.6, 0, Math.PI*2); ctx.fill();

    // Corps boss (éclipse - disque noir avec anneau corona)
    ctx.fillStyle = vulnerable ? '#ff6600' : '#000';
    ctx.beginPath(); ctx.arc(bx, by, bR, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = vulnerable ? '#ffaa00' : `hsl(${coronaHue},100%,65%)`;
    ctx.lineWidth = vulnerable ? 5 : 3;
    ctx.globalAlpha = vulnerable ? 0.92 + 0.08 * Math.sin(bgT*0.3) : 0.72;
    ctx.beginPath(); ctx.arc(bx, by, bR, 0, Math.PI*2); ctx.stroke();
    ctx.globalAlpha = 1;

    // Oeil central (rouge en phase rage, ou selon phase)
    if (!vulnerable) {
      const eyeCol = phase === 0 ? '#cc2222' : phase === 1 ? '#2255cc' : '#cc4400';
      const er = bR * (0.25 + 0.04 * Math.sin(boss.t * 2.2));
      const eyeG = ctx.createRadialGradient(bx, by, 2, bx, by, er);
      eyeG.addColorStop(0, '#fff'); eyeG.addColorStop(0.35, eyeCol); eyeG.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = eyeG; ctx.beginPath(); ctx.arc(bx, by, er, 0, Math.PI*2); ctx.fill();
    } else {
      // Vulnérable: boss "ouvert"
      ctx.fillStyle = 'rgba(255,200,50,.9)';
      const er = bR * (0.28 + 0.06 * Math.sin(bgT*0.35));
      ctx.beginPath(); ctx.arc(bx, by, er, 0, Math.PI*2); ctx.fill();
      // Tap hint
      ctx.fillStyle = 'rgba(255,255,255,' + (0.55+0.45*Math.sin(bgT*0.25)).toFixed(2) + ')';
      ctx.font = 'bold 14px system-ui'; ctx.textAlign = 'center';
      ctx.fillText('TAP !', bx, by + bR + 26);
    }

    // Phase info bar
    const phaseNames = ['Phase 1', 'Phase 2', 'Phase 3'];
    const phaseColors = ['#ffcc44', '#44ccff', '#ff5522'];
    const barW = W * 0.62, barX = (W - barW) / 2, barY = H * 0.06;
    ctx.fillStyle = 'rgba(0,0,0,.52)';
    ctx.beginPath(); ctx.roundRect(barX - 4, barY - 4, barW + 8, 20, 5); ctx.fill();
    const pctBar = phaseTick / PHASE_DUR;
    const grad2 = ctx.createLinearGradient(barX, 0, barX+barW, 0);
    grad2.addColorStop(0, phaseColors[phase]);
    grad2.addColorStop(1, phaseColors[phase] + '44');
    ctx.fillStyle = grad2;
    ctx.beginPath(); ctx.roundRect(barX, barY, barW * (1-pctBar), 12, 5); ctx.fill();
    ctx.strokeStyle = phaseColors[phase]; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.roundRect(barX, barY, barW, 12, 5); ctx.stroke();
    ctx.fillStyle = '#fff'; ctx.font = 'bold 11px system-ui'; ctx.textAlign = 'center';
    ctx.fillText(phaseNames[Math.min(phase,2)], W/2, barY + 9);

    // Laser (phase 2+)
    if (laserActive && phase >= 1) {
      const lLen = Math.max(W, H) * 1.5;
      const lg = ctx.createLinearGradient(bx, by, bx + Math.cos(laserAngle)*lLen, by + Math.sin(laserAngle)*lLen);
      lg.addColorStop(0, `hsla(${coronaHue},100%,72%,.92)`);
      lg.addColorStop(0.5, `hsla(${coronaHue},100%,65%,.55)`);
      lg.addColorStop(1, `hsla(${coronaHue},100%,55%,.0)`);
      ctx.strokeStyle = lg; ctx.lineWidth = 10 + 4 * Math.sin(bgT * 0.18);
      ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(bx, by);
      ctx.lineTo(bx + Math.cos(laserAngle)*lLen, by + Math.sin(laserAngle)*lLen);
      ctx.stroke();
      // Core laser bright
      ctx.strokeStyle = 'rgba(255,255,220,.82)'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(bx, by);
      ctx.lineTo(bx + Math.cos(laserAngle)*lLen, by + Math.sin(laserAngle)*lLen);
      ctx.stroke();
    }

    // Projectiles
    projectiles.forEach(p => {
      const pg = ctx.createRadialGradient(p.x, p.y, 1, p.x, p.y, 9);
      pg.addColorStop(0, `hsla(${coronaHue},95%,80%,.92)`);
      pg.addColorStop(1, `hsla(${coronaHue},95%,55%,0)`);
      ctx.fillStyle = pg; ctx.beginPath(); ctx.arc(p.x, p.y, 9, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#fff'; ctx.globalAlpha = 0.7;
      ctx.beginPath(); ctx.arc(p.x, p.y, 3.5, 0, Math.PI*2); ctx.fill();
      ctx.globalAlpha = 1;
    });

    // Bombes (phase 3)
    bombs.forEach(b => {
      const bpx = b.x * W;
      const bg3 = ctx.createRadialGradient(bpx, b.y, 2, bpx, b.y, b.r*2);
      bg3.addColorStop(0, 'rgba(255,120,0,.88)'); bg3.addColorStop(1, 'rgba(255,60,0,0)');
      ctx.fillStyle = bg3; ctx.beginPath(); ctx.arc(bpx, b.y, b.r*2, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#cc4400'; ctx.beginPath(); ctx.arc(bpx, b.y, b.r, 0, Math.PI*2); ctx.fill();
      ctx.strokeStyle = '#ffaa44'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(bpx, b.y, b.r, 0, Math.PI*2); ctx.stroke();
      // Mèche
      ctx.strokeStyle = '#ffdd44'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(bpx, b.y - b.r); ctx.lineTo(bpx + 3, b.y - b.r - 8); ctx.stroke();
      ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(bpx+3, b.y - b.r - 8, 2.5, 0, Math.PI*2); ctx.fill();
    });

    // Particles
    particles.forEach(p => {
      ctx.globalAlpha = p.life / 28; ctx.fillStyle = p.col;
      ctx.beginPath(); ctx.arc(p.x, p.y, 3.5, 0, Math.PI*2); ctx.fill();
    });
    ctx.globalAlpha = 1;

    // Hit flash
    if (hitFlash > 0) {
      ctx.fillStyle = `rgba(255,50,0,${(hitFlash/25*0.28).toFixed(2)})`;
      ctx.fillRect(0, 0, W, H);
    }

    // Joueur
    const pDrawX = player.drawX * W;
    const vis = invTimer === 0 || Math.floor(bgT/7)%2===0;
    if (vis) {
      const plg = ctx.createRadialGradient(pDrawX, py, 4, pDrawX, py, 28);
      plg.addColorStop(0, 'rgba(100,200,255,.38)'); plg.addColorStop(1, 'rgba(60,140,255,0)');
      ctx.fillStyle = plg; ctx.beginPath(); ctx.arc(pDrawX, py, 28, 0, Math.PI*2); ctx.fill();
      drawCosmonaut(ctx, pDrawX, py, 14, 0);
    }

    // Side arrows hint
    ctx.globalAlpha = 0.28;
    ctx.fillStyle = '#88ccff'; ctx.font = 'bold 28px system-ui'; ctx.textAlign = 'center';
    ctx.fillText('\u2190', W*0.07, py+8);
    ctx.fillText('\u2192', W*0.93, py+8);
    ctx.globalAlpha = 1;
  };
  loop();
}
window.gameStart = gameStart;

function _hitBoss(cv) {
  if (!vulnerable || !GPS0_running()) return;
  vulnerable = false; vulnTimer = 0;
  const W = cv.width, H = cv.height;
  const bx = boss.x * W, by = H * 0.24;
  _boom(bx, by, 14);
  navigator.vibrate && navigator.vibrate([15, 5, 30, 5, 50]);
}

function _boom(x, y, n) {
  for (let i = 0; i < n; i++) {
    const ang = Math.random() * Math.PI * 2, spd = 2 + Math.random() * 4;
    const hue = 20 + Math.floor(Math.random() * 60);
    particles.push({
      x: x + (Math.random()-.5)*20, y: y + (Math.random()-.5)*20,
      vx: Math.cos(ang)*spd, vy: Math.sin(ang)*spd - 1, life: 28,
      col: `hsl(${hue},100%,70%)`
    });
  }
}

function _spawnFx(x, y, col, n) {
  for (let i = 0; i < n; i++) particles.push({
    x: x+(Math.random()-.5)*8, y: y+(Math.random()-.5)*8,
    vx:(Math.random()-.5)*3.5, vy:-2+Math.random()*2, life:28, col
  });
}

function _ptToSegDist(px, py, ax, ay, bx, by) {
  const dx = bx-ax, dy = by-ay;
  const t = Math.max(0, Math.min(1, ((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)));
  return Math.hypot(px-(ax+t*dx), py-(ay+t*dy));
}

function _drawVictory(ctx, W, H, bx, by) {
  victoryTick++;
  ctx.fillStyle = '#000'; ctx.fillRect(0,0,W,H);
  // Explosion boss
  for (let i = 0; i < 24; i++) {
    const ang = (i/24)*Math.PI*2 + victoryTick*0.04;
    const r = Math.min(victoryTick*2.2, W*0.42);
    const pulse = 0.6 + 0.4*Math.sin(victoryTick*0.18+i);
    const hue2 = (i*15 + victoryTick*2) % 360;
    ctx.globalAlpha = Math.max(0, 0.88 - victoryTick/220) * pulse;
    ctx.strokeStyle = `hsl(${hue2},100%,65%)`; ctx.lineWidth = 3+pulse*3;
    ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(bx+Math.cos(ang)*r, by+Math.sin(ang)*r); ctx.stroke();
  }
  ctx.globalAlpha = 1;
  // Particules survivantes
  particles.forEach(p => {
    ctx.globalAlpha = p.life/28; ctx.fillStyle = p.col;
    ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI*2); ctx.fill();
  });
  ctx.globalAlpha = 1;
  // Texte victoire
  if (victoryTick > 40) {
    const alpha = Math.min(1, (victoryTick-40)/30);
    ctx.globalAlpha = alpha;
    ctx.fillStyle = '#ffdd88'; ctx.font = 'bold 26px system-ui'; ctx.textAlign = 'center';
    ctx.fillText('\uD83C\uDF1F \u00c9clipseVaincu ! \uD83C\uDF1F', W/2, H*0.44);
    ctx.fillStyle = 'rgba(255,220,130,.75)'; ctx.font = '15px system-ui';
    ctx.fillText('La Lune d\'\u00c9clipse est lib\u00e9r\u00e9e', W/2, H*0.53);
    ctx.globalAlpha = 1;
  }
}
</script>
</body>
</html>"""

with open(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau9.html", "w", encoding="utf-8") as f:
    f.write(content)

import os
size = os.path.getsize(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau9.html")
print(f"OK: {size} bytes")

with open(r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau9.html", encoding="utf-8") as f:
    txt = f.read()

checks = {
    "gameStart":         "gameStart" in txt,
    "3phases":           "PHASE_DUR" in txt,
    "GPS0_TIMER_135":    "GPS0_TIMER_SEC = 135" in txt,
    "projectiles":       "projectiles.push" in txt,
    "laser":             "laserAngle" in txt,
    "bombes_p3":         "bombs.push" in txt,
    "vulnerable_tap":    "_hitBoss" in txt,
    "loseLife":          "loseLife()" in txt,
    "inv_2s":            "INV_FRAMES = 120" in txt,
    "laser_collision":   "_ptToSegDist" in txt,
    "dodge_lateral":     "DODGE_RANGE" in txt,
    "endGame":           "endGame(true)" in txt,
    "victory_anim":      "_drawVictory" in txt,
    "corona":            "coronaAngles" in txt,
    "drawCosmonaut":     "drawCosmonaut" in txt,
    "phase_bar":         "phaseNames" in txt,
}
for k, v in checks.items():
    print(f"  {'OK' if v else 'MISSING'}: {k}")
