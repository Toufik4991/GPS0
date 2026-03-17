'use strict';
window.GPS0_Finale = {
  lancer() {
    const ov = document.createElement('div');
    ov.style.cssText = 'position:fixed;inset:0;z-index:2000;background:rgba(10,10,26,0.97);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px;animation:fin-in 1s ease;';
    ov.innerHTML = '<h1 style="font-size:3rem;color:#FFD700;text-shadow:0 0 40px #FFD700,0 0 80px rgba(255,215,0,0.5);">GPS0</h1>' +
      '<p style="color:#C8A2C8;font-size:1.2rem;text-align:center;max-width:300px">Tu as conquis toutes les zones cosmiques !<br>La Lune est<br>impressionnée... un peu.</p>' +
      '<div style="color:#FFD700;font-size:1.4rem;font-weight:bold">🌙 Aventure accomplie !</div>' +
      '<button id="fin-retour" style="padding:14px 32px;background:linear-gradient(135deg,#C8A2C8,#9a72c8);border:none;border-radius:16px;color:#0A0A1A;font-weight:bold;font-size:1rem;cursor:pointer">Rejouer</button>';
    document.body.appendChild(ov);
    document.getElementById('fin-retour').addEventListener('click', () => location.reload());
    GPS0_Audio && GPS0_Audio.stopMusique && GPS0_Audio.stopMusique();
  }
};
