'use strict';
window.GPS0_Economie = (() => {
  const TAUX = { clair_de_lune: 1, face_cachee: 2, eclipse_totale: 5, trou_noir: 0 };
  let _timer = null, _tnTimer = null, _activeFn = null;

  function get() {
    const s = localStorage.getItem('gps0_economie');
    return s ? JSON.parse(s) : { poussieres: 0, energie: { actuelle: 100, max: 100, dernierCalcul: Date.now() } };
  }
  function save(v) { localStorage.setItem('gps0_economie', JSON.stringify(v)); }

  function energiePC() { const e = get().energie; return Math.round(e.actuelle / e.max * 100); }

  function ajouterPoussieres(n) { const e = get(); e.poussieres += n; save(e); updateHUD(); }

  function rechargePassive() {
    const e = get();
    const bonus = Math.floor((Date.now() - e.energie.dernierCalcul) / 900000); // 15min = 900000ms
    if (bonus > 0) {
      e.energie.actuelle = Math.min(e.energie.max, e.energie.actuelle + bonus);
      e.energie.dernierCalcul = Date.now();
      save(e); updateHUD();
    }
  }

  function demarrerConsommation(diffId, activeFn) {
    _activeFn = activeFn;
    arreterConsommation();
    if (diffId === 'trou_noir') { _cycleTrouNoir(); return; }
    const taux = TAUX[diffId] || 1;
    _timer = setInterval(() => {
      if (!(_activeFn && _activeFn())) return;
      const e = get();
      e.energie.actuelle = Math.max(0, e.energie.actuelle - taux);
      e.energie.dernierCalcul = Date.now();
      save(e); updateHUD();
    }, 10000);
  }

  function _cycleTrouNoir() {
    if (_activeFn) _activeFn(true);
    _tnTimer = setTimeout(() => {
      if (_activeFn) _activeFn(false);
      _tnTimer = setTimeout(_cycleTrouNoir, 170000);
    }, 10000);
  }

  function arreterConsommation() { clearInterval(_timer); _timer = null; clearTimeout(_tnTimer); _tnTimer = null; }
  function isEpuise() { return energiePC() <= 0; }

  function updateHUD() {
    const e = get(), pc = Math.round(e.energie.actuelle / e.energie.max * 100);
    const bar = document.getElementById('energie-barre');
    const pd = document.getElementById('poussieres');
    const hud = document.querySelector('.hud-energie');
    if (bar) { bar.style.width = pc + '%'; bar.classList.toggle('critique', pc < 20); }
    if (pd) pd.textContent = e.poussieres;
    if (hud) hud.setAttribute('aria-valuenow', pc);
  }

  return { get, save, energiePC, ajouterPoussieres, rechargePassive, demarrerConsommation, arreterConsommation, isEpuise, updateHUD };
})();
