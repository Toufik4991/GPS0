# GPS0 — gddV5 — Document Maître Final

---

## 1. IDENTITÉ DU PROJET

- **Nom** : GPS0
- **Type** : Jeu mobile 2D narratif — PWA (Progressive Web App)
- **Techno** : HTML5, CSS3, JavaScript vanilla (zero framework, zero bundler)
- **URL déployée** : https://toufik4991.github.io/GPS0/
- **Repo GitHub** : https://github.com/Toufik4991/GPS0
- **Version** : 3.45.0 — Service Worker `gps0-v62`
- **Date de cette version** : 22 mars 2026
- **Auteur** : Toufik

---

## 2. CONCEPT DU JEU

GPS0 est une aventure GPS cosmique urbaine jouable sur smartphone. Le joueur incarne un cosmonaute qui explore le monde réel grâce au GPS et à la boussole de son téléphone. À chaque point GPS atteint dans le monde réel, un mini-jeu se débloque. L'objectif est de collecter des poussières d'étoiles à travers 9 mini-jeux variés puis d'affronter le boss solaire final. La Lune, personnage narrateur sarcastique, commente la progression du joueur tout au long de l'aventure.

---

## 3. ARBORESCENCE FINALE

```
GPS0/
├── index.html              — Page principale (SPA), contient tous les écrans/modals
├── service-worker.js       — Service Worker PWA, cache CORE v62
├── manifest.json           — Manifest PWA (fullscreen, portrait, icônes)
├── gps_config.json         — Configuration des 3 parcours GPS (9 zones chacun)
├── boutique_config.json    — Catalogue des 3 fragments de lune (boutique)
├── .gitignore              — Exclusions git (scripts temp, backups)
├── README.md               — Readme minimal
│
├── css/
│   ├── main.css            — Styles globaux (HUD, boussole, modals, animations, responsive)
│   └── minijeux.css        — Styles partagés des mini-jeux (imports)
│
├── js/
│   ├── app.js              — Contrôleur principal (init, navigation, modals, iframe mini-jeux)
│   ├── audio.js            — Système audio (Web Audio API, musiques, SFX synthétisés + fichiers)
│   ├── avatar.js           — Capture selfie caméra (32×32 base64, injection CSS)
│   ├── boussole.js         — Boussole (états, halo distance, rotation fusée)
│   ├── economie.js         — Économie (énergie, poussières, fragments, cooldowns, HUD)
│   ├── finale.js           — Séquence finale (zoom selfie, confettis, BRAVO, score, BISOUS)
│   ├── gps.js              — Suivi GPS (watchPosition, Haversine, émetteur événements)
│   ├── lune.js             — Personnage Lune (dialogues par catégorie, queue, surveillance)
│   ├── minijeux.js         — Stub lance-jeux (le vrai lancement est dans app.js via iframe)
│   └── moteur-minijeu.js   — Moteur auto-runner/platformer (physique, plateformes, ennemis)
│
├── minijeux/
│   ├── shared.js           — Infrastructure commune des mini-jeux (HUD, timer, vies, cosmonaute)
│   ├── niveau1.html        — N1 : Glisse la Fronde (slingshot physique)
│   ├── niveau2.html        — N2 : Oiseau Magma (flappy bird lave)
│   ├── niveau3.html        — N3 : Astéroïdes Rebonds (platformer rebond)
│   ├── niveau4.html        — N4 : Séquence Cristaux (simon mémoire)
│   ├── niveau5.html        — N5 : 1,2,3 Soleil ! (red light green light)
│   ├── niveau6.html        — N6 : Agar.io Cosmique (agar.io + joystick)
│   ├── niveau7.html        — N7 : Mots Cosmiques (devinettes mots + clavier AZERTY)
│   ├── niveau8.html        — N8 : Station Alien (dodge vertical, vaisseaux)
│   └── niveau9.html        — N9 : Boss Solaire (combat boss SVG + Canvas)
│
├── assets/
│   ├── backgrounds/
│   │   ├── bg-n3.svg       — Fond N3 : champ d'astéroïdes bleu profond
│   │   ├── bg-n4.svg       — Fond N4 : caverne de cristaux purple
│   │   ├── bg-n5.svg       — Fond N5 : course au soleil (rayons dorés)
│   │   ├── bg-n6.svg       — Fond N6 : grille agar.io cosmique
│   │   ├── bg-n7.svg       — Fond N7 : lettres flottantes + constellations
│   │   ├── bg-n8.svg       — Fond N8 : station métallique industrielle
│   │   └── bg-n9.svg       — Fond N9 : void infernal solaire
│   │
│   └── audio/
│       ├── musique/
│       │   ├── exploration/
│       │   │   ├── musique_menu0.mp3   — Musique exploration #0
│       │   │   ├── musique_menu1.mp3   — Musique exploration #1
│       │   │   ├── musique_menu2.mp3   — Musique exploration #2
│       │   │   ├── musique_menu3.mp3   — Musique exploration #3
│       │   │   └── musique_menu4.mp3   — Musique exploration #4
│       │   └── finale/
│       │       └── musique_finale.mp3  — Musique séquence finale
│       └── sfx/
│           ├── achat.mp3               — SFX achat boutique
│           ├── boss_hit.mp3            — SFX touche boss
│           ├── boussole_on.mp3         — SFX activation boussole
│           ├── boussole_off.mp3        — SFX désactivation boussole
│           ├── collecte_poussiere.mp3  — SFX collecte poussière
│           ├── ennemi_touche.mp3       — SFX ennemi touché
│           ├── halo_bip.mp3            — SFX feedback distance
│           ├── laser_warning.mp3       — SFX alerte laser
│           ├── lune_apparait.mp3       — SFX apparition bulle lune
│           ├── plateforme_active.mp3   — SFX plateforme
│           ├── saut_cosmonaute.mp3     — SFX saut
│           └── zone_detectee.mp3       — SFX zone atteinte
│
├── svg/
│   └── icons.svg           — Symboles SVG inline (gradient astéroïde, filtre glow, sablier)
│
└── docs/
    ├── gddV3.md            — GDD historique (changelog bugs 1-26)
    └── gddV5.md            — CE FICHIER — Document maître final
```

