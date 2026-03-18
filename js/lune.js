'use strict';
window.GPS0_Lune = (() => {
  const R = {
    arrivee_zone: [
      "Oh, t'as quand même réussi à trouver. J'y croyais plus.",
      "Bon. Te voilà. Tu as mis le temps...",
      "Enfin ! J'ai failli m'endormir en t'attendant.",
      "Tu marches ou tu danses ? Difficile a dire de là-haut.",
      "Ah, le GPS fonctionne encore. Petit miracle quotidien !",
      "Bravo ! Seulement 47 détours pour y arriver.",
      "Tu as trouve ! Mes cratères en tremblent d'émotion."
    ],
    navigation_lente: [
      "Une tortue spatiale irait plus vite !",
      "Tu fais du tourisme ou tu joues ?",
      "À ce rythme, on va rater la prochaine pleine lune.",
      "Mes cratères bougent plus vite que toi.",
      "Tu es sûr que tes jambes fonctionnent encore ?",
      "Meme un satellite en panne va plus rapidement."
    ],
    navigation_erratique: [
      "Tu tournes en rond comme un satellite déréglé !",
      "C'est pas un labyrinthe, juste... tout droit.",
      "Tu cherches quoi ? Le passage secret ?",
      "GPS cassé ou c'est toi qui bugs ?",
      "On dirait une mouche dans un bocal..."
    ],
    energie_faible: [
      "Tu vas vider ta batterie avant d'arriver sur Mars !",
      "Recharge-toi, tu fais pitié à voir.",
      "Économise ton énergie... oh wait, trop tard.",
      "Ta boussole va rendre l'âme, tire-la pas trop.",
      "Meme moi j'ai plus d'energie que toi ce soir.",
      "Allez, un petit effort ! Ou pas..."
    ],
    performance_excellente: [
      "Pas mal pour un terrien ! J'suis presque impressionnée.",
      "Tu connais le chemin par cœur maintenant ?",
      "Bon, t'es pas complètement nul finalement.",
      "Speed run spatial ! Mes compliments.",
      "Tu me rappelles... moi, quand j'etais jeune planète."
    ],
    avant_boss: [
      "Le boss arrive. Bonne chance. (tu vas en avoir besoin)",
      "Dernière ligne droite ! Montre-nous tes talents.",
      "C'est le moment de vérité, petit cosmonaute.",
      "Boss final ! J'espere que t'as pris des vitamines."
    ],
    random_fun: [
      "Tu marches beaucoup pour quelqu'un qui a un écran.",
      "T'as pense à regarder ou tu mets les pieds ?",
      "Alors, cette vie de cosmonaute urbain ?",
      "Tu collectes les poussières d'étoiles... mais moi je fabrique !",
      "J'ai vu passer trois cometes pendant ton dernier trajet.",
      "Tu sais que je t'observe depuis 384 400 km ?",
      "Meme les aliens rigolent de tes trajectoires."
    ]
  };
  const COOLDOWN = 60000;
  let cooling = false, tId = null, dernierT = 0;

  function _loadVus() { try { return JSON.parse(localStorage.getItem('gps0_lune_repliques_vues') || '{}'); } catch { return {}; } }
  function _saveVus(v) { try { localStorage.setItem('gps0_lune_repliques_vues', JSON.stringify(v)); } catch {} }

  function pick(cat) {
    const pool = R[cat] || R.random_fun;
    const vus = _loadVus();
    const seen = vus[cat] || [];
    const dispo = pool.filter((_, i) => !seen.includes(i));
    const src = dispo.length ? dispo : pool;
    const idx = Math.floor(Math.random() * src.length);
    const real = pool.indexOf(src[idx]);
    if (!vus[cat]) vus[cat] = [];
    vus[cat].push(real);
    if (vus[cat].length >= pool.length) vus[cat] = [];
    _saveVus(vus);
    return pool[real];
  }

  function parler(cat) {
    const now = Date.now();
    if (cooling || (now - dernierT) < COOLDOWN) return;
    cooling = true; dernierT = now;
    const bulle = document.getElementById('lune-bulle');
    const txt = document.getElementById('lune-texte');
    if (!bulle || !txt) return;
    txt.textContent = pick(cat);
    bulle.classList.add('visible');
    GPS0_Audio && GPS0_Audio.playSFX('lune_apparait');
    clearTimeout(tId);
    tId = setTimeout(() => { bulle.classList.remove('visible'); cooling = false; }, 5000);
  }

  function demarrerSurveillance() {
    setInterval(() => { if (Math.random() < 0.05) parler('random_fun'); }, 180000);
  }

  return { parler, demarrerSurveillance };
})();
