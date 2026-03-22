"""GPS0 — N9 SVG Boss refonte (Bug 19)
Supprime les yeux lune canvas, ajoute vrai SVG créature boss.
"""

with open('minijeux/niveau9.html', 'r', encoding='utf-8') as f:
    code = f.read()

# ── 1. TUTO_TEXT ───────────────────────────────────────────────────────────────
code = code.replace(
    'window.TUTO_TEXT = "Niveau 9 \u2014 Boss Final \u00b7 Glisse ton doigt pour bouger \u00b7 Tape le boss quand il brille orange \u00b7 3 phases \u00d7 45s";',
    'window.TUTO_TEXT = "\ud83d\udc7b Affronte le Gardien Cosmique ! \u00b7 Glisse pour esquiver \u00b7 Tape quand l\'oeil brille \ud83d\udc41<br><small>3 vies \u00b7 3 phases \u00d7 45s \u00b7 Survive au laser !</small>";'
)

# ── 2. CSS SVG boss ────────────────────────────────────────────────────────────
new_css = """
#boss-wrap{position:absolute;left:50%;top:1%;transform:translateX(-50%);width:min(58vw,240px);pointer-events:none;z-index:5}
#boss-svg{width:100%;height:auto;overflow:visible}
@keyframes bPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.04) translateY(-2px)}}
@keyframes tentWig{0%,100%{transform-box:fill-box;transform-origin:50% 0;transform:rotate(-7deg)}50%{transform-box:fill-box;transform-origin:50% 0;transform:rotate(7deg)}}
.boss-body{animation:bPulse 2.8s ease-in-out infinite}
.boss-tent{animation:tentWig 2.4s ease-in-out infinite}
.boss-tent:nth-child(2){animation-delay:-.55s;animation-duration:2.9s}
.boss-tent:nth-child(3){animation-delay:-1.1s;animation-duration:2.1s}
.boss-tent:nth-child(4){animation-delay:-1.7s;animation-duration:2.6s}
.boss-tent:nth-child(5){animation-delay:-.9s;animation-duration:2.0s}
.boss-tent:nth-child(6){animation-delay:-2.1s;animation-duration:2.5s}
.boss-tent:nth-child(7){animation-delay:-.3s;animation-duration:2.8s}
.boss-tent:nth-child(8){animation-delay:-1.4s;animation-duration:2.2s}
"""
code = code.replace('</style>', new_css + '</style>', 1)

