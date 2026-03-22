/**
 * GPS0 — shared.js v2.0 (Bug 14)
 * Moteur commun à tous les mini-jeux.
 * Chaque niveauN.html doit exposer :
 *   - window.NIVEAU (number)
 *   - window.TUTO_TEXT (string HTML)
 *   - window.gameStart() — appelé après GO!
 *   - window.gameReset() — appelé par Rejouer (stop + reinit)
 *   Optionnel :
 *   - window.onResize() — appelé au resize canvas
 */
'use strict';
(function () {

  // ── ÉTAT GLOBAL ────────────────────────────────────────────────────────────
  let lives = 3, dust = 0, timerSec = 150, timerTotal = 150, running = false, gameover = false;
  let timerInterval = null;
  let _rafIds = []; // requestAnimationFrame ids à annuler pour rejouer
  let _evHandlers = []; // { el, type, fn } à retirer pour rejouer

  // ── ÉLÉMENTS DOM ──────────────────────────────────────────────────────────
  const _q = id => document.getElementById(id);
  let livesEl, timerEl, scoreEl;

  // ── SELFIE ─────────────────────────────────────────────────────────────────
  let selfieImg = null;
  function _loadSelfie() {
    const b64 = localStorage.getItem('gps0_avatar_selfie_base64');
    if (!b64) return;
    const img = new Image();
    img.onload = () => { selfieImg = img; };
    img.src = b64;
  }

  // ── DESSIN COSMONAUTE v3.12 (jetpack animé, visière dégradée, limbes) ──────
  window.drawCosmonaut = function (ctx, x, y, r, angle, state) {
    state = state || 'idle';
    const flaming = (state === 'fly' || state === 'jump');
    const t = Date.now() * 0.004;
    const legA = (state === 'run') ? Math.sin(t * 6) * 0.28 : 0;
    const armA = (state === 'run') ? Math.sin(t * 6 + Math.PI) * 0.2 : 0;
    ctx.save();
    ctx.translate(x, y + (state === 'idle' ? Math.sin(t * 1.5) * r * 0.04 : 0));
    if (angle) ctx.rotate(angle);
    // ── Jetpack ────────────────────────────────────────────────────────────
    ctx.fillStyle = '#6a7e9c';
    ctx.strokeStyle = 'rgba(40,60,100,0.55)'; ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.ellipse(-r*0.58, -r*0.04, r*0.22, r*0.42, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#4a5e7c';
    ctx.beginPath(); ctx.ellipse(-r*0.58, -r*0.04, r*0.08, r*0.18, 0, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = (Date.now() % 1200 < 600) ? '#ff4040' : '#881010';
    ctx.beginPath(); ctx.arc(-r*0.58, -r*0.32, r*0.055, 0, Math.PI*2); ctx.fill();
    if (flaming) {
      const fh = r * (0.32 + Math.sin(t * 18) * 0.1);
      const fB = r * 0.38;
      const fG = ctx.createLinearGradient(-r*0.58, fB, -r*0.58, fB + fh);
      fG.addColorStop(0, 'rgba(255,220,60,0.95)'); fG.addColorStop(0.5, 'rgba(255,110,20,0.8)'); fG.addColorStop(1, 'rgba(255,60,0,0)');
      ctx.fillStyle = fG;
      ctx.beginPath(); ctx.ellipse(-r*0.58, fB + fh*0.42, r*0.1, fh*0.52, 0, 0, Math.PI*2); ctx.fill();
      const fG2 = ctx.createLinearGradient(-r*0.58, fB, -r*0.58, fB + fh*0.6);
      fG2.addColorStop(0, 'rgba(255,255,255,0.9)'); fG2.addColorStop(1, 'rgba(255,220,60,0)');
      ctx.fillStyle = fG2;
      ctx.beginPath(); ctx.ellipse(-r*0.58, fB + fh*0.2, r*0.045, fh*0.25, 0, 0, Math.PI*2); ctx.fill();
    }
    // ── Jambe gauche ────────────────────────────────────────────────────────
    ctx.save(); ctx.translate(-r*0.2, r*0.48); ctx.rotate(-legA);
    ctx.fillStyle = '#b0bfd0'; ctx.strokeStyle = 'rgba(70,90,130,0.3)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.ellipse(0, r*0.27, r*0.15, r*0.3, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#7a8ca8'; ctx.beginPath(); ctx.ellipse(0, r*0.56, r*0.17, r*0.08, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    ctx.restore();
    // ── Jambe droite ────────────────────────────────────────────────────────
    ctx.save(); ctx.translate(r*0.2, r*0.48); ctx.rotate(legA);
    ctx.fillStyle = '#b0bfd0'; ctx.strokeStyle = 'rgba(70,90,130,0.3)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.ellipse(0, r*0.27, r*0.15, r*0.3, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#7a8ca8'; ctx.beginPath(); ctx.ellipse(0, r*0.56, r*0.17, r*0.08, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    ctx.restore();
    // ── Corps principal ─────────────────────────────────────────────────────
    const bG = ctx.createLinearGradient(-r*0.48, -r*0.18, r*0.48, r*0.52);
    bG.addColorStop(0, '#e6edf8'); bG.addColorStop(0.55, '#ccd4e6'); bG.addColorStop(1, '#a8b4cc');
    ctx.fillStyle = bG; ctx.strokeStyle = 'rgba(70,100,150,0.4)'; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.ellipse(0, r*0.18, r*0.44, r*0.55, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = 'rgba(79,195,247,0.38)';
    ctx.beginPath(); ctx.ellipse(0, r*0.16, r*0.3, r*0.1, 0, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#FFD700';
    ctx.beginPath(); ctx.arc(r*0.2, r*0.07, r*0.055, 0, Math.PI*2); ctx.fill();
    // ── Bras gauche ─────────────────────────────────────────────────────────
    ctx.save(); ctx.translate(-r*0.44, -r*0.06); ctx.rotate(-0.28 - armA);
    ctx.fillStyle = '#c0cad8'; ctx.strokeStyle = 'rgba(70,90,130,0.3)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.ellipse(0, r*0.26, r*0.13, r*0.3, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#8090ac'; ctx.beginPath(); ctx.ellipse(0, r*0.54, r*0.15, r*0.1, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    ctx.restore();
    // ── Bras droit ──────────────────────────────────────────────────────────
    ctx.save(); ctx.translate(r*0.44, -r*0.06); ctx.rotate(0.28 + armA);
    ctx.fillStyle = '#c0cad8'; ctx.strokeStyle = 'rgba(70,90,130,0.3)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.ellipse(0, r*0.26, r*0.13, r*0.3, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#8090ac'; ctx.beginPath(); ctx.ellipse(0, r*0.54, r*0.15, r*0.1, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    ctx.restore();
    // ── Casque ──────────────────────────────────────────────────────────────
    const hG = ctx.createRadialGradient(-r*0.18, -r*0.46, r*0.04, 0, -r*0.25, r*0.57);
    hG.addColorStop(0, 'rgba(175,215,255,0.85)'); hG.addColorStop(0.4, 'rgba(95,140,215,0.6)'); hG.addColorStop(1, 'rgba(45,28,110,0.38)');
    ctx.fillStyle = hG; ctx.strokeStyle = 'rgba(120,175,230,0.9)'; ctx.lineWidth = 2.2;
    ctx.beginPath(); ctx.arc(0, -r*0.25, r*0.54, 0, Math.PI*2); ctx.fill(); ctx.stroke();
    // ── Visière ─────────────────────────────────────────────────────────────
    ctx.save();
    ctx.beginPath(); ctx.arc(0, -r*0.25, r*0.41, 0, Math.PI*2); ctx.clip();
    if (selfieImg) {
      ctx.drawImage(selfieImg, -r*0.41, -r*0.66, r*0.82, r*0.82);
    } else {
      const vG = ctx.createRadialGradient(r*0.1, -r*0.38, r*0.03, 0, -r*0.25, r*0.41);
      vG.addColorStop(0, 'rgba(145,195,255,0.95)'); vG.addColorStop(0.5, 'rgba(75,110,215,0.9)'); vG.addColorStop(1, 'rgba(45,25,115,0.9)');
      ctx.fillStyle = vG; ctx.fillRect(-r, -r, r*2, r*2);
      ctx.fillStyle = '#FFD700'; ctx.beginPath(); ctx.arc(0, -r*0.25, r*0.27, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#111';
      ctx.beginPath(); ctx.arc(-r*0.09, -r*0.32, r*0.05, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(r*0.09, -r*0.32, r*0.05, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(0, -r*0.17, r*0.155, 0.2, Math.PI - 0.2);
      ctx.strokeStyle = '#111'; ctx.lineWidth = r*0.055; ctx.stroke();
    }
    ctx.restore();
    // Reflets visière
    ctx.fillStyle = 'rgba(255,255,255,0.26)';
    ctx.beginPath(); ctx.ellipse(-r*0.12, -r*0.43, r*0.13, r*0.07, -0.5, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.1)';
    ctx.beginPath(); ctx.ellipse(-r*0.04, -r*0.34, r*0.07, r*0.04, -0.3, 0, Math.PI*2); ctx.fill();
    ctx.restore();
  };

  // ── HUD ────────────────────────────────────────────────────────────────────
  window.GPS0_lives = () => lives;
  window.GPS0_running = () => running;

  function _updateLives() {
    if (!livesEl) return;
    livesEl.textContent = '❤'.repeat(Math.max(0, lives)) + '♡'.repeat(Math.max(0, 3 - lives));
  }
  function _updateTimer() {
    if (!timerEl) return;
    const m = Math.floor(timerSec / 60), s = timerSec % 60;
    timerEl.textContent = m + ':' + (s < 10 ? '0' : '') + s;
  }
  window.addDust = function (n) {
    dust += n;
    if (scoreEl) scoreEl.textContent = dust + ' ✨';
  };

  // ── FLASH ROUGE ─────────────────────────────────────────────────────────────
  function _flashRed() {
    let el = _q('flash-overlay');
    if (!el) {
      el = document.createElement('div');
      el.id = 'flash-overlay';
      el.style.cssText = 'position:fixed;inset:0;z-index:900;pointer-events:none;border:8px solid red;background:rgba(255,0,0,0.3);opacity:0;transition:none';
      document.body.appendChild(el);
    }
    el.style.opacity = '0.7';
    // Screenshake
    document.body.style.transform = 'translateX(5px)';
    setTimeout(() => { document.body.style.transform = 'translateX(-5px)'; }, 60);
    setTimeout(() => { document.body.style.transform = 'translateX(3px)'; }, 120);
    setTimeout(() => { document.body.style.transform = ''; }, 200);
    setTimeout(() => { el.style.opacity = '0'; }, 300);
  }

  window.loseLife = function () {
    if (!running) return;
    lives--;
    _updateLives();
    _flashRed();
    if (lives <= 0) window.endGame(false);
  };

  // ── FIN DE JEU ─────────────────────────────────────────────────────────────
  window.endGame = function (success) {
    if (gameover) return;
    gameover = true; running = false;
    clearInterval(timerInterval);
    let finalDust;
    // Récompense personnalisée (ex: efficacité N1 ou boss N9)
    if (window.GPS0_rewardOverride !== undefined) {
      finalDust = Math.min(50, Math.max(1, Math.round(window.GPS0_rewardOverride)));
    } else {
      // Formule chrono : gain = floor((tempsJoué / tempsTotal) * 50)
      const tempsJoue = timerTotal - timerSec;
      finalDust = Math.floor((tempsJoue / timerTotal) * 50);
      if (tempsJoue > 5 && finalDust < 1) finalDust = 1; // min 1 si > 5 secondes
      finalDust = Math.min(50, finalDust); // max 50
    }
    setTimeout(() => {
      window.parent.postMessage({
        source: 'gps0_minijeu',
        success,
        niveau: window.NIVEAU || 1,
        poussieres: finalDust
      }, '*');
    }, 800);
  };

  // ── QUITTER ─────────────────────────────────────────────────────────────────
  function _quitter() {
    running = false; gameover = true;
    clearInterval(timerInterval);
    window.parent.postMessage({ source: 'gps0_minijeu', quit: true }, '*');
  }

  // ── RÉSOLUTION CANVAS ──────────────────────────────────────────────────────
  window.GPS0_resizeCanvas = function (cv) {
    const gc = cv.parentElement || document.getElementById('game-container');
    cv.width = gc ? gc.clientWidth : window.innerWidth;
    cv.height = gc ? gc.clientHeight : window.innerHeight;
    if (window.onResize) window.onResize();
  };

  // ── COUNTDOWN ──────────────────────────────────────────────────────────────
  function _countdown() {
    return new Promise(resolve => {
      const ov = document.createElement('div');
      ov.id = 'cd-overlay';
      ov.style.cssText = 'position:fixed;inset:0;z-index:800;background:rgba(0,0,0,0.88);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px';
      const num = document.createElement('div');
      num.style.cssText = 'font-size:7rem;font-weight:900;color:#fff;text-shadow:0 0 40px rgba(200,162,200,0.8)';
      ov.appendChild(num);
      document.body.appendChild(ov);
      let count = 5;
      const tick = () => {
        if (count > 0) {
          num.textContent = count;
          num.style.transform = 'scale(0.5)';
          num.style.transition = 'none';
          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              num.style.transform = 'scale(1)';
              num.style.transition = 'transform 0.35s ease-out';
            });
          });
          count--;
          setTimeout(tick, 900);
        } else {
          num.textContent = 'GO!';
          num.style.color = '#FFD700';
          num.style.textShadow = '0 0 60px #FFD700';
          num.style.transform = 'scale(1.3)';
          setTimeout(() => { ov.remove(); resolve(); }, 700);
        }
      };
      tick();
    });
  }

  // ── TUTO OVERLAY ───────────────────────────────────────────────────────────
  function _showTuto() {
    return new Promise(resolve => {
      const ov = document.createElement('div');
      ov.id = 'tuto-overlay';
      ov.style.cssText = 'position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.92);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px;padding:32px;text-align:center';
      const n = window.NIVEAU || 1;
      const emojis = ['','🌑','🌒','🌓','🌔','🌕','🌖','🌗','🌘','🌑'];
      const names = ['','Lune de Verre','Lune de Cendre','Lune de Lierre','Lune de Givre',"Lune d'Ombre","Lune de Fer","Lune de Tempête","Lune de Cristal","Lune d'Éclipse"];
      ov.innerHTML = `
        <div style="font-size:3rem">${emojis[n]}</div>
        <div style="font-size:1.4rem;font-weight:900;color:#C8A2C8">${names[n]}</div>
        <div style="font-size:0.95rem;color:rgba(255,255,255,0.85);max-width:300px;line-height:1.6">${window.TUTO_TEXT || ''}</div>
        <button id="tuto-ok" style="padding:14px 40px;border:none;border-radius:16px;font-size:1rem;font-weight:bold;cursor:pointer;background:linear-gradient(135deg,#C8A2C8,#8860a8);color:#fff;margin-top:8px">Compris !</button>`;
      document.body.appendChild(ov);
      document.getElementById('tuto-ok').addEventListener('click', () => {
        ov.remove();
        resolve();
      }, { once: true });
    });
  }

  // ── BOUTON QUITTER ─────────────────────────────────────────────────────────
  function _addQuitButton() {
    const btn = document.createElement('button');
    btn.id = 'btn-quit';
    btn.textContent = '✕';
    btn.style.cssText = 'position:fixed;top:10px;right:10px;z-index:950;width:40px;height:40px;border-radius:50%;border:2px solid rgba(255,255,255,0.3);background:rgba(0,0,0,0.6);color:#fff;font-size:1.1rem;cursor:pointer;font-weight:bold;line-height:1';
    btn.addEventListener('click', () => {
      const conf = document.createElement('div');
      conf.style.cssText = 'position:fixed;inset:0;z-index:1000;background:rgba(0,0,0,0.85);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;text-align:center;padding:32px';
      conf.innerHTML = `
        <div style="font-size:1.3rem;font-weight:bold;color:#fff">Quitter ?</div>
        <div style="font-size:0.9rem;color:rgba(255,255,255,0.7)">Tu perdras ta progression<br>et gagneras 0 ✨</div>
        <div style="display:flex;gap:16px">
          <button id="quit-oui" style="padding:12px 28px;border:none;border-radius:12px;background:#c0392b;color:#fff;font-weight:bold;cursor:pointer;font-size:1rem">Oui, quitter</button>
          <button id="quit-non" style="padding:12px 28px;border:none;border-radius:12px;background:rgba(255,255,255,0.15);color:#fff;font-weight:bold;cursor:pointer;font-size:1rem">Non, continuer</button>
        </div>`;
      document.body.appendChild(conf);
      running = false;
      document.getElementById('quit-oui').addEventListener('click', () => _quitter(), { once: true });
      document.getElementById('quit-non').addEventListener('click', () => { conf.remove(); running = true; }, { once: true });
    });
    document.body.appendChild(btn);
  }

  // ── DÉMARRAGE ──────────────────────────────────────────────────────────────
  function _startTimer() {
    _updateTimer();
    timerInterval = setInterval(() => {
      if (!running) return;
      timerSec--;
      _updateTimer();
      if (timerSec <= 0) {
        if (window.GPS0_onTimerExpired) { window.GPS0_onTimerExpired(); }
        else { window.endGame(false); }
      }
    }, 1000);
  }
  // Expose timerSec pour les jeux qui en ont besoin (ex: N9 rage mode)
  window.GPS0_timerSec = () => timerSec;

  async function _boot() {
    // Permettre aux niveaux de définir leur durée : window.GPS0_TIMER_SEC = 180 (3min)
    if (window.GPS0_TIMER_SEC && window.GPS0_TIMER_SEC > 0) {
      timerSec = window.GPS0_TIMER_SEC;
    }
    timerTotal = timerSec; // mémoriser la durée totale pour le calcul du gain
    livesEl = _q('lives');
    timerEl = _q('timer');
    scoreEl = _q('score-hud');
    _updateLives();
    _updateTimer();
    _loadSelfie();
    // Phase 1 : tuto
    await _showTuto();
    // Phase 2 : countdown
    await _countdown();
    // Phase 3 : jeu (bouton quitter APRÈS le countdown)
    _addQuitButton();
    running = true;
    _startTimer();
    if (window.gameStart) window.gameStart();
  }

  // Lancer au DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _boot);
  } else {
    _boot();
  }

})();
