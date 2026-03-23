# 🗺️ GPS1 — Guide de Clonage depuis GPS0

**Basé sur :** GPS0 v3.50.0  
**Auteur :** Toufik49  
**Objectif :** Créer un nouveau jeu de piste GPS (GPS1, GPS2…) en partant de GPS0.  
Tu gardes tout le moteur, tu changes uniquement : les jeux, le style, les dialogues et les coordonnées GPS.

---

## 📐 Architecture GPS0 — Ce que fait chaque fichier

```
GPS1/
│
├── index.html            ← Page principale (modals, HUD, splash, boussole)
├── manifest.json         ← Config PWA (nom, icône, couleurs)
├── service-worker.js     ← Cache PWA (incrémenter CACHE à chaque modif)
├── gps_config.json       ← 🎯 TES COORDONNÉES GPS + parcours
│
├── css/
│   ├── main.css          ← 🎨 THÈME VISUEL (couleurs, logo, fond)
│   └── minijeux.css      ← Style commun aux mini-jeux (HUD, modals)
│
├── js/
│   ├── app.js            ← Orchestrateur principal — NE PAS TOUCHER
│   ├── gps.js            ← Moteur GPS (Haversine, watchPosition) — NE PAS TOUCHER
│   ├── boussole.js       ← Boussole SVG — NE PAS TOUCHER
│   ├── economie.js       ← Économie (énergie, poussière, fragments) — NE PAS TOUCHER
│   ├── audio.js          ← Sons Web Audio + MP3 — NE PAS TOUCHER
│   ├── avatar.js         ← Selfie cosmonaute — NE PAS TOUCHER
│   ├── finale.js         ← Cinématique fin de jeu — NE PAS TOUCHER
│   ├── lune.js           ← 🗨️ DIALOGUES de la Lune (NPC) — à adapter
│   └── moteur-minijeu.js ← Lance les mini-jeux dans l'iframe — NE PAS TOUCHER
│
├── minijeux/
│   ├── shared.js         ← Moteur commun à tous les jeux — NE PAS TOUCHER
│   ├── niveau1.html      ← 🎮 TES MINI-JEUX (1 fichier par zone GPS)
│   ├── niveau2.html
│   ├── ...
│   └── niveau9.html
│
├── assets/
│   ├── audio/
│   │   ├── musique/exploration/ ← 🎵 musique_menu0-4.mp3 (5 tracks)
│   │   ├── musique/finale/      ← musique_finale.mp3
│   │   └── sfx/                 ← Sons MP3 (12 fichiers — garder ou remplacer)
│   └── backgrounds/
│       └── bg-n1.svg … bg-n9.svg ← 🖼️ Fond SVG de chaque mini-jeu
│
└── svg/
    └── icons.svg         ← Boussole, fusée, astéroïde — NE PAS TOUCHER
```

---

## ✅ Checklist de clonage (ordre à suivre)

### ÉTAPE 1 — Copier le projet

```bash
# Copier GPS0 → GPS1
cp -r GPS0 GPS1
cd GPS1
git init
git remote add origin [TON_REPO_GITHUB]
```

### ÉTAPE 2 — Identifier et modifier (6 fichiers seulement)

| Priorité | Fichier | Ce qu'on change |
|---|---|---|
| 🔴 Critique | `gps_config.json` | Coordonnées GPS, noms des zones, parcours |
| 🔴 Critique | `minijeux/niveau1-9.html` | Les 9 mini-jeux complets |
| 🟠 Style | `css/main.css` | Thème couleurs + nom du jeu |
| 🟠 Style | `assets/backgrounds/bg-n1-9.svg` | Fonds visuels des mini-jeux |
| 🟡 Optionnel | `js/lune.js` | Dialogues NPC adaptés au thème |
| 🟡 Optionnel | `manifest.json` | Nom PWA + icônes |

---

## 🎯 ÉTAPE 2A — Modifier `gps_config.json`

Structure complète. Copier-coller et remplacer les valeurs :

