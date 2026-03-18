'use strict';
window.GPS0_App = (() => {
  let _parcoursId = null;

  async function init() {
    GPS0_Economie.rechargePassive();
    await _splash();
    if (!(await _fullscreen())) await _fullscreenGate();
    await _pseudo();
    await _selfie();
    await _difficulte();
    _parcoursId = await _parcours();
    await _chargerJeu();
    _bindUI();
    _clock();
    GPS0_Economie.updateHUD();
    GPS0_Lune.demarrerSurveillance();
    GPS0_Audio.playMusiqueExploration();
    document.getElementById('app').classList.add('visible');
  }

  function _splash() {
    return new Promise(r => setTimeout(() => { document.getElementById('splash').classList.remove('visible'); r(); }, 2000));
  }

  async function _fullscreen() {
    try { await document.documentElement.requestFullscreen(); return true; } catch { return false; }
  }

  function _fullscreenGate() {
    return new Promise(r => {
      const g = document.getElementById('fullscreen-gate');
      g.classList.add('visible');
      const done = async () => {
        try { await document.documentElement.requestFullscreen(); } catch {}
        g.classList.remove('visible'); r();
      };
      document.getElementById('btn-fullscreen').addEventListener('click', done, { once: true });
      document.getElementById('btn-close-fs').addEventListener('click', done, { once: true });
    });
  }

  function _pseudo() {
    if (localStorage.getItem('gps0_pseudo')) return Promise.resolve();
    const m = document.getElementById('modal-pseudo'); m.showModal();
    return new Promise(r => {
      document.getElementById('form-pseudo').addEventListener('submit', e => {
        e.preventDefault();
        const v = document.getElementById('pseudo-input').value.trim() || 'Explorateur';
        localStorage.setItem('gps0_pseudo', v); m.close(); r();
      }, { once: true });
    });
  }

  async function _selfie() {
    if (GPS0_Avatar.getSelfie()) { GPS0_Avatar.injecterDansJeux(GPS0_Avatar.getSelfie()); return; }
    const m = document.getElementById('modal-selfie'); m.showModal();
    const ok = await GPS0_Avatar.demarrerCamera();
    if (!ok) { m.close(); return; }
    return new Promise(r => {
      let cap = null;
      document.getElementById('selfie-capture').addEventListener('click', () => {
        cap = GPS0_Avatar.capturer();
        document.getElementById('selfie-capture').hidden = true;
        document.getElementById('selfie-retake').hidden = false;
        document.getElementById('selfie-confirm').hidden = false;
        document.getElementById('selfie-video').hidden = true;
      });
      document.getElementById('selfie-retake').addEventListener('click', () => {
        cap = null;
        document.getElementById('selfie-capture').hidden = false;
        document.getElementById('selfie-retake').hidden = true;
        document.getElementById('selfie-confirm').hidden = true;
        document.getElementById('selfie-video').hidden = false;
      });
      const finish = b64 => {
        GPS0_Avatar.arreterCamera(); m.close();
        if (b64) { GPS0_Avatar.setSelfie(b64); GPS0_Avatar.injecterDansJeux(b64); }
        r();
      };
      document.getElementById('selfie-confirm').addEventListener('click', () => finish(cap));
      document.getElementById('selfie-skip').addEventListener('click', () => finish(null));
    });
  }

  function _difficulte() {
    if (localStorage.getItem('gps0_difficulte')) return Promise.resolve();
    const m = document.getElementById('modal-difficulte'); m.showModal();
    let choix = null;
    document.querySelectorAll('.diff-carte').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.diff-carte').forEach(b => b.setAttribute('aria-pressed','false'));
        btn.setAttribute('aria-pressed','true'); choix = btn.dataset.val;
        document.getElementById('diff-suivant').disabled = false;
      });
    });
    return new Promise(r => {
      document.getElementById('diff-suivant').addEventListener('click', () => {
        if (!choix) return;
        localStorage.setItem('gps0_difficulte', choix); m.close(); r();
      }, { once: true });
    });
  }

  function _parcours() {
    const m = document.getElementById('modal-parcours'); m.showModal();
    let choix = null;
    document.querySelectorAll('.parcours-carte').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.parcours-carte').forEach(b => b.setAttribute('aria-pressed','false'));
        btn.setAttribute('aria-pressed','true'); choix = btn.dataset.val;
        document.getElementById('parcours-commencer').disabled = false;
      });
    });
    document.getElementById('btn-code-defi').addEventListener('click', () => {
      const inp = document.getElementById('code-defi-input');
      inp.hidden = !inp.hidden;
    });
    return new Promise(r => {
      document.getElementById('parcours-commencer').addEventListener('click', () => {
        if (!choix) return; m.close(); r(choix);
      }, { once: true });
    });
  }

  async function _chargerJeu() {
    await GPS0_GPS.chargerConfig();
    if (!GPS0_GPS.chargerProgression()) GPS0_GPS.appliquerParcours(_parcoursId);

    const diff = localStorage.getItem('gps0_difficulte') || 'clair_de_lune';
    GPS0_Economie.demarrerConsommation(diff, force => {
      if (typeof force === 'boolean') { GPS0_Boussole.forceEtat(force ? 'on' : 'off'); return; }
      return GPS0_Boussole.estActif();
    });

    // Code défi
    const cm = { parcours_1: 'PP', parcours_2: 'RD', parcours_3: 'MF' };
    const n = new Date();
    const code = 'LUNE-' + (cm[_parcoursId]||'PP') + '-' + String(n.getDate()).padStart(2,'0') + String(n.getMonth()+1).padStart(2,'0') + String(n.getFullYear()).slice(-2) + '-' + String(n.getHours()).padStart(2,'0') + String(n.getMinutes()).padStart(2,'0');
    const toast = document.getElementById('code-toast'), cv = document.getElementById('code-defi-val');
    if (toast && cv) { cv.textContent = code; toast.hidden = false; setTimeout(() => { toast.hidden = true; }, 6000); }

    _majObjectif();
    GPS0_GPS.demarrerSuivi();

    let _navLastDist = null, _navStale = 0, _navLastBear = null, _navDirChg = 0, _navDirTimer = null;
    GPS0_GPS.on('position', d => {
      if (!GPS0_Economie.isEpuise()) GPS0_Boussole.updatePosition(d);
      // Navigation lente : dist change < 5m sur ~2 min
      if (_navLastDist !== null) {
        if (Math.abs(d.dist - _navLastDist) < 5) {
          if (++_navStale >= 12) { GPS0_Lune.parler('navigation_lente'); _navStale = 0; }
        } else { _navStale = 0; }
      }
      _navLastDist = d.dist;
      // Navigation erratique : 8+ changements direction en 1 min
      if (_navLastBear !== null) {
        const diff = Math.abs(d.bearing - _navLastBear);
        if ((diff > 180 ? 360 - diff : diff) > 45) {
          _navDirChg++;
          if (!_navDirTimer) _navDirTimer = setTimeout(() => { _navDirChg = 0; _navDirTimer = null; }, 60000);
          if (_navDirChg >= 8) { GPS0_Lune.parler('navigation_erratique'); _navDirChg = 0; clearTimeout(_navDirTimer); _navDirTimer = null; }
        }
      }
      _navLastBear = d.bearing;
    });
    GPS0_GPS.on('zone_atteinte', zone => {
      GPS0_Lune.parler('arrivee_zone');
      GPS0_Audio.playSFX('zone_detectee');
      GPS0_Boussole.forceEtat('zone');
      GPS0_Economie.ajouterPoussieres(5);
    });
    GPS0_GPS.on('jeu_termine', () => {
      GPS0_Finale && GPS0_Finale.lancer && GPS0_Finale.lancer();
    });
    GPS0_GPS.on('erreur', msg => console.warn('[GPS0] GPS:', msg));

    // Surveiller énergie
    setInterval(() => {
      if (GPS0_Economie.isEpuise()) {
        if (GPS0_Boussole.getEtat() !== 'epuise') {
          GPS0_Boussole.forceEtat('epuise');
          GPS0_Lune.parler('energie_faible');
        }
      } else if (GPS0_Economie.energiePC() < 25) {
        GPS0_Lune.parler('energie_faible');
      }
    }, 10000);
  }

  function _majObjectif() {
    const z = GPS0_GPS.zoneActuelle();
    const ne = document.getElementById('objectif-nom'), pe = document.getElementById('zones-progress');
    if (ne) ne.textContent = z ? z.nom : 'Tous les points visites !';
    if (pe) pe.textContent = GPS0_GPS.progressionStr();
    if (z && z.final) setTimeout(() => GPS0_Lune.parler('avant_boss'), 2000);
  }

  function _bindUI() {
    document.getElementById('toggle-boussole')?.addEventListener('click', () => {
      if (GPS0_Economie.isEpuise()) return;
      GPS0_Boussole.toggle();
      GPS0_Audio.playSFX(GPS0_Boussole.estActif() ? 'boussole_on' : 'boussole_off');
    });

    document.getElementById('btn-jouer')?.addEventListener('click', () => {
      const z = GPS0_GPS.zoneActuelle(); if (z) _lancerMiniJeu(z.mini_jeu);
    });

    const mb = document.getElementById('menu-btn'), mp = document.getElementById('menu-panel');
    mb?.addEventListener('click', () => {
      const h = mp.hidden; mp.hidden = !h; mb.setAttribute('aria-expanded', !h ? 'true' : 'false');
    });

    document.getElementById('menu-audio')?.addEventListener('click', () => {
      const on = GPS0_Audio.toggle();
      document.getElementById('menu-audio').textContent = on ? 'Son' : 'Son coupe';
    });

    document.getElementById('menu-difficulte')?.addEventListener('click', () => {
      mp.hidden = true; mb.setAttribute('aria-expanded', 'false');
      const mdiff = document.getElementById('modal-difficulte');
      const diff = localStorage.getItem('gps0_difficulte');
      if (diff) {
        document.querySelectorAll('.diff-carte').forEach(b => {
          b.setAttribute('aria-pressed', b.dataset.val === diff ? 'true' : 'false');
        });
        document.getElementById('diff-suivant').disabled = false;
      }
      mdiff.showModal();
      document.getElementById('diff-suivant').addEventListener('click', () => {
        const choix = document.querySelector('.diff-carte[aria-pressed="true"]')?.dataset.val;
        if (!choix) return;
        localStorage.setItem('gps0_difficulte', choix);
        GPS0_Economie.demarrerConsommation(choix, force => {
          if (typeof force === 'boolean') { GPS0_Boussole.forceEtat(force ? 'on' : 'off'); return; }
          return GPS0_Boussole.estActif();
        });
        mdiff.close();
      }, { once: true });
    });

    document.getElementById('menu-reset')?.addEventListener('click', () => {
      if (!confirm('Reinitialiser la progression ?')) return;
      ['gps0_zones_actives','gps0_economie','gps0_pseudo','gps0_difficulte','gps0_avatar_selfie_base64','gps0_minijeux_progression'].forEach(k => localStorage.removeItem(k));
      location.reload();
    });

    document.addEventListener('minijeu:complete', e => {
      GPS0_Economie.ajouterPoussieres(e.detail?.poussieres || 10);
      GPS0_GPS.zoneSuivante(); _majObjectif();
      GPS0_Boussole.forceEtat('off');
      document.getElementById('app').classList.add('visible');
    });
    document.addEventListener('minijeu:failed', () => {
      document.getElementById('app').classList.add('visible');
    });
    GPS0_GPS.on('zone_changee', () => _majObjectif());
  }

  function _lancerMiniJeu(niveau) {
    document.getElementById('app').classList.remove('visible');
    const iframe = document.createElement('iframe');
    iframe.src = 'minijeux/niveau' + niveau + '.html';
    iframe.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;border:none;z-index:1000;background:#0A0A1A';
    iframe.setAttribute('title', 'Mini-jeu niveau ' + niveau);
    document.body.appendChild(iframe);
    const handler = e => {
      if (!e.data || e.data.source !== 'gps0_minijeu') return;
      window.removeEventListener('message', handler);
      iframe.remove();
      document.dispatchEvent(new CustomEvent(e.data.success ? 'minijeu:complete' : 'minijeu:failed', { detail: e.data }));
    };
    window.addEventListener('message', handler);
  }

  function _clock() {
    const t0 = Date.now();
    const tick = () => {
      const s = Math.floor((Date.now() - t0) / 1000);
      const el = document.getElementById('chrono');
      if (el) el.textContent = String(Math.floor(s/60)).padStart(2,'0') + ':' + String(s%60).padStart(2,'0');
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  return { init };
})();

window.addEventListener('DOMContentLoaded', () => window.GPS0_App.init());
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('service-worker.js').catch(() => {}));
}
