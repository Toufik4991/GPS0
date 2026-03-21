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
  let lives = 3, dust = 0, timerSec = 150, running = false, gameover = false;
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

  // ── DESSIN COSMONAUTE ──────────────────────────────────────────────────────
  window.drawCosmonaut = function (ctx, x, y, r, angle) {
    ctx.save();
    ctx.translate(x, y);
    if (angle) ctx.rotate(angle);
    // Corps
    ctx.beginPath();
    ctx.ellipse(0, r * 0.5, r * 0.55, r * 0.7, 0, 0, Math.PI * 2);
    ctx.fillStyle = '#dde4ee'; ctx.fill();
    ctx.strokeStyle = 'rgba(100,140,200,0.4)'; ctx.lineWidth = 1.5; ctx.stroke();
    // Casque
    ctx.beginPath(); ctx.arc(0, -r * 0.15, r * 0.55, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(60,120,200,0.25)'; ctx.fill();
    ctx.strokeStyle = '#8ab4d4'; ctx.lineWidth = 2; ctx.stroke();
    // Visage : selfie ou smiley
    ctx.save();
    ctx.beginPath(); ctx.arc(0, -r * 0.15, r * 0.44, 0, Math.PI * 2); ctx.clip();
    if (selfieImg) {
      ctx.drawImage(selfieImg, -r * 0.44, -r * 0.59, r * 0.88, r * 0.88);
    } else {
      // Smiley jaune
      ctx.fillStyle = '#FFD700';
      ctx.beginPath(); ctx.arc(0, -r * 0.15, r * 0.4, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#333';
      ctx.beginPath(); ctx.arc(-r * 0.14, -r * 0.24, r * 0.07, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(r * 0.14, -r * 0.24, r * 0.07, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath();
      ctx.arc(0, -r * 0.08, r * 0.22, 0.2, Math.PI - 0.2);
      ctx.strokeStyle = '#333'; ctx.lineWidth = r * 0.07; ctx.stroke();
    }
    ctx.restore();
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
    const played = 150 - timerSec;
    let base;
    if (played < 30) base = 1 + Math.floor(Math.random() * 5);
    else if (played < 60) base = 5 + Math.floor(Math.random() * 10);
    else if (played < 100) base = 15 + Math.floor(Math.random() * 15);
    else if (played < 130) base = 30 + Math.floor(Math.random() * 10);
    else base = 40 + Math.floor(Math.random() * 10);
    const finalDust = Math.min(60, base + dust + (success ? 10 : 0));
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
      if (timerSec <= 0) window.endGame(false);
    }, 1000);
  }

  async function _boot() {
    // Attendre que le DOM soit prêt
    livesEl = _q('lives');
    timerEl = _q('timer');
    scoreEl = _q('score-hud');
    _updateLives();
    _updateTimer();
    _addQuitButton();
    _loadSelfie();
    // Phase 1: tuto
    await _showTuto();
    // Phase 2: countdown
    await _countdown();
    // Phase 3: démarrer jeu
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
