# 🌙 GPS0 — Game Design Document v3.0

**Version :** 3.16.0 - Bugs globaux : astéroïde zone-coloré+vitesse, gain chrono progressif, localStorage immédiat
**Date :** 22/03/2026
**Auteur :** Toufik49
**Statut :** Opérationnel - Bugs 1-2-3 appliqués intégralement

---

## Changements v3.16.0 (Bugs globaux 1-2-3)

### A. Astéroïde — États visuels (Bug 1)
- **Lumineux** : GPS actif (`data-etat="on"`) + vitesse > 0.3 m/s (`data-moving="true"`) → glow coloré selon zone
- **Grisé** : GPS inactif (`off`/`epuise`) OU vitesse ≤ 0.3 m/s (`data-moving="false"` ou absent)
- Keyframes zone-specific : `ast-glow-rouge` / `ast-glow-orange` / `ast-glow-vert` / `ast-glow` (bleu)
- Vitesse transmise depuis `gps.js` via `pos.coords.speed` dans chaque emit `position`
- `boussole.js updatePosition()` : set `data-moving="true"` si speed null ou > 0.3 m/s sinon `"false"`
- `_render('off')` et `_render('epuise')` : `delete w.dataset.moving` + `delete w.dataset.zone`
- `data-etat="zone"` (zone atteinte) : toujours lumineux bleu indépendamment della vitesse