```json
{
  "version": "1.0",
  "parcours": {
    "parcours_1": {
      "nom": "Nom de ton parcours 1",
      "emoji": "🏃",
      "code": "P1",
      "description": "Description courte",
      "zones": [
        {
          "id": 1,
          "nom": "Zone 1 — Nom du lieu",
          "lat": 47.0000,
          "lng": -0.0000,
          "rayon": 30,
          "mini_jeu": 1
        },
        { "id": 2, "nom": "Zone 2", "lat": 47.0001, "lng": -0.0001, "rayon": 30, "mini_jeu": 2 },
        { "id": 3, "nom": "Zone 3", "lat": 47.0002, "lng": -0.0002, "rayon": 30, "mini_jeu": 3 },
        { "id": 4, "nom": "Zone 4", "lat": 47.0003, "lng": -0.0003, "rayon": 30, "mini_jeu": 4 },
        { "id": 5, "nom": "Zone 5", "lat": 47.0004, "lng": -0.0004, "rayon": 30, "mini_jeu": 5 },
        { "id": 6, "nom": "Zone 6", "lat": 47.0005, "lng": -0.0005, "rayon": 30, "mini_jeu": 6 },
        { "id": 7, "nom": "Zone 7", "lat": 47.0006, "lng": -0.0006, "rayon": 30, "mini_jeu": 7 },
        { "id": 8, "nom": "Zone 8", "lat": 47.0007, "lng": -0.0007, "rayon": 30, "mini_jeu": 8 },
        { "id": 9, "nom": "Zone 9", "lat": 47.0008, "lng": -0.0008, "rayon": 30, "mini_jeu": 9 }
      ]
    },
    "parcours_2": {
      "nom": "Nom parcours 2",
      "emoji": "🚶",
      "code": "P2",
      "description": "Description",
      "zones": [ /* MÊME FORMAT × 9 zones */ ]
    },
    "parcours_3": {
      "nom": "Nom parcours 3",
      "emoji": "🏔️",
      "code": "P3",
      "description": "Description",
      "zones": [ /* MÊME FORMAT × 9 zones */ ]
    }
  }
}
```

**⚠️ Règles importantes :**
- `"rayon": 30` = 30 mètres. Augmenter à 50 pour zones ouvertes, baisser à 20 en zone dense
- `"mini_jeu": N` doit correspondre au fichier `minijeux/niveauN.html` (1 à 9)
- Chaque parcours DOIT avoir exactement 9 zones
- Les coordonnées GPS se trouvent sur Google Maps : clic droit → "Qu'y a-t-il ici ?"

---

## 🎮 ÉTAPE 2B — Créer tes mini-jeux (`minijeux/niveauN.html`)

### Template minimal d'un mini-jeu (à copier pour chaque niveau)

```html
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
  <link rel="stylesheet" href="../css/minijeux.css">
  <style>
    /* Fond du mini-jeu */
    html, body { background: #000 url(../assets/backgrounds/bg-n1.svg) center/cover no-repeat; }
    /* Tes styles CSS ici */
  </style>
</head>
<body>
<div id="hud-bar"></div>
<canvas id="cv"></canvas>
<script src="shared.js"></script>
<script>
/* ══════════════════════════════════════════════════════
   CONFIGURATION OBLIGATOIRE (avant tout le reste)
══════════════════════════════════════════════════════ */
window.NIVEAU = 1;                      // ← numéro 1 à 9
window.GPS0_TIMER_SEC = 150;            // ← durée en secondes (ex: 90, 120, 150, 180, 300)
window.GPS0_onTimerExpired = function(){ endGame(true); };  // ← 'true' = victoire si survie
                                        //   'false' = défaite si temps écoulé
window.TUTO_TEXT = "Ton texte de tuto ici !<br><small>Sous-texte optionnel</small>";

/* OPTIONS AVANCÉES (toutes facultatives) */
// window.GPS0_MAX_LIVES = 3;           // ← vies (défaut: 3)
// window.GPS0_HIDE_TIMER = true;       // ← cache le timer (jeux sans chrono)
// window.GPS0_rewardOverride = 50;     // ← forcer une récompense fixe (50 poussières)

/* ══════════════════════════════════════════════════════
   FONCTIONS OBLIGATOIRES
══════════════════════════════════════════════════════ */

// Appelé quand le joueur clique GO! (après le tuto)
window.gameStart = function() {
  // Lance ton jeu ici
  loop();
};

// Appelé quand le joueur clique "Rejouer"
window.gameReset = function() {
  // Réinitialise toutes tes variables de jeu
  // ⚠️ NE PAS appeler gameStart() ici — shared.js le fait automatiquement
};

/* ══════════════════════════════════════════════════════
   TON CODE DE JEU
══════════════════════════════════════════════════════ */
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');

function loop() {
  if (!GPS0_running()) return;          // ← TOUJOURS vérifier en début de boucle
  requestAnimationFrame(loop);

  ctx.clearRect(0, 0, cv.width, cv.height);
  // ... ton rendu ici
}

/* ══════════════════════════════════════════════════════
   FONCTIONS FOURNIES PAR shared.js (utilisables partout)
══════════════════════════════════════════════════════ */
// GPS0_running()          → true si le jeu tourne
// loseLife()              → retire 1 vie (game over si vies = 0)
// addDust(n)              → ajoute n poussières au score
// endGame(success)        → termine le jeu (true=victoire, false=défaite)
// GPS0_timerSec()         → retourne les secondes restantes
// drawCosmonaut(ctx, x, y, r, angle, state) → dessine le cosmonaute
//   states: 'idle' | 'run' | 'fly' | 'jump'
// GPS0_resizeCanvas(canvas) → adapte le canvas à l'écran

</script>
</body>
</html>
```

