'use strict';
window.GPS0_App = (() => {
  let _parcoursId = null;
  let _zoneAutoTimer = null;

  async function init() {
    GPS0_Economie.rechargePassive();
    await _splash();
    _fixCosmosFloating(); // Bug 3 : SVG flottants hors zone boussole
    await _requestPermissions();
    await _pseudo();
    await _selfie();
    _parcoursId = await _parcours();
    await _difficulte();
    await _chargerJeu();
    _bindUI();
    GPS0_Economie.updateHUD();
    GPS0_Lune.demarrerSurveillance();
    document.getElementById('app').classList.add('visible');
  }

  function _fixCosmosFloating() {
    // Repositionne les SVG flottants si trop proches du centre (zone boussole) — 250px minimum
    setTimeout(() => {
      const cx = window.innerWidth / 2, cy = window.innerHeight / 2;
      const MIN_DIST = 250;
      document.querySelectorAll('.cf').forEach(el => {
        for (let attempt = 0; attempt < 12; attempt++) {
          const r = el.getBoundingClientRect();
          const ecx = r.left + r.width / 2, ecy = r.top + r.height / 2;
          const dx = ecx - cx, dy = ecy - cy;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist >= MIN_DIST) break;
          if (dist > 2) {
            const angle = Math.atan2(dy, dx);
            const push = MIN_DIST - dist + 30;
            el.style.transform = (el.style.transform || '') + ' translate(' + Math.round(Math.cos(angle) * push) + 'px,' + Math.round(Math.sin(angle) * push) + 'px)';
          } else {
            const angle = Math.random() * Math.PI * 2;
            el.style.transform = 'translate(' + Math.round(Math.cos(angle) * MIN_DIST) + 'px,' + Math.round(Math.sin(angle) * MIN_DIST) + 'px)';
          }
        }
      });
    }, 200);
  }

  function _splash() {
    return new Promise(r => {
      const splash = document.getElementById('splash');
      const btn = document.createElement('button');
      btn.id = 'btn-splash-start';
      btn.className = 'btn-primary';
      btn.textContent = 'Commencer l’aventure 🚀';
      splash.querySelector('.splash-content').appendChild(btn);
      btn.addEventListener('click', async () => {
        try { await document.documentElement.requestFullscreen(); } catch {}
        // Demander la permission orientation (iOS 13+ exige un geste utilisateur)
        try {
          if (typeof DeviceOrientationEvent !== 'undefined' &&
              typeof DeviceOrientationEvent.requestPermission === 'function') {
            await DeviceOrientationEvent.requestPermission();
          }
        } catch {}
        GPS0_Audio.playMusiqueExploration();
        splash.style.opacity = '0';
        setTimeout(() => { splash.classList.remove('visible'); splash.style.opacity = ''; r(); }, 650);
      }, { once: true });
    });
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
    // Affiche le pseudo dans l’objectif-nom dès qu’il est connu
    function _afficherPseudo() {
      const p = localStorage.getItem('gps0_pseudo');
      if (p) {
        const el = document.getElementById('objectif-sub');
        if (el) el.textContent = '\uD83D\uDC64 ' + p;
      }
    }
    if (localStorage.getItem('gps0_pseudo')) { _afficherPseudo(); return Promise.resolve(); }
    const m = document.getElementById('modal-pseudo'); m.showModal();
    return new Promise(r => {
      document.getElementById('form-pseudo').addEventListener('submit', e => {
        e.preventDefault();
        const v = document.getElementById('pseudo-input').value.trim() || 'Explorateur';
        localStorage.setItem('gps0_pseudo', v); _afficherPseudo(); m.close(); r();
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
    _startGlobalClock();

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
      _pauseGlobalClock(); // Zone bleue : horloge en pause
      // Afficher boutons JOUER + POINT SUIVANT côte à côte
      const wb = document.getElementById('zone-btns');
      if (wb) wb.hidden = false;
    });
    GPS0_GPS.on('jeu_termine', () => {
      // La finale est déclenchée via le bouton 'Finir l'aventure' dans _afficherResultats
      // (uniquement au point GPS 9 avec final:true) — ne pas lancer ici
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
        // Zone bleue : seul le bouton JOUER lance le mini-jeu — pas l'astéroïde
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

    // Bouton JOUER en haut (zone atteinte)
    document.getElementById('btn-jouer-haut')?.addEventListener('click', () => {
      if (_zoneAutoTimer) { clearTimeout(_zoneAutoTimer); _zoneAutoTimer = null; }
      const wb = document.getElementById('zone-btns');
      if (wb) wb.hidden = true;
      const z = GPS0_GPS.zoneActuelle();
      if (z) _lancerMiniJeu(z.mini_jeu);
    });

    // Bouton POINT SUIVANT (zone atteinte, sans jouer)
    document.getElementById('btn-prochain-point')?.addEventListener('click', () => {
      const wb = document.getElementById('zone-btns');
      if (wb) wb.hidden = true;
      GPS0_GPS.zoneSuivante(); _majObjectif();
      GPS0_Boussole.forceEtat('off');
      _resumeGlobalClock();
    });

    const mb = document.getElementById('menu-btn'), mp = document.getElementById('menu-panel');
    mb?.addEventListener('click', () => {
      const isOpen = mp.classList.toggle('open');
      mb.setAttribute('aria-expanded', String(isOpen));
    });

    document.getElementById('menu-audio')?.addEventListener('click', () => {
      const on = GPS0_Audio.toggle();
      document.getElementById('menu-audio').textContent = on ? '🔊 Son' : '🔇 Son OFF';
    });

    document.getElementById('menu-difficulte')?.addEventListener('click', () => {
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
      document.getElementById('modal-confirm-reset')?.showModal();
    });
    document.getElementById('reset-oui')?.addEventListener('click', () => {
      localStorage.clear();
      sessionStorage.clear();
      try { document.cookie.split(';').forEach(c => { document.cookie = c.replace(/^ +/, '').replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/'); }); } catch {}
      location.reload(true);
    });
    document.getElementById('reset-non')?.addEventListener('click', () => {
      document.getElementById('modal-confirm-reset')?.close();
    });

    document.getElementById('menu-debug')?.addEventListener('click', () => {
      const isOn = localStorage.getItem('gps0_debug_on') === '1';
      if (!isOn) {
        const mdp = prompt('🔒 Mot de passe debug :');
        if (mdp !== 'jules') { if (mdp !== null) alert('Mot de passe incorrect.'); return; }
        localStorage.setItem('gps0_debug_on', '1');
      }
      _majToggleDebug();
      document.getElementById('modal-demo').showModal();
    });
    document.getElementById('debug-toggle')?.addEventListener('click', () => {
      if (localStorage.getItem('gps0_debug_on') === '1') {
        localStorage.removeItem('gps0_debug_on');
        _majToggleDebug();
      }
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
      _resumeGlobalClock();
      document.getElementById('app').classList.add('visible');
      _afficherResultats(true, e.detail?.poussieres || 5, e.detail?.niveau);
    });
    document.addEventListener('minijeu:failed', e => {
      _resumeGlobalClock();
      document.getElementById('app').classList.add('visible');
      _afficherResultats(false, e.detail?.poussieres || 0, e.detail?.niveau);
    });
    GPS0_GPS.on('zone_changee', () => _majObjectif());

    // Orientation device → boussole relative (bearing géo − heading téléphone)
    // Android (absolute): alpha = rotation CCW depuis le Nord → heading = (360 − alpha) % 360
    // iOS: webkitCompassHeading = déjà un heading direct (degrés depuis nord, CW)
    window.addEventListener('deviceorientationabsolute', e => {
      if (e.alpha !== null) GPS0_Boussole.setDeviceHeading((360 - e.alpha + 360) % 360);
    }, true);
    window.addEventListener('deviceorientation', e => {
      if (typeof e.webkitCompassHeading === 'number') {
        GPS0_Boussole.setDeviceHeading(e.webkitCompassHeading);
      } else if (e.absolute && e.alpha !== null) {
        GPS0_Boussole.setDeviceHeading((360 - e.alpha + 360) % 360);
      }
    }, true);
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
        const invIcone = fr.svg ? '<span class="inv-frag-icone inv-frag-svg">' + fr.svg + '</span>' : '<span class="inv-frag-icone">' + (fr.emoji || '🌙') + '</span>';
        row.innerHTML = invIcone
          + '<span class="inv-frag-infos"><span class="inv-frag-nom">' + fr.nom + '</span>'
          + '<span class="inv-frag-qty">x' + qty + (qty === 0 ? ' — vide' : '') + '</span></span>';
        row.appendChild(useBtn);
        elF.appendChild(row);
      });
    }
    modal.showModal();
  }


  function _ouvrirIframe(niveau) {
    _pauseGlobalClock();
    GPS0_Lune.setMiniJeuActif(true);
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
      GPS0_Lune.setMiniJeuActif(false);
      document.getElementById('app').classList.add('visible');
      _resumeGlobalClock();
      if (e.data.quit) return; // Quitter sans résultat
      document.dispatchEvent(new CustomEvent(e.data.success ? 'minijeu:complete' : 'minijeu:failed', { detail: e.data }));
    };
    window.addEventListener('message', handler);
  }

  function _lancerMiniJeu(niveau) {
    if (typeof GPS0_Economie !== 'undefined' && typeof GPS0_Economie.isCooldown === 'function' && GPS0_Economie.isCooldown(niveau)) {
      const r = GPS0_Economie.getCooldownRestant(niveau);
      const dl = document.getElementById('distance-label');
      if (dl) { dl.textContent = '⏳ Cooldown: ' + GPS0_Economie.formatCooldown(r); setTimeout(() => { dl.textContent = '---'; }, 4000); }
      return;
    }
    _ouvrirIframe(niveau);
  }

  function _afficherCountdown(niveau) {
    return new Promise(resolve => {
      const ov = document.createElement('div');
      ov.id = 'countdown-overlay';
      // Cosmonaut info
      const selfieB64 = typeof GPS0_Avatar !== 'undefined' ? GPS0_Avatar.getSelfie() : null;
      const luneNames = ['',' Séléné',' Phobos',' Titan',' Europe',' Ganymède',' Io',' Callisto',' Encelade',' Boss Final'];
      const luneEmojis = ['','🌛','🔥','🌿','❄️','👻','🤖','🌪️','💎','☄️'];
      const n = niveau || 1;
      // Draw selfie on canvas
      const cosmoHtml = selfieB64
        ? `<canvas id="cdCountCv" width="72" height="72" class="countdown-cosmo" style="border-radius:50%;border:3px solid rgba(79,195,247,.7)"></canvas>`
        : `<div class="countdown-cosmo" style="background:rgba(79,195,247,.2);border-radius:50%;width:72px;height:72px;border:3px solid rgba(79,195,247,.7);display:flex;align-items:center;justify-content:center;font-size:2.5rem">🚀</div>`;
      const luneLabel = `<div style="font-size:1.1rem;color:rgba(200,162,200,.9);font-weight:bold;letter-spacing:.05em">${luneEmojis[n]} Lune ${luneNames[n] || n}</div>`;
      ov.innerHTML = cosmoHtml + luneLabel + '<div id="cdNum" class="countdown-num">5</div>';
      ov.style.cssText = 'position:fixed;inset:0;z-index:2000;background:rgba(0,0,0,.92);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px';
      document.body.appendChild(ov);

      // Draw selfie if available
      if (selfieB64) {
        const cvEl = document.getElementById('cdCountCv');
        if (cvEl) {
          const img = new Image();
          img.onload = () => {
            const ctx = cvEl.getContext('2d');
            ctx.beginPath(); ctx.arc(36, 36, 33, 0, Math.PI * 2); ctx.clip();
            ctx.drawImage(img, 0, 0, 72, 72);
          };
          img.src = selfieB64;
        }
      }

      const numEl = document.getElementById('cdNum');
      let count = 5;
      const tick = () => {
        if (!numEl) return;
        if (count > 0) {
          numEl.textContent = count;
          numEl.className = 'countdown-num';
          void numEl.offsetWidth; // reflow
          numEl.className = 'countdown-num';
          count--;
          setTimeout(tick, 1000);
        } else {
          numEl.textContent = 'GO!';
          numEl.className = 'countdown-go';
          setTimeout(() => { ov.remove(); resolve(); }, 600);
        }
      };
      setTimeout(tick, 200);
    });
  }

  // === HORLOGE GLOBALE (pause pendant mini-jeux) ===
  let _clockStart = null, _clockPaused = 0, _clockPauseAt = null, _clockActive = false;
  function _startGlobalClock() {
    if (_clockStart !== null) return; // déjà démarré
    _clockStart = Date.now();
    _clockActive = true;
    const tick = () => {
      if (!_clockStart) return;
      let elapsed = _clockPaused;
      if (_clockActive) elapsed += Date.now() - _clockStart;
      const s = Math.floor(elapsed / 1000);
      const el = document.getElementById('chrono');
      if (el) el.textContent = String(Math.floor(s/60)).padStart(2,'0') + ':' + String(s%60).padStart(2,'0');
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }
  function _pauseGlobalClock() {
    if (!_clockActive) return;
    _clockPaused += Date.now() - _clockStart;
    _clockStart = Date.now();
    _clockActive = false;
  }
  function _resumeGlobalClock() {
    _clockStart = Date.now();
    _clockActive = true;
  }

  function _majToggleDebug() {
    const isOn = localStorage.getItem('gps0_debug_on') === '1';
    const btn = document.getElementById('debug-toggle');
    if (!btn) return;
    btn.textContent = isOn ? '🟢 Debug ON — cliquer pour désactiver' : '⚫ Debug OFF';
    btn.style.background = isOn ? 'rgba(50,120,50,.4)' : 'rgba(50,50,50,.4)';
    btn.style.color = isOn ? '#69FF47' : 'rgba(255,255,255,.35)';
    btn.style.cursor = isOn ? 'pointer' : 'default';
  }

  let _resultNiveau = null;
  function _afficherResultats(succes, poussieres, niveau) {
    _resultNiveau = niveau;
    const overlay = document.getElementById('overlay-resultats');
    if (!overlay) return;
    document.getElementById('res-icon').textContent = succes ? '🌟' : '💫';
    document.getElementById('res-titre').textContent = succes ? 'Lune complétée !' : 'Presque...';

    // Afficher les poussières avec animation de gain
    const resP = document.getElementById('res-poussieres');
    if (resP) {
      resP.textContent = poussieres > 0 ? '+' + poussieres + ' ✨' : '';
      resP.classList.remove('gain-anim');
      // force reflow pour relancer l'animation
      void resP.offsetWidth;
      if (poussieres > 0) resP.classList.add('gain-anim');
    }

    // ✅ localStorage mis à jour IMMÉDIATEMENT (sans attendre le clic bouton)
    if (poussieres > 0) {
      GPS0_Economie.ajouterPoussieres(poussieres);
      GPS0_Economie.updateHUD();
    }

    overlay.style.display = 'flex';
    // Détecter si c'est la dernière zone (level 9 / final)
    const currentZone = GPS0_GPS.zoneActuelle();
    const isFinalZone = !!(currentZone && currentZone.final && succes);
    const finaleBtn = document.getElementById('res-finale');
    const suivantBtn = document.getElementById('res-suivant');
    const recompenseBtn = document.getElementById('res-recompense');
    if (isFinalZone) {
      if (suivantBtn) suivantBtn.style.display = 'none';
      if (recompenseBtn) recompenseBtn.style.display = 'none';
      if (finaleBtn) finaleBtn.style.display = '';
    } else {
      if (suivantBtn) suivantBtn.style.display = '';
      if (recompenseBtn) recompenseBtn.style.display = '';
      if (finaleBtn) finaleBtn.style.display = 'none';
    }
    // Bind result buttons
    document.getElementById('res-rejouer').onclick = () => {
      overlay.style.display = 'none';
      if (_resultNiveau) _ouvrirIframe(_resultNiveau);
    };
    if (recompenseBtn) recompenseBtn.onclick = () => {
      overlay.style.display = 'none';
      // Poussières déjà ajoutées — juste navigation
      if (_resultNiveau) GPS0_Economie.setCooldown(_resultNiveau);
      const wb = document.getElementById('zone-btns');
      if (wb) wb.hidden = true;
      GPS0_GPS.zoneSuivante(); _majObjectif();
      GPS0_Boussole.forceEtat('off');
      _resumeGlobalClock();
    };
    if (suivantBtn) suivantBtn.onclick = () => {
      overlay.style.display = 'none';
      const wb2 = document.getElementById('zone-btns');
      if (wb2) wb2.hidden = true;
      GPS0_GPS.zoneSuivante(); _majObjectif();
      GPS0_Boussole.forceEtat('off');
      _resumeGlobalClock();
    };
    if (finaleBtn) finaleBtn.onclick = () => {
      overlay.style.display = 'none';
      GPS0_Finale && GPS0_Finale.lancer && GPS0_Finale.lancer();
    };
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
      const icone = fr.svg ? '<span class="fragment-icone fragment-svg">' + fr.svg + '</span>' : '<span class="fragment-icone">' + (fr.emoji || '🌟') + '</span>';
      btn.innerHTML = icone + '<span class="fragment-infos"><span class="fragment-nom">' + fr.nom + '</span><span class="fragment-desc">' + fr.desc + '</span></span><span class="fragment-prix">' + fr.prix + ' ✨</span><span class="fragment-acheter">ACHETER</span>';
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
