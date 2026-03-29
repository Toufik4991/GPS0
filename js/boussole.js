'use strict';
window.GPS0_Boussole = (() => {
  let etat = 'off';
  let _deviceHeading = null; // heading téléphone en degrés depuis le Nord magnétique (null = inconnu)
  const _headingBuf = []; // tampon de lissage (moyenne circulaire sur 5 valeurs)
  const _HEADING_SMOOTH = 5;
  function _circularMean(arr) {
    let sx = 0, sy = 0;
    arr.forEach(a => { sx += Math.cos(a * Math.PI / 180); sy += Math.sin(a * Math.PI / 180); });
    return (Math.atan2(sy / arr.length, sx / arr.length) * 180 / Math.PI + 360) % 360;
  }
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
    if (dist <= rayon) {
      // Ne setter 'zone' que si on n'y est pas déjà (évite le spam de _render)
      if (etat !== 'zone') _setEtat('zone');
      return;
    }
    if (etat === 'off' || etat === 'epuise') return;
    _halo(dist); _fusee(bearing); _distance(dist);
  }

  function _halo(dist) {
    const h = document.getElementById('halo'); if (!h) return;
    const w = document.getElementById('asteroide-wrapper');
    let zone;
    if (dist > 100)      { zone = 'rouge';  h.dataset.etat = 'rouge'; }
    else if (dist > 50)  { zone = 'orange'; h.dataset.etat = 'orange'; }
    else if (dist > 10)  { zone = 'vert';   h.dataset.etat = 'vert'; }
    else                 { zone = 'bleu';   h.dataset.etat = 'bleu'; }
    if (w) w.dataset.zone = zone;
  }
  function _fusee(bear) {
    const f = document.getElementById('fusee-wrapper');
    if (!f) return;
    // Bearing relatif = bearing géographique − heading du téléphone
    // Formule : si heading=0 (pointe nord), bear=90 → affiche 90° (droite) ✓
    //           si heading=90 (pointe est), bear=90 → affiche 0° (haut = droit devant) ✓
    const h = _deviceHeading !== null ? _deviceHeading : 0;
    const rel = ((bear - h) + 360) % 360;
    f.style.transform = `rotate(${rel}deg)`;
  }
  function setDeviceHeading(h) {
    _headingBuf.push(h);
    if (_headingBuf.length > _HEADING_SMOOTH) _headingBuf.shift();
    _deviceHeading = _circularMean(_headingBuf);
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
        if (w) { delete w.dataset.zone; }
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
        if (w) { delete w.dataset.zone; }
        tl && (tl.textContent = 'Boussole épuisée ⚡');
        t && (t.dataset.active = 'false', t.dataset.epuise = 'true');
        bj && (bj.hidden = true);
        break;
      case 'zone':
        f && f.classList.remove('hidden');
        h && (h.dataset.etat = 'bleu');
        tl && (tl.textContent = 'Zone détectée 🎯');
        bj && (bj.hidden = false);
        emit('zone_active', null);
        break;
    }
  }

  function estActif() { return etat === 'on'; }
  function getEtat() { return etat; }
  return { toggle, forceEtat, updatePosition, estActif, getEtat, on, setDeviceHeading };
})();