### Contrat des mini-jeux — Ce que shared.js gère automatiquement

| Fonctionnalité | Géré par shared.js | Tu t'en occupes |
|---|---|---|
| Compte à rebours "3…2…1…GO!" | ✅ | ❌ |
| Affichage du tutoriel | ✅ | ❌ |
| Timer en secondes | ✅ | ❌ |
| Barre de vies | ✅ | ❌ |
| Score dust | ✅ | ❌ |
| Overlay victoire/défaite | ✅ | ❌ |
| Bouton "Rejouer" | ✅ | ❌ |
| Envoi du résultat à l'app | ✅ | ❌ |
| Calcul des poussières | ✅ | ❌ |
| Dessin du cosmonaute | ✅ (drawCosmonaut) | ❌ |
| Logique du jeu | ❌ | ✅ |
| Rendu graphique | ❌ | ✅ |
| Détection de victoire/défaite | ❌ | ✅ (via endGame/loseLife) |

### Formule de récompense automatique (shared.js)

```
tempsJoue = timerTotal - timerSec   (secondes écoulées)

Victoire : finalDust = floor( tempsJoue / timerTotal × 50 )  → max 50 poussières
Défaite  : finalDust = floor( tempsJoue / timerTotal × 15 )  → max 15 poussières
```

Plus le joueur joue longtemps, plus il gagne de poussières.  
Pour un jeu avec récompense fixe : `window.GPS0_rewardOverride = 50;` avant `endGame(true)`.

---

## 🎨 ÉTAPE 2C — Changer le thème (`css/main.css`)

Seules les variables CSS au début du fichier sont à modifier :

```css
:root {
  --bg:      #0A0A1A;    /* Couleur de fond principale (espace noir) */
  --bg2:     #0D1B2A;    /* Couleur de fond secondaire (dégradé bas) */
  --accent:  #C8A2C8;    /* Couleur principale : logo, boutons, accents */
  --gold:    #FFD700;    /* Couleur secondaire : étoiles, sous-titres */
  --ok:      #69FF47;    /* Couleur "succès" (vert) */
  --danger:  #FF6B6B;    /* Couleur "danger" (rouge) */
  --halo-rouge:  #FF3333;
  --halo-orange: #FF8C00;
  --halo-vert:   #69FF47;
  --halo-bleu:   #4FC3F7;  /* Couleur halo boussole direction */
}
```

### Exemples de thèmes prêts à l'emploi

| Thème | --bg | --bg2 | --accent | --gold |
|---|---|---|---|---|
| 🌊 Océan | `#030d1a` | `#051e38` | `#4FC3F7` | `#00d4aa` |
| 🌿 Forêt | `#071a07` | `#0d2e0d` | `#69FF47` | `#FFD700` |
| 🔥 Volcan | `#1a0305` | `#2e0a0d` | `#FF6B6B` | `#FF8C00` |
| 🏙️ Urbain | `#101018` | `#181820` | `#4FC3F7` | `#C8A2C8` |
| 🌸 Sakura | `#1a0718` | `#2e0d2a` | `#FFB6C1` | `#FF69B4` |

**Changer le nom du jeu dans le splash :**  
Dans `index.html`, chercher `<h1 class="logo-gps0">GPS0</h1>` → remplacer par `GPS1`.

---

## 🖼️ ÉTAPE 2D — Backgrounds des mini-jeux (`assets/backgrounds/`)

Chaque `bg-nX.svg` est utilisé comme arrière-plan du mini-jeu X.  
Format : SVG vectoriel, viewBox quelconque, taille d'affichage = 100% de l'écran.

Template SVG minimal :
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">
  <!-- Fond gradient -->
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0a0a1a"/>
      <stop offset="100%" stop-color="#1a0a2e"/>
    </linearGradient>
  </defs>
  <rect width="400" height="800" fill="url(#bg)"/>
  <!-- Ajoute tes éléments décoratifs SVG ici -->
