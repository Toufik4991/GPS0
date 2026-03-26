'use strict';
window.GPS0_GPS = (() => {
  let config = null, zonesActives = [], zoneIndex = 0, watchId = null;
  let _zoneAtteintePending = false; // debounce : n'emet zone_atteinte qu'une fois par zone
  const _l = {};
  function on(e, fn) { (_l[e] = _l[e] || []).push(fn); }
  function emit(e, d) { (_l[e] || []).forEach(fn => fn(d)); }

  // ✅ Haversine vérifié : R=6371000m, degrés→radians, résultat en mètres
  function haversine(la1, ln1, la2, ln2) {
    const R = 6371000, dLa = (la2 - la1) * Math.PI / 180, dLn = (ln2 - ln1) * Math.PI / 180;
    const a = Math.sin(dLa/2)**2 + Math.cos(la1*Math.PI/180) * Math.cos(la2*Math.PI/180) * Math.sin(dLn/2)**2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }
  function bearing(la1, ln1, la2, ln2) {
    const dLn = (ln2 - ln1) * Math.PI / 180, la1r = la1 * Math.PI/180, la2r = la2 * Math.PI/180;
    const y = Math.sin(dLn) * Math.cos(la2r);
    const x = Math.cos(la1r) * Math.sin(la2r) - Math.sin(la1r) * Math.cos(la2r) * Math.cos(dLn);
    return ((Math.atan2(y, x) * 180 / Math.PI) + 360) % 360;
  }

  async function chargerConfig() {
    const res = await fetch('gps_config.json');
    config = await res.json();
    return config;
  }

  // v3.1 : chaque parcours a ses propres zones
  function appliquerParcours(id) {
    const p = config.parcours[id];
    if (!p || !p.zones) { console.error('[GPS0] Parcours inconnu:', id); return []; }
    zonesActives = [...p.zones];
    zoneIndex = 0;
    localStorage.setItem('gps0_zones_actives', JSON.stringify({ zones: zonesActives, index: 0, parcours: id }));
    return zonesActives;
  }

  function chargerProgression() {
    const s = localStorage.getItem('gps0_zones_actives');
    if (!s) return false;
    const d = JSON.parse(s);
    zonesActives = d.zones; zoneIndex = d.index || 0;
    return true;
  }
  function zoneActuelle() { return zonesActives[zoneIndex] || null; }
  function zoneSuivante() {
    _zoneAtteintePending = false; // reset pour la prochaine zone
    _confirmationsZone = 0;       // reset compteur de confirmations
    if (zoneIndex < zonesActives.length - 1) {
      zoneIndex++;
      const s = JSON.parse(localStorage.getItem('gps0_zones_actives'));
      s.index = zoneIndex; localStorage.setItem('gps0_zones_actives', JSON.stringify(s));
      emit('zone_changee', zoneIndex);
      return zonesActives[zoneIndex];
    }
    emit('jeu_termine', null);
    return null;
  }
  function progressionStr() { return (zoneIndex + 1) + '/' + zonesActives.length; }
  function nomParcours(id) {
    if (!config) return '';
    const pid = id || (JSON.parse(localStorage.getItem('gps0_zones_actives') || '{}').parcours);
    return (pid && config.parcours[pid] && config.parcours[pid].nom) || '';
  }

  // Qualité GPS : compteur de confirmations consécutives dans la zone
  let _confirmationsZone = 0;
  const CONFIRMATIONS_REQUISES = 3; // 3 lectures consécutives dans la zone pour valider
  const PRECISION_MAX = 25;         // ignorer les positions avec accuracy > 25m

  function demarrerSuivi() {
    if (!navigator.geolocation) { emit('erreur', 'GPS non disponible sur cet appareil'); return; }
    watchId = navigator.geolocation.watchPosition(pos => {
      const zone = zoneActuelle(); if (!zone) return;
      // Zone placeholder (coords 0,0) : ignorer
      if (zone.lat === 0 && zone.lng === 0) { emit('position', { lat: 0, lng: 0, dist: 9999, bearing: 0, zone }); return; }
      // Filtre qualité : ignorer si précision GPS trop faible
      const accuracy = pos.coords.accuracy;
      if (accuracy > PRECISION_MAX) {
        emit('position_imprecise', { accuracy });
        return;
      }
      const dist = Math.round(haversine(pos.coords.latitude, pos.coords.longitude, zone.lat, zone.lng));
      const bear = bearing(pos.coords.latitude, pos.coords.longitude, zone.lat, zone.lng);
      const spd = pos.coords.speed;
      emit('position', { lat: pos.coords.latitude, lng: pos.coords.longitude, dist, bearing: bear, zone, speed: spd, accuracy });
      if (dist <= (zone.rayon || 30)) {
        _confirmationsZone++;
        // Valider la zone seulement après N lectures consécutives dans le rayon
        if (!_zoneAtteintePending && _confirmationsZone >= CONFIRMATIONS_REQUISES) {
          _zoneAtteintePending = true;
          emit('zone_atteinte', zone);
        }
      } else {
        _confirmationsZone = 0; // reset si on sort de la zone
        _zoneAtteintePending = false;
      }
    }, err => emit('erreur', err.message), { enableHighAccuracy: true, maximumAge: 0, timeout: 10000 });
  }
  function arreterSuivi() { if (watchId !== null) { navigator.geolocation.clearWatch(watchId); watchId = null; } }

  return { chargerConfig, appliquerParcours, chargerProgression, zoneActuelle, zoneSuivante, progressionStr, nomParcours, demarrerSuivi, arreterSuivi, on };
})();