---

## 4. ARCHITECTURE TECHNIQUE

### 4.1 Structure générale

Le projet est une **SPA (Single Page Application)** pure HTML/CSS/JS sans framework. Tout est dans `index.html` qui charge les modules JS via `<script>`. Les mini-jeux sont lancés dans des `<iframe>` qui communiquent avec l'app parente via `postMessage`.

### 4.2 Chaîne de chargement

```
index.html
 ├── css/main.css (styles globaux)
 ├── svg/icons.svg (symboles SVG inline)
 ├── js/audio.js → window.GPS0_Audio
 ├── js/avatar.js → window.GPS0_Avatar
 ├── js/gps.js → window.GPS0_GPS
 ├── js/boussole.js → window.GPS0_Boussole
 ├── js/economie.js → window.GPS0_Economie
 ├── js/lune.js → window.GPS0_Lune
 ├── js/minijeux.js → window.GPS0_MiniJeu (stub)
 ├── js/finale.js → window.GPS0_Finale
 └── js/app.js → window.GPS0_App (contrôleur principal, s'initialise)
```

Chaque module est une **IIFE** (Immediately Invoked Function Expression) exportée sur `window.GPS0_*`.

### 4.3 Flux de navigation

```
Splash (logo + bouton)
  → Permissions (GPS + caméra)
    → Pseudo (saisie nom)
      → Selfie (capture caméra 32×32)
        → Parcours (choix itinéraire ou code)
          → Difficulté (4 niveaux)
            → Chargement config GPS
              → Écran principal (HUD + boussole + lune)
                → Navigation GPS vers zone N
                  → Zone atteinte → Boutons JOUER / SUIVANT
                    → Mini-jeu (iframe) → Résultat → Poussières
                      → Zone suivante → ... → Zone 9 (final: true)
                        → Séquence Finale (5 phases)
```

### 4.4 Système de sauvegarde (localStorage)

