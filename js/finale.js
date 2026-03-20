'use strict';
window.GPS0_Finale = {
  lancer() {
    // Keyframes injectées une seule fois
    if (!document.getElementById('fin-keyframes')) {
      const s = document.createElement('style');
      s.id = 'fin-keyframes';
      s.textContent = '@keyframes fin-in{from{opacity:0;transform:scale(0.85)}to{opacity:1;transform:scale(1)}}' +
        '@keyframes fin-etoiles{0%,100%{opacity:.4;transform:scale(1)}50%{opacity:1;transform:scale(1.4)}}';
      document.head.appendChild(s);
    }
    // Particules étoiles
    const particules = Array.from({length: 24}, (_, i) => {
      const ang = (i / 24) * 360, r = 60 + Math.random() * 120;
      const x = 50 + Math.cos(ang * Math.PI / 180) * r, y = 50 + Math.sin(ang * Math.PI / 180) * r;
      const size = 4 + Math.random() * 6;
      return `<div style="position:absolute;left:${x}%;top:${y}%;width:${size}px;height:${size}px;border-radius:50%;background:#FFD700;animation:fin-etoiles ${1 + Math.random()}s ease-in-out infinite;animation-delay:${Math.random() * 1.5}s"></div>`;
    }).join('');

    const ov = document.createElement('div');
    ov.id = 'overlay-finale';
    ov.style.cssText = 'position:fixed;inset:0;z-index:2000;background:rgba(10,10,26,0.97);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px;animation:fin-in 1.2s cubic-bezier(0.22,1,0.36,1) both;overflow:hidden;';
    ov.innerHTML =
      `<div style="position:absolute;inset:0;pointer-events:none">${particules}</div>` +
      '<h1 style="font-size:3.5rem;color:#FFD700;text-shadow:0 0 40px #FFD700,0 0 80px rgba(255,215,0,0.5);letter-spacing:0.12em;font-style:italic">GPS0</h1>' +
      '<div style="font-size:3rem">🏆</div>' +
      '<p style="color:#C8A2C8;font-size:1.15rem;text-align:center;max-width:300px;line-height:1.6">Tu as conquis toutes les zones cosmiques !<br><em>La Lune est impressionnée... un peu.</em></p>' +
      '<div style="color:#FFD700;font-size:1.3rem;font-weight:bold">🌙 Aventure accomplie !</div>' +
      '<button id="fin-retour" style="padding:16px 40px;background:linear-gradient(135deg,#C8A2C8,#9a72c8);border:none;border-radius:20px;color:#0A0A1A;font-weight:bold;font-size:1.1rem;cursor:pointer;letter-spacing:0.05em">Rejouer 🚀</button>';
    document.body.appendChild(ov);
    document.getElementById('fin-retour').addEventListener('click', () => location.reload());
    GPS0_Audio && GPS0_Audio.stopMusique && GPS0_Audio.stopMusique();
    setTimeout(() => { GPS0_Audio && GPS0_Audio.playMusiqueFinale && GPS0_Audio.playMusiqueFinale(); }, 600);
  }
};
