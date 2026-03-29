'use strict';
window.GPS0_App = (() => {
  let _parcoursId = null;
  let _zoneAutoTimer = null;
  let _enZone = false;

  function _setZoneBtnsActif(actif) {
    const btnJouer = document.getElementById('btn-jouer-haut');
    const btnSuivant = document.getElementById('btn-prochain-point');
    if (!btnJouer || !btnSuivant) return;
    btnJouer.disabled = !actif;
    btnSuivant.disabled = !actif;
  }

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
    // Affiche le pseudo dans le menu
    function _afficherPseudo() {
      const p = localStorage.getItem('gps0_pseudo');
      if (p) {
        const el = document.getElementById('menu-joueur');
        if (el) el.textContent = '\uD83D\uDC64 Joueur : ' + p;
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

    const mainPanel = document.getElementById('parcours-choix-principal');
    const predefPanel = document.getElementById('parcours-predef-panel');
    const rejoindrePanel = document.getElementById('parcours-rejoindre-panel');

    function _showMain() {
      mainPanel.hidden = false; predefPanel.hidden = true; rejoindrePanel.hidden = true;
    }
    function _showPredef() {
      mainPanel.hidden = true; predefPanel.hidden = false; rejoindrePanel.hidden = true;
    }
    function _showRejoindre() {
      mainPanel.hidden = true; predefPanel.hidden = true; rejoindrePanel.hidden = false;
    }

    document.getElementById('btn-balades-predef').addEventListener('click', _showPredef);
    document.getElementById('btn-rejoindre-balade').addEventListener('click', _showRejoindre);
    document.getElementById('parcours-retour-predef').addEventListener('click', _showMain);
    document.getElementById('parcours-retour-rejoindre').addEventListener('click', _showMain);

    // Sélection parcours prédéfini
    document.querySelectorAll('.parcours-carte').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.parcours-carte').forEach(b => b.setAttribute('aria-pressed', 'false'));
        btn.setAttribute('aria-pressed', 'true');
        choix = btn.dataset.val;
        document.getElementById('parcours-commencer').disabled = false;
      });
    });

    // Code balade 6 chiffres
    const codeInput = document.getElementById('code-balade-input');
    const codeErr = document.getElementById('code-balade-err');
    const codeBtn = document.getElementById('btn-rejoindre-go');
    const PARCOURS_CODES = { '1': 'parcours_1', '2': 'parcours_2', '3': 'parcours_3' };

    if (codeInput) {
      codeInput.addEventListener('input', function() {
        const val = this.value.replace(/\D/g, '').slice(0, 6);
        this.value = val;
        if (val.length === 6) {
          // Code format: XYYYYY where X=parcours (1-3), YYYYY=seed
          const pId = PARCOURS_CODES[val[0]];
          if (pId) {
            codeErr.textContent = '✅ Code valide !';
            codeErr.style.color = '#69FF47';
            codeBtn.disabled = false;
            choix = pId;
            localStorage.setItem('gps0_code_balade', val);
          } else {
            codeErr.textContent = 'Code invalide';
            codeErr.style.color = '#FF6B6B';
            codeBtn.disabled = true;
            codeInput.classList.add('shake');
            setTimeout(() => codeInput.classList.remove('shake'), 500);
          }
        } else {
          codeErr.textContent = '';
          codeBtn.disabled = true;
        }
      });
    }

    return new Promise(r => {
      document.getElementById('parcours-commencer').addEventListener('click', () => {
        if (!choix) return; m.close(); r(choix);
      }, { once: true });
      if (codeBtn) codeBtn.addEventListener('click', () => {
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

    // Code balade 6 chiffres (format: X=parcours + 5 chiffres déterministes)
    const pIdx = { parcours_1: '1', parcours_2: '2', parcours_3: '3' };
    const n = new Date();
    const seed = String(n.getDate() * 100 + n.getHours() * 37 + n.getMinutes()).padStart(5, '0').slice(0, 5);
    const codeBalade = (pIdx[_parcoursId] || '1') + seed;
    localStorage.setItem('gps0_code_balade', codeBalade);
    // Afficher dans le menu (plus de toast ni barre basse)
    const menuCode = document.getElementById('menu-code-balade');
    if (menuCode) menuCode.textContent = '\uD83D\uDD11 Code : ' + codeBalade;

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
      // Zone quittée : désactiver boutons si joueur sort de la zone bleue
      if (_enZone) {
        const zone = GPS0_GPS.zoneActuelle();
        if (zone && d.dist > (zone.rayon || 30) + 15) {
          _enZone = false;
          _setZoneBtnsActif(false);
          _resumeGlobalClock();
        }
      }
    });
    GPS0_GPS.on('zone_atteinte', zone => {
      GPS0_Lune.parler('arrivee_zone');
      GPS0_Audio.playSFX('zone_detectee');
      GPS0_Audio.playSFX('halo_bip');
      GPS0_Boussole.forceEtat('zone');
      _pauseGlobalClock(); // Zone bleue : horloge en pause
      _enZone = true;
      _setZoneBtnsActif(true);
    });
    GPS0_GPS.on('jeu_termine', () => {
      // La finale est déclenchée via le bouton 'Finir l'aventure' dans _afficherResultats
      // (uniquement au point GPS 9 avec final:true) — ne pas lancer ici
    });
    GPS0_GPS.on('erreur', msg => console.warn('[GPS0] GPS:', msg));
    let _signalFaibleAt = 0;
    GPS0_GPS.on('position_imprecise', ({ accuracy }) => {
      // Signal trop faible : informer une fois toutes les 30s max
      const dist = document.getElementById('dist-value');
      if (dist) dist.textContent = '...';
      const now = Date.now();
      if (now - _signalFaibleAt > 30000) {
        _signalFaibleAt = now;
        GPS0_Lune.parler('signal_faible');
      }
    });

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
    // Mise à jour menu : nom balade
    const menuBalade = document.getElementById('menu-balade');
    if (menuBalade) menuBalade.textContent = '\uD83D\uDDFA\uFE0F Balade : ' + (GPS0_GPS.nomParcours() || '—');
    // Mise à jour menu : point actuel
    const menuPoint = document.getElementById('menu-point-actuel');
    if (menuPoint) menuPoint.textContent = '\uD83D\uDCCC Point : ' + GPS0_GPS.progressionStr();
    if (z && z.final) setTimeout(() => GPS0_Lune.parler('avant_boss'), 2000);    // Bouton SUIVANT → FINIR \uD83C\uDFC1 au dernier point GPS
    const btnSuivant = document.getElementById('btn-prochain-point');
    if (btnSuivant) {
      if (z && z.final) {
        btnSuivant.textContent = 'FINIR \uD83C\uDFC1';
        btnSuivant.style.background = 'linear-gradient(135deg,#FFD700,#FF8C00)';
        btnSuivant.style.color = '#0A0A1A';
        btnSuivant.style.fontWeight = 'bold';
        btnSuivant.dataset.isFinal = '1';
      } else {
        btnSuivant.textContent = 'SUIVANT';
        btnSuivant.style.background = '';
        btnSuivant.style.color = '';
        btnSuivant.style.fontWeight = '';
        btnSuivant.dataset.isFinal = '0';
      }
    }  }

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

    // Bouton JOUER (toujours visible, actif uniquement en zone bleue)
    document.getElementById('btn-jouer-haut')?.addEventListener('click', () => {
      if (_zoneAutoTimer) { clearTimeout(_zoneAutoTimer); _zoneAutoTimer = null; }
      const z = GPS0_GPS.zoneActuelle();
      if (z) _lancerMiniJeu(z.mini_jeu);
    });

    // Bouton SUIVANT (toujours visible, actif uniquement en zone bleue)
    document.getElementById('btn-prochain-point')?.addEventListener('click', () => {
      const _btn = document.getElementById('btn-prochain-point');
      if (_btn && _btn.dataset.isFinal === '1') {
        // Dernier point GPS → lancer la finale
        _enZone = false;
        _setZoneBtnsActif(false);
        _resumeGlobalClock();
        GPS0_Finale && GPS0_Finale.lancer && GPS0_Finale.lancer();
        return;
      }
      _enZone = false;
      _setZoneBtnsActif(false);
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

    document.getElementById('menu-selfie-refaire')?.addEventListener('click', async () => {
      mp.classList.remove('open');
      mb.setAttribute('aria-expanded', 'false');
      GPS0_Avatar.clearSelfie();
      const m = document.getElementById('modal-selfie'); m.showModal();
      // Reset UI état initial
      document.getElementById('selfie-capture').hidden = false;
      document.getElementById('selfie-retake').hidden = true;
      document.getElementById('selfie-confirm').hidden = true;
      document.getElementById('selfie-video').hidden = false;
      const ok = await GPS0_Avatar.demarrerCamera();
      if (!ok) {
        document.getElementById('selfie-capture').hidden = true;
        const errEl = document.createElement('p');
        errEl.style.cssText = 'color:#FF6B6B;font-size:0.85rem;text-align:center;margin:8px 0';
        errEl.textContent = 'Cam\u00e9ra indisponible.';
        m.querySelector('.selfie-actions').insertAdjacentElement('beforebegin', errEl);
        return;
      }
      let cap = null;
      const capBtn = document.getElementById('selfie-capture');
      const retakeBtn = document.getElementById('selfie-retake');
      const confirmBtn = document.getElementById('selfie-confirm');
      const skipBtn = document.getElementById('selfie-skip');
      const finish = b64 => {
        GPS0_Avatar.arreterCamera(); m.close();
        if (b64) { GPS0_Avatar.setSelfie(b64); GPS0_Avatar.injecterDansJeux(b64); }
      };
      capBtn.addEventListener('click', () => {
        cap = GPS0_Avatar.capturer();
        capBtn.hidden = true; retakeBtn.hidden = false; confirmBtn.hidden = false;
        document.getElementById('selfie-video').hidden = true;
      }, { once: true });
      retakeBtn.addEventListener('click', () => {
        cap = null; capBtn.hidden = false; retakeBtn.hidden = true; confirmBtn.hidden = true;
        document.getElementById('selfie-video').hidden = false;
      }, { once: true });
      confirmBtn.addEventListener('click', () => finish(cap), { once: true });
      skipBtn.addEventListener('click', () => finish(null), { once: true });
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
      if (!_enZone) _resumeGlobalClock();
      document.getElementById('app').classList.add('visible');
      _afficherResultats(true, e.detail?.poussieres || 5, e.detail?.niveau);
    });
    document.addEventListener('minijeu:failed', e => {
      if (!_enZone) _resumeGlobalClock();
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
      if (!_enZone) _resumeGlobalClock();
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
      const luneNames = ['','Niveau 1','Niveau 2','Niveau 3','Niveau 4','Niveau 5','Niveau 6','Niveau 7','Niveau 8','Niveau 9 — Boss Final'];
      const luneEmojis = ['','🚀','🌋','⬆️','🔮','🧲','🌑','🫧','🛸','☄️'];
      const n = niveau || 1;
      // Draw selfie on canvas
      const cosmoHtml = selfieB64
        ? `<canvas id="cdCountCv" width="72" height="72" class="countdown-cosmo" style="border-radius:50%;border:3px solid rgba(79,195,247,.7)"></canvas>`
        : `<div class="countdown-cosmo" style="background:rgba(79,195,247,.2);border-radius:50%;width:72px;height:72px;border:3px solid rgba(79,195,247,.7);display:flex;align-items:center;justify-content:center;font-size:2.5rem">🚀</div>`;
      const luneLabel = `<div style="font-size:1.1rem;color:rgba(200,162,200,.9);font-weight:bold;letter-spacing:.05em">${luneEmojis[n]} ${luneNames[n] || ('Niveau '+n)}</div>`;
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
      // Poussières déjà ajoutées — retour à la MAP, boutons restent actifs
      if (_resultNiveau) GPS0_Economie.setCooldown(_resultNiveau);
      _setZoneBtnsActif(true);
    };
    if (suivantBtn) suivantBtn.onclick = () => {
      overlay.style.display = 'none';
      // Retour à la MAP — le joueur choisit via les boutons fixes
      _setZoneBtnsActif(true);
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
    if (soldeEl) soldeEl.textContent = poussieres + ' \u2728';
    container.innerHTML = '';
    frags.forEach(fr => {
      // Même structure que l'inventaire : div.inv-fragment-row
      const row = document.createElement('div');
      row.className = 'inv-fragment-row' + (poussieres < fr.prix ? ' bq-disabled' : '');
      const icone = fr.svg
        ? '<span class="inv-frag-icone inv-frag-svg">' + fr.svg + '</span>'
        : '<span class="inv-frag-icone">' + (fr.emoji || '\uD83C\uDF1F') + '</span>';
      row.innerHTML = icone
        + '<span class="inv-frag-infos">'
        + '<span class="inv-frag-nom">' + fr.nom + '</span>'
        + '<span class="inv-frag-qty">' + fr.desc + '</span>'
        + '<span class="bq-prix">' + fr.prix + ' \u2728</span>'
        + '</span>';
      const buyBtn = document.createElement('button');
      buyBtn.className = 'inv-frag-use';
      buyBtn.textContent = '\uD83D\uDED2 Acheter';
      buyBtn.disabled = poussieres < fr.prix;
      buyBtn.onclick = () => {
        if (typeof GPS0_Economie !== 'undefined' && typeof GPS0_Economie.acheterFragment === 'function') {
          const ok = GPS0_Economie.acheterFragment(fr.id, fr.prix);
          if (ok) { GPS0_Audio.playSFX('achat'); GPS0_Economie.updateHUD(); modal.close(); }
          else { row.classList.add('erreur'); setTimeout(() => row.classList.remove('erreur'), 800); }
        }
      };
      row.appendChild(buyBtn);
      container.appendChild(row);
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