| Clé | Format | Usage |
|-----|--------|-------|
| `gps0_pseudo` | string | Nom du joueur |
| `gps0_avatar_selfie_base64` | string (data:image/png;base64,...) | Selfie 32×32 |
| `gps0_difficulte` | string ("clair"/"cache"/"eclipse"/"trou_noir") | Difficulté choisie |
| `gps0_code_balade` | string | Code parcours rejoint |
| `gps0_zones_actives` | JSON array [{id, nom, lat, lng, rayon, mini_jeu}] | Progression zones |
| `gps0_economie` | JSON {energie:{actuelle,max}, poussieres, fragments:{}, cooldowns:{}} | État économie |
| `gps0_audio_enabled` | "1" / "0" | Son activé/désactivé |
| `gps0_lune_repliques_vues` | JSON object {catégorie: [indices]} | Répliques déjà vues |
| `gps0_perms_asked` | "1" | Permissions déjà demandées |
| `gps0_debug_on` | "1" / "0" | Mode debug |

La sauvegarde se fait immédiatement à chaque changement d'état (énergie, poussières, progression zone).

---

## 5. ÉCRANS DU JEU

### 5.1 Splash (`#splash`)
- Logo GPS0 avec animation pulse
- Bouton "DÉMARRER L'AVENTURE"
- Transition : → Permissions

### 5.2 Permissions (`#modal-permissions`)
- Demande accès GPS et caméra
- Boutons "Autoriser" / "Plus tard"
- Transition : → Pseudo

### 5.3 Pseudo (`#modal-pseudo`)
- Champ texte pour saisir son nom de cosmonaute
- Bouton confirmer
- Transition : → Selfie

### 5.4 Selfie (`#modal-selfie`)
- Flux vidéo caméra dans un hublot circulaire
- Bouton "Capturer" → aperçu 200×200
- Boutons "Recommencer" / "Valider" / "Passer"
- Transition : → Parcours

### 5.5 Parcours (`#modal-parcours`)
- Grille de parcours prédéfinis (3 itinéraires)
- OU champ de saisie code pour rejoindre un parcours
- Transition : → Difficulté

### 5.6 Difficulté (`#modal-difficulte`)
- 4 niveaux :
  - 🌕 Clair de Lune (facile)
  - 🌗 Face Cachée (normal)
  - 🌑 Éclipse Totale (dur)
  - 🕳️ Trou Noir (extrême)
- Affecte la consommation d'énergie
- Transition : → Écran principal

### 5.7 Écran principal (`#app`)
- **HUD haut** : poussières ✨, énergie %, chrono global, boutons boutique/inventaire/menu
- **Centre** : astéroïde avec anneau d'énergie + fusée directionnelle + halo coloré de distance
- **Bulle Lune** : dialogues sarcastiques de la lune (apparaît/disparaît auto)
- **Barre objectif** : objectif textuel + progression "X/9"
- **Boutons zone** : apparaissent quand zone GPS atteinte → "JOUER 🎮" / "POINT SUIVANT →"

### 5.8 Mini-jeu (iframe plein écran)
- Chargé dans iframe depuis `minijeux/niveauX.html`
- HUD intégré : ❤❤❤ vies, timer, score poussières
- Countdown 3-2-1-GO avant démarrage
- Tutoriel overlay au premier lancement
- Bouton ✕ quitter avec confirmation
- Résultat envoyé au parent via `postMessage`

### 5.9 Résultats (overlay dans app)
- Affiche : succès/échec, poussières gagnées, temps joué
- Bouton "Continuer" → zone suivante

### 5.10 Boutique (`#modal-boutique`)
- 3 fragments de lune achetables avec poussières
- Chaque fragment restaure de l'énergie

### 5.11 Inventaire (`#modal-inventaire`)
- Fragments possédés avec bouton "Utiliser"
- Stats résumées

### 5.12 Séquence Finale
- 5 phases automatiques (voir §9 Narration)
- Créée dynamiquement par `finale.js`

---

## 6. SYSTÈME GPS & NAVIGATION

### 6.1 Boussole
- **États** : `off` → `on` → `zone` (quand atteinte) → `epuise` (énergie 0)
- **Fusée SVG** : pointe vers la direction du prochain point GPS en temps réel
- **Calcul** : cap magnétique du téléphone (`deviceorientationabsolute`) combiné au bearing GPS (Haversine)
- **Fichier** : `js/boussole.js`