### B. Système de gain par chrono (Bug 3)
- **Formule** : `gain = Math.floor((tempsJoué / tempsTotal) * 50)`
- Minimum 1 poussière si `tempsJoué > 5s`
- Maximum 50 poussières si timer épuisé
- Résultat identique succès et échec (basé sur le temps, pas l'issue)
- `timerTotal` mémorisé au boot dans `shared.js`, configurable via `window.GPS0_TIMER_SEC`
- Valeur par défaut : 150s (2min30). Niveaux 3min : `window.GPS0_TIMER_SEC = 180`
- `GPS0_rewardOverride` toujours prioritaire (N1 slingshot, N9 boss)

### C. Poussières intégrées immédiatement (Bug 2)
- `_afficherResultats()` dans `app.js` appelle `GPS0_Economie.ajouterPoussieres()` **immédiatement** à l'affichage de l'overlay
- Plus besoin de cliquer "Prendre la récompense" pour sauvegarder
- Bouton "Prendre la récompense" = navigation vers point suivant + `setCooldown()`
- Animation gain : `#res-poussieres` avec keyframe `res-gain-pop` (scale 0.4→1.25→1)
- Service Worker : `gps0-v32` / APP_VERSION `3.12.0`

---

## Changements v3.15.0 (Bug 14 — Jeu 2 redesign)

### A. Architecture mini-jeux — shared.js
- Nouveau fichier `minijeux/shared.js` : moteur commun à tous les 9 niveaux
- **Contrat** : chaque `niveauN.html` expose `window.NIVEAU`, `window.TUTO_TEXT`, `window.gameStart()`, optionnel `window.gameReset()` et `window.onResize()`
- **Séquence de boot** : tuto overlay → "Compris!" → countdown 5→4→3→2→1→GO! → `gameStart()`
- **Exports** : `drawCosmonaut`, `addDust`, `loseLife`, `endGame`, `GPS0_resizeCanvas`, `GPS0_lives`, `GPS0_running`

### B. UI — Tutoriel dans l'iframe
- Le tuto s'affiche dans l'iframe **après** loading, AVANT le countdown
- "Compris!" déclenche le countdown puis le jeu
- `TUTO_TEXT` est une string HTML propre à chaque niveau

### C. Bouton ✕ Quitter
- Présent sur tous les niveaux, coin supérieur droit (z-index 950)
- Confirmation modal avant quit
- Envoie `{source:'gps0_minijeu', quit:true}` au parent
- `app.js._ouvrirIframe()` gère ce message → ferme iframe sans écran de résultat

### D. Smiley fallback
- Si aucun selfie en localStorage, `drawCosmonaut()` dessine un smiley 😊 (cercle jaune, yeux, sourire)

### E. Flash rouge sur perte de vie
- `loseLife()` : bordure rouge 8px + fond rgba(255,0,0,0.3) → opacity 0.7 → 0 en 300ms
- Screenshake : body translateX(5→-5→3→0)px en 200ms

### F. Boussole — fix état inactif
- `boussole.js case 'off'` : `delete w.dataset.zone` pour que CSS `grayscale(1) brightness(0.5)` s'applique correctement

### G. Debug Rejouer — bypass cooldown
- `res-rejouer` appelle `_ouvrirIframe()` directement sans passer par `_lancerMiniJeu()`
- `_ouvrirIframe(niveau)` extrait dans `app.js` gère tout le cycle iframe

### H. 9 mini-jeux refonte complète
| N | Nom | Mécanique | Nouveautés Bug 14 |
|---|-----|-----------|------------------|
| 1 | Verre | Lance-pierre | Drag opposé au vecteur, trajectoire prédictive, blocs HP, caméra suit |
| 2 | Cendre | Flappy Bird | Vitesse progressive (2.4→5.8), colonnes roche+lave animée, cristaux +dust, jetpack glow, ciel volcanique |
| 3 | Lierre | Doodle Jump | Accéléromètre + swipe, 4 types plateformes, espacement réduit |
| 4 | Givre | Swing/Pendule | Tap accroche, swipe longueur corde, physique pendule |
| 5 | Ombre | Labyrinthe | Rayon lumière 70px, lampes +20px (doré +12), D-pad continu 4 boutons, maze 33×33 |
| 6 | Fer | Agar.io | Croissance +10%, vitesse inverse, 25 ennemis, map 3×, IA évitement |
| 7 | Tempête | Jetpack | Poussée -40%, gravité +20%, rebond sol/plafond, obstacles -30% |
| 8 | Cristal | Course Cristal | Piste auto, cristaux normaux/rouges/dorés(×5)/bleus, combos, power-ups |
| 9 | Éclipse | Boss Fight | Phases par HP (66%→33%), lasers, charges, spirales, rage mode, gold projs |

### I. Boss Fight (N9) — Phases par HP
- Phase 1 : HP 100→66% — tir modéré, pattern ciblé
- Phase 2 : HP 66→33% — lasers 0.7s warning, charges, 2 proj spread
- Phase 3 : HP 33→0% — spirales 6-dir, 3 proj spread, regen HP lente
- Rage Mode : si timer épuisé → boss en mode frénétique 2.5s puis Game Over
- Récompenses dust : Phase kill 1=50, 2=45, 3=40, Rage=35

### J. Service Worker
- Bumped vers `gps0-v26`
- `minijeux/shared.js` ajouté au CORE cache

---

## Changements v3.10.0 (Bug 13)

### B. Pop-ups Lune
- Fond opaque `rgba(0,0,0,0.85)`, texte blanc gras
- Durée d'affichage : **13 secondes**
- Délai minimum entre deux pop-ups : **8 secondes** (système de queue FIFO)

### C. Énergie HUD
- Emoji ⚡ remplacé par **SVG éclair doré** (#FFD700) avec drop-shadow lumineux

### D. SVG flottants cosmos
- Opacité globale réduite de **-40%** sur tous les éléments flottants
- Zone d'exclusion autour du centre portée à **250px** (était 180px)

### E. Halos astéroïde
- Keyframes de lueur améliorées : `drop-shadow` plus intense + `transform:scale(1.15)` au pic
- Couleurs par zone : rouge / orange / vert / bleu

### F. État astéroïde
- **Inactif** (`data-etat="off"`) : `grayscale(1) brightness(0.5)`, animation en pause
- **Actif zone** (`data-etat="zone"`) : animation 2s, lueur vive

### G. Compte à rebours avant mini-jeu
- Overlay fullscreen 5→4→3→2→1→GO! avant chaque mini-jeu
- Affiche selfie du cosmonaute + nom de la lune

### H. Économie poussières (mini-jeux)
- Formule temps-basée : `poussieres = calcDust()` variant selon temps joué
- Palette : 1-6pts (<30s) → 5-15pts (<60s) → 15-30pts (<120s) → 30-40pts (<150s) → 40-50pts (>150s) + bonus +10 si victoire, max 60

### I. Cosmonaute + selfie
- Selfie avatar visible sur le personnage dans chaque mini-jeu
- Backgrounds thématiques par lune (pas de fond noir uni)

### J. Fin de jeu
- Bouton "🏆 Finir l'aventure !" **uniquement au point GPS 9** (zone avec `final:true`)
- Les autres zones : bouton "Suivant" habituel

### K. 9 mini-jeux refontes complètes
| # | Lune | Mécanique |
|---|------|-----------|
| 1 | Verre | Slingshot / Angry Birds — fronde DRAG, blocs de cristal |
| 2 | Cendre | Flappy Bird — gravité forte, colonnes de lave |
| 3 | Lierre | Doodle Jump — plateformes jungle, tilt/swipe |
| 4 | Givre | Swing / Pendule — TAP pour s'accrocher, pics de glace |
| 5 | Ombre | Labyrinthe 31×31 — rayon lumière 90px, pièges d'ombre |
| 6 | Fer | Agar.io — croissance par absorption, IA ennemis |
| 7 | Tempête | Jetpack Joyride — défilement, obstacles typés, power-ups |
| 8 | Cristal | Crossy Road — vue dessus, vagues cristaux, rivières |
| 9 | Éclipse | Boss Fight 3 phases — projectiles dorés à renvoyer |

---

## RÈGLE DE PRIORITÉ v3.0

> **GDD v3.0 remplace INTÉGRALEMENT le v2.0.** Toute contradiction entre v2.0 et v3.0 est tranchée **en faveur du v3.0**. Ce document intègre toutes les décisions finales et ne contient aucune ambiguïté.

**Changements majeurs v3.0 :**
- 🎮 **9 Mini-jeux CSS/HTML** (remplace Godot complètement)
- 👤 **Avatar selfie pixelisé** comme tête littérale du héros
- 📍 **GPS zones fixes uniquement** (suppression génération dynamique)
- 🌙 **Lune narratrice taquine** (35+ répliques contextuelles)
- 🎨 **SVG sophistiqués** avec effets cosmos avancés
- 🎵 **Audio optimisé** (11 fichiers : 4+6+1)
- ⚡ **Performance 8-bit** (pas d'optimisation complexe nécessaire)

**Changements majeurs v3.1 :**
- Moteur platformer horizontal style Mario (camera scrollante)
- Monde plus large que lecran (MONDE_W configurable par niveau)
- Controles full-screen : zone gauche 50pct / zone droite 50pct / bouton saut centre
- Architecture hybride : 9 fichiers HTML + 1 moteur commun (moteur-minijeu.js)
- Mode Demo protege par mot de passe developpeur
- Service Worker v7

**Changements majeurs v3.2 :**
- HUD refonte : [ ?? Timer ][ ? Poussi?res ][ ?? Boutique ][ ?? Inventaire ][ ? Menu ]
- Menu ? hamburger integre dans le bandeau HUD (haut droite), dropdown
- Boutique Lunaire accessible via icone ?? dans le HUD (4 articles)
  - ?? ?clat de Lune : +10% energie ? 5 ?
  - ???? Fragment Lunaire : +25% energie ? 15 ?
  - ?? Gros Fragment : +50% energie ? 30 ?
  - ???? Coeur de Lune : energie 100% complete ? 50 ?
- Inventaire ?? accessible via icone dans HUD : voir fragments + utiliser
- Asteroide cliquable directement (flash lumineux, pas de bouton JOUER separe)
- Anneau energie SVG 240px entoure l'asteroide (hors limites 200px asteroid)
- Asteriode grise + halo dim quand inactif (data-etat=off)
- Assets fonds d'ecran mini-jeux : assets/backgrounds/fond_ecran1-9.jpeg
- Service Worker v9 / APP_VERSION 3.1.4

**Changements majeurs v3.9.0 (Bug 12) :**
- **9 Mini-jeux remplacés** : Mécaniques inspirées de jeux populaires :
  - N1 🌑 Lune de Verre — Slingshot / Angry Birds (fronde, physique parabolique)
  - N2 🌒 Lune de Cendre — Flappy Bird (tap=saut, éviter colonnes de lave)
  - N3 🌓 Lune de Lierre — Doodle Jump (rebonds infinis, plateformes procédurales)
  - N4 🌔 Lune de Givre — Swing / Corde (pendule, attraper stalactites)
  - N5 🌕 Lune d'Ombre — Dark Maze (labyrinthe obscur, lampe torche)
  - N6 🌖 Lune de Fer — Agar.io (absorber particules, grandir)
  - N7 🌗 Lune de Tempête — Jetpack Joyride (maintien=montée, obstacles électriques)
  - N8 🌘 Lune de Cristal — Crossy Road (swipe directionnel, éviter voitures + eau)
  - N9 🌑 Lune d'Éclipse — Duel Réflexe / Ready Steady Bang (appuyer au signal vert)
- **Fermeture modale** : Bouton "croix lunaire" SVG (crescent + ×, 44×44px) sur toutes les modales
- **Guide du Cosmonaute** : 5 étapes avec contenu utile (Comment jouer, 9 Lunes, Poussières, Objets, Astuces)
- **Pop-up Lune** : Durée 20s (était 5s) + bouton fermer (×)
- **Halo astéroïde** : Glow coloré sur le SVG selon distance (rouge >100m, orange 50-100m, vert 10-50m, bleu <10m) via data-zone
- **Navigation GPS** : Bouton "Point suivant" toujours visible en zone (passer sans jouer)
- **Résultats post-jeu** : Overlay avec 3 boutons : Rejouer / Prendre récompense / Point suivant
- **Reset total** : Modale de confirmation avant localStorage.clear() + sessionStorage.clear() + reload
- **Boutique/Inventaire** : Suppression halos SVG (filtres/blur) + suppression champ rarete
- Service Worker v24 / APP_VERSION 3.9.0

**Changements majeurs v3.8.0 (Bug 11) :**
- **9 Lunes thématiques** : Chaque mini-jeu a sa propre mécanique unique (remplace auto-runner générique) :
  - N1 🔮 Lune de Verre — Ray-casting miroirs (toggle '/' et '\' sur tap)
  - N2 🔥 Lune de Cendre — Gravité inversée auto-runner (tap=flip gravDir)
  - N3 🌿 Lune de Lierre — Plantes/vignes comme plateformes (10 graines)
  - N4 ❄ Lune de Givre — Glace avec inertie FRICTION=0.985 + vent
  - N5 👻 Lune d'Ombre — Mode fantôme HOLD (3s max, cooldown 4s) contre pièges
  - N6 🧲 Lune de Fer — Aimant : tap sur blocs métalliques pour attirer (rouges=piégés)
  - N7 🌬 Lune de Tempête — Auto-runner + rafales inversant le saut
  - N8 💎 Lune de Cristal — Tap rapide pour briser cristaux HP 3-8 dans ordre
  - N9 🌑 Lune d'Éclipse — Boss 3 phases : gravité → miroirs → fantôme (9 HP boss)
- **SVG animés Boutique/Inventaire** : 4 SVGs inline animés remplacent les emojis (éclat, fragment, gros, cœur) avec champ `rarete` (Commun/Peu commun/Rare/Légendaire)
- **Debug toggle persistant** : localStorage `gps0_debug_on=1` — mot de passe une seule fois, toggle ON/OFF button dans modal-debug
- **SVG flottants** : Exclusion zone 120px → 180px, opacity `.88` → `.18` (subtils)
- **Zone bleue Fix** : Seul `#btn-jouer-haut` lance le mini-jeu (clic astéroïde en zone = ignoré)
- Service Worker v23 / APP_VERSION 3.8.0

**Changements majeurs v3.7.0 (Bug 10) :**
- **Écran permissions** : Suppression caméra — seulement GPS + Pseudo dans la checklist
- **Caméra iOS Safari** : getUserMedia avec `{ video: {facingMode:"user", width:{ideal:640}, height:{ideal:640}}, audio:false }`, attributs `autoplay playsinline muted`, attente `loadedmetadata`, fallback si caméra indisponible
- **SVG flottants** : Check distancé 120px du centre retardé à 200ms (layout complet) ; UFO repositionné à `top:15%` pour éviter la zone boussole pendant son animation
- **Astéroïde** : Suppression définitive de `#energie-pct` (texte %) + suppression des mises à jour `#distance-label` dans boussole.js → asteroid : aucun texte, juste animation visuelle
- **Pop-ups indices** : `GPS0_Lune.parler()` vérifie `getEtat() !== 'zone'` → jamais de pop-up en zone bleue ✅
- **Niveau 1 → "Facile"** : Renommage complet dans toutes les occurrences ✅
- **Timer global** : `#chrono` ajouté au HUD (visible 00:00), se PAUSE en zone bleue (`zone_atteinte` → `_pauseGlobalClock()`) et pendant mini-jeux, reprend à la fin de chaque mini-jeu
- **Niveau 9 BOSS** : Refonte complète en AUTO-RUNNER Mario Run style :
  - Le joueur court automatiquement (VX=4.2), input unique = saut (court/long)
  - Monde 3x la largeur d'écran avec boucle (téléportation à gauche en fin de monde)
  - 12 plateformes en hauteur + sol complet (pas de trous — combat boss)
  - 12 ★ ÉTOILES ROUGES dans le monde → chaque collecte = -1 HP Boss
  - Boss oscille horizontalement en haut d'écran, tire des projectiles toutes les 2.5s→1.9s→1.2s (phases 1→2→3)
  - 3 phases (9 HP total : 1-6 HP = phase 1, 5-3 HP = phase 2, 2-0 HP = phase 3) avec changement de couleur/taille/vitesse
  - Barre de vie du boss visible en HUD + bannière de changement de phase
  - 3 vies joueur, 3 minutes, récompense 25 poussières sur victoire
- Service Worker v22 / APP_VERSION 3.7.0

---

## 1. Vision du jeu

> *"GPS0 est une aventure hybride entre le monde réel et des mini-jeux platformer CSS sophistiqués. Le joueur explore sa ville, découvre des zones mystérieuses guidé par une boussole magique, et plonge dans des mini-jeux pixel art où **SON PROPRE VISAGE** pixelisé devient littéralement la tête du héros cosmonaute. Chaque pas dans la ville réelle débloque un nouveau niveau immersif créé en CSS/HTML natif."*

**Ce que GPS0 v3.0 n'est PAS :**
- Pas de Godot (remplacé par CSS/HTML natif pour contrôle total)
- Pas de génération GPS dynamique (9 zones fixes choisies manuellement)
- Pas de narration de lieu (Lune taquine, pas historique des endroits)
- Pas de physique complexe (collisions rectangles simples suffisantes)
- Pas de compatibilité universelle (Chrome/Safari priorité)

**Ce que GPS0 v3.0 EST :**
- Aventure GPS réelle + Mini-jeux 8-bit immersifs
- Avatar personnel comme héros (selfie = tête du cosmonaute)
- Performance "8-bit assumée" sans optimisation poussée
- Architecture légère 100% CSS/JS vanilla

---

## 2. Concept Core Simplifié (GPS → Mini-jeux)

```
MONDE RÉEL                         MINI-JEUX CSS/HTML
──────────────────                 ────────────────────────
📍 Zone GPS 1 (fixe)   →   débloque   🎮 Niveau 1 (Tutoriel)
📍 Zone GPS 2 (fixe)   →   débloque   🎮 Niveau 2 (Slimes + trous)
📍 Zone GPS 3 (fixe)   →   débloque   🎮 Niveau 3 (Multi-slimes)
📍 Zone GPS 4 (fixe)   →   débloque   🎮 Niveau 4 (Double saut)
📍 Zone GPS 5 (fixe)   →   débloque   🎮 Niveau 5 (Plateformes)
📍 Zone GPS 6 (fixe)   →   débloque   🎮 Niveau 6 (Lasers tempo)
📍 Zone GPS 7 (fixe)   →   débloque   🎮 Niveau 7 (Mix avancé)
📍 Zone GPS 8 (fixe)   →   débloque   🎮 Niveau 8 (Challenge)
📍 Zone GPS 9 (fixe)   →   débloque   🎮 Niveau 9 (Final difficile)

9 coordonnées GPS fixes dans gps_config.json
= 9 mini-jeux CSS/HTML avec avatar selfie intégré
Le Niveau 9 = Niveau final très difficile (pas de boss spécial)
```

**Génération des points :** ~~Dynamique supprimée~~. Utilise **exclusivement** les 9 zones fixes du fichier `gps_config.json`. Les parcours changent uniquement l'**ordre de visite** des 9 mêmes zones.

**Mode Libre :** Débloqué après complétion **complète** du niveau 9 (`gps0_mode_libre_debloque = true`).

---

## 3. Identité visuelle (IDENTIQUE v2.0)

### Palette de couleurs (INVARIABLE)

| Usage | Hex |
|---|---|
| Fond principal (noir nuit) | `#0A0A1A` |
| Accent primaire (lilas lune) | `#C8A2C8` |
| Accent secondaire (or lunaire) | `#FFD700` |
| Halo ROUGE (> 151m) | `#FF3333` |
| Halo ORANGE (81–150m) | `#FF8C00` |
| Halo VERT (31–80m) | `#69FF47` |
| Halo BLEU (≤ 30m) | `#4FC3F7` |
| Halo GRIS (boussole OFF) | `#555555` |
| Succès | `#69FF47` |
| Danger | `#FF6B6B` |

### Style général
- Thème : nuit mystérieuse, magie lunaire, aventure urbaine/cosmique
- Graphismes : pixel art rétro + SVG sophistiqués pour mini-jeux
- Texte sur fond sombre : `color: #fff; font-weight: bold`
- Emoji spatiaux : ✨ poussières, ⚡ énergie, 🎯 zones, 🚀 jouer, 🛸 accueil, 🌟 classement

### Fond animé (écran principal uniquement)
- Dégradé : `#0A0A1A → #0D1B2A`
- 3 couches d'étoiles CSS (particules `translateX` en boucle infinie) :
  - Couche 1 : 60s, opacity 0.3, taille 1px
  - Couche 2 : 90s, opacity 0.5, taille 1.5px
  - Couche 3 : 120s, opacity 0.2, taille 2px
- 1 couche nuages très discrets (opacity 0.05), translateX 200s
- **Nouveau v3.0 :** Nébuleuses animées avec filtres SVG avancés pour mini-jeux

### SVG Sophistiqués v3.0
- Tous les SVG utilisent `<defs>` avec gradients radiaux/linéaires
- **Filtres SVG requis :** `glow-soft`, `stellar-shimmer`, `casque-brillance`
- **Patterns :** `surface-lunaire`, `metal-cristal`, `aurore-boreale`
- **Animations :** `nebuleuse-respiration`, `scintillement-stellaire`
- Usage obligatoire : `<use href="svg/icons.svg#id">` — jamais de SVG inline dans HTML principal

---

## 4. SPA — Séquence de lancement (ÉTAT RÉEL v3.5)

```
Ouverture app
    ↓
Splash interactif (logo GPS0 animé + bouton)
→ Bouton inject dynamiquement : « Commencer l'aventure 🚀 »
→ Sur clic : requestFullscreen() + GPS0_Audio.playMusiqueExploration() + fade-out splash
    ↓
requestPermissions() — géolocalisation + orientation
    ↓
Modale Pseudo (si gps0_pseudo absent)
→ Input « Ton pseudo d'explorateur »
→ Bouton « Confirmer ✨ » — sauvegarde gps0_pseudo
    ↓
Capture Selfie Avatar
→ Caméra frontale 320×320 → pixelisation 32×32
→ Sauvegarde gps0_avatar_selfie_base64
→ Pas d'explication textuelle — interface directe
    ↓
Modale Parcours (showParcoursModal)
→ 3 parcours + option code défi
→ Bouton « Commencer 🚀 »
    ↓
Modale Difficulté
→ 4 cartes cliquables
    ↓
Chargement Zones Fixes + Mini-jeux
    ↓
Init GPS, Boussole, Économie, Lune, HUD
    ↓
Écran principal — La Boussole
```

**Règles absolues :**
- La musique démarre UNIQUEMENT sur interaction utilisateur (clic bouton splash) — Web Audio API policy
- `_tuto()` (guide cosmonaute) est NON BLOQUANT — accessible uniquement depuis menu ❓
- Pas de chrono. Pas de fullscreen gate bloquant (fullscreen tenté silencieusement au clic splash)
- Selfie : affiché directement après pseudo, pas d'écran d'explication préalable

---

## 5. SPA — Écran principal (Boussole + HUD)

### HUD (bandeau haut, toujours visible)

```
┌──────────────────────────────────────────────┐
│  ✨ 145   ⚡ 78%   [🏪]   [🎒]   [☰]       │
└──────────────────────────────────────────────┘
```

- Fond : `rgba(0,0,0,0.6)`, `backdrop-filter: blur`
- **✨ Poussières** (`#poussieres`) : nombre en temps réel
- **⚡ Énergie** (`#hud-energie-val`) : pourcentage mis à jour par `GPS0_Economie.updateHUD()`
- **🏪 Boutique** (`#hud-boutique`) : ouvre modal boutique
- **🎒 Inventaire** (`#hud-inventaire`) : ouvre modal inventaire
- **☰ Menu** (`#menu-btn`) : toggle panneau menu
- ~~⏱️ Chrono~~ : **supprimé définitivement**

### Menu Principal (☰ Toggle)

**Comportement :**
- `display:none` par défaut (`.menu-panel` CSS)
- Clic sur `#menu-btn` → toggle classe `.open` → `display:flex`
- Re-clic → ferme (retire `.open`)
- Jamais ouvert par défaut, jamais visible sans action utilisateur

**6 items :**

| ID | Label | Action |
|---|---|---|
| `menu-audio` | 🔊 Son | Toggle audio ON/OFF |
| `menu-difficulte` | ⚙️ Difficulté | Modal confirmation + reload |
| `menu-reset` | 🔄 Réinitialiser | Efface localStorage + reload |
| `menu-demo` | 🎮 Tester un niveau | Ouvre modal niveaux **sans mot de passe** |
| `menu-debug` | 🐛 Mode Debug | Demande mot de passe `jules`, ouvre modal niveaux |
| `menu-guide` | ❓ Guide du cosmonaute | Ouvre `_ouvrirTuto()` non bloquant |

### Boussole — États

| État | Comportement |
|---|---|
| **OFF (défaut)** | Astéroïde grisé, immobile. Fusée masquée. Halo gris. Aucune consommation d'énergie. |
| **ON** | Astéroïde tourne. Fusée pointe vers GPS cible (bearing RELATIF au téléphone). Halo coloré actif. Consommation énergie selon difficulté. |
| **ÉPUISÉ** (énergie = 0) | ON impossible. Icône rouge barrée. Système d'indices actif. Halo gris permanent. Message : "Recharge ta boussole !" |
| **ZONE** (distance ≤ 30m) | Astéroïde pulse fort bleu. Fusée vibre. Bouton "JOUER 🚀" au centre de l'astéroïde. Flash bleu + SFX zone_detectee. |

**Règle absolue : La détection de zone (≤ 30m) s'active MÊME si la boussole est OFF.**

### Boussole — Orientation device (v3.5.1)

La flèche (fusée) affiche un **bearing relatif à l'orientation du téléphone**, pas le bearing géographique brut :

```
bearing_affiché = (bearing_géo − heading_device + 360) % 360
```

| Source | Plateforme | API |
|---|---|---|
| `event.webkitCompassHeading` | iOS | Heading direct (0–360°, CW depuis nord) |
| `event.alpha` (absolute) | Android | Rotation CCW → heading = `(360 − alpha) % 360` |

- `deviceorientationabsolute` prioritaire sur Android
- `deviceorientation` avec `webkitCompassHeading` pour iOS  
- Si aucun heading disponible → fallback bearing géo (0°, ancien comportement)
- Permission iOS 13+ demandée au clic du bouton splash (geste utilisateur requis)

**Conséquence** : si tu tiens le téléphone pointé vers la cible, la flèche pointe vers le haut (droit devant). Si tu tournes 90° à droite, la flèche tourne 90° à gauche pour continuer à pointer vers la cible.

### Halo de proximité

Visible uniquement si boussole ON (sauf gris = OFF/épuisé).

| Couleur | Distance | Pulsation |
|---|---|---|
| 🔴 `#FF3333` | > 151m | Lente |
| 🟠 `#FF8C00` | 81–150m | Normale |
| 🟢 `#69FF47` | 31–80m | Rapide |
| 🔵 `#4FC3F7` | ≤ 30m | Très rapide + zone détectée |
| ⚫ `#555555` | OFF / épuisé | Pas de pulsation |

### Barre basse

```
┌─────────────────────────────────────┐
│  🎯  "Le Point GPS 4"               │
│       Prochain objectif             │
└─────────────────────────────────────┘
```

---

### Menu Principal (Burger Menu)

Le bouton `☰` dans le HUD (haut droite) ouvre le menu par **toggle CSS** (`.open` class).

- Caché par défaut : `display:none`
- Clic → `.open` → `display:flex` en colonne
- Re-clic → ferme
- **6 items** : Son, Difficulté, Réinitialiser, Tester niveau, Mode Debug, Guide cosmonaute

Voir section 5 pour le détail complet.


## 6. SPA — Système de Difficulté (IDENTIQUE v2.0)

**Fichier :** `js/difficulte.js`
**localStorage :** `gps0_difficulte`

### 4 niveaux

| ID | Nom | Emoji | Mécanique |
|---|---|---|---|
| `clair_de_lune` | Clair de Lune | 🌙 | -1% énergie / 10s |
| `face_cachee` | Face Cachée | 🌑 | -2% énergie / 10s |
| `eclipse_totale` | Éclipse Totale | 🌚 | -5% énergie / 10s |
| `trou_noir` | Trou Noir | 🕳️ | Cycle auto : 10s ON / 170s OFF. Toggle manuel désactivé. |

### Modale difficulté
- 4 cartes cliquables avec nom, emoji, description
- Affiché au premier lancement, modifiable depuis Paramètres
- Sauvegarde du choix dans localStorage

---

## 7. SPA — Système GPS Zones Fixes v3.0

**Fichier :** `js/gps.js` — **RÉVISION MAJEURE v3.0**
**localStorage :** `gps0_zones_actives`

### ⭐ CHANGEMENT MAJEUR : Zones GPS Fixes Uniquement

```json
{
  "version": "3.0",
  "zones_fixes": [
    { "id": 1, "nom": "Le Point GPS 1", "lat": 47.25865295634987, "lng": -0.07232092747517298, "rayon": 30, "mini_jeu": 1 },
    { "id": 2, "nom": "Le Point GPS 2", "lat": 47.25922301993599, "lng": -0.07496422077580976, "rayon": 30, "mini_jeu": 2 },
    { "id": 3, "nom": "Le Point GPS 3", "lat": 47.25957512835827, "lng": -0.07585838017127501, "rayon": 30, "mini_jeu": 3 },
    { "id": 4, "nom": "Le Point GPS 4", "lat": 47.25855640527987, "lng": -0.07438732146623522, "rayon": 30, "mini_jeu": 4 },
    { "id": 5, "nom": "Le Point GPS 5", "lat": 47.257773005061290, "lng": -0.07572423946778357, "rayon": 30, "mini_jeu": 5 },
    { "id": 6, "nom": "Le Point GPS 6", "lat": 47.257047880177915, "lng": -0.07570440178130702, "rayon": 30, "mini_jeu": 6 },
    { "id": 7, "nom": "Le Point GPS 7", "lat": 47.256649766044300, "lng": -0.07403862750361210, "rayon": 30, "mini_jeu": 7 },
    { "id": 8, "nom": "Le Point GPS 8", "lat": 47.253662326392785, "lng": -0.07059828273820297, "rayon": 30, "mini_jeu": 8 },
    { "id": 9, "nom": "Le Point GPS 9", "lat": 47.255649980795920, "lng": -0.06899643397777900, "rayon": 30, "mini_jeu": 9, "final": true }
  ],
  "parcours": {
    "parcours_1": {
      "nom": "La Promenade du Papy",
      "emoji": "🧓",
      "ordre": [1,2,3,4,5,6,7,8,9],
      "description": "Parcours tranquille pour découvrir GPS0"
    },
    "parcours_2": {
      "nom": "La Randonnée",
      "emoji": "🚶",
      "ordre": [1,4,7,2,5,8,3,6,9],
      "description": "Exploration en étoile pour aventuriers"
    },
    "parcours_3": {
      "nom": "La Marche Funèbre",
      "emoji": "💀",
      "ordre": [1,3,5,7,9,2,4,6,8],
      "description": "Parcours difficile pour experts"
    }
  }
}
```

**⚠️ SUPPRESSION v3.0 :** Plus de génération dynamique avec offsets. Un parcours = ordre différent des 9 mêmes zones fixes.

### Code défi
- Format : `LUNE-XX-DDMMYY-HHMM`
- XX = `PP` (Papy) / `RD` (Rando) / `MF` (Funèbre)
- Exemple : `LUNE-PP-150326-1430`

## 8. Système Avatar Selfie Pixelisé

**Fichier :** `js/avatar.js` — **NOUVEAU système v3.0**
**localStorage :** `gps0_avatar_selfie_base64`

### Capture & Pixelisation

```javascript
// Séquence selfie améliorée
1. Caméra frontale (facingMode: "user", 320×320)
2. Cadre carré centré + preview temps réel
3. Capture → Canvas 32×32 + pixelisation 8-bit
4. Palette 16 couleurs + image-rendering: pixelated
5. Export PNG base64 → localStorage
6. Injection dans tous les mini-jeux via CSS custom properties
```

### Intégration Mini-jeux

**CRITIQUE :** Le selfie 32×32 du joueur remplace **littéralement** la tête du personnage dans tous les mini-jeux.

```html
<!-- Tête Avatar = Selfie du Joueur -->
<foreignObject class="selfie-container">
  <div class="selfie-pixelise" style="--joueur-selfie-url: url(data:image/png;base64,...)"></div>
</foreignObject>

<!-- Corps = Astronaute générique 8-bit -->
<g class="corps-astronaute">
  <rect class="torse" fill="#C8A2C8"/>
  <g class="jetpack"><!-- Jetpack avec flammes --></g>
</g>

<!-- Casque = Semi-transparent pour voir le visage -->
<circle class="casque-spatial" fill="url(#casque-transparent)" opacity="0.8"/>
```

**Système AvatarManager :**
- `chargerSelfieDansJeu()` : Injecte le selfie dans tous les mini-jeux
- `animerAvatarEtat(etat)` : Gère les animations marche/saut/danger/victoire
- `mettreAJourAvatar(base64)` : Met à jour le selfie en temps réel

---

﻿## 9. Mini-jeux CSS/HTML — Architecture Réelle (v3.1)

**Architecture hybride : 9 fichiers HTML indépendants + 1 moteur JS commun**

### Fichiers

```
js/
└── moteur-minijeu.js    # Moteur platformer horizontal commun

minijeux/
├── niveau1.html         # Tutoriel  (spawn simple, 0 ennemis)
├── niveau2.html         # Slimes + trous
├── niveau3.html         # Multi-slimes + trous larges
├── niveau4.html         # Double saut + plateformes mobiles
├── niveau5.html         # Lasers temporisés
├── niveau6.html         # Mix + pics
├── niveau7.html         # Tout combiné + vitesse accrue
├── niveau8.html         # Challenge complet
└── niveau9.html         # Niveau final très difficile
```

### Configuration par Niveau (GPS0_NIVEAU_CFG)

Chaque niveau.html définit window.GPS0_NIVEAU_CFG avant de charger moteur-minijeu.js :

```javascript
window.GPS0_NIVEAU_CFG = {
  niveau: 1,
  monde_w: 1.0,       // facteur : monde largeur = écran x monde_w
  gravite: 0.46,
  saut_force: -11,
  vitesse: 3.6,
  vies: 3,
  total_poussieres: 8,
  double_saut: false, // activé au niveau 4+
  spawn_x: 80,
  plateformes: [      // {x, y, w, h, sol?, mobile?, fragile?, range?, speed?, axis?}
    { x:0, y:h-40, w:monde_w, h:40, sol:true },
    ...
  ],
  slimes: [           // {pi: index_plateforme, col?, speed?, dir?}
  ],
  poussieres: [       // {pi: index_plateforme}
  ],
  lasers: [           // {x, y, w, offset?, warn?, on?, off?}
  ],
  pics: [             // {pi? | x+y, h?, col?}
  ],
  lune_start: "Voici ton premier pas cosmique !",
  msg_win: "Bien joué !",
  msg_lose: "La Lune te juge."
};
```

### Caméra Scrollante (style Mario)

```javascript
// Monde div#monde de largeur MONDE_W pixels
// Caméra suit le joueur avec lerp 12%
if (MONDE_W > W) {
  const tgt = Math.max(0, Math.min(jx - W * 0.35, MONDE_W - W));
  camX += (tgt - camX) * 0.12;
  monde.style.transform = "translateX(" + (-Math.round(camX)) + "px)";
}
```

### Contrôles Full-Screen (INVISIBLES)

```
┌─────────────────────────────────────────┐
│ HUD (48px fixe)                         │
├────────────────────────────────────────────┤
│                                            │
│       Monde de jeu (scrollant)            │
│  [zone tactile G]  [zone saut]  [zone D]  │
│  TRANSPARENTES — aucune flèche visible    │
└─────────────────────────────────────────┘
```

- Zones tactiles `background:transparent; border:none; color:transparent`
- Aucun symbole ◀ ▲ ▶ affiché
- Le joueur interagit par tâtonnement / feeling
- Les plateformes avec leur halo lumineux guident visuellement
- **Clavier** : flèches / QZSD (debug desktop)

### Plateformes — Visuels et Quantités

**Halo lumineux** : Toutes les plateformes flottantes (`.plate:not(.sol)` et `.plateforme:not(.sol)`) ont un glow CSS violet doux :
```css
box-shadow: 0 4px 12px rgba(0,0,0,0.5), 0 0 14px rgba(200,162,200,0.55), 0 0 30px rgba(200,162,200,0.25);
```
- Crée un contraste net sur le fond spatial sombre
- Le joueur voit clairement où sauter sans aide textuelle

**Densité** : Chaque niveau a ~20-26 plateformes (5 sols + 15-21 flottantes) sur un monde de 4 écrans de large.

**Dispersion des poussières** : réparties sur toute la longueur — début, milieu, haut, fin. Exploration requise.

### Overlay Fin de Mini-jeu

**3 boutons verticaux** — ordre fixe :
```
🎁 Prendre les X poussières  ← visible seulement en victoire
🔄 Recommencer
❌ Abandonner
```
- `flex-direction: column`, `align-items: stretch`, `width: min(300px, 90vw)`
- Bouton récompense en tête de liste si victoire, absent si défaite
<div id="lune-ingame"><!-- bulle Lune in-game --></div>
<div id="monde">
  <div id="bg-etoiles"></div>
  <!-- plateformes, slimes, poussieres générés par JS -->
  <div id="joueur">
    <div id="casque"><div id="tete-selfie"></div></div>
    <div id="corps"></div>
    <div id="jambes"><div class="jambe"></div><div class="jambe"></div></div>
  </div>
</div>
<div id="zone-gauche"></div>
<div id="zone-droite"></div>
<button id="btn-saut">↑</button>
<div id="tuto-overlay"><!-- overlay tutoriel --></div>
<div id="overlay-fin"><!-- victoire/défaite --></div>
<script>window.GPS0_NIVEAU_CFG = { ... };</script>
<script src="../js/moteur-minijeu.js"></script>
```

### Avatar Selfie dans les Mini-jeux

```javascript
// moteur-minijeu.js - injection automatique du selfie
try {
  const b64 = window.parent.GPS0_Avatar && window.parent.GPS0_Avatar.getSelfie();
  if (b64) document.getElementById("tete-selfie").style.backgroundImage = "url(" + b64 + ")";
} catch(e) {}
```

```css
#tete-selfie {
  image-rendering: pixelated;
  background: var(--selfie-url, linear-gradient(135deg, #C8A2C8, #9a72c8));
  background-size: cover;
}
```

### Communication Mini-jeu ↔ SPA (via iframe)

```javascript
// SPA lance le mini-jeu dans un iframe (app.js)
function _lancerMiniJeu(niveau) {
  document.getElementById("app").classList.remove("visible");
  const iframe = document.createElement("iframe");
  iframe.src = "minijeux/niveau" + niveau + ".html";
  document.body.appendChild(iframe);
}

// Mini-jeu → SPA (moteur-minijeu.js)
window.parent.postMessage({
  source: "gps0_minijeu",
  success: true,          // ou false
  niveau: cfg.niveau,
  poussieres: TOTAL,      // ou etoiles collectées si échec
  etoiles: 3              // ou 1 si échec
}, "*");

// SPA ← Mini-jeu (app.js)
document.addEventListener("minijeu:complete", e => {
  GPS0_Economie.ajouterPoussieres(e.detail?.poussieres || 10);
  GPS0_GPS.zoneSuivante();
  GPS0_Boussole.forceEtat("off");
  document.getElementById("app").classList.add("visible");
});
document.addEventListener("minijeu:failed", () => {
  document.getElementById("app").classList.add("visible");
});
```

### Mécaniques par Niveau (ÉTAT v3.5)

| Niveau | Nouveauté | monde_w | Etoiles | Slimes | Lasers | Pics | Double saut |
|--------|-----------|---------|---------|--------|--------|------|-------------|
| 1 | Tutoriel | 4× | 12 | 0 | 0 | 0 | non |
| 2 | Slimes + trous | 4× | 16 | 5 | 0 | 0 | non |
| 3 | Multi-slimes | 4× | 18 | 8 | 0 | 0 | non |
| 4 | Double saut + mobiles | 4× | 18 | 0 | 0 | 0 | **oui** |
| 5 | Lasers + fragiles | 4× | 16 | 0 | 4 | 0 | oui |
| 6 | Mix + pics | 4× | 20 | 3 | 3 | 3 | oui |
| 7 | Tout combiné + rapide | 4× | 22 | 4 | 4 | 4 | oui |
| 8 | Challenge Oméga | 4× | 24 | 5 | 6 | 6 | oui (2 vies) |
| 9 | Final | — | — | — | — | — | oui |

## 10. Lune Narratrice Taquine

**Fichier :** `js/lune.js` — **Répertoire élargi v3.0**

### Répliques par Contexte

```javascript
const luneRepliques = {
  // Arrivée en zone (5-7 répliques)
  arrivee_zone: [
    "Oh, t'as quand même réussi à trouver. J'y croyais plus.",
    "Bon. Te voilà. Tu as mis le temps...",
    "Enfin ! J'ai failli m'endormir en t'attendant.",
    "Tu marches ou tu danses ? Difficile à dire de là-haut.",
    "Ah, le GPS fonctionne encore. Petit miracle quotidien !",
    "Bravo ! Seulement 47 détours pour y arriver.",
    "Tu as trouvé ! Mes cratères en tremblent d'émotion."
  ],

  // Navigation lente (6 répliques)
  navigation_lente: [
    "Une tortue spatiale irait plus vite !",
    "Tu fais du tourisme ou tu joues ?",
    "À ce rythme, on va rater la prochaine pleine lune.",
    "Mes cratères bougent plus vite que toi.",
    "Tu es sûr que tes jambes fonctionnent encore ?",
    "Même un satellite en panne va plus rapidement."
  ],

  // Navigation erratique (5 répliques)
  navigation_erratique: [
    "Tu tournes en rond comme un satellite déréglé !",
    "C'est pas un labyrinthe, juste... tout droit.",
    "Tu cherches quoi ? Le passage secret ?",
    "GPS cassé ou c'est toi qui bugs ?",
    "On dirait une mouche dans un bocal..."
  ],

  // Énergie faible (6 répliques)
  energie_faible: [
    "Tu vas vider ta batterie avant d'arriver sur Mars !",
    "Recharge-toi, tu fais pitié à voir.",
    "Économise ton énergie... oh wait, trop tard.",
    "Ta boussole va rendre l'âme, tire-la pas trop.",
    "Même moi j'ai plus d'énergie que toi ce soir.",
    "Allez, un petit effort ! Ou pas..."
  ],

  // Performance excellente (5 répliques)
  performance_excellente: [
    "Pas mal pour un terrien ! J'suis presque impressionnée.",
    "Tu connais le chemin par cœur maintenant ?",
    "Bon, t'es pas complètement nul finalement.",
    "Speed run spatial ! Mes compliments.",
    "Tu me rappelles... moi, quand j'étais jeune planète."
  ],

  // Avant boss (4 répliques)
  avant_boss: [
    "Le boss arrive. Bonne chance. (tu vas en avoir besoin)",
    "Dernière ligne droite ! Montre-nous tes talents.",
    "C'est le moment de vérité, petit cosmonaute.",
    "Boss final ! J'espère que t'as pris des vitamines."
  ],

  // Random taquin (7 répliques)
  random_fun: [
    "Tu marches beaucoup pour quelqu'un qui a un écran.",
    "T'as pensé à regarder où tu mets les pieds ?",
    "Alors, cette vie de cosmonaute urbain ?",
    "Tu collectes les poussières d'étoiles... mais moi je fabrique !",
    "J'ai vu passer trois comètes pendant ton dernier trajet.",
    "Tu sais que je t'observe depuis 384 400 km ?",
    "Même les aliens rigolent de tes trajectoires."
  ]
};
```

### Système d'Apparition Intelligent

```javascript
// Déclencheurs contextuels
- Arrivée zone : Toujours (réplique aléatoire)
- Navigation lente : Si vitesse < 2 km/h pendant 2+ min
- Navigation erratique : Si changements direction > 8 en 1 min
- Énergie faible : Si énergie < 25%
- Performance excellente : Si temps record + énergie > 70%
- Random : 5% chance toutes les 3 minutes
```

---

## 11. Système Audio Optimisé

**Fichier :** `js/audio.js` — **AudioManager v3.0**
**Technologie :** Web Audio API (pas de balise `<audio>`)

### Fichiers Audio Requis (11 total)

```
assets/audio/
├── musique/
│   ├── exploration/
│   │   ├── musique_menu0.mp3    [Ambient spatial 1]
│   │   ├── musique_menu1.mp3    [Ambient spatial 2]
│   │   ├── musique_menu2.mp3    [Ambient spatial 3]
│   │   └── musique_menu3.mp3    [Ambient spatial 4]
│   └── finale/
│       └── musique_finale.mp3   [Animation finale épique]
└── sfx/ (6 essentiels)
    ├── boussole_on.mp3          [Activation boussole]
    ├── boussole_off.mp3         [Désactivation boussole]
    ├── zone_detectee.mp3        [Zone GPS atteinte]
    ├── halo_bip.mp3             [Changement couleur halo]
    ├── lune_apparait.mp3        [Bulle narrative Lune]
    └── achat.mp3                [Achat en boutique]
```

**Note :** Pas de musique Godot (supprimée avec Godot). Les mini-jeux CSS utilisent la musique d'exploration.

### API AudioManager v3.0

```javascript
// Musiques
GPS0_Audio.playMusiqueExploration(); // Rotation 4 pistes
GPS0_Audio.playFinale();             // Animation finale
GPS0_Audio.stopMusique();

// SFX Mini-jeux (nouveaux)
GPS0_Audio.playSFX("saut_cosmonaute");      // Saut avatar
GPS0_Audio.playSFX("collecte_poussiere");   // Collectible pris
GPS0_Audio.playSFX("ennemi_touche");        // Slime touché
GPS0_Audio.playSFX("plateforme_active");    // Plateforme mobile
GPS0_Audio.playSFX("laser_warning");        // Laser en warning
GPS0_Audio.playSFX("boss_hit");             // Boss touché

// Contrôles
GPS0_Audio.toggle();      // ON/OFF global
GPS0_Audio.stopAll();     // Arrêt complet
```

---

## 12. Architecture des Fichiers v3.0

```
GPS0/
├── index.html                  # SPA principale
├── manifest.json               # PWA config
├── gps_config.json             # 9 zones fixes + 3 parcours
├── css/
│   ├── main.css               # SPA + animations cosmos
│   └── minijeux.css           # Styles spécifiques mini-jeux
├── js/
│   ├── app.js                 # Orchestration SPA
│   ├── gps.js                 # GPS zones fixes uniquement
│   ├── boussole.js            # Système boussole inchangé
│   ├── avatar.js              # Selfie pixelisé + injection mini-jeux
│   ├── economie.js            # Poussières + énergie
│   ├── lune.js                # Narratrice taquine élargie
│   ├── audio.js               # AudioManager v3.0
│   ├── moteur-minijeu.js      # Moteur platformer horizontal commun
│   └── finale.js              # Animation finale inchangée
├── minijeux/
│   ├── niveau1.html           # Tutoriel CSS
│   ├── niveau2.html           # Slimes spatiaux
│   ├── niveau3.html           # Multi-slimes
│   ├── niveau4.html           # Double saut + mobiles
│   ├── niveau5.html           # Lasers temporisés
│   ├── niveau6.html           # Mix temporel
│   ├── niveau7.html           # Combiné rapide
│   ├── niveau8.html           # Challenge complet
│   └── niveau9.html           # Boss CSS 3 phases
├── svg/
│   └── icons.svg              # SVG sophistiqués + effets
├── assets/
│   └── audio/                 # 11 fichiers audio optimisés
└── service-worker.js          # Cache PWA + mini-jeux
```

---

## 13. Métriques de Performance v3.0

### Objectifs Techniques

| Métrique | v2.0 (Godot) | v3.0 (CSS) | Amélioration |
|----------|-------------|------------|-------------|
| **Taille totale** | 8-12MB | <3MB | -70% |
| **Chargement initial** | 15-30s | 5-8s | -75% |
| **Temps lancement mini-jeu** | 3-5s | <1s | -80% |
| **Compatibilité mobile** | Variable | Excellente | +100% |
| **Debug & maintenance** | Complexe | Simple | +200% |
| **Intégration avatar** | Bridge requis | Native | Parfaite |

### Optimisations CSS/HTML

- **GPU Acceleration** : `will-change` sur toutes les animations
- **Requestanimationframe** : Animations fluides 60fps
- **CSS Custom Properties** : Variables dynamiques pour selfie
- **SVG Inline optimisé** : Defs réutilisables + filtres
- **Image pixelated** : Rendu 8-bit natif navigateur
- **Preload critique** : Mini-jeux en background SPA

---

## 14. localStorage — Clés v3.0

| Clé | Contenu |
|---|---|
| `gps0_avatar_selfie_base64` | **[NOUVEAU]** Selfie pixelisé 32×32 |
| `gps0_minijeux_progression` | **[NOUVEAU]** Progression 9 niveaux CSS |
| `gps0_zones_actives` | **[MODIFIÉ]** Ordre parcours des zones fixes |
| `gps0_lune_repliques_vues` | **[NOUVEAU]** Éviter répétition répliques |
| `gps0_pseudo` | Pseudo explorateur (inchangé) |
| `gps0_difficulte` | Niveau difficulté (inchangé) |
| `gps0_economie` | Poussières + énergie (inchangé) |
| `gps0_audio_enabled` | Son ON/OFF (inchangé) |

---

## 15. Questions de Cohérence Future

### 🔴 **CRITIQUES — Répondre MAINTENANT**

#### A. Architecture Mini-jeux

**Q1.** ~~Les 9 mini-jeux CSS auront-ils **chacun leur propre fichier HTML** ou **un seul moteur JS dynamique** ?~~

> ✅ **Résolu v3.1 :** Hybride retenu — 9 fichiers HTML séparés + 1 moteur commun moteur-minijeu.js. Chaque niveau définit sa config dans window.GPS0_NIVEAU_CFG.

**Q2.** **Performance mobile** : Les animations SVG + CSS complexes vont-elles **lag sur mobiles anciens** ?
- Fallbacks nécessaires pour animations ?
- Detection performance automatique ?

**Q3.** Le système **selfie 32×32 en CSS background-image** va-t-il **fonctionner sur tous navigateurs** avec `image-rendering: pixelated` ?

#### B. Gameplay & Progression

**Q4.** **Cooldown 5 minutes** sur les mini-jeux : cohérent avec **exploration GPS réelle** qui prend 15-45 minutes ?
- Réduire cooldown à 2-3 min ?
- Cooldown différent selon difficulté ?

**Q5.** **9 zones fixes** : que se passe-t-il si le joueur est **physiquement incapable** d'aller à une zone (propriété privée, danger, etc.) ?
- Système de remplacement de zone ?
- Mode "simulation GPS" pour tests ?

**Q6.** **Avatar selfie** : système de **modération automatique** nécessaire pour éviter contenus inappropriés ?

#### C. Audio & Immersion

**Q7.** **11 fichiers audio** : taille totale acceptable ? Compression/format optimal ?
- MP3 vs OGG vs WebM ?
- Streaming vs préchargement complet ?

**Q8.** **Lune taquine** : fréquence d'apparition pour éviter **spam** mais garder **engagement** ?
- Cooldown entre répliques ?
- Système de pertinence contextuelle ?

#### D. PWA & Distribution

**Q9.** **Service Worker** : cache des mini-jeux HTML pour fonctionnement **offline** ?
- Stratégie cache-first ou network-first ?

**Q10.** **GitHub Pages** : suffisant pour héberger avec **gps_config.json modifiable** ?
- Système update des coordonnées GPS ?

### 🟡 **SUGGESTIONS D'AMÉLIORATION**

#### E. Extensions Potentielles

**Q11.** **Éditeur de niveaux** : permettre aux joueurs de créer leurs propres **mini-jeux CSS simples** ?

**Q12.** **Multijoueur asynchrone** : partage des **temps de parcours** entre amis sur mêmes zones ?

**Q13.** **Accessibilité** : mini-jeux jouables **sans GPS** pour personnes à mobilité réduite ?

---

## 16. Roadmap Développement v3.0

### ✅ **Phase 1-4 : SPA Terminée** (selon v2.0)

### 🔄 **Phase 5 : Mini-jeux CSS** (remplace Godot)
1. **Moteur mini-jeux** : Architecture CSS/HTML + événements natifs
2. **Avatar intégration** : Injection selfie dans tous niveaux
3. **Niveau 1** : Tutoriel complet avec animations cosmos
4. **Niveaux 2-8** : Progression mécanique selon concepts
5. **Niveau 9** : Boss CSS 3 phases avec SVG sophistiqué
6. **Audio mini-jeux** : SFX + musique intégrés
7. **Performance** : Optimisation mobile 60fps
8. **Debug** : Mode test tous niveaux

### 🔄 **Phase 6 : Polish & Tests**
- Tests GPS réels sur les 9 zones fixes
- Optimisation audio (compression, streaming)
- Tests avatar selfie multi-navigateurs
- Validation accessibilité & performance

### 🔄 **Phase 7 : Déploiement**
- PWA GitHub Pages avec Service Worker
- Cache offline mini-jeux + assets
- Monitoring GPS précision réelle

---

**📅 GDD v3.5 mis à jour :** 20/03/2026
**🎯 Status :** 🟢 Opérationnel — SW v16 / APP 3.5.0 en production
**✍️ Prochaine étape :** Tests GPS terrain + Niveau 9 final

---

*Ce GDD v3.0 remplace intégralement le v2.0. Aucune implémentation sans validation préalable des questions de cohérence.*

---

## ⭐ SECTIONS DÉTAILLÉES ADDITIONNELLES v3.0

### A. API JavaScript Complète

```javascript
// === GPS0_App - Orchestration Principale ===
window.GPS0_App = {
  init() {
    // Séquence lancement complète
    this.showSplash()
      .then(() => this.requestFullscreen())
      .then(() => this.checkPseudo())
      .then(() => this.captureAvatar())
      .then(() => this.selectDifficulte())
      .then(() => this.selectParcours())
      .then(() => this.initGame());
  },

  async showSplash() { /* Splash 2s */ },
  async requestFullscreen() { /* PWA fullscreen */ },
  async checkPseudo() { /* Modal pseudo si absent */ },
  async captureAvatar() { /* Capture selfie si absent */ },
  async selectDifficulte() { /* Modal 4 difficultés */ },
  async selectParcours() { /* Modal 3 parcours + codes */ },
  async initGame() { /* Init GPS + Boussole + HUD */ }
};

// === GPS0_MiniJeu - Moteur Unifié ===
window.GPS0_MiniJeu = {
  async demarrer(niveau, avatarBase64) {
    this.config = await ConfigurationManager.chargerNiveau(niveau);
    this.joueur = new JoueurAvatar(avatarBase64);
    this.gameState = new GameState(niveau, this.config);

    AvatarManager.chargerSelfieDansJeu(avatarBase64);
    ConfigurationManager.appliquerConfiguration(this.config);

    this.gameLoop();
  },

  gameLoop() {
    if (this.gameState.etat !== 'playing') return;

    this.updatePhysics();
    this.updateControls();
    this.updateAnimations();
    this.checkCollisions();
    this.checkVictory();

    requestAnimationFrame(() => this.gameLoop());
  },

  // Contrôles tactiles
  setupControls() {
    document.querySelector('.zone-gauche').addEventListener('touchstart', () => {
      this.joueur.deplacer('gauche');
    });

    document.querySelector('.zone-droite').addEventListener('touchstart', () => {
      if (this.config.nouvelles_mecaniques?.includes('double_saut')) {
        this.joueur.doubleSaut();
      } else {
        this.joueur.sauter();
      }
    });
  }
};

// === GPS0_Economie - Gestion Complète ===
window.GPS0_Economie = {
  get() {
    const stored = localStorage.getItem('gps0_economie');
    return stored ? JSON.parse(stored) : {
      poussieres: 0,
      energie: { actuelle: 100, max: 100, dernierCalcul: Date.now() }
    };
  },

  save(economie) {
    localStorage.setItem('gps0_economie', JSON.stringify(economie));
  },

  ajouterPoussieres(quantite) {
    const economie = this.get();
    economie.poussieres += quantite;
    this.save(economie);
    this.updateHUD();
  },

  consommerEnergie(pourcentage) {
    const economie = this.get();
    economie.energie.actuelle = Math.max(0, economie.energie.actuelle - pourcentage);
    economie.energie.dernierCalcul = Date.now();
    this.save(economie);
    this.updateHUD();
  },

  rechargerEnergie() {
    const economie = this.get();
    const maintenant = Date.now();
    const ecoulé = maintenant - economie.energie.dernierCalcul;
    const recharge = Math.floor(ecoulé / (15 * 60 * 1000)); // +1% par 15min

    if (recharge > 0) {
      economie.energie.actuelle = Math.min(
        economie.energie.max,
        economie.energie.actuelle + recharge
      );
      economie.energie.dernierCalcul = maintenant;
      this.save(economie);
      this.updateHUD();
    }
  },

  updateHUD() {
    const economie = this.get();
    document.querySelector('.hud-poussieres').textContent = economie.poussieres;

    const sablier = document.querySelector('.sablier-energie rect');
    const percent = economie.energie.actuelle / economie.energie.max;
    sablier.style.transform = `scaleY(${percent})`;

    if (percent < 0.2) {
      sablier.style.fill = '#FF6B6B'; // Rouge si < 20%
      sablier.style.animation = 'energie-critique 0.5s infinite';
    } else {
      sablier.style.fill = '#4FC3F7';
      sablier.style.animation = 'none';
    }
  }
};
```

### B. localStorage Complet v3.0

```javascript
// Gestion centralisée de tous les localStorage
const GPS0_Storage = {
  // === DONNÉES PRINCIPALES ===
  'gps0_pseudo': 'string', // Pseudo explorateur
  'gps0_difficulte': 'string', // ID difficulté active
  'gps0_parcours_actif': 'object', // Parcours + ordre zones
  'gps0_avatar_selfie_base64': 'string', // Selfie pixelisé 32×32

  // === PROGRESSION & SCORES ===
  'gps0_progression': {
    point_actuel: 1,
    points_completes: [1, 2], // IDs zones terminées
    premier_lancement: false,
    mode_libre_debloque: false
  },

  'gps0_scores_niveaux': {
    '1': { etoiles: 3, poussieres: 5, temps_restant: 240, date: '2026-03-15' },
    '2': { etoiles: 2, poussieres: 7, temps_restant: 180, date: '2026-03-15' }
  },

  'gps0_cooldowns': {
    '1': 1741997000000, // Timestamp fin cooldown niveau 1
    '2': 0               // Pas de cooldown actif
  },

  // === ÉCONOMIE ===
  'gps0_economie': {
    poussieres: 145,
    energie: {
      actuelle: 70,
      max: 100,
      dernierCalcul: 1741996800000
    }
  },

  'gps0_inventaire': {
    eclat_lune: 2,
    fragment_lunaire: 0,
    gros_fragment: 1,
    coeur_lune: 0
  },

  // === INTERFACE & PARAMÈTRES ===
  'gps0_audio_enabled': 'true',
  'gps0_boussole': { etat: 'off' }, // 'on' | 'off' | 'epuise'
  'gps0_lune_repliques_vues': ['arrivee_zone_1', 'navigation_lente_3'],

  // === STATISTIQUES ===
  'gps0_stats': {
    sessions_totales: 15,
    temps_jeu_total: 7200000, // ms
    distance_parcourue: 5.2, // km
    zones_decouvertes: 6,
    niveaux_termines: 4
  }
};

// Helper pour migrer localStorage entre versions
function migrateStorage() {
  const version = localStorage.getItem('gps0_storage_version') || '1.0';

  if (version === '1.0') {
    // Migration v1.0 → v3.0
    console.log('[STORAGE] Migration v1.0 → v3.0...');

    // Migrer ancien avatar vers nouveau format
    const oldAvatar = localStorage.getItem('gps0_avatar');
    if (oldAvatar && !localStorage.getItem('gps0_avatar_selfie_base64')) {
      // Conversion ancien format
      localStorage.setItem('gps0_avatar_selfie_base64', oldAvatar);
    }

    localStorage.setItem('gps0_storage_version', '3.0');
  }
}
```

### C. Conventions de Code v3.0

```javascript
// === CONVENTIONS DE NOMMAGE ===
// Modules : PascalCase avec préfixe GPS0_
window.GPS0_App, window.GPS0_Audio, window.GPS0_Economie

// Fonctions : camelCase
function demarrerNiveau(numero) {}
function calculerDistance(lat1, lng1, lat2, lng2) {}

// Variables : camelCase
let joueurPosition, tempsRestant, niveauActuel

// Constantes : SNAKE_CASE
const PALETTE_COULEURS, DUREE_COOLDOWN_MINUTES, MAX_POUSSIERES_NIVEAU

// Classes : PascalCase
class MiniJeuMoteur, class AvatarManager, class ConfigurationManager

// Événements : kebab-case avec namespace
'spa:start-level', 'minijeu:complete', 'boss:defeated'

// === GESTION D'ERREURS ===
// Toujours try/catch pour APIs externes
try {
  const audioBuffer = await GPS0_Audio.loadSFX('zone_detectee');
} catch (error) {
  console.warn('[AUDIO] SFX non disponible:', error.message);
  // Graceful degradation, pas d'erreur bloquante
}

// === PERFORMANCE ===
// Animations : requestAnimationFrame uniquement
function animate() {
  updatePositions();
  requestAnimationFrame(animate);
}

// CSS : will-change pour animations importantes
.avatar-cosmonaute.marche { will-change: transform; }

// Debounce pour événements fréquents (GPS)
const debouncedUpdatePosition = debounce(updatePosition, 1000);

// === LOGGING ===
// Préfixes par module
console.log('[GPS] Position mise à jour:', lat, lng);
console.warn('[AUDIO] Fichier manquant:', filename);
console.error('[MINI-JEU] Configuration invalide:', config);
```

### D. Déploiement & Performance v3.0

```javascript
// === SERVICE WORKER CONFIG ===
const CACHE_VERSION = 'gps0-v3.0.1';
const CACHE_STATIC = [
  '/',
  '/index.html',
  '/css/main.css',
  '/css/minijeux.css',
  '/js/app.js',
  '/js/minijeux.js',
  '/js/avatar.js',
  '/svg/icons.svg',
  '/config/niveaux/niveau1.json',
  '/config/niveaux/niveau2.json',
  // ... tous les niveaux
];

const CACHE_AUDIO = [
  '/assets/audio/musique/exploration/musique_menu0.mp3',
  '/assets/audio/musique/exploration/musique_menu1.mp3',
  '/assets/audio/musique/exploration/musique_menu2.mp3',
  '/assets/audio/musique/exploration/musique_menu3.mp3',
  '/assets/audio/sfx/boussole_on.mp3',
  '/assets/audio/sfx/boussole_off.mp3',
  '/assets/audio/sfx/zone_detectee.mp3',
  '/assets/audio/sfx/halo_bip.mp3',
  '/assets/audio/sfx/lune_apparait.mp3',
  '/assets/audio/sfx/achat.mp3'
];

// Stratégie cache
self.addEventListener('fetch', event => {
  // Cache-first pour assets statiques
  if (CACHE_STATIC.includes(new URL(event.request.url).pathname)) {
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
  }
  // Network-first pour données GPS
  else if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match(event.request))
    );
  }
});

// === OPTIMISATIONS MOBILE ===
// Lazy loading des niveaux
async function preloadNiveauSuivant(niveauActuel) {
  if (niveauActuel < 9) {
    const prochainConfig = await fetch(`config/niveaux/niveau${niveauActuel + 1}.json`);
    // Précharge en arrière-plan
  }
}

// Gestion mémoire
function cleanupNiveauPrecedent() {
  // Nettoie les éléments DOM du niveau terminé
  document.querySelectorAll('.ennemi, .collectible').forEach(el => el.remove());

  // Libère les écouteurs d'événements
  document.removeEventListener('touchstart', handleTouch);
}

// Détection performance
function detectPerformance() {
  const start = performance.now();
  requestAnimationFrame(() => {
    const fps = 1000 / (performance.now() - start);

    if (fps < 30) {
      console.warn('[PERF] FPS bas détecté, mode dégradé activé');
      document.body.classList.add('mode-degrade');
    }
  });
}
```

---

**📅 GDD v3.5 mis à jour :** 20/03/2026
**🎯 Status :** 🟢 Opérationnel — SW v16 / APP 3.5.0 en production
**✍️ Prochaine étape :** Tests GPS terrain + Niveau 9 final

---

*Ce GDD v3.5 reflète l'état EXACT du code en production. Toute modification du code doit être répercutée ici simultanément.*