</svg>
```

---

## 🗨️ ÉTAPE 2E — Dialogues de la Lune (`js/lune.js`)

Chercher l'objet `const R = { ... }` en début de fichier et modifier les tableaux de répliques.  
Chaque catégorie est un tableau de strings. Lune pioche au hasard dans un tableau.

```javascript
const R = {
  arrivee_zone: [
    // Joué quand le joueur arrive à une zone GPS
    "Réplique 1",
    "Réplique 2",
  ],
  navigation_lente: [
    // Joué si le joueur bouge peu pendant longtemps
  ],
  navigation_erratique: [
    // Joué si le joueur change souvent de direction
  ],
  energie_faible: [
    // Joué quand l'énergie descend sous 30%
  ],
  performance_excellente: [
    // Joué après un mini-jeu réussi vite
  ],
  avant_boss: [
    // Joué avant le niveau 9 (boss)
  ],
  random_fun: [
    // Joué aléatoirement pendant la navigation
  ],
  signal_faible: [
    // Joué quand le GPS est imprécis (accuracy > 25m)
  ]
};
```

---

## 📱 ÉTAPE 2F — Manifest PWA (`manifest.json`)

```json
{
  "name": "GPS1",
  "short_name": "GPS1",
  "start_url": "./index.html",
  "scope": "./",
  "display": "fullscreen",
  "orientation": "portrait",
  "background_color": "#0A0A1A",
  "theme_color": "#0A0A1A",
  "description": "Ton aventure GPS urbaine",
  "icons": []
}
```

---

## ⚙️ ÉTAPE 3 — Service Worker (après chaque modification)

Dans `service-worker.js`, la première ligne est :
```javascript
const CACHE = 'gps0-v71';
```

→ Changer le préfixe : `'gps1-v1'`  
→ Incrémenter le numéro à **chaque fois** qu'un fichier est modifié.

Si tu ne l'incrémentes pas, les joueurs verront l'ancienne version.

---

## 🚀 ÉTAPE 4 — Déploiement GitHub Pages

```bash
git add -A
git commit -m "[GPS1] Initial clone depuis GPS0"
git push origin main
```

Puis dans les Settings GitHub du repo → Pages → Source : `main` branch.  
URL : `https://[TON_COMPTE].github.io/GPS1/`

---

## 📋 Checklist finale avant livraison

```
□ gps_config.json — 3 parcours × 9 zones, coordonnées réelles testées
□ niveau1.html à niveau9.html — 9 jeux fonctionnels, window.NIVEAU correct
□ Chaque niveauN a : GPS0_TIMER_SEC, GPS0_onTimerExpired, TUTO_TEXT, gameStart(), gameReset()
□ css/main.css — variables :root adaptées au thème
□ index.html — titre GPS0 → GPS1
□ manifest.json — name/short_name mis à jour
□ assets/backgrounds/bg-n1-9.svg — fonds adaptés au thème
□ js/lune.js — répliques adaptées au thème/univers
□ service-worker.js — CACHE = 'gps1-vX' avec X incrémenté
□ Test en mode demo (bouton debug dans l'app) pour chaque niveau
□ Test GPS terrain sur au moins 1 zone
```

---

## 🧩 Ce que tu n'as PAS besoin de toucher

Ces fichiers forment le **moteur GPS0** — stable, testé, réutilisable tel quel :

| Fichier | Rôle |
|---|---|
| `js/app.js` | Orchestration principale (onboarding, parcours, jeux, fin) |
| `js/gps.js` | Tracking GPS (Haversine, précision 25m, 3 confirmations) |
| `js/boussole.js` | Boussole SVG + états |
| `js/economie.js` | Énergie, poussière, boutique |
| `js/audio.js` | Web Audio API (sons synthétisés + MP3) |
| `js/avatar.js` | Selfie cosmonaute |
| `js/finale.js` | Cinématique de fin |
| `js/moteur-minijeu.js` | Lanceur iframe mini-jeux |
| `minijeux/shared.js` | Moteur commun jeux (NE JAMAIS MODIFIER) |
| `svg/icons.svg` | Boussole, fusée, astéroïde |
| `css/minijeux.css` | HUD des mini-jeux |
| `assets/audio/sfx/*.mp3` | 12 sons d'effets |

---

## ⚡ Résumé en une phrase

> **Copie GPS0, change `gps_config.json` (tes points GPS), les 9 `niveauN.html` (tes jeux), le thème dans `:root` de `main.css`, et incrémente le cache dans `service-worker.js`. C'est tout.**