### 6.2 Points GPS
- Définis dans `gps_config.json`
- Structure par zone : `{id, nom, lat, lng, rayon, mini_jeu, final?}`
- Rayon de détection : 30 mètres par défaut
- Zone finale : `"final": true` sur le point 9

### 6.3 Halo de distance
- Anneau lumineux autour de l'astéroïde central
- Couleur dynamique :
  - **Rouge** : > 200m
  - **Orange** : 100-200m
  - **Vert** : 50-100m
  - **Bleu pulsant** : < 50m (zone proche)

### 6.4 Fusée SVG
- Wrapper 104×104px centré sur l'astéroïde (200×200 parent)
- SVG 131×131px, rotation CSS `transform: rotate(Xdeg)`
- Direction = bearing vers zone cible − heading magnétique du téléphone

### 6.5 Astéroïde
- Anneau d'énergie SVG (cercle de progression)
- Centré dans le compass-panel
- Glow animé selon la distance

### 6.6 Distance
- Calcul Haversine (lat/lng → mètres)
- Pas d'affichage numérique (choix design v3.2, feedback uniquement via halo coloré)

---

## 7. LES 9 POINTS + BOSS

### Point 1 — Glisse la Fronde
- **Fichier** : `minijeux/niveau1.html`
- **Mécanique** : Slingshot physique. Glisser pour viser, relâcher pour tirer des orbes sur des météorites. 3 vagues de difficulté croissante. Étoiles bonus collectables.
- **Rendu** : Canvas 2D
- **Timer** : 150s (défaut shared.js)
- **Poussières** : Variables selon étoiles bonus collectées (max ~50)
- **STATUT** : ✅ Fonctionnel

### Point 2 — Oiseau Magma
- **Fichier** : `minijeux/niveau2.html`
- **Mécanique** : Flappy bird cosmique. Tap pour monter, relâcher pour tomber. Éviter les murs de lave avec gap rétrécissant. Collecter des cristaux.
- **Rendu** : Canvas 2D
- **Timer** : 150s
- **Poussières** : 1 par cristal collecté (max 5 cristaux + survie bonus)
- **STATUT** : ✅ Fonctionnel