# ── 3. HTML SVG boss (avant <canvas>) ─────────────────────────────────────────
boss_html = """
<div id="boss-wrap">
<svg id="boss-svg" viewBox="0 0 256 220" xmlns="http://www.w3.org/2000/svg">
<defs>
  <radialGradient id="bBodyG" cx="42%" cy="36%" r="62%">
    <stop offset="0%"   stop-color="#7c3acc" id="bbg0"/>
    <stop offset="55%"  stop-color="#380d66" id="bbg1"/>
    <stop offset="100%" stop-color="#140528" id="bbg2"/>
  </radialGradient>
  <radialGradient id="bEyeG" cx="44%" cy="40%" r="58%">
    <stop offset="0%"   stop-color="#ffffff"/>
    <stop offset="20%"  stop-color="#00eeff" id="beye0"/>
    <stop offset="60%"  stop-color="#0040bb" id="beye1"/>
    <stop offset="100%" stop-color="#001133"/>
  </radialGradient>
  <radialGradient id="bGlowG" cx="50%" cy="50%" r="50%">
    <stop offset="0%"   stop-color="#00eeff" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="#00eeff" stop-opacity="0"/>
  </radialGradient>
  <filter id="bGlow" x="-35%" y="-35%" width="170%" height="170%">
    <feGaussianBlur stdDeviation="7" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="bGlowS" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3.5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="tentGlow" x="-50%" y="-30%" width="200%" height="160%">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>

<!-- Halo ambiant -->
<ellipse cx="128" cy="110" rx="120" ry="100" fill="url(#bBodyG)" opacity="0.20" filter="url(#bGlow)"/>

<!-- Tentacules (derrière le corps) -->
<g id="boss-tents">
  <path class="boss-tent" d="M 80,152 Q 38,196 20,240" stroke="#8833cc" stroke-width="8.5" fill="none" stroke-linecap="round" filter="url(#tentGlow)" opacity="0.88"/>
  <path class="boss-tent" d="M 100,160 Q 58,206 40,250" stroke="#6622aa" stroke-width="6.5" fill="none" stroke-linecap="round" filter="url(#tentGlow)" opacity="0.78"/>
  <path class="boss-tent" d="M 128,163 Q 105,218 92,258" stroke="#aa44dd" stroke-width="7.5" fill="none" stroke-linecap="round" filter="url(#tentGlow)" opacity="0.82"/>
  <path class="boss-tent" d="M 155,160 Q 170,212 170,255" stroke="#7733bb" stroke-width="6.5" fill="none" stroke-linecap="round" filter="url(#tentGlow)" opacity="0.78"/>
  <path class="boss-tent" d="M 176,152 Q 218,196 236,240" stroke="#8833cc" stroke-width="8.5" fill="none" stroke-linecap="round" filter="url(#tentGlow)" opacity="0.88"/>
  <path class="boss-tent" d="M 63,128 Q 16,150 0,188" stroke="#5522aa" stroke-width="5.5" fill="none" stroke-linecap="round" filter="url(#tentGlow)" opacity="0.68"/>
  <path class="boss-tent" d="M 193,128 Q 240,150 256,188" stroke="#5522aa" stroke-width="5.5" fill="none" stroke-linecap="round" filter="url(#tentGlow)" opacity="0.68"/>
  <path class="boss-tent" d="M 111,162 Q 72,224 55,264" stroke="#9944dd" stroke-width="5" fill="none" stroke-linecap="round" filter="url(#tentGlow)" opacity="0.62"/>
</g>

<!-- Corps principal -->
<g class="boss-body">
  <ellipse cx="128" cy="108" rx="106" ry="80" fill="url(#bBodyG)" filter="url(#bGlow)"/>
  <!-- Nébuleuses internes -->
  <ellipse cx="105" cy="88" rx="38" ry="28" fill="#aa44cc" opacity="0.13"/>
  <ellipse cx="158" cy="116" rx="26" ry="20" fill="#cc2266" opacity="0.11"/>
  <ellipse cx="92" cy="126" rx="20" ry="15" fill="#4422aa" opacity="0.14"/>
  <ellipse cx="152" cy="90" rx="18" ry="14" fill="#662299" opacity="0.12"/>
</g>

<!-- Halo autour de l'œil -->
<circle cx="128" cy="102" r="54" fill="url(#bGlowG)" filter="url(#bGlow)" id="boss-eye-glow" opacity="0.40"/>

<!-- Œil principal unique -->
<g id="boss-eye">
  <circle cx="128" cy="102" r="44" fill="url(#bEyeG)" filter="url(#bGlowS)"/>
  <!-- Pupille verticale (fente de serpent) -->
  <ellipse id="boss-pupil" cx="128" cy="102" rx="10" ry="30" fill="#000222"/>
  <!-- Reflet doux -->
  <ellipse cx="113" cy="88"  rx="10" ry="6.5" fill="rgba(255,255,255,0.46)" transform="rotate(-22,113,88)"/>
  <!-- Bord lumineux cyan -->
  <circle cx="128" cy="102" r="44" fill="none" stroke="#00ddff" stroke-width="1.8" opacity="0.55"/>
</g>

<!-- Anneau rouge (phase 2) -->
<ellipse cx="128" cy="108" rx="112" ry="86" fill="none" stroke="#cc1133" stroke-width="3" opacity="0" id="boss-red-ring"/>

</svg>
</div>
"""

