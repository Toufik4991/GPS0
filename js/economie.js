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
    if (fragment.full_recharge) {
      e.energie.actuelle = e.energie.max;
    } else if (fragment.bonus_energie) {
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
    const pct = document.getElementById('energie-pct');
    const pd = document.getElementById('poussieres');
    if (cercle) {
      const r = 108, circ = 2 * Math.PI * r; // anneau 240px SVG entourant asteroide
      cercle.style.strokeDasharray = circ;
      cercle.style.strokeDashoffset = circ * (1 - pc / 100);
      const col = pc > 50 ? '#4FC3F7' : pc > 20 ? '#FFD700' : '#FF3333';
      cercle.setAttribute('stroke', col);
    }
    if (pct) { pct.textContent = pc + '%'; }
    if (pd) pd.textContent = e.poussieres;
    // HUD énergie label
    const hudEnergieVal = document.getElementById('hud-energie-val');
    if (hudEnergieVal) hudEnergieVal.textContent = pc + '%';
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
const _SVG_ECLAT = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40"><defs><radialGradient id="frec-g" cx="60%" cy="35%" r="65%"><stop offset="0%" stop-color="#fff"/><stop offset="60%" stop-color="#C8E8FF"/><stop offset="100%" stop-color="#8ab4d4" stop-opacity="0"/></radialGradient><style>@keyframes ec-p{0%,100%{opacity:.85}50%{opacity:1}}@keyframes ec-s{0%,100%{opacity:0;transform:scale(.5)}50%{opacity:1;transform:scale(1)}}.ec-b{animation:ec-p 2s ease-in-out infinite}.ec-s{animation:ec-s 1.8s ease-in-out infinite;transform-origin:center}</style></defs><path class="ec-b" d="M26,8 A12,12 0 1,1 26,32 A8,8 0 1,0 26,8Z" fill="url(#frec-g)"/><circle class="ec-s" cx="10" cy="12" r="1.5" fill="#fff"/><circle class="ec-s" cx="32" cy="8" r="1" fill="#C8E8FF" style="animation-delay:.6s"/><circle class="ec-s" cx="8" cy="28" r="1.2" fill="#fff" style="animation-delay:1.2s"/></svg>`;
const _SVG_FRAGMENT = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44" width="44" height="44"><defs><radialGradient id="frfr-g" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#6ab4d4"/><stop offset="100%" stop-color="#2a4a6a"/></radialGradient></defs><path d="M14,8 L28,6 L38,16 L36,30 L26,38 L12,36 L6,24 L10,12 Z" fill="url(#frfr-g)"/><line x1="16" y1="10" x2="24" y2="28" stroke="#4FC3F7" stroke-width="1" opacity=".7"/><line x1="20" y1="8" x2="34" y2="22" stroke="#4FC3F7" stroke-width=".8" opacity=".5"/><line x1="10" y1="22" x2="26" y2="30" stroke="#69ccff" stroke-width=".8" opacity=".6"/></svg>`;
const _SVG_GROS = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" width="50" height="50"><defs><radialGradient id="frgr-g" cx="40%" cy="30%" r="70%"><stop offset="0%" stop-color="#7a6aa8"/><stop offset="100%" stop-color="#2a1a4a"/></radialGradient></defs><path d="M12,10 L30,6 L44,18 L42,36 L28,46 L10,40 L4,26 L8,14 Z" fill="url(#frgr-g)"/><polygon points="18,14 22,6 26,14" fill="#a06aff" opacity=".9"/><polygon points="30,20 36,14 38,24" fill="#7a4ade" opacity=".9"/><polygon points="14,28 10,36 20,32" fill="#c88aff" opacity=".8"/></svg>`;
const _SVG_COEUR = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 56 56" width="56" height="56"><defs><radialGradient id="frcl-g" cx="40%" cy="30%" r="70%"><stop offset="0%" stop-color="#fffcaa" stop-opacity=".95"/><stop offset="40%" stop-color="#e8c8f0" stop-opacity=".8"/><stop offset="100%" stop-color="#C8A2C8" stop-opacity=".4"/></radialGradient></defs><circle cx="28" cy="28" r="20" fill="url(#frcl-g)" opacity=".9"/><circle cx="28" cy="28" r="9" fill="#FFD700" opacity=".95"/><line x1="28" y1="4" x2="28" y2="10" stroke="#C8A2C8" stroke-width="2" opacity=".6"/><line x1="28" y1="46" x2="28" y2="52" stroke="#C8A2C8" stroke-width="2" opacity=".6"/><line x1="4" y1="28" x2="10" y2="28" stroke="#C8A2C8" stroke-width="2" opacity=".6"/><line x1="46" y1="28" x2="52" y2="28" stroke="#C8A2C8" stroke-width="2" opacity=".6"/></svg>`;

window.GPS0_Economie_FRAGMENTS = {
  eclat_lune:    { id: 'eclat_lune',    nom: 'Éclat de Lune',   emoji: '🌙', svg: _SVG_ECLAT,    desc: '+10% énergie instantanément', bonus_energie: 10,  prix: 5,  couleur: '#C8A2C8' },
  fragment_lune: { id: 'fragment_lune', nom: 'Fragment Lunaire', emoji: '💧', svg: _SVG_FRAGMENT, desc: '+25% énergie instantanément', bonus_energie: 25,  prix: 15, couleur: '#4FC3F7' },
  gros_fragment: { id: 'gros_fragment', nom: 'Gros Fragment',    emoji: '💎', svg: _SVG_GROS,     desc: '+50% énergie instantanément', bonus_energie: 50,  prix: 30, couleur: '#a06aff' },
  coeur_lune:    { id: 'coeur_lune',    nom: 'Cœur de Lune',    emoji: '✨', svg: _SVG_COEUR,    desc: 'Énergie 100% complète !',    full_recharge: true, prix: 50, couleur: '#FFD700' }
};
