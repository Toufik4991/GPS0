'use strict';
window.GPS0_Economie = (() => {
  const TAUX = { clair_de_lune: 1, face_cachee: 2, eclipse_totale: 5, trou_noir: 0 };
  const COOLDOWN_MS = 5 * 60 * 1000; // 5 minutes
  let _timer = null, _tnTimer = null, _activeFn = null;

  function get() {
    const s = localStorage.getItem('gps0_economie');
    return s ? JSON.parse(s) : {
      poussieres: 0,
      energie: { actuelle: 100, max: 100, dernierCalcul: Date.now() },
      cooldowns: {},
      fragments: {}
    };
  }
  function save(v) { localStorage.setItem('gps0_economie', JSON.stringify(v)); }

  function energiePC() { const e = get().energie; return Math.round(e.actuelle / e.max * 100); }

  function ajouterPoussieres(n) { const e = get(); e.poussieres += n; save(e); updateHUD(); }
  function retirerPoussieres(n) {
    const e = get();
    if (e.poussieres < n) return false;
    e.poussieres -= n; save(e); updateHUD(); return true;
  }

  // ── COOLDOWN ────────────────────────────────────
  function setCooldown(niveau) {
    const e = get();
    if (!e.cooldowns) e.cooldowns = {};
    e.cooldowns[niveau] = Date.now() + COOLDOWN_MS;
    save(e);
  }
  function getCooldownRestant(niveau) {
    const e = get();
    if (!e.cooldowns || !e.cooldowns[niveau]) return 0;
    return Math.max(0, e.cooldowns[niveau] - Date.now());
  }
  function isCooldown(niveau) { return getCooldownRestant(niveau) > 0; }
  function formatCooldown(ms) {
    const s = Math.ceil(ms / 1000);
    return String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
  }

  // ── FRAGMENTS DE LUNE (boutique) ─────────────────
  function getFragments() { return get().fragments || {}; }
  function acheterFragment(id, prix) {
    const e = get();
    if (!e.fragments) e.fragments = {};
    if (e.poussieres < prix) return false;
    e.poussieres -= prix;
    e.fragments[id] = (e.fragments[id] || 0) + 1;
    save(e); updateHUD(); return true;
  }
  function utiliserFragment(id) {
    const e = get();
    if (!e.fragments || !e.fragments[id] || e.fragments[id] <= 0) return false;
    // Appliquer le bonus selon le fragment
    const fragment = GPS0_Economie_FRAGMENTS[id];
    if (!fragment) return false;
    e.fragments[id]--;
    if (fragment.bonus_energie) {
      e.energie.actuelle = Math.min(e.energie.max, e.energie.actuelle + (e.energie.max * fragment.bonus_energie / 100));
    }
    save(e); updateHUD(); return true;
  }

  // ── ÉNERGIE ────────────────────────────────────
  function rechargePassive() {
    const e = get();
    const bonus = Math.floor((Date.now() - e.energie.dernierCalcul) / 900000);
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
    // Mise à jour cercle énergie dans l'astéroïde
    const cercle = document.getElementById('energie-cercle');
    const sable = document.getElementById('energie-sable');
    const pct = document.getElementById('energie-pct');
    const pd = document.getElementById('poussieres');
    if (cercle) {
      const r = 28, circ = 2 * Math.PI * r;
      cercle.style.strokeDasharray = circ;
      cercle.style.strokeDashoffset = circ * (1 - pc / 100);
      const col = pc > 50 ? '#4FC3F7' : pc > 20 ? '#FFD700' : '#FF3333';
      cercle.setAttribute('stroke', col);
    }
    if (sable) {
      sable.style.height = pc + '%';
      const col = pc > 50 ? 'rgba(79,195,247,0.35)' : pc > 20 ? 'rgba(255,215,0,0.35)' : 'rgba(255,51,51,0.45)';
      sable.style.background = col;
    }
    if (pct) { pct.textContent = pc + '%'; }
    if (pd) pd.textContent = e.poussieres;
    // Aussi mettre a jour aria
    const hudEnergie = document.querySelector('.hud-energie');
    if (hudEnergie) hudEnergie.setAttribute('aria-valuenow', pc);
  }

  return {
    get, save, energiePC, ajouterPoussieres, retirerPoussieres,
    rechargePassive, demarrerConsommation, arreterConsommation, isEpuise, updateHUD,
    setCooldown, getCooldownRestant, isCooldown, formatCooldown,
    getFragments, acheterFragment, utiliserFragment
  };
})();

// Catalogue fragments — lu par la boutique et economie
window.GPS0_Economie_FRAGMENTS = {
  petit_fragment:  { id: 'petit_fragment',  nom: 'Petit Fragment de Lune',  emoji: '🌙', desc: '+25% énergie instantanément', bonus_energie: 25, prix: 30,  couleur: '#C8A2C8' },
  gros_fragment:   { id: 'gros_fragment',   nom: 'Grand Fragment de Lune',  emoji: '🌕', desc: '+50% énergie instantanément', bonus_energie: 50, prix: 60,  couleur: '#FFD700' },
  eclat_stellaire: { id: 'eclat_stellaire', nom: 'Éclat Stellaire',         emoji: '⭐', desc: '+75% énergie — réservé aux braves', bonus_energie: 75, prix: 100, couleur: '#69FF47' }
};
