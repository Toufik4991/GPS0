'use strict';
window.GPS0_Boussole = (() => {
  let etat = 'off';
  const _l = {};
  function on(e, fn) { (_l[e] = _l[e] || []).push(fn); }
  function emit(e, d) { (_l[e] || []).forEach(fn => fn(d)); }

  function toggle() {
    if (etat === 'epuise') return;
    _setEtat(etat === 'off' ? 'on' : 'off');
  }
  function forceEtat(e) { _setEtat(e); }

  function _setEtat(nouvel) {
    etat = nouvel; _render(); emit('etat', etat);
  }

  function updatePosition({ dist, bearing, zone }) {
    const rayon = zone.rayon || 30;
    if (dist <= rayon) { _setEtat('zone'); return; }
    if (etat === 'off' || etat === 'epuise') return;
    _halo(dist); _fusee(bearing); _distance(dist);
  }

  function _halo(dist) {
    const h = document.getElementById('halo'); if (!h) return;
    if (dist > 151) h.dataset.etat = 'rouge';
    else if (dist > 80) h.dataset.etat = 'orange';
    else if (dist > 30) h.dataset.etat = 'vert';
    else h.dataset.etat = 'bleu';
  }
  function _fusee(bear) {
    const f = document.getElementById('fusee-wrapper');
    if (f) f.style.transform = `rotate(${bear}deg)`;
  }
  // Pas d'affichage de distance en chiffres (design GPS0 v3.2)
  function _distance() {}

  function _render() {
    const w = document.getElementById('asteroide-wrapper');
    const f = document.getElementById('fusee-wrapper');
    const t = document.getElementById('toggle-boussole');
    const tl = t ? t.querySelector('.toggle-label') : null;
    const h = document.getElementById('halo');
    const dl = document.getElementById('distance-label');
    const bj = document.getElementById('btn-jouer');
    if (!w) return;
    w.dataset.etat = etat;
    switch (etat) {
      case 'off':
        f && f.classList.add('hidden');
        h && (h.dataset.etat = 'off');
        dl && (dl.textContent = '---');
        tl && (tl.textContent = 'Activer la boussole');
        t && (t.dataset.active = 'false', t.dataset.epuise = 'false');
        bj && (bj.hidden = true);
        break;
      case 'on':
        f && f.classList.remove('hidden');
        tl && (tl.textContent = 'Désactiver la boussole');
        t && (t.dataset.active = 'true', t.dataset.epuise = 'false');
        bj && (bj.hidden = true);
        break;
      case 'epuise':
        f && f.classList.add('hidden');
        h && (h.dataset.etat = 'off');
        dl && (dl.textContent = 'Recharge ta boussole !');
        tl && (tl.textContent = 'Boussole épuisée ⚡');
        t && (t.dataset.active = 'false', t.dataset.epuise = 'true');
        bj && (bj.hidden = true);
        break;
      case 'zone':
        f && f.classList.remove('hidden');
        h && (h.dataset.etat = 'bleu');
        dl && (dl.textContent = 'Zone atteinte ! ✅');
        tl && (tl.textContent = 'Zone détectée 🎯');
        bj && (bj.hidden = false);
        emit('zone_active', null);
        break;
    }
  }

  function estActif() { return etat === 'on'; }
  function getEtat() { return etat; }
  return { toggle, forceEtat, updatePosition, estActif, getEtat, on };
})();
