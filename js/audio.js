'use strict';
window.GPS0_Audio = (() => {
  let enabled = localStorage.getItem('gps0_audio_enabled') !== '0';
  let ctx = null, srcActuel = null, piste = 0;
  const pistes = [
    'assets/audio/musique/exploration/musique_menu0.mp3',
    'assets/audio/musique/exploration/musique_menu1.mp3',
    'assets/audio/musique/exploration/musique_menu2.mp3',
    'assets/audio/musique/exploration/musique_menu3.mp3'
  ];
  const sfxMap = {
    boussole_on: 'assets/audio/sfx/boussole_on.mp3',
    boussole_off: 'assets/audio/sfx/boussole_off.mp3',
    zone_detectee: 'assets/audio/sfx/zone_detectee.mp3',
    halo_bip: 'assets/audio/sfx/halo_bip.mp3',
    lune_apparait: 'assets/audio/sfx/lune_apparait.mp3',
    achat: 'assets/audio/sfx/achat.mp3',
    saut_cosmonaute: 'assets/audio/sfx/saut_cosmonaute.mp3',
    collecte_poussiere: 'assets/audio/sfx/collecte_poussiere.mp3',
    ennemi_touche: 'assets/audio/sfx/ennemi_touche.mp3',
    plateforme_active: 'assets/audio/sfx/plateforme_active.mp3',
    laser_warning: 'assets/audio/sfx/laser_warning.mp3',
    boss_hit: 'assets/audio/sfx/boss_hit.mp3'
  };

  function _ctx() { if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)(); return ctx; }

  async function _loadBuf(url) {
    try {
      const r = await fetch(url); if (!r.ok) return null;
      return await _ctx().decodeAudioData(await r.arrayBuffer());
    } catch { return null; }
  }

  async function playMusiqueExploration() {
    if (!enabled) return;
    stopMusique();
    const buf = await _loadBuf(pistes[piste % pistes.length]); if (!buf) return;
    const c = _ctx(), src = c.createBufferSource(), g = c.createGain();
    g.gain.value = 0.4; src.buffer = buf;
    src.connect(g).connect(c.destination);
    src.loop = false; src.onended = () => { piste++; playMusiqueExploration(); };
    src.start(); srcActuel = src;
  }

  function stopMusique() { if (srcActuel) { try { srcActuel.stop(); } catch {} srcActuel = null; } }

  async function playSFX(nom) {
    if (!enabled) return;
    const url = sfxMap[nom]; if (!url) return;
    const buf = await _loadBuf(url); if (!buf) return;
    const c = _ctx(), src = c.createBufferSource(), g = c.createGain();
    g.gain.value = 0.7; src.buffer = buf;
    src.connect(g).connect(c.destination); src.start();
  }

  function toggle() {
    enabled = !enabled;
    localStorage.setItem('gps0_audio_enabled', enabled ? '1' : '0');
    if (!enabled) stopMusique(); else playMusiqueExploration();
    return enabled;
  }

  function isEnabled() { return enabled; }
  return { playMusiqueExploration, stopMusique, playSFX, toggle, isEnabled };
})();
