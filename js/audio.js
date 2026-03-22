'use strict';
window.GPS0_Audio = (() => {
  let enabled = localStorage.getItem('gps0_audio_enabled') !== '0';
  let ctx = null, srcActuel = null, piste = 0;
  const pistes = [
    'assets/audio/musique/exploration/musique_menu0.mp3',
    'assets/audio/musique/exploration/musique_menu1.mp3',
    'assets/audio/musique/exploration/musique_menu2.mp3',
    'assets/audio/musique/exploration/musique_menu3.mp3',
    'assets/audio/musique/exploration/musique_menu4.mp3'
  ];
  const sfxMap = {
    boussole_on:         'assets/audio/sfx/boussole_on.mp3',
    boussole_off:        'assets/audio/sfx/boussole_off.mp3',
    zone_detectee:       'assets/audio/sfx/zone_detectee.mp3',
    halo_bip:            'assets/audio/sfx/halo_bip.mp3',
    lune_apparait:       'assets/audio/sfx/lune_apparait.mp3',
    achat:               'assets/audio/sfx/achat.mp3',
    saut_cosmonaute:     'assets/audio/sfx/saut_cosmonaute.mp3',
    collecte_poussiere:  'assets/audio/sfx/collecte_poussiere.mp3',
    ennemi_touche:       'assets/audio/sfx/ennemi_touche.mp3',
    plateforme_active:   'assets/audio/sfx/plateforme_active.mp3',
    laser_warning:       'assets/audio/sfx/laser_warning.mp3',
    boss_hit:            'assets/audio/sfx/boss_hit.mp3'
  };

  /* ── Sons synthétisés (zéro fichier, Web Audio pur) ── */
  const synthSFX = {
    tap(c) {
      const o = c.createOscillator(), g = c.createGain();
      o.type = 'sine'; o.frequency.value = 880;
      g.gain.setValueAtTime(0.3, c.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.08);
      o.connect(g).connect(c.destination); o.start(); o.stop(c.currentTime + 0.08);
    },
    perte_vie(c) {
      const o = c.createOscillator(), g = c.createGain();
      o.type = 'sawtooth'; o.frequency.setValueAtTime(440, c.currentTime);
      o.frequency.exponentialRampToValueAtTime(110, c.currentTime + 0.35);
      g.gain.setValueAtTime(0.35, c.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.4);
      o.connect(g).connect(c.destination); o.start(); o.stop(c.currentTime + 0.4);
    },
    victoire(c) {
      [523, 659, 784, 1047].forEach((f, i) => {
        const o = c.createOscillator(), g = c.createGain();
        o.type = 'sine'; o.frequency.value = f;
        const t = c.currentTime + i * 0.12;
        g.gain.setValueAtTime(0.25, t);
        g.gain.exponentialRampToValueAtTime(0.001, t + 0.25);
        o.connect(g).connect(c.destination); o.start(t); o.stop(t + 0.25);
      });
    },
    defaite(c) {
      [392, 330, 262, 196].forEach((f, i) => {
        const o = c.createOscillator(), g = c.createGain();
        o.type = 'triangle'; o.frequency.value = f;
        const t = c.currentTime + i * 0.18;
        g.gain.setValueAtTime(0.3, t);
        g.gain.exponentialRampToValueAtTime(0.001, t + 0.3);
        o.connect(g).connect(c.destination); o.start(t); o.stop(t + 0.3);
      });
    },
    countdown(c) {
      const o = c.createOscillator(), g = c.createGain();
      o.type = 'square'; o.frequency.value = 660;
      g.gain.setValueAtTime(0.2, c.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.12);
      o.connect(g).connect(c.destination); o.start(); o.stop(c.currentTime + 0.12);
    },
    countdown_go(c) {
      [660, 880, 1100].forEach((f, i) => {
        const o = c.createOscillator(), g = c.createGain();
        o.type = 'square'; o.frequency.value = f;
        const t = c.currentTime + i * 0.06;
        g.gain.setValueAtTime(0.25, t);
        g.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
        o.connect(g).connect(c.destination); o.start(t); o.stop(t + 0.15);
      });
    },
    confetti(c) {
      for (let i = 0; i < 8; i++) {
        const o = c.createOscillator(), g = c.createGain();
        o.type = 'sine'; o.frequency.value = 800 + Math.random() * 1200;
        const t = c.currentTime + i * 0.07;
        g.gain.setValueAtTime(0.15, t);
        g.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
        o.connect(g).connect(c.destination); o.start(t); o.stop(t + 0.2);
      }
    },
    boss_ambiance(c) {
      const o = c.createOscillator(), g = c.createGain();
      o.type = 'sawtooth'; o.frequency.value = 55;
      o.frequency.linearRampToValueAtTime(80, c.currentTime + 1.5);
      g.gain.setValueAtTime(0.18, c.currentTime);
      g.gain.linearRampToValueAtTime(0.08, c.currentTime + 1.5);
      g.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 2);
      o.connect(g).connect(c.destination); o.start(); o.stop(c.currentTime + 2);
    }
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
    const c = _ctx();
    if (c.state === 'suspended') { try { await c.resume(); } catch {} }
    const buf = await _loadBuf(pistes[piste % pistes.length]);
    if (!buf) { piste++; setTimeout(playMusiqueExploration, 100); return; }
    const src = c.createBufferSource(), g = c.createGain();
    g.gain.value = 0.4; src.buffer = buf;
    src.connect(g).connect(c.destination);
    src.loop = false; src.onended = () => { piste++; playMusiqueExploration(); };
    src.start(); srcActuel = src;
  }

  async function playMusiqueFinale() {
    if (!enabled) return;
    stopMusique();
    const c = _ctx();
    if (c.state === 'suspended') { try { await c.resume(); } catch {} }
    const buf = await _loadBuf('assets/audio/musique/finale/musique_finale.mp3'); if (!buf) return;
    const src = c.createBufferSource(), g = c.createGain();
    g.gain.value = 0.55; src.buffer = buf;
    src.connect(g).connect(c.destination);
    src.loop = false; src.start(); srcActuel = src;
  }

  function stopMusique() { if (srcActuel) { try { srcActuel.stop(); } catch {} srcActuel = null; } }

  async function playSFX(nom) {
    if (!enabled) return;
    const c = _ctx();
    if (c.state === 'suspended') { try { await c.resume(); } catch {} }
    // Sons synthétisés (priorité)
    if (synthSFX[nom]) { synthSFX[nom](c); return; }
    // Sons fichier mp3
    const url = sfxMap[nom]; if (!url) return;
    const buf = await _loadBuf(url); if (!buf) return;
    const src = c.createBufferSource(), g = c.createGain();
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
  return { playMusiqueExploration, playMusiqueFinale, stopMusique, playSFX, toggle, isEnabled };
})();
