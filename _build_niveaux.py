#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de génération des niveaux 2-8 pour GPS0 auto-runner"""
import os

base = 'minijeux'

CSS_COMMON = '''*{box-sizing:border-box;margin:0;padding:0}html,body{height:100%;overflow:hidden;background:#0A0A1A;color:#fff;font-family:"Trebuchet MS",sans-serif;touch-action:none}#hud{position:fixed;top:0;left:0;right:0;z-index:50;display:flex;justify-content:space-between;align-items:center;padding:8px 16px;background:rgba(0,0,0,.7);backdrop-filter:blur(6px);border-bottom:1px solid rgba(200,162,200,.2);font-weight:bold;font-size:.9rem}#mj-e{color:#FFD700}#mj-v{color:#FF6B6B;letter-spacing:2px}#btn-q{background:none;border:1px solid rgba(255,255,255,.3);color:rgba(255,255,255,.6);padding:4px 10px;border-radius:8px;cursor:pointer;font-size:.8rem}#monde{position:fixed;inset:0;overflow:hidden;BGSTYLE}.bg-e{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.35) 1px,transparent 1px);background-size:55px 55px;animation:dr 45s linear infinite;pointer-events:none}@keyframes dr{to{transform:translateX(55px)}}.plate{position:absolute;border-radius:8px;background:linear-gradient(180deg,#5a5a6e,#3a3a4e);border-top:2px solid rgba(200,162,200,.4);box-shadow:0 4px 12px rgba(0,0,0,.5)}.plate:not(.sol){box-shadow:0 4px 12px rgba(0,0,0,.5),0 0 14px rgba(200,162,200,.55),0 0 30px rgba(200,162,200,.25)}.plate.sol{background:linear-gradient(180deg,#4a4a5e,#2a2a3e)}.plate.mobile{background:linear-gradient(180deg,#1a4a5e,#0a2a3e);border-top-color:rgba(79,195,247,.8);box-shadow:0 4px 12px rgba(0,0,0,.5),0 0 20px rgba(79,195,247,.5)}.plate.fragile{background:linear-gradient(180deg,#6e4a2a,#4e2a0a);border-top-color:rgba(255,140,0,.6)}.plate.glissante{background:linear-gradient(180deg,#2a5a7e,#1a3a5e);border-top-color:rgba(100,220,255,.9)}#joueur{position:absolute;width:40px;height:52px;display:flex;flex-direction:column;align-items:center;pointer-events:none}#casque{width:36px;height:36px;border-radius:50%;background:rgba(79,195,247,.15);border:2px solid rgba(79,195,247,.6);overflow:hidden;flex-shrink:0}#ts{width:100%;height:100%;image-rendering:pixelated;background-color:#9a72c8;background-size:cover;background-position:center}#corps{width:28px;height:20px;border-radius:4px;background:linear-gradient(180deg,#C8A2C8,#9a72c8);display:flex;align-items:center;justify-content:center;margin-top:1px}#corps::after{content:"";width:8px;height:8px;border-radius:50%;background:#FFD700}#jambes{display:flex;gap:4px;margin-top:1px}.jambe{width:10px;height:10px;border-radius:2px;background:#9a72c8}@keyframes sc{from{opacity:.7;transform:scale(.9)}to{opacity:1;transform:scale(1.1)}}.slime{position:absolute;width:38px;height:30px;border-radius:50% 50% 40% 40%;display:flex;align-items:center;justify-content:center;font-size:.9rem}.laser-h{position:absolute;border-radius:3px;background:linear-gradient(90deg,transparent,#FF3333,transparent);box-shadow:0 0 12px #FF3333;opacity:0;transition:opacity .2s;height:6px}.laser-h.warn{background:linear-gradient(90deg,transparent,#FF8C00,#FFD700,#FF8C00,transparent);box-shadow:0 0 8px #FF8C00;opacity:.6}.laser-h.actif{opacity:1}.pic{position:absolute;clip-path:polygon(50% 0%,100% 100%,0% 100%);background:linear-gradient(180deg,#FF6B6B,#CC0000)}#ctrl-bar{position:fixed;bottom:0;left:0;right:0;height:110px;z-index:45;display:flex;align-items:center;justify-content:center;background:transparent;padding:8px}#bs{width:100%;max-width:600px;height:80px;border-radius:14px;border:2px solid rgba(79,195,247,.2);background:rgba(79,195,247,.05);color:rgba(255,255,255,.25);font-size:2.5rem;cursor:pointer;touch-action:none;user-select:none;-webkit-user-select:none}#lune{position:fixed;top:56px;left:50%;transform:translateX(-50%);background:rgba(10,10,26,.95);border:1px solid rgba(255,255,255,.4);border-radius:14px;padding:8px 14px;font-size:.9rem;color:#fff;font-weight:bold;opacity:0;transition:opacity .4s;max-width:90vw;z-index:60;pointer-events:none;white-space:nowrap}#lune.v{opacity:1}#tuto{position:fixed;inset:0;z-index:100;background:rgba(10,10,26,.93);backdrop-filter:blur(8px);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;padding:32px}#tuto h2{color:#C8A2C8;font-size:1.35rem;text-align:center;font-weight:bold}#tuto p{color:rgba(255,255,255,.85);text-align:center;font-size:.9rem;line-height:1.6;max-width:300px;font-weight:bold}.ti{display:flex;align-items:center;gap:12px;background:rgba(255,255,255,.06);border-radius:12px;padding:10px 16px;width:100%;max-width:300px;font-size:.85rem;font-weight:bold}#btn-st{padding:14px 32px;background:linear-gradient(135deg,#C8A2C8,#9a72c8);border:none;border-radius:16px;color:#0A0A1A;font-weight:bold;font-size:1rem;cursor:pointer;margin-top:8px}#ov{position:fixed;inset:0;z-index:100;display:none;background:rgba(10,10,26,.93);backdrop-filter:blur(10px);flex-direction:column;align-items:center;justify-content:center;gap:20px}#ov.v{display:flex}#ot{font-size:2rem;font-weight:900}#ot.win{color:#69FF47}#ot.lose{color:#FF6B6B}.bo{padding:14px 32px;border:none;border-radius:16px;font-weight:bold;font-size:1rem;cursor:pointer}#bb{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.3);color:#fff}#br{background:linear-gradient(135deg,#C8A2C8,#9a72c8);color:#0A0A1A}EXTRASTYLE'''