### Point 3 — Astéroïdes Rebonds
- **Fichier** : `minijeux/niveau3.html`
- **Mécanique** : Platformer à rebond automatique. Tap gauche/droite pour se déplacer. Esquiver les astéroïdes, monter vers le sommet. Bulle protectrice après un hit.
- **Rendu** : Canvas 2D
- **Timer** : 120s
- **Fond** : `bg-n3.svg` (champ d'astéroïdes bleu)
- **Poussières** : Cristaux collectés en montant (variable)
- **STATUT** : ✅ Fonctionnel

### Point 4 — Séquence Cristaux
- **Fichier** : `minijeux/niveau4.html`
- **Mécanique** : Simon Says mémoire. 9 cristaux colorés s'allument en séquence. Reproduire la séquence. 15 rounds en 3 tiers. 1 erreur = bouclier, 2 erreurs = vie perdue.
- **Rendu** : Canvas 2D
- **Timer** : 300s (5 min)
- **Fond** : `bg-n4.svg` (caverne de cristaux)
- **Poussières** : 0-50 selon rounds atteints (1+2+7 par tier)
- **STATUT** : ✅ Fonctionnel

### Point 5 — 1, 2, 3 Soleil !
- **Fichier** : `minijeux/niveau5.html`
- **Mécanique** : Red light / green light spatial. Tap pour avancer quand le soleil a le dos tourné. STOP immédiat quand il se retourne. Barre de progression 0→100%.
- **Rendu** : Canvas 2D
- **Timer** : 150s
- **Fond** : `bg-n5.svg` (rayons solaires)
- **Poussières** : 50 si < 90s, sinon 30
- **STATUT** : ✅ Fonctionnel

### Point 6 — Agar.io Cosmique
- **Fichier** : `minijeux/niveau6.html`
- **Mécanique** : Clone d'Agar.io. Joystick tactile pour déplacer sa cellule. Manger les ennemis plus petits, fuir les plus gros. Collecter des cristaux. 1 seule vie.
- **Rendu** : Canvas 2D + joystick DOM
- **Timer** : 150s
- **Fond** : `bg-n6.svg` (grille agar.io)
- **Poussières** : 1 par cristal (max 50)
- **STATUT** : ✅ Fonctionnel

### Point 7 — Mots Cosmiques
- **Fichier** : `minijeux/niveau7.html`
- **Mécanique** : Devinettes de mots spatiaux. 10 définitions avec émoji. Sélectionner un mot, taper les lettres au clavier AZERTY agrandi, valider. Animation étoiles explosives par mot trouvé.
- **Rendu** : DOM (cartes + clavier) + Canvas FX (étoiles)
- **Timer** : 150s
- **Fond** : `bg-n7.svg` (lettres + constellations)
- **Mots** : ETOILE, COMETE, ORBITE, NEBULEUSE, CRATERE, GALAXIE, SATELLITE, FUSEE, APESANTEUR, COSMOS
- **Poussières** : 2 par mot + 30 bonus si 10/10 = 50 max
- **STATUT** : ✅ Fonctionnel

### Point 8 — Station Alien
- **Fichier** : `minijeux/niveau8.html`
- **Mécanique** : Dodge vertical. Maintenir pour monter, relâcher pour descendre. Éviter les vaisseaux aliens qui traversent. 3 phases avec accélération. 10s sans input = vie perdue.
- **Rendu** : Canvas 2D
- **Timer** : 120s
- **Fond** : `bg-n8.svg` (panneaux métalliques)
- **Poussières** : Cristaux collectés (variable)
- **STATUT** : ✅ Fonctionnel

### Point 9 — Boss Solaire (Affrontement Éclipse)
- **Fichier** : `minijeux/niveau9.html`
- **Mécanique** : Combat boss. Esquiver projectiles, lasers et bombes solaires. Taper l'œil du boss quand il brille pour infliger des dégâts. 3 phases × 45s avec difficulté croissante.
- **Rendu** : SVG (boss) + Canvas (gameplay) hybride
- **Timer** : 150s
- **Fond** : `bg-n9.svg` (void infernal)
- **Poussières** : 6 par hit réussi × 3 phases (max variable)
- **STATUT** : ✅ Fonctionnel

---

## 8. SYSTÈME DE POUSSIÈRES

### 8.1 Comment elles sont gagnées

Les poussières d'étoiles (✨) sont la monnaie du jeu. Elles sont gagnées exclusivement en jouant aux mini-jeux. Chaque mini-jeu a son propre système de récompense.

### 8.2 Tableau récapitulatif

| Niveau | Jeu | Poussières min | Poussières max | Méthode |
|--------|-----|---------------|----------------|---------|
| N1 | Fronde | 0 | ~50 | Étoiles bonus + survie |
| N2 | Oiseau Magma | 0 | ~50 | Cristaux + survie |
| N3 | Astéroïdes | 0 | ~50 | Cristaux en montant |
| N4 | Cristaux Mémoire | 0 | 50 | Rounds atteints (3 tiers) |
| N5 | 1,2,3 Soleil | 30 | 50 | 50 si <90s, sinon 30 |
| N6 | Agar.io | 0 | 50 | 1 par cristal (50 max) |
| N7 | Mots | 0 | 50 | 2/mot + 30 bonus (10/10) |
| N8 | Station | 0 | ~50 | Cristaux collectés |
| N9 | Boss | 0 | ~54 | 6/hit × phases |

**Maximum théorique total** : ~450-500 poussières (si tous les niveaux joués parfaitement)

### 8.3 Stockage

Clé localStorage : `gps0_economie` → champ `poussieres` (entier)

### 8.4 Usage

- **Boutique** : acheter des fragments de lune (30/60/100 poussières)
- **Score final** : affiché dans la séquence finale
- **Narratif** : représente l'énergie cosmique collectée pendant l'aventure

### 8.5 Affichage

- HUD principal : icône ✨ + nombre
- HUD mini-jeu : "X ✨" en haut à droite
- Résultats : total gagné affiché

---

## 9. NARRATION

### 9.1 Histoire

Le joueur est un cosmonaute échoué sur Terre qui doit retrouver son chemin à travers 9 points GPS disséminés dans la ville. À chaque point, un défi cosmique l'attend sous forme de mini-jeu. La Lune, personnage sarcastique et moqueur, l'accompagne en commentant ses actions. Après avoir vaincu le boss solaire au point 9, le cosmonaute complète sa mission et reçoit les félicitations.

### 9.2 Personnages

- **Le Cosmonaute** : avatar du joueur (sprite détaillé avec casque, jetpack, visière affichant le selfie). Dessiné procéduralement dans `shared.js` via `drawCosmonaut()`.
- **La Lune** : narratrice sarcastique. Apparaît dans une bulle de dialogue. 7 catégories de répliques + commentaires aléatoires.

### 9.3 Dialogues de la Lune

| Catégorie | Déclencheur | Exemples |
|-----------|-------------|----------|
| `arrivee_zone` | Zone GPS atteinte | "Oh, t'as quand même réussi à trouver..." |
| `navigation_lente` | Vitesse faible | "Une tortue spatiale irait plus vite !" |
| `navigation_erratique` | Direction instable | "Tu tournes en rond comme un satellite déréglé !" |
| `energie_faible` | Énergie < 20% | "Tu vas vider ta batterie avant Mars !" |
| `performance_excellente` | Bon score | "Pas mal pour un terrien !" |
| `avant_boss` | Avant zone 9 | "Le boss arrive. Bonne chance..." |
| `random_fun` | Toutes les 180s | Commentaires aléatoires |

**Système anti-spam** : 8s minimum entre bulles, max 2/minute, queue de messages, suppression pendant mini-jeux. Rotation des répliques non vues.

### 9.4 Séquence finale (5 phases)

| Phase | Timing | Description |
|-------|--------|-------------|
| 1. Zoom Face | 0-3s | Selfie du joueur zoom avec glow doré (120px circle) |
| 2. Confettis | 0-20s | 50 émoji étoiles + 30 particules tombantes |
| 3. BRAVO | +2s | "🎉 BRAVO {PSEUDO} 🎉" texte doré lumineux |
| 4. Score | +4s | Récap stats : 💫 poussières, 🎮 jeux gagnés, ⏱️ temps |
| 5. Continuer | +7s | Bouton "Continuer 🌙" → fondu vers "BISOUS 💋" |

---

## 10. VISUELS & ASSETS

### 10.1 SVG Backgrounds (7 fichiers)

| Fichier | Thème | Couleur dominante |
|---------|-------|-------------------|
| bg-n3.svg | Champ d'astéroïdes, nébuleuse, rochers flottants | Bleu profond #050510 |
| bg-n4.svg | Caverne cristaux, stalactites, glow gaussien | Purple #060310 |
| bg-n5.svg | Rayons solaires, sentier d'étoiles | Violet→noir #1a0e2e |
| bg-n6.svg | Grille agar.io, particules nourriture | Noir + vert lime |
| bg-n7.svg | Lettres flottantes, lignes constellations | Bleu-purple #0a0a1a |
| bg-n8.svg | Panneaux métal, rivets, voyants industriels | Gris sombre #060610 |
| bg-n9.svg | Void infernal, lueur solaire, éruptions | Noir→orange #1a0800 |

### 10.2 Fichiers audio

**Musiques (6 fichiers) :**
- `musique_menu0.mp3` à `musique_menu4.mp3` — 5 pistes d'exploration (rotation automatique)
- `musique_finale.mp3` — Musique de la séquence finale

**SFX fichiers (12 fichiers) :**
- `achat.mp3`, `boss_hit.mp3`, `boussole_on.mp3`, `boussole_off.mp3`
- `collecte_poussiere.mp3`, `ennemi_touche.mp3`, `halo_bip.mp3`
- `laser_warning.mp3`, `lune_apparait.mp3`, `plateforme_active.mp3`
- `saut_cosmonaute.mp3`, `zone_detectee.mp3`

**SFX synthétisés (Web Audio API, dans audio.js) :**
- `tap` — Bip de touche
- `perte_vie` — Son de dégât
- `victoire` — Fanfare courte
- `defaite` — Son triste
- `countdown` — Bip countdown 3-2-1
- `countdown_go` — Bip GO
- `confetti` — Effet confettis
- `boss_ambiance` — Ambiance boss

### 10.3 SVG inline

- `svg/icons.svg` — Gradient astéroïde, filtre glow, symbole sablier

### 10.4 Palette de couleurs

| Usage | Couleur |
|-------|---------|
| Background principal | #0A0A1A |
| Accent primaire (bleu) | #4FC3F7 |
| Or / poussières | #FFD700 |
| Succès | #4CAF50 |
| Danger | #F44336 |
| Halo rouge (loin) | #FF1744 |
| Halo orange (moyen) | #FF9100 |
| Halo vert (proche) | #00E676 |
| Halo bleu (zone) | #448AFF |

### 10.5 Fonts

- `system-ui, sans-serif` — Font système native (aucune font externe)

### 10.6 Style visuel

Thème spatial/cosmique sombre. Fond noir étoilé avec particules animées (CSS parallax). Éléments UI avec `backdrop-filter: blur()`, bordures semi-transparentes, glow effects. Émojis largement utilisés pour les icônes. Design mobile-first avec zones de touche 48px minimum.

---

## 11. SYSTÈMES TECHNIQUES

### 11.1 Canvas

- Chaque mini-jeu (sauf N7) utilise un `<canvas>` 2D redimensionné dynamiquement
- `GPS0_resizeCanvas(cv)` dans shared.js adapte le canvas au container
- N9 utilise un hybride SVG (boss) + Canvas (gameplay)

### 11.2 Animations

- **CSS** : parallax starfield, pulse logo, glow halo, confettis flottants, flame flicker fusée
- **JS/requestAnimationFrame** : boucles de jeu des 9 mini-jeux, particules, explosions étoiles
- **Transitions** : opacity/transform CSS avec timing functions

### 11.3 Géolocalisation

- API : `navigator.geolocation.watchPosition()` (haute précision activée)
- Calcul distance : formule Haversine (js/gps.js)
- Calcul bearing : formule trigonométrique standard
- Rayon de détection zone : 30m (configurable dans gps_config.json)

### 11.4 Caméra

- API : `navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })`
- Capture : canvas 32×32 converti en base64 PNG
- Aperçu : canvas 200×200
- Stocké en localStorage, injecté comme CSS variable dans les jeux

### 11.5 Responsive

- Approche : mobile-first, `100dvh` pour la hauteur
- `viewport-fit=cover` pour les notches iPhone
- `env(safe-area-inset-*)` pour padding safe areas
- Pas de breakpoints desktop (conçu mobile uniquement)
- Touch targets : minimum 48px

### 11.6 Touch events

- Mini-jeux : `touchstart`, `touchmove`, `touchend` sur canvas
- `-webkit-tap-highlight-color: transparent` pour supprimer le flash
- `touch-action: none` pour empêcher scroll/zoom pendant le jeu
- Joystick virtuel (N6) via calcul d'angle touch

### 11.7 Son

- `AudioContext` Web Audio API (createOscillator pour synthèse)
- Gestion suspension/resume du contexte audio
- Toggle on/off avec persistance localStorage
- Musique exploration : 5 pistes en rotation automatique (onended)
- Volume : contrôle via GainNode

### 11.8 Service Worker

- Cache-first strategy pour les ressources CORE (57 fichiers)
- Network-first avec fallback cache pour le reste
- Nettoyage automatique des anciens caches à l'activation
- Force `skipWaiting()` + `clients.claim()` pour mise à jour immédiate

---

## 12. BUGS CONNUS & LIMITATIONS

### 12.1 Bugs fixés pendant l'audit

| Bug | Description | Fix |
|-----|-------------|-----|
| N5 récursion infinie | `window.onResize` → `GPS0_resizeCanvas` → `onResize` → stack overflow | `onResize` appelle uniquement `_fixSize()` |
| N7 grille trop petite | Mots croisés 13×13 illisible sur mobile | Recodé en liste de devinettes + clavier AZERTY agrandi |
| SW JPEG fantômes | 9 entrées `fond_ecran*.jpeg` dans CORE mais fichiers inexistants | Entrées supprimées |
| console.log debug | `js/minijeux.js` loguait en production | Remplacé par commentaire |
| Fichiers orphelins | `bg-n1.svg`, `bg-n2.svg` trackés mais jamais référencés | Retirés du repo |
| .gitkeep inutiles | 4 `.gitkeep` dans dossiers peuplés | Retirés du repo |

### 12.2 Limitations connues

| Limitation | Détail |
|-----------|--------|
| Parcours 3 placeholder | "La Marche Funèbre" a toutes ses coordonnées à (0,0) — non jouable |
| Pas d'icône PWA | `manifest.json` a un tableau `icons: []` vide |
| iOS Safari boussole | `deviceorientationabsolute` non supporté sur iOS < 16.4, fallback sur `deviceorientation` |
| Desktop non supporté | Pas de GPS sur desktop, jeu conçu mobile uniquement |
| Mode hors-ligne partiel | Les assets audio (~10MB) doivent être cachés au premier chargement |
| `_rafIds` / `_evHandlers` | Déclarés dans shared.js mais jamais utilisés (prévus mais non implémentés) |
| Event listener GPS permanent | `deviceorientation` listener jamais retiré (permanent tant que l'app tourne) |
| Musique retry infini | Si tous les fichiers mp3 exploration échouent, `playMusiqueExploration` boucle indéfiniment |
| `boutique_config.json` non utilisé | La boutique utilise les fragments hardcodés dans `economie.js`, pas le fichier JSON externe |

### 12.3 Navigateurs supportés

- ✅ Chrome Android 90+
- ✅ Samsung Internet 15+
- ⚠️ Safari iOS 16.4+ (boussole limitée, permissions supplémentaires)
- ❌ Firefox Android (deviceorientation non fiable)
- ❌ Desktop (pas de GPS)

---

## 13. TABLEAU RÉCAPITULATIF

| Point | Zone GPS (Parcours 1) | Mini-jeu | Timer | Poussières max | Statut |
|-------|----------------------|----------|-------|----------------|--------|
| 1 | Papy Point 1 (47.259, -0.072) | Glisse la Fronde | 150s | ~50 | ✅ |
| 2 | Papy Point 2 (47.259, -0.075) | Oiseau Magma | 150s | ~50 | ✅ |
| 3 | Papy Point 3 (47.260, -0.076) | Astéroïdes Rebonds | 120s | ~50 | ✅ |
| 4 | Papy Point 4 (47.259, -0.074) | Séquence Cristaux | 300s | 50 | ✅ |
| 5 | Papy Point 5 (47.258, -0.076) | 1,2,3 Soleil ! | 150s | 50 | ✅ |
| 6 | Papy Point 6 (47.257, -0.076) | Agar.io Cosmique | 150s | 50 | ✅ |
| 7 | Papy Point 7 (47.257, -0.074) | Mots Cosmiques | 150s | 50 | ✅ |
| 8 | Papy Point 8 (47.254, -0.071) | Station Alien | 120s | ~50 | ✅ |
| 9 | Papy Point 9 (47.256, -0.069) | Boss Solaire | 150s | ~54 | ✅ |

**9/9 mini-jeux fonctionnels. Tous jouables.**

---

## 14. STATS FINALES DU PROJET

| Métrique | Valeur |
|----------|--------|
| Fichiers trackés (git) | 57 |
| Poids total repo | ~11.9 MB |
| Lignes JS | 2 269 |
| Lignes CSS | 336 |
| Lignes HTML | 4 227 |
| **Total lignes de code** | **6 832** |
| Nombre d'écrans/modals | 12 |
| Nombre de mini-jeux | 9 |
| Assets audio (MP3) | 18 |
| Assets SVG backgrounds | 7 |
| Assets SVG inline | 1 |
| Parcours GPS définis | 3 (2 fonctionnels, 1 placeholder) |
| Version Service Worker | gps0-v62 |
| Version App | 3.45.0 |
| Date dernier commit | 22 mars 2026 |

---

*Document généré automatiquement par audit du code source. Chaque information est vérifiable dans les fichiers du repo.*
