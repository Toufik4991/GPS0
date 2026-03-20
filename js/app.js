'use strict';
window.GPS0_App = (() => {
  let _parcoursId = null;

  async function init() {
    GPS0_Economie.rechargePassive();
    await _splash();
    if (!(await _fullscreen())) await _fullscreenGate();
    await _requestPermissions();
    await _pseudo();
    await _selfie();
    await _tuto();
    _parcoursId = await _parcours();
    await _difficulte();
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

  function _requestPermissions() {
    if (localStorage.getItem('gps0_perms_asked')) return Promise.resolve();
    const m = document.getElementById('modal-permissions');
    if (!m) return Promise.resolve();
    m.showModal();
    const _doRequest = async () => {
      // GPS : simple getCurrentPosition pour déclencher la demande native
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(() => {}, () => {}, { timeout: 3000 });
      }
      // Caméra : ouvrir puis fermer immédiatement pour obtenir la permission
      try {
        const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
        s.getTracks().forEach(t => t.stop());
      } catch (e) { /* ignoré — l'utilisateur a refusé ou pas de caméra */ }
      localStorage.setItem('gps0_perms_asked', '1');
      m.close();
    };
    return new Promise(r => {
      document.getElementById('perm-accepter').addEventListener('click', () => { _doRequest().then(r); }, { once: true });
      document.getElementById('perm-passer').addEventListener('click', () => { localStorage.setItem('gps0_perms_asked', '1'); m.close(); r(); }, { once: true });
    });
  }

  async function _fullscreen() {
    const el = document.documentElement;
    const req = el.requestFullscreen || el.webkitRequestFullscreen || el.mozRequestFullScreen;
    if (!req) return false;
    try { await req.call(el); return true; } catch { return false; }
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
    if (!ok) {
      document.getElementById('selfie-capture').hidden = true;
      const errEl = document.createElement('p');
      errEl.style.cssText = 'color:#FF6B6B;font-size:0.85rem;text-align:center;margin:8px 0';
      errEl.textContent = 'Camera indisponible. Clique sur Passer pour continuer.';
      m.querySelector('.selfie-actions').insertAdjacentElement('beforebegin', errEl);
    }
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
    const CODE_MAP = { PP: 'parcours_1', RD: 'parcours_2', MF: 'parcours_3' };

    function _selectionnerParcours(id) {
      document.querySelectorAll('.parcours-carte').forEach(b => {
        b.setAttribute('aria-pressed', b.dataset.val === id ? 'true' : 'false');
      });
      choix = id;
      document.getElementById('parcours-commencer').disabled = false;
    }

    document.querySelectorAll('.parcours-carte').forEach(btn => {
      btn.addEventListener('click', () => {
        _selectionnerParcours(btn.dataset.val);
        // Si code defi etait entre, le vider pour eviter confusion
        const inp = document.getElementById('code-defi-input');
        const err = document.getElementById('code-defi-err');
        if (inp) inp.value = '';
        if (err) err.textContent = '';
      });
    });

    // Code defi : afficher/masquer
    document.getElementById('btn-code-defi').addEventListener('click', () => {
      const form = document.getElementById('code-defi-form');
      if (form) form.hidden = !form.hidden;
    });

    // Code defi : parser en temps reel
    const codeInput = document.getElementById('code-defi-input');
    const codeErr = document.getElementById('code-defi-err');
    if (codeInput) {
      codeInput.addEventListener('input', function() {
        const val = this.value.trim().toUpperCase();
        const match = val.match(/^LUNE-(PP|RD|MF)-\d{6}-\d{4}$/);
        if (match) {
          const id = CODE_MAP[match[1]];
          _selectionnerParcours(id);
          if (codeErr) { codeErr.textContent = '✅ Code valide ! Parcours chargé.'; codeErr.style.color = '#69FF47'; }
          localStorage.setItem('gps0_code_defi_entre', val);
        } else if (val.length > 5) {
          if (codeErr) { codeErr.textContent = 'Format : LUNE-PP-180326-1430'; codeErr.style.color = '#FF6B6B'; }
        } else {
          if (codeErr) codeErr.textContent = '';
        }
      });
    }

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
      GPS0_Audio.playSFX('halo_bip');
      GPS0_Boussole.forceEtat('zone');
      // Auto-lancement du mini-jeu apres un court delai d'annonce
      if (zone && zone.mini_jeu) {
        setTimeout(() => {
          // Verifier que le joueur est toujours dans la zone (pas sorti entretemps)
          if (GPS0_Boussole.getEtat() === 'zone') _lancerMiniJeu(zone.mini_jeu);
        }, 2500);
      }
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
    // toggle-boussole button hidden — tout passe par l'astéroïde

    // Astéroïde : toggle boussole (off/on) OU lancement mini-jeu (zone)
    document.getElementById('asteroide-wrapper')?.addEventListener('click', () => {
      const w = document.getElementById('asteroide-wrapper');
      if (!w) return;
      const etat = w.dataset.etat;
      const svg = w.querySelector('.asteroide-svg');
      const flash = () => { if (svg) { svg.classList.add('flash'); setTimeout(() => svg.classList.remove('flash'), 420); } };

      if (etat === 'zone') {
        flash();
        const z = GPS0_GPS.zoneActuelle(); if (z) _lancerMiniJeu(z.mini_jeu);
        return;
      }
      if (etat === 'epuise') {
        GPS0_Lune.parler('energie_faible');
        return;
      }
      // Toggle boussole on/off
      if (GPS0_Economie.isEpuise()) return;
      flash();
      GPS0_Boussole.toggle();
      GPS0_Audio.playSFX(GPS0_Boussole.estActif() ? 'boussole_on' : 'boussole_off');
    });

    const mb = document.getElementById('menu-btn'), mp = document.getElementById('menu-panel');
    mb?.addEventListener('click', () => {
      const h = mp.hidden; mp.hidden = !h; mb.setAttribute('aria-expanded', !h ? 'true' : 'false');
    });

    document.getElementById('menu-audio')?.addEventListener('click', () => {
      mp.hidden = true; mb.setAttribute('aria-expanded', 'false');
      const on = GPS0_Audio.toggle();
      document.getElementById('menu-audio').textContent = on ? '🔊 Son' : '🔇 Son OFF';
    });

    document.getElementById('menu-difficulte')?.addEventListener('click', () => {
      mp.hidden = true; mb.setAttribute('aria-expanded', 'false');
      const diff = localStorage.getItem('gps0_difficulte');
      const _noms = { clair_de_lune: '\u{1F315} Clair de Lune', face_cachee: '\u{1F317} Face Cach\u00e9e', eclipse_totale: '\u{1F311} \u00c9clipse Totale', trou_noir: '\u{1F573}\uFE0F Trou Noir' };
      const actuel = _noms[diff] || diff || '?';
      const modal = document.getElementById('modal-confirm-diff');
      const texte = document.getElementById('confirm-diff-texte');
      if (texte) texte.textContent = 'Difficult\u00e9 actuelle : ' + actuel + '.';
      if (modal) {
        modal.showModal();
        document.getElementById('confirm-diff-oui').onclick = () => {
          modal.close();
          ['gps0_zones_actives','gps0_economie','gps0_difficulte','gps0_minijeux_progression'].forEach(k => localStorage.removeItem(k));
          location.reload();
        };
        document.getElementById('confirm-diff-non').onclick = () => modal.close();
      }
    });

    document.getElementById('menu-reset')?.addEventListener('click', () => {
      mp.hidden = true; mb.setAttribute('aria-expanded', 'false');
      if (!confirm('Reinitialiser la progression ?')) return;
      ['gps0_zones_actives','gps0_economie','gps0_pseudo','gps0_difficulte','gps0_avatar_selfie_base64','gps0_minijeux_progression'].forEach(k => localStorage.removeItem(k));
      location.reload();
    });

    document.getElementById('menu-demo')?.addEventListener('click', () => {
      mp.hidden = true; mb.setAttribute('aria-expanded', 'false');
      const mdp = prompt('🔒 Mot de passe debug :');
      if (mdp !== 'jules') { if (mdp !== null) alert('Mot de passe incorrect.'); return; }
      document.getElementById('modal-demo').showModal();
    });
    document.querySelectorAll('.demo-niveau-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.getElementById('modal-demo').close();
        _lancerMiniJeu(parseInt(btn.dataset.niveau));
      });
    });
    document.getElementById('demo-fermer')?.addEventListener('click', () => {
      document.getElementById('modal-demo').close();
    });


    document.getElementById('boutique-fermer')?.addEventListener('click', () => {
      document.getElementById('modal-boutique').close();
    });
    // HUD boutique + inventaire
    // Menu : toggle strict — PAS de fermeture automatique au clic extérieur
    document.getElementById('hud-boutique')?.addEventListener('click', () => _ouvrirBoutique());
    document.getElementById('hud-inventaire')?.addEventListener('click', () => _ouvrirInventaire());
    document.getElementById('inventaire-fermer')?.addEventListener('click', () => {
      document.getElementById('modal-inventaire').close();
    });

    document.addEventListener('minijeu:complete', e => {
      GPS0_Economie.ajouterPoussieres(e.detail?.poussieres || 10);
      if (typeof GPS0_Economie.setCooldown === 'function') GPS0_Economie.setCooldown(e.detail?.niveau || 0);
      GPS0_GPS.zoneSuivante(); _majObjectif();
      GPS0_Boussole.forceEtat('off');
      document.getElementById('app').classList.add('visible');
    });
    document.addEventListener('minijeu:failed', () => {
      document.getElementById('app').classList.add('visible');
    });
    GPS0_GPS.on('zone_changee', () => _majObjectif());
  }

  function _ouvrirInventaire() {
    const modal = document.getElementById('modal-inventaire');
    if (!modal) return;
    const eco = GPS0_Economie.get();
    const pc = GPS0_Economie.energiePC();
    const elP = document.getElementById('inv-poussieres');
    const elE = document.getElementById('inv-energie');
    const elF = document.getElementById('inv-fragments');
    if (elP) elP.textContent = eco.poussieres;
    if (elE) elE.textContent = Math.round(eco.energie.actuelle) + '/' + eco.energie.max;
    if (elF) {
      elF.innerHTML = '';
      const catalog = window.GPS0_Economie_FRAGMENTS || {};
      Object.values(catalog).forEach(fr => {
        const qty = (eco.fragments && eco.fragments[fr.id]) || 0;
        const row = document.createElement('div');
        row.className = 'inv-fragment-row';
        const useBtn = document.createElement('button');
        useBtn.className = 'inv-frag-use';
        useBtn.textContent = 'Utiliser';
        useBtn.disabled = qty <= 0;
        useBtn.onclick = () => {
          if (GPS0_Economie.utiliserFragment(fr.id)) {
            GPS0_Economie.updateHUD();
            _ouvrirInventaire();
          }
        };
        row.innerHTML = '<span class="inv-frag-icone">' + (fr.emoji||'🌙') + '</span>'
          + '<span class="inv-frag-infos"><span class="inv-frag-nom">' + fr.nom + '</span>'
          + '<span class="inv-frag-qty">x' + qty + (qty === 0 ? ' — vide' : '') + '</span></span>';
        row.appendChild(useBtn);
        elF.appendChild(row);
      });
    }
    modal.showModal();
  }


  function _lancerMiniJeu(niveau) {
    if (typeof GPS0_Economie !== 'undefined' && typeof GPS0_Economie.isCooldown === 'function' && GPS0_Economie.isCooldown(niveau)) {
      const r = GPS0_Economie.getCooldownRestant(niveau);
      const dl = document.getElementById('distance-label');
      if (dl) { dl.textContent = '⏳ Cooldown: ' + GPS0_Economie.formatCooldown(r); setTimeout(() => { dl.textContent = '---'; }, 4000); }
      return;
    }
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

  function _ouvrirBoutique() {
    const modal = document.getElementById('modal-boutique');
    if (!modal) return;
    const container = document.getElementById('boutique-fragments');
    const soldeEl = document.getElementById('boutique-solde');
    if (!container) return;
    const _frCat = window.GPS0_Economie_FRAGMENTS || {};
    const frags = Object.values(_frCat);
    const poussieres = (typeof GPS0_Economie !== 'undefined' && typeof GPS0_Economie.get === 'function') ? GPS0_Economie.get().poussieres : 0;
    if (soldeEl) soldeEl.textContent = poussieres + ' ✨';
    container.innerHTML = '';
    frags.forEach(fr => {
      const btn = document.createElement('button');
      btn.className = 'fragment-carte';
      btn.disabled = poussieres < fr.prix;
            btn.innerHTML = '<span class="fragment-icone">' + (fr.emoji||'🌟') + '</span><span class="fragment-infos"><span class="fragment-nom">' + fr.nom + '</span><span class="fragment-desc">' + fr.desc + '</span></span><span class="fragment-prix">' + fr.prix + ' ✨</span><span class="fragment-acheter">ACHETER</span>';
      btn.onclick = () => {
        if (typeof GPS0_Economie !== 'undefined' && typeof GPS0_Economie.acheterFragment === 'function') {
          const ok = GPS0_Economie.acheterFragment(fr.id, fr.prix);
          if (ok) { GPS0_Audio.playSFX('achat'); GPS0_Economie.updateHUD(); modal.close(); }
          else { btn.classList.add('erreur'); setTimeout(() => btn.classList.remove('erreur'), 800); }
        }
      };
      container.appendChild(btn);
    });
    modal.showModal();
  }

  function _tuto() {
    if (localStorage.getItem('gps0_tuto_vu')) return Promise.resolve();
    const m = document.getElementById('modal-tuto'); if (!m) return Promise.resolve();
    m.showModal();

    let currentStep = 0;
    const totalSteps = 4;
    const steps = m.querySelectorAll('.intro-step');
    const dots = m.querySelectorAll('.intro-dot');
    const prevBtn = document.getElementById('intro-prev');
    const nextBtn = document.getElementById('intro-next');

    function gotoStep(n) {
      steps.forEach((s, i) => s.classList.toggle('active', i === n));
      dots.forEach((d, i) => d.classList.toggle('active', i === n));
      prevBtn.disabled = n === 0;
      nextBtn.textContent = n === totalSteps - 1 ? 'C\u2019est parti ! \uD83D\uDE80' : 'Suivant \u2192';
    }

    return new Promise(r => {
      prevBtn.addEventListener('click', () => { if (currentStep > 0) gotoStep(--currentStep); });
      nextBtn.addEventListener('click', () => {
        if (currentStep < totalSteps - 1) { gotoStep(++currentStep); }
        else { localStorage.setItem('gps0_tuto_vu', '1'); m.close(); r(); }
      });
    });
  }

  return { init };
})();

window.addEventListener('DOMContentLoaded', () => window.GPS0_App.init());
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('service-worker.js').then(reg => {
      reg.addEventListener('updatefound', () => {
        // Mise à jour silencieuse — pas de toast visible
        const nw = reg.installing;
        if (nw) nw.addEventListener('statechange', () => { /* silent update */ });
      });
    }).catch(() => {});
    if (navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage('GET_VERSION');
      navigator.serviceWorker.addEventListener('message', ev => {
        if (ev.data?.type === 'VERSION') {
          const el = document.getElementById('debug-version');
          if (el) el.textContent = 'v' + ev.data.version;
        }
      });
    }
  });
}