def make_html(num, titre, bg_style, extra_style, total, tuto_p, tuto_items, cfg_js):
    css = CSS_COMMON.replace('BGSTYLE', bg_style).replace('EXTRASTYLE', extra_style)
    tuto_html = ''.join([f'<div class="ti"><span>{a}</span><span>{b}</span></div>' for a,b in tuto_items])
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover"><title>GPS0 - Niveau {num}</title><style>{css}</style></head><body>
<div id="hud"><span>Niveau {num} - {titre}</span><span id="mj-e">0/{total} ✨</span><span id="mj-v">❤️❤️❤️</span><button id="btn-q">Quitter</button></div>
<div id="lune"></div><div id="monde"><div class="bg-e"></div></div>
<div id="joueur"><div id="casque"><div id="ts"></div></div><div id="corps"></div><div id="jambes"><div class="jambe"></div><div class="jambe"></div></div></div>
<div id="ctrl-bar"><button id="bs">⬆</button></div>
<div id="tuto"><h2>Niveau {num} - {titre}</h2><p>{tuto_p}</p>{tuto_html}<button id="btn-st">GO ! 🚀</button></div>
<div id="ov"><div id="ot"></div><div id="os"></div><div id="op"></div><div style="display:flex;flex-direction:column;gap:10px;margin-top:16px;width:min(300px,90vw);align-items:stretch"><button class="bo" id="bc" style="display:none">🎁 Prendre la récompense</button><button class="bo" id="br" style="display:none">🔄 Recommencer</button><button class="bo" id="bb" style="display:none">❌ Abandonner</button></div></div>
<script>{cfg_js}</script>
<script src="../js/moteur-minijeu.js"></script></body></html>'''

# ===== NIVEAU 3 : Vent Cosmique - plateformes glissantes + vent latéral =====
n3_cfg = r"""(function(){var W=window.innerWidth,H=window.innerHeight;window.GPS0_NIVEAU_CFG={
  niveau:3,total_poussieres:12,vitesse:4.0,monde_w:4,
  lune_start:'Le vent cosmique souffle ! Tiens bon !',
  wind:{freq:0.7,force:2.2},
  plateformes:[
    {x:0,y:H-60,w:Math.round(W*.52),h:60,sol:true},
    {x:Math.round(W*.80),y:H-60,w:Math.round(W*.50),h:60,sol:true},
    {x:Math.round(W*1.58),y:H-60,w:Math.round(W*.42),h:60,sol:true},
    {x:Math.round(W*2.35),y:H-60,w:Math.round(W*.48),h:60,sol:true},
    {x:Math.round(W*3.10),y:H-60,w:Math.round(W*.90),h:60,sol:true},
    {x:Math.round(W*.06),y:H-155,w:120,h:18,glissante:true},
    {x:Math.round(W*.32),y:H-230,w:115,h:18,glissante:true},
    {x:Math.round(W*.55),y:H-175,w:110,h:18},
    {x:Math.round(W*.78),y:H-250,w:115,h:18,glissante:true},
    {x:Math.round(W*1.02),y:H-190,w:110,h:18,glissante:true},
    {x:Math.round(W*1.25),y:H-280,w:115,h:18},
    {x:Math.round(W*1.48),y:H-200,w:110,h:18,glissante:true},
    {x:Math.round(W*1.72),y:H-320,w:105,h:18,glissante:true},
    {x:Math.round(W*1.95),y:H-210,w:110,h:18},
    {x:Math.round(W*2.20),y:H-270,w:115,h:18,glissante:true},
    {x:Math.round(W*2.45),y:H-185,w:110,h:18,glissante:true},
    {x:Math.round(W*2.68),y:H-350,w:105,h:18},
    {x:Math.round(W*2.92),y:H-230,w:110,h:18,glissante:true},
    {x:Math.round(W*3.20),y:H-280,w:115,h:18,glissante:true},
    {x:Math.round(W*3.52),y:H-200,w:110,h:18}
  ],
  slimes:[
    {pi:7,dir:1,speed:1.3,col:'#69FF47'},
    {pi:10,dir:-1,speed:1.5,col:'#ff9944'},
    {pi:13,dir:1,speed:1.4,col:'#69FF47'}
  ],
  poussieres:[{pi:5},{pi:6},{pi:7},{pi:8},{pi:9},{pi:10},{pi:11},{pi:12},{pi:13},{pi:15},{pi:17},{pi:18}],
  powerups:[{pi:16,type:'shield'}]
};})();"""

n3 = make_html(3, 'Vent Cosmique',
    'background:linear-gradient(180deg,#0a1a2a 0%,#0a2a1a 100%)',
    '#monde::before{content:"";position:absolute;inset:0;background:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 200 200\'%3E%3Cpath d=\'M0 100 Q50 80 100 100 Q150 120 200 100\' stroke=\'rgba(100,200,255,0.08)\' fill=\'none\' stroke-width=\'2\'/%3E%3C/svg%3E") repeat-x;animation:wd 3s linear infinite;}@keyframes wd{from{background-position:0}to{background-position:200px}}',
    12,
    'Le vent souffle fort ! Les plateformes bleues sont GLISSANTES. Contrôle tes sauts et surfe sur les rafales !',
    [('💨','Vent latéral qui oscille - adapte ta trajectoire !'),('🟦','Plateformes bleues = très glissantes'),('🛡','Bouclier disponible contre les ennemis')],
    n3_cfg
)
with open(os.path.join(base,'niveau3.html'),'w',encoding='utf-8') as f:
    f.write(n3)
print('N3 OK')

# ===== NIVEAU 4 : Nuit Stellaire - obscurité, lucioles =====
n4_cfg = r"""(function(){var W=window.innerWidth,H=window.innerHeight;window.GPS0_NIVEAU_CFG={
  niveau:4,total_poussieres:10,vitesse:3.8,monde_w:4,
  lune_start:'La nuit cosmique tombe... suis les lucioles !',
  darkness:true,
  plateformes:[
    {x:0,y:H-60,w:Math.round(W*.50),h:60,sol:true},
    {x:Math.round(W*.78),y:H-60,w:Math.round(W*.48),h:60,sol:true},
    {x:Math.round(W*1.55),y:H-60,w:Math.round(W*.44),h:60,sol:true},
    {x:Math.round(W*2.28),y:H-60,w:Math.round(W*.46),h:60,sol:true},
    {x:Math.round(W*3.05),y:H-60,w:Math.round(W*.95),h:60,sol:true},
    {x:Math.round(W*.10),y:H-165,w:115,h:18},
    {x:Math.round(W*.35),y:H-280,w:110,h:18},
    {x:Math.round(W*.58),y:H-200,w:115,h:18},
    {x:Math.round(W*.82),y:H-175,w:110,h:18},
    {x:Math.round(W*1.05),y:H-310,w:105,h:18},
    {x:Math.round(W*1.30),y:H-220,w:115,h:18},
    {x:Math.round(W*1.52),y:H-185,w:110,h:18},
    {x:Math.round(W*1.75),y:H-360,w:105,h:18},
    {x:Math.round(W*2.00),y:H-245,w:110,h:18},
    {x:Math.round(W*2.22),y:H-195,w:115,h:18},
    {x:Math.round(W*2.50),y:H-330,w:105,h:18},
    {x:Math.round(W*2.75),y:H-220,w:110,h:18},
    {x:Math.round(W*3.00),y:H-190,w:115,h:18},
    {x:Math.round(W*3.30),y:H-300,w:105,h:18},
    {x:Math.round(W*3.62),y:H-230,w:112,h:18}
  ],
  slimes:[
    {pi:7,dir:-1,speed:1.4,col:'#ff3a3a'},
    {pi:11,dir:1,speed:1.6,col:'#ff3a3a'},
    {pi:16,dir:-1,speed:1.5,col:'#ff3a3a'}
  ],
  poussieres:[{pi:5},{pi:6},{pi:7},{pi:8},{pi:9},{pi:10},{pi:12},{pi:14},{pi:17},{pi:19}],
  powerups:[{pi:15,type:'double_jump'}]
};})();"""

n4 = make_html(4, 'Nuit Stellaire',
    'background:#000005',
    '#dark-ov{transition:background .1s}',
    10,
    'La nuit cosmique est tombée ! Visibilité réduite autour du cosmonaute. Suis les étoiles pour trouver ton chemin !',
    [('🌍','Obscurité totale - seul ton halo éclaire'),('👾','Ennemis rouges dans le noir !'),('⚡','Double saut dissimulé dans les ténèbres')],
    n4_cfg
)
with open(os.path.join(base,'niveau4.html'),'w',encoding='utf-8') as f:
    f.write(n4)
print('N4 OK')

# ===== NIVEAU 5 : Éclipse Fragile - plateformes qui s'effondrent =====
n5_cfg = r"""(function(){var W=window.innerWidth,H=window.innerHeight;window.GPS0_NIVEAU_CFG={
  niveau:5,total_poussieres:13,vitesse:4.5,monde_w:4,
  lune_start:'Les plateformes s\'effondrent au moindre contact !',
  plateformes:[
    {x:0,y:H-60,w:Math.round(W*.45),h:60,sol:true},
    {x:Math.round(W*.75),y:H-60,w:Math.round(W*.42),h:60,sol:true},
    {x:Math.round(W*1.50),y:H-60,w:Math.round(W*.40),h:60,sol:true},
    {x:Math.round(W*2.25),y:H-60,w:Math.round(W*.44),h:60,sol:true},
    {x:Math.round(W*3.02),y:H-60,w:Math.round(W*.98),h:60,sol:true},
    {x:Math.round(W*.08),y:H-150,w:110,h:18,fragile:true},
    {x:Math.round(W*.28),y:H-260,w:105,h:18,fragile:true},
    {x:Math.round(W*.50),y:H-195,w:110,h:18,fragile:true},
    {x:Math.round(W*.72),y:H-175,w:105,h:18},
    {x:Math.round(W*.94),y:H-290,w:110,h:18,fragile:true},
    {x:Math.round(W*1.18),y:H-210,w:105,h:18,fragile:true},
    {x:Math.round(W*1.40),y:H-165,w:110,h:18,fragile:true},
    {x:Math.round(W*1.62),y:H-340,w:100,h:18,fragile:true},
    {x:Math.round(W*1.85),y:H-240,w:105,h:18,fragile:true},
    {x:Math.round(W*2.08),y:H-185,w:110,h:18,fragile:true},
    {x:Math.round(W*2.32),y:H-310,w:100,h:18,fragile:true},
    {x:Math.round(W*2.58),y:H-230,w:105,h:18,fragile:true},
    {x:Math.round(W*2.82),y:H-175,w:110,h:18,fragile:true},
    {x:Math.round(W*3.12),y:H-280,w:105,h:18,fragile:true},
    {x:Math.round(W*3.45),y:H-210,w:110,h:18,fragile:true}
  ],
  slimes:[],
  poussieres:[{pi:5},{pi:6},{pi:7},{pi:9},{pi:10},{pi:11},{pi:12},{pi:13},{pi:14},{pi:15},{pi:16},{pi:18},{pi:19}],
  powerups:[{pi:8,type:'double_jump'},{pi:17,type:'shield'}]
};})();"""

n5 = make_html(5, 'Éclipse Fragile',
    'background:linear-gradient(180deg,#1a0a2a 0%,#2a0a0a 100%)',
    '.plate.fragile{animation:tremble .15s ease-in-out infinite alternate;}.plate.fragile.falling{animation:none}@keyframes tremble{from{transform:translateX(-1px)}to{transform:translateX(1px)}}',
    13,
    'ATTENTION : chaque plateforme orange s\'effondre dès que tu la touches ! Ne pas s\'attarder, saut enchaîné obligatoire !',
    [('🟠','Plateformes orange = s\'effondrent au toucher !'),('⚡','Enchaîne les sauts sans t\'arrêter'),('⚡','Double saut caché pour les endroits durs')],
    n5_cfg
)
with open(os.path.join(base,'niveau5.html'),'w',encoding='utf-8') as f:
    f.write(n5)
print('N5 OK')

# ===== NIVEAU 6 : Gravité Inversée =====
n6_cfg = r"""(function(){var W=window.innerWidth,H=window.innerHeight;window.GPS0_NIVEAU_CFG={
  niveau:6,total_poussieres:12,vitesse:4.2,monde_w:5,
  lune_start:'La gravité s\'inverse ! Saut = chute, chute = saut !',
  gravity_zones:[
    {x:Math.round(W*0.60),w:Math.round(W*0.80)},
    {x:Math.round(W*1.80),w:Math.round(W*0.80)},
    {x:Math.round(W*3.00),w:Math.round(W*0.80)},
    {x:Math.round(W*4.00),w:Math.round(W*0.80)}
  ],
  plateformes:[
    {x:0,y:H-60,w:Math.round(W*.55),h:60,sol:true},
    {x:Math.round(W*.58),y:0,w:Math.round(W*.85),h:60,sol:true},
    {x:Math.round(W*1.62),y:H-60,w:Math.round(W*.80),h:60,sol:true},
    {x:Math.round(W*2.62),y:0,w:Math.round(W*.80),h:60,sol:true},
    {x:Math.round(W*3.62),y:H-60,w:Math.round(W*.60),h:60,sol:true},
    {x:Math.round(W*4.30),y:0,w:Math.round(W*.70),h:60,sol:true},
    {x:Math.round(W*.08),y:H-165,w:110,h:18},
    {x:Math.round(W*.30),y:H-290,w:105,h:18},
    {x:Math.round(W*.65),y:40,w:110,h:18},
    {x:Math.round(W*.88),y:110,w:105,h:18},
    {x:Math.round(W*1.12),y:230,w:110,h:18},
    {x:Math.round(W*1.40),y:H-200,w:110,h:18},
    {x:Math.round(W*1.68),y:H-320,w:105,h:18},
    {x:Math.round(W*2.00),y:H-185,w:110,h:18},
    {x:Math.round(W*2.30),y:60,w:105,h:18},
    {x:Math.round(W*2.55),y:165,w:110,h:18},
    {x:Math.round(W*2.85),y:H-260,w:105,h:18},
    {x:Math.round(W*3.10),y:H-180,w:110,h:18},
    {x:Math.round(W*3.40),y:70,w:105,h:18},
    {x:Math.round(W*3.70),y:200,w:110,h:18},
    {x:Math.round(W*4.00),y:H-280,w:105,h:18},
    {x:Math.round(W*4.35),y:130,w:110,h:18}
  ],
  slimes:[
    {pi:9,dir:1,speed:1.3,col:'#69FF47'},
    {pi:14,dir:-1,speed:1.5,col:'#ff9944'},
    {pi:19,dir:1,speed:1.4,col:'#69FF47'}
  ],
  poussieres:[{pi:6},{pi:7},{pi:8},{pi:9},{pi:10},{pi:11},{pi:13},{pi:15},{pi:16},{pi:17},{pi:18},{pi:20}],
  powerups:[{pi:12,type:'double_jump'}]
};})();"""

n6 = make_html(6, 'Gravité Inversée',
    'background:linear-gradient(180deg,#1a2a0a 0%,#0a0a2a 100%)',
    '#gz-indicator{position:fixed;top:48px;left:50%;transform:translateX(-50%);font-size:.75rem;color:rgba(150,255,100,.6);pointer-events:none;z-index:30}',
    12,
    'ZONES DE GRAVITÉ INVERSÉE ! Dans ces zones, tu cours sur le plafond ! Les sauts t\'envoyent vers le bas. Adapte ta logique !',
    [('🔃','Zones vertes = gravité inversée, tu coures au plafond !'),('🔵','Zones normales = gravité normale vers le bas'),('⚡','Double saut disponible - fonctionne dans les 2 sens')],
    n6_cfg
)
with open(os.path.join(base,'niveau6.html'),'w',encoding='utf-8') as f:
    f.write(n6)
print('N6 OK')

# ===== NIVEAU 7 : Vitesse Stellaire - accélération progressive =====
n7_cfg = r"""(function(){var W=window.innerWidth,H=window.innerHeight;window.GPS0_NIVEAU_CFG={
  niveau:7,total_poussieres:15,vitesse:3.5,monde_w:5,vitesse_ramp:20,
  lune_start:'La vitesse augmente... accroche-toi !',
  plateformes:[
    {x:0,y:H-60,w:Math.round(W*.48),h:60,sol:true},
    {x:Math.round(W*.75),y:H-60,w:Math.round(W*.45),h:60,sol:true},
    {x:Math.round(W*1.48),y:H-60,w:Math.round(W*.42),h:60,sol:true},
    {x:Math.round(W*2.18),y:H-60,w:Math.round(W*.45),h:60,sol:true},
    {x:Math.round(W*2.90),y:H-60,w:Math.round(W*.42),h:60,sol:true},
    {x:Math.round(W*3.60),y:H-60,w:Math.round(W*.40),h:60,sol:true},
    {x:Math.round(W*4.20),y:H-60,w:Math.round(W*.80),h:60,sol:true},
    {x:Math.round(W*.06),y:H-145,w:110,h:18},
    {x:Math.round(W*.26),y:H-240,w:105,h:18},
    {x:Math.round(W*.48),y:H-180,w:110,h:18},
    {x:Math.round(W*.68),y:H-310,w:100,h:18},
    {x:Math.round(W*.90),y:H-170,w:110,h:18},
    {x:Math.round(W*1.12),y:H-265,w:105,h:18},
    {x:Math.round(W*1.35),y:H-195,w:110,h:18},
    {x:Math.round(W*1.58),y:H-350,w:100,h:18},
    {x:Math.round(W*1.82),y:H-210,w:105,h:18},
    {x:Math.round(W*2.05),y:H-180,w:110,h:18},
    {x:Math.round(W*2.28),y:H-290,w:105,h:18},
    {x:Math.round(W*2.52),y:H-165,w:110,h:18},
    {x:Math.round(W*2.75),y:H-380,w:100,h:18},
    {x:Math.round(W*2.98),y:H-200,w:105,h:18},
    {x:Math.round(W*3.22),y:H-170,w:110,h:18},
    {x:Math.round(W*3.45),y:H-320,w:100,h:18},
    {x:Math.round(W*3.68),y:H-195,w:105,h:18},
    {x:Math.round(W*3.92),y:H-270,w:100,h:18},
    {x:Math.round(W*4.20),y:H-180,w:110,h:18},
    {x:Math.round(W*4.45),y:H-340,w:100,h:18}
  ],
  slimes:[
    {pi:10,dir:1,speed:1.8,col:'#ff9944'},
    {pi:14,dir:-1,speed:2.0,col:'#ff3a3a'},
    {pi:18,dir:1,speed:2.2,col:'#ff9944'},
    {pi:22,dir:-1,speed:2.4,col:'#ff3a3a'}
  ],
  poussieres:[{pi:7},{pi:8},{pi:9},{pi:10},{pi:11},{pi:12},{pi:13},{pi:15},{pi:16},{pi:17},{pi:19},{pi:20},{pi:21},{pi:23},{pi:25}],
  powerups:[{pi:24,type:'shield'},{pi:26,type:'double_jump'}]
};})();"""

n7 = make_html(7, 'Vitesse Stellaire',
    'background:linear-gradient(135deg,#0a001a 0%,#1a000a 50%,#0a0a1a 100%)',
    '#speed-bar{position:fixed;bottom:115px;left:0;right:0;height:4px;background:rgba(255,100,0,0);transition:background .5s;z-index:40}',
    15,
    'La vitesse AUGMENTE automatiquement jusqu\'à x2.5 en 3 minutes ! Anticipation maximale requise pour esquiver !',
    [('🏎','Accélération progressive automatique - les réflexes seront mis à l\'épreuve !'),('👾','Ennemis de plus en plus rapides'),('🛡','Bouclier et double saut disponibles')],
    n7_cfg
)
with open(os.path.join(base,'niveau7.html'),'w',encoding='utf-8') as f:
    f.write(n7)
print('N7 OK')

# ===== NIVEAU 8 : Labyrinthe Spiral - le plus difficile =====
n8_cfg = r"""(function(){var W=window.innerWidth,H=window.innerHeight;window.GPS0_NIVEAU_CFG={
  niveau:8,total_poussieres:16,vitesse:4.8,monde_w:6,
  lune_start:'Le labyrinthe ultime... tu n\'en reviendras peut-être pas.',
  plateformes:[
    {x:0,y:H-60,w:Math.round(W*.40),h:60,sol:true},
    {x:Math.round(W*.68),y:H-60,w:Math.round(W*.38),h:60,sol:true},
    {x:Math.round(W*1.35),y:H-60,w:Math.round(W*.38),h:60,sol:true},
    {x:Math.round(W*2.02),y:H-60,w:Math.round(W*.38),h:60,sol:true},
    {x:Math.round(W*2.70),y:H-60,w:Math.round(W*.38),h:60,sol:true},
    {x:Math.round(W*3.38),y:H-60,w:Math.round(W*.38),h:60,sol:true},
    {x:Math.round(W*4.05),y:H-60,w:Math.round(W*.38),h:60,sol:true},
    {x:Math.round(W*4.72),y:H-60,w:Math.round(W*.90),h:60,sol:true},
    {x:Math.round(W*.04),y:H-140,w:95,h:18,fragile:true},
    {x:Math.round(W*.22),y:H-250,w:90,h:18},
    {x:Math.round(W*.40),y:H-380,w:90,h:18,mobile:true,axis:'y',range:60,speed:1.5},
    {x:Math.round(W*.58),y:H-190,w:95,h:18,fragile:true},
    {x:Math.round(W*.76),y:H-160,w:90,h:18},
    {x:Math.round(W*.94),y:H-310,w:90,h:18,fragile:true},
    {x:Math.round(W*1.12),y:H-440,w:85,h:18,mobile:true,axis:'y',range:80,speed:1.8},
    {x:Math.round(W*1.30),y:H-200,w:90,h:18,fragile:true},
    {x:Math.round(W*1.48),y:H-165,w:95,h:18},
    {x:Math.round(W*1.66),y:H-350,w:90,h:18,fragile:true},
    {x:Math.round(W*1.85),y:H-480,w:85,h:18,mobile:true,axis:'y',range:90,speed:2.0},
    {x:Math.round(W*2.05),y:H-240,w:90,h:18,fragile:true},
    {x:Math.round(W*2.25),y:H-175,w:95,h:18},
    {x:Math.round(W*2.45),y:H-390,w:90,h:18,fragile:true},
    {x:Math.round(W*2.65),y:H-160,w:90,h:18,fragile:true},
    {x:Math.round(W*2.85),y:H-300,w:85,h:18,mobile:true,axis:'y',range:100,speed:2.2},
    {x:Math.round(W*3.05),y:H-170,w:90,h:18,fragile:true},
    {x:Math.round(W*3.25),y:H-420,w:85,h:18},
    {x:Math.round(W*3.45),y:H-200,w:90,h:18,fragile:true},
    {x:Math.round(W*3.65),y:H-160,w:95,h:18},
    {x:Math.round(W*3.88),y:H-340,w:90,h:18,mobile:true,axis:'y',range:110,speed:2.0},
    {x:Math.round(W*4.10),y:H-190,w:90,h:18,fragile:true},
    {x:Math.round(W*4.30),y:H-380,w:85,h:18},
    {x:Math.round(W*4.52),y:H-220,w:90,h:18,fragile:true},
    {x:Math.round(W*4.72),y:H-175,w:95,h:18}
  ],
  slimes:[
    {pi:9,dir:1,speed:1.6,col:'#ff3a3a'},
    {pi:12,dir:-1,speed:1.8,col:'#ff9944'},
    {pi:16,dir:1,speed:2.0,col:'#ff3a3a'},
    {pi:20,dir:-1,speed:1.7,col:'#ff9944'},
    {pi:27,dir:1,speed:2.2,col:'#ff3a3a'}
  ],
  poussieres:[{pi:8},{pi:9},{pi:10},{pi:11},{pi:13},{pi:14},{pi:15},{pi:17},{pi:18},{pi:19},{pi:21},{pi:22},{pi:24},{pi:26},{pi:29},{pi:31}],
  powerups:[{pi:25,type:'double_jump'},{pi:30,type:'shield'}]
};})();"""

n8 = make_html(8, 'Labyrinthe Spiral',
    'background:linear-gradient(180deg,#050510 0%,#0a0520 50%,#050510 100%)',
    '.plate{box-shadow:0 4px 12px rgba(0,0,0,.8),0 0 20px rgba(200,100,255,.4),0 0 45px rgba(200,100,255,.15)!important}.plate.sol{box-shadow:0 4px 12px rgba(0,0,0,.9)!important}',
    16,
    'LE NIVEAU ULTIME. Plateformes qui s\'effondrent ET mobiles ET slimes rapides. Chaque erreur coûte cher. Bonne chance !',
    [('💀','Le niveau le plus difficile du jeu'),('🟠+🔵','Fragiles + mobiles combinées'),('💜','Réflexes parfaits nécessaires')],
    n8_cfg
)
with open(os.path.join(base,'niveau8.html'),'w',encoding='utf-8') as f:
    f.write(n8)
print('N8 OK')

# ===== Re-écrire NIVEAU 2 aussi (cohérence) =====
n2_cfg = r"""(function(){var W=window.innerWidth,H=window.innerHeight;window.GPS0_NIVEAU_CFG={
  niveau:2,total_poussieres:14,vitesse:4.2,monde_w:4,
  lune_start:'Attention ! Les plateformes bougent verticalement !',
  plateformes:[
    {x:0,y:H-60,w:Math.round(W*.55),h:60,sol:true},
    {x:Math.round(W*.82),y:H-60,w:Math.round(W*.48),h:60,sol:true},
    {x:Math.round(W*1.60),y:H-60,w:Math.round(W*.45),h:60,sol:true},
    {x:Math.round(W*2.38),y:H-60,w:Math.round(W*.48),h:60,sol:true},
    {x:Math.round(W*3.12),y:H-60,w:Math.round(W*.88),h:60,sol:true},
    {x:Math.round(W*.08),y:H-160,w:115,h:18,mobile:true,axis:'y',range:70,speed:1.2},
    {x:Math.round(W*.30),y:H-240,w:110,h:18,mobile:true,axis:'y',range:90,speed:1.5},
    {x:Math.round(W*.55),y:H-190,w:110,h:18,mobile:true,axis:'y',range:60,speed:1.0},
    {x:Math.round(W*.76),y:H-180,w:110,h:18},
    {x:Math.round(W*.98),y:H-260,w:105,h:18,mobile:true,axis:'y',range:80,speed:1.3},
    {x:Math.round(W*1.22),y:H-175,w:110,h:18,mobile:true,axis:'y',range:100,speed:1.6},
    {x:Math.round(W*1.45),y:H-220,w:110,h:18},
    {x:Math.round(W*1.68),y:H-300,w:105,h:18,mobile:true,axis:'y',range:70,speed:1.1},
    {x:Math.round(W*1.92),y:H-195,w:110,h:18,mobile:true,axis:'y',range:90,speed:1.4},
    {x:Math.round(W*2.18),y:H-270,w:105,h:18},
    {x:Math.round(W*2.42),y:H-180,w:110,h:18,mobile:true,axis:'y',range:110,speed:1.7},
    {x:Math.round(W*2.70),y:H-250,w:105,h:18,mobile:true,axis:'y',range:80,speed:1.2},
    {x:Math.round(W*2.95),y:H-190,w:110,h:18},
    {x:Math.round(W*3.22),y:H-310,w:105,h:18,mobile:true,axis:'y',range:90,speed:1.5},
    {x:Math.round(W*3.55),y:H-220,w:110,h:18,mobile:true,axis:'y',range:70,speed:1.3}
  ],
  slimes:[
    {pi:8,dir:1,speed:1.4,col:'#69FF47'},
    {pi:11,dir:-1,speed:1.5,col:'#69FF47'},
    {pi:14,dir:1,speed:1.3,col:'#69FF47'}
  ],
  poussieres:[{pi:5},{pi:6},{pi:7},{pi:8},{pi:9},{pi:10},{pi:11},{pi:12},{pi:13},{pi:14},{pi:15},{pi:16},{pi:18},{pi:19}],
  powerups:[{pi:17,type:'double_jump'}]
};})();"""

n2 = make_html(2, 'Orbe Mobile',
    'background:#0A0A1A',
    '',
    14,
    'Le runner avance seul ! Les plateformes BOUGENT verticalement. Timing et précision de saut requis !',
    [('⬆','Appui court = petit saut | long = grand saut'),
     ('🔵','Plateformes bleues = mobiles, attends le bon moment !'),
     ('⬛','Les trous font chuter - 3 vies')],
    n2_cfg
)
with open(os.path.join(base,'niveau2.html'),'w',encoding='utf-8') as f:
    f.write(n2)
print('N2 (re) OK')

print('=== Tous les niveaux 2-8 générés ! ===')
