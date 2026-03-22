'use strict';
window.GPS0_Finale = {
  lancer() {
    const pseudo = localStorage.getItem('gps0_pseudo') || 'Explorateur';
    const selfie = typeof GPS0_Avatar !== 'undefined' ? GPS0_Avatar.getSelfie() : null;
    const eco = typeof GPS0_Economie !== 'undefined' && GPS0_Economie.get ? GPS0_Economie.get() : {};
    const totalDust = eco.poussieres || 0;

    // Récupérer stats depuis localStorage
    const prog = JSON.parse(localStorage.getItem('gps0_zones_actives') || '{}');
    const zonesCount = (prog.zones || []).length;
    const zonesDone = prog.index || 0;

    // Temps total depuis le chrono
    const chronoEl = document.getElementById('chrono');
    const tempsTotal = chronoEl ? chronoEl.textContent : '00:00';

    // Styles
    if (!document.getElementById('fin-keyframes')) {
      const s = document.createElement('style'); s.id = 'fin-keyframes';
      s.textContent = `
        @keyframes fin-in{from{opacity:0;transform:scale(0.85)}to{opacity:1;transform:scale(1)}}
        @keyframes fin-confetti{0%{transform:translateY(-10vh) rotate(0deg);opacity:1}100%{transform:translateY(110vh) rotate(720deg);opacity:0}}
        @keyframes fin-zoom{0%{transform:scale(0.5);opacity:0}60%{transform:scale(1.1);opacity:1}100%{transform:scale(1)}}
        @keyframes fin-glow{0%,100%{text-shadow:0 0 20px #FFD700,0 0 40px rgba(255,215,0,.5)}50%{text-shadow:0 0 40px #FFD700,0 0 80px rgba(255,215,0,.7)}}
        @keyframes fin-fade{from{opacity:0}to{opacity:1}}
      `;
      document.head.appendChild(s);
    }

    GPS0_Audio && GPS0_Audio.stopMusique && GPS0_Audio.stopMusique();

    // Container
    const ov = document.createElement('div'); ov.id = 'overlay-finale';
    ov.style.cssText = 'position:fixed;inset:0;z-index:2000;background:rgba(10,10,26,0.98);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0;animation:fin-in 1.2s cubic-bezier(0.22,1,0.36,1) both;overflow:hidden';
    document.body.appendChild(ov);

    // PHASE 1 : Zoom visage cosmonaute (0-3s)
    const faceDiv = document.createElement('div');
    faceDiv.style.cssText = 'animation:fin-zoom 2s cubic-bezier(0.22,1,0.36,1) both;margin-bottom:16px';
    if (selfie) {
      const cv = document.createElement('canvas'); cv.width = 120; cv.height = 120;
      cv.style.cssText = 'border-radius:50%;border:4px solid rgba(255,215,0,.7);box-shadow:0 0 30px rgba(255,215,0,.4)';
      faceDiv.appendChild(cv);
      const img = new Image(); img.onload = () => {
        const c = cv.getContext('2d');
        c.beginPath(); c.arc(60, 60, 56, 0, Math.PI * 2); c.clip();
        c.drawImage(img, 0, 0, 120, 120);
      }; img.src = selfie;
    } else {
      faceDiv.innerHTML = '<div style="width:120px;height:120px;border-radius:50%;border:4px solid rgba(255,215,0,.7);box-shadow:0 0 30px rgba(255,215,0,.4);background:rgba(79,195,247,.15);display:flex;align-items:center;justify-content:center;font-size:3.5rem">🚀</div>';
    }
    ov.appendChild(faceDiv);

    // PHASE 2 : Confettis étoiles (démarrent immédiatement, 20s)
    const confettiBox = document.createElement('div');
    confettiBox.style.cssText = 'position:absolute;inset:0;pointer-events:none;overflow:hidden';
    const confettiChars = ['⭐', '✨', '🌟', '💫', '🪐'];
    const confettiColors = ['#FFD700', '#C0C0C0', '#FFB347', '#87CEEB', '#DDA0DD'];
    for (let i = 0; i < 50; i++) {
      const p = document.createElement('span');
      const size = 10 + Math.random() * 20;
      const left = Math.random() * 100;
      const delay = Math.random() * 8;
      const dur = 4 + Math.random() * 6;
      p.textContent = confettiChars[i % confettiChars.length];
      p.style.cssText = `position:absolute;left:${left}%;top:-5%;font-size:${size}px;animation:fin-confetti ${dur}s linear ${delay}s infinite;opacity:0.8;`;
      confettiBox.appendChild(p);
    }
    // Particules dorées/argentées rondes
    for (let i = 0; i < 30; i++) {
      const p = document.createElement('div');
      const size = 3 + Math.random() * 6;
      const left = Math.random() * 100;
      const delay = Math.random() * 10;
      const dur = 5 + Math.random() * 8;
      p.style.cssText = `position:absolute;left:${left}%;top:-3%;width:${size}px;height:${size}px;border-radius:50%;background:${confettiColors[i % confettiColors.length]};animation:fin-confetti ${dur}s linear ${delay}s infinite;opacity:0.6;`;
      confettiBox.appendChild(p);
    }
    ov.appendChild(confettiBox);

    // SFX confettis
    setTimeout(() => {
      GPS0_Audio && GPS0_Audio.playSFX && GPS0_Audio.playSFX('confetti');
      GPS0_Audio && GPS0_Audio.playMusiqueFinale && GPS0_Audio.playMusiqueFinale();
    }, 600);

    // PHASE 3 : Message BRAVO (après 2s)
    setTimeout(() => {
      const bravo = document.createElement('div');
      bravo.style.cssText = 'animation:fin-fade 1.5s ease both;text-align:center';
      bravo.innerHTML = `<div style="font-size:2.2rem;color:#FFD700;font-weight:bold;animation:fin-glow 2s ease-in-out infinite;letter-spacing:0.05em">🎉 BRAVO ${_escHtml(pseudo)} ! 🎉</div>`;
      ov.appendChild(bravo);
    }, 2000);

    // PHASE 4 : Récap des scores (après 4s)
    setTimeout(() => {
      const recap = document.createElement('div');
      recap.style.cssText = 'animation:fin-fade 1.5s ease both;background:rgba(255,255,255,.05);border:1px solid rgba(255,215,0,.2);border-radius:16px;padding:20px 24px;margin:12px 20px;max-width:320px;width:calc(100% - 40px)';
      recap.innerHTML = `
        <div style="text-align:center;margin-bottom:12px;font-size:1rem;color:var(--gold,#FFD700);font-weight:bold">📊 Récapitulatif</div>
        <div style="display:flex;flex-direction:column;gap:8px;font-size:0.88rem;color:rgba(255,255,255,.85)">
          <div>⭐ Poussières collectées : <strong style="color:#FFD700">${totalDust}</strong></div>
          <div>🎮 Jeux réussis : <strong style="color:#69FF47">${zonesDone}/${zonesCount}</strong></div>
          <div>⏱️ Temps total : <strong style="color:#4FC3F7">${tempsTotal}</strong></div>
        </div>`;
      ov.appendChild(recap);
    }, 4000);

    // PHASE 5 : Bouton FIN → transition bisous (après 7s)
    setTimeout(() => {
      const btnWrap = document.createElement('div');
      btnWrap.style.cssText = 'animation:fin-fade 1s ease both;margin-top:16px';
      const btnFin = document.createElement('button');
      btnFin.style.cssText = 'padding:16px 44px;background:linear-gradient(135deg,#C8A2C8,#9a72c8);border:none;border-radius:20px;color:#0A0A1A;font-weight:bold;font-size:1.1rem;cursor:pointer;letter-spacing:0.05em;min-height:48px;min-width:44px;touch-action:manipulation';
      btnFin.textContent = 'Continuer 🌙';
      btnWrap.appendChild(btnFin);
      ov.appendChild(btnWrap);

      btnFin.addEventListener('click', () => {
        // TRANSITION BISOUS
        ov.style.transition = 'opacity 2s ease';
        ov.style.opacity = '0';
        setTimeout(() => {
          ov.remove();
          _afficherBisous();
        }, 2000);
      }, { once: true });
    }, 7000);

    function _afficherBisous() {
      const bis = document.createElement('div'); bis.id = 'overlay-bisous';
      bis.style.cssText = 'position:fixed;inset:0;z-index:2001;background:#000;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;animation:fin-fade 2s ease both';
      bis.innerHTML = `
        <div style="font-size:5rem;animation:fin-zoom 1.5s ease both">🌝</div>
        <div style="font-size:1.6rem;color:#fff;font-weight:bold;animation:fin-fade 2s ease 1s both">BISOUS 💋</div>`;
      document.body.appendChild(bis);
      // Bouton quitter après 5s
      setTimeout(() => {
        const btn = document.createElement('button');
        btn.textContent = 'Quitter 🚪';
        btn.style.cssText = 'padding:14px 36px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.3);border-radius:16px;color:#fff;font-size:1rem;cursor:pointer;animation:fin-fade 1s ease both;min-height:48px;touch-action:manipulation';
        btn.addEventListener('click', () => location.reload());
        bis.appendChild(btn);
      }, 5000);
    }

    function _escHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
  }
};
