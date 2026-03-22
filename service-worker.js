const CACHE = 'gps0-v52';
const APP_VERSION = '3.36.0';
const CORE = [
  'index.html',
  'css/main.css',
  'css/minijeux.css',
  'js/app.js',
  'js/gps.js',
  'js/boussole.js',
  'js/economie.js',
  'js/lune.js',
  'js/avatar.js',
  'js/audio.js',
  'js/minijeux.js',
  'js/moteur-minijeu.js',
  'js/finale.js',
  'gps_config.json',
  'manifest.json',
  'minijeux/shared.js',
  'minijeux/niveau1.html',
  'minijeux/niveau2.html',
  'minijeux/niveau3.html',
  'minijeux/niveau4.html',
  'minijeux/niveau5.html',
  'minijeux/niveau6.html',
  'minijeux/niveau7.html',
  'minijeux/niveau8.html',
  'minijeux/niveau9.html',
  'assets/backgrounds/fond_ecran1.jpeg',
  'assets/backgrounds/fond_ecran2.jpeg',
  'assets/backgrounds/fond_ecran3.jpeg',
  'assets/backgrounds/fond_ecran4.jpeg',
  'assets/backgrounds/fond_ecran5.jpeg',
  'assets/backgrounds/fond_ecran6.jpeg',
  'assets/backgrounds/fond_ecran7.jpeg',
  'assets/backgrounds/fond_ecran8.jpeg',
  'assets/backgrounds/fond_ecran9.jpeg',
  'assets/audio/sfx/achat.mp3',
  'assets/audio/sfx/boussole_on.mp3',
  'assets/audio/sfx/boussole_off.mp3',
  'assets/audio/sfx/boss_hit.mp3',
  'assets/audio/sfx/collecte_poussiere.mp3',
  'assets/audio/sfx/ennemi_touche.mp3',
  'assets/audio/sfx/halo_bip.mp3',
  'assets/audio/sfx/laser_warning.mp3',
  'assets/audio/sfx/lune_apparait.mp3',
  'assets/audio/sfx/plateforme_active.mp3',
  'assets/audio/sfx/saut_cosmonaute.mp3',
  'assets/audio/sfx/zone_detectee.mp3',
  'assets/audio/musique/exploration/musique_menu0.mp3',
  'assets/audio/musique/exploration/musique_menu1.mp3',
  'assets/audio/musique/exploration/musique_menu2.mp3',
  'assets/audio/musique/exploration/musique_menu3.mp3',
  'assets/audio/musique/exploration/musique_menu4.mp3',
  'assets/audio/musique/finale/musique_finale.mp3'
];self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(CORE).catch(() => {})).then(() => self.skipWaiting())
  );
});
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request).then(res => {
      if (res && res.ok) {
        const c = res.clone();
        caches.open(CACHE).then(cc => cc.put(e.request, c));
      }
      return res;
    }).catch(() => caches.match(e.request).then(r => r || caches.match('index.html')))
  );
});
self.addEventListener('message', e => {
  if (e.data === 'GET_VERSION') {
    e.source.postMessage({ type: 'VERSION', version: APP_VERSION, cache: CACHE });
  }
});