code = code.replace('<canvas id="cv"></canvas>', boss_html + '\n<canvas id="cv"></canvas>')

# ── 4. Supprimer les yeux maléfiques de _drawMoon() ───────────────────────────
eyes_start = '  // === YEUX MALÉFIQUES ==='
shadow_start = '  const shadowG = ctx.createLinearGradient'

si = code.find(eyes_start)
ei = code.find(shadow_start, si)
if si > 0 and ei > si:
    code = code[:si] + '  ' + code[ei:]
    print('[OK] Yeux maléfiques supprimés de _drawMoon')
else:
    print('[WARN] Yeux maléfiques non trouvés / déjà supprimés')

# ── 5. Fonction _updateBossSVG() ───────────────────────────────────────────────
boss_js = '''
function _updateBossSVG(ph, bgT, vuln, player) {
  // Couleurs corps selon phase
  const pc = [
    ['#7c3acc','#380d66','#140528'],
    ['#aa2255','#560022','#1e0010'],
    ['#cc1133','#660011','#220008']
  ];
  const p = Math.min(ph, 2);
  const c = vuln ? ['#ff8800','#cc3300','#440800'] : pc[p];
  const s0 = document.getElementById('bbg0');
  const s1 = document.getElementById('bbg1');
  const s2 = document.getElementById('bbg2');
  if (s0) s0.setAttribute('stop-color', c[0]);
  if (s1) s1.setAttribute('stop-color', c[1]);
  if (s2) s2.setAttribute('stop-color', c[2]);
  // Pupille suit la position du joueur
  const pupil = document.getElementById('boss-pupil');
  if (pupil && player) {
    const dx = (player.x - 0.5) * 36;
    pupil.setAttribute('cx', 128 + dx);
  }
  // Anneau rouge phase 2
  const rr = document.getElementById('boss-red-ring');
  if (rr) {
    const ro = p >= 2 ? (0.28 + 0.22 * Math.sin(bgT * 0.08)).toFixed(2) : '0';
    rr.setAttribute('opacity', ro);
  }
  // Halo œil
  const eg = document.getElementById('boss-eye-glow');
  if (eg) {
    const eo = vuln ? (0.80 + 0.20 * Math.sin(bgT * 0.20)).toFixed(2)
                    : (0.28 + 0.12 * Math.sin(bgT * 0.06)).toFixed(2);
    eg.setAttribute('opacity', eo);
  }
  // Eye cyan glow selon phase
  const e0 = document.getElementById('beye0');
  const e1 = document.getElementById('beye1');
  const eyeC = [['#00eeff','#0040bb'],['#ee66ff','#6600bb'],['#ff4444','#aa0022']];
  if (e0) e0.setAttribute('stop-color', vuln ? '#ffaa00' : eyeC[p][0]);
  if (e1) e1.setAttribute('stop-color', vuln ? '#ff4400' : eyeC[p][1]);
  // Tentacule couleur
  const tc = vuln ? '#ff8800' : ['#8833cc','#aa2266','#cc1133'][p];
  document.querySelectorAll('.boss-tent').forEach(t => t.setAttribute('stroke', tc));
}

'''

# Insérer avant function _drawMoon
code = code.replace('function _drawMoon(', boss_js + 'function _drawMoon(', 1)

# ── 6. Appeler _updateBossSVG dans la game loop ────────────────────────────────
code = code.replace(
    '    _drawMoon(ctx, W, H, phase, bgT, vulnerable, boss.t);',
    '    _drawMoon(ctx, W, H, phase, bgT, vulnerable, boss.t);\n    _updateBossSVG(phase, bgT, vulnerable, player);',
    1
)

# ── WRITE ──────────────────────────────────────────────────────────────────────
with open('minijeux/niveau9.html', 'w', encoding='utf-8') as f:
    f.write(code)

size = len(code)
print(f'[OK] niveau9.html SVG boss refonte complète ({size} chars)!')
