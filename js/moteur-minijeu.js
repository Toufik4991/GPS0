'use strict';
(function(cfg){
const W=window.innerWidth,H=window.innerHeight;
const MONDE_W=Math.round(W*(cfg.monde_w||1));
// AUTO-RUNNER - mouvement auto vers droite, saut tap/hold
const G=cfg.gravite||0.55,JF=cfg.saut_force||-14,VXbase=cfg.vitesse||4.5;
const TOTAL=cfg.total_poussieres||8;
const DOUBLE_SAUT=!!cfg.double_saut;
let jx=cfg.spawn_x||80,jy=cfg.spawn_y||(H-120);
let vx=0,vy=0,air=true,sauts_restants=DOUBLE_SAUT?2:1;
let doubleJumpActive=false,shieldActive=false;
let jumpStartMs=0;
let vies=cfg.vies||3,etoiles=0,running=false,invincible=false;
let tempsRestant=180,timerEl=null,timerMs=0,totalMs=0;
let camX=0;
const monde=document.getElementById('monde');
const plates=[],slimes=[],pds=[],lasers=[],pics=[],powerups=[];

// Selfie joueur
try{const b=window.parent.GPS0_Avatar&&window.parent.GPS0_Avatar.getSelfie();if(b){const el=document.getElementById('ts');if(el){el.style.backgroundImage='url('+b+')';el.style.backgroundSize='cover';}}}catch(e){}

function mkEl(cls,x,y,w,h){const e=document.createElement('div');e.className=cls;e.style.position='absolute';e.style.left=x+'px';e.style.top=y+'px';e.style.width=w+'px';e.style.height=h+'px';monde.appendChild(e);return e;}

function mkPlate(c){
  const t='plate'+(c.sol?' sol':c.mobile?' mobile':c.fragile?' fragile':c.glissante?' glissante':'');
  const e=mkEl(t,c.x,c.y,c.w,c.h);
  if(c.glissante)e.style.background='linear-gradient(90deg,rgba(100,200,255,0.7),rgba(150,230,255,0.5))';
  if(c.invisible)e.style.opacity='0';
  const obj=Object.assign({},c,{e,sol:!!c.sol,mobile:!!c.mobile,fragile:!!c.fragile,glissante:!!c.glissante,mx0:c.x,my0:c.y,mt:0,alpha:0,falling:false,visible:!c.invisible});
  plates.push(obj);
  return obj;
}

function build(){
  // Style lune
  const _st=document.createElement('style');
  _st.textContent='#lune{background:rgba(10,10,26,.95)!important;border:1px solid rgba(255,255,255,.4)!important;color:#fff!important;font-weight:bold!important}';
  document.head.appendChild(_st);

  if(MONDE_W>W){monde.style.width=MONDE_W+'px';monde.style.right='auto';}

  // Platforms
  (cfg.plateformes||[]).forEach(c=>{
    const sc=c.sol?c:Object.assign({},c,{y:Math.round(H-(H-c.y)*1.2)});
    mkPlate(sc);
  });

  // Slimes
  (cfg.slimes||[]).forEach(c=>{
    const p=plates[c.pi];if(!p)return;
    const e=mkEl('slime',p.x+p.w/2-19,p.y-32,38,30);
    const col=c.col||'#69FF47';
    const darks={'#69FF47':'#22aa22','#ff9944':'#aa5500','#ff3a3a':'#aa0000'};
    const dark=darks[col]||'#226622';
    e.style.background='radial-gradient(circle at 40% 35%,'+col+','+dark+')';
    e.style.boxShadow='0 0 14px '+col+'88';
    e.textContent='\uD83D\uDC7E';
    e.style.display='flex';e.style.alignItems='center';e.style.justifyContent='center';
    e.style.fontSize='.9rem';e.style.borderRadius='50% 50% 40% 40%';
    slimes.push({e,x:p.x+p.w/2-19,y:p.y-32,bx:p.x,bw:p.w,vx:(c.speed||1.2)*(c.dir||1)});
  });

  // Poussieres (SVG etoile halo jaune)
  (cfg.poussieres||[]).forEach((c,i)=>{
    const p=plates[c.pi];if(!p)return;
    const cnt=(cfg.poussieres||[]).filter(d=>d.pi===c.pi).length;
    const idx=(cfg.poussieres||[]).slice(0,i).filter(d=>d.pi===c.pi).length;
    const ox=p.w/(cnt+1)*(idx+1);
    const e=document.createElementNS('http://www.w3.org/2000/svg','svg');
    e.setAttribute('viewBox','-1 -1 22 22');e.setAttribute('width','22');e.setAttribute('height','22');
    e.style.position='absolute';e.style.left=(p.x+ox-11)+'px';e.style.top=(p.y-30)+'px';
    e.style.filter='drop-shadow(0 0 8px #FFD700) drop-shadow(0 0 22px #FFA500) drop-shadow(0 0 45px #FF6600)';
    e.style.animation='sc 1.1s ease-in-out infinite alternate';
    e.style.pointerEvents='none';
    const star=document.createElementNS('http://www.w3.org/2000/svg','polygon');
    const pts=[];
    for(let k=0;k<10;k++){const a=Math.PI/5*k-Math.PI/2;const r=k%2===0?9:4.5;pts.push((10+r*Math.cos(a)).toFixed(2)+','+(10+r*Math.sin(a)).toFixed(2));}
    star.setAttribute('points',pts.join(' '));star.setAttribute('fill','#FFD700');star.setAttribute('stroke','#FFA500');star.setAttribute('stroke-width','0.8');
    e.appendChild(star);monde.appendChild(e);
    pds.push({e,x:p.x+ox-11,y:p.y-30,col:false});
  });

  // Power-ups (double saut ou bouclier)
  (cfg.powerups||[]).forEach(c=>{
    const p=plates[c.pi];if(!p)return;
    const e=document.createElement('div');
    e.style.cssText='position:absolute;font-size:1.4rem;text-align:center;line-height:1;animation:sc 1.1s ease-in-out infinite alternate;pointer-events:none;z-index:5;';
    e.textContent=c.type==='shield'?'\uD83D\uDEE1':'\u26A1';
    e.style.left=(p.x+p.w/2-16)+'px';e.style.top=(p.y-36)+'px';
    monde.appendChild(e);
    powerups.push({e,x:p.x+p.w/2-16,y:p.y-36,type:c.type,col:false});
  });

  // Lasers
  (cfg.lasers||[]).forEach(c=>{
    const e=mkEl('laser-h',c.x,c.y,c.w,6);
    lasers.push(Object.assign({},c,{e,t:c.offset||0,warn_dur:c.warn||1500,on_dur:c.on||2000,off_dur:c.off||2000,phase:'off'}));
  });

  // Pics
  (cfg.pics||[]).forEach(c=>{
    let px=c.x!=null?c.x:0,py=c.y!=null?c.y:0;
    if(c.pi!=null&&plates[c.pi]){const p=plates[c.pi];px=p.x+p.w/2-11;py=p.y-(c.h||16);}
    const e=mkEl('pic',px,py,22,c.h||18);
    e.style.clipPath='polygon(50% 0%,100% 100%,0% 100%)';
    e.style.background=c.col||'linear-gradient(180deg,#FF6B6B,#CC0000)';
    pics.push({e,x:px,y:py});
  });

  // Timer
  timerEl=document.createElement('span');timerEl.id='mj-timer';
  timerEl.style.cssText='color:#4FC3F7;font-weight:bold;margin:0 8px;font-size:.9rem';
  timerEl.textContent='3:00';
  const hud=document.getElementById('hud');
  if(hud){const bq=hud.querySelector('#btn-q');if(bq)hud.insertBefore(timerEl,bq);else hud.appendChild(timerEl);}

  // Texte tuto
  const tp=document.querySelector('#tuto p');
  if(tp)tp.textContent='AUTO-RUNNER : le personnage avance tout seul ! Appui court = petit saut, appui long = grand saut. 3 minutes pour collecter un max de poussières d\'étoiles !';

  // Effet nuit N4
  if(cfg.darkness){
    const ov=document.createElement('div');ov.id='dark-ov';
    ov.style.cssText='position:fixed;inset:0;background:radial-gradient(circle at 50% 70%,transparent 100px,rgba(0,0,5,0.93) 240px);pointer-events:none;z-index:20;';
    document.body.appendChild(ov);
  }
}

function tryJump(){
  if(!running)return;
  const maxSauts=doubleJumpActive?2:(DOUBLE_SAUT?2:1);
  if(sauts_restants<=0)return;
  const held=Date.now()-jumpStartMs;
  const force=held>220?JF:JF*0.55;
  vy=force*(sauts_restants<maxSauts?0.88:1);
  sauts_restants--;air=true;
  sfx('saut_cosmonaute');
}

function fisica(){
  // === AUTO-MOVE droite ===
  const elapsed=totalMs/1000;
  // rampe vitesse progressive (N7)
  const speedMult=cfg.vitesse_ramp?Math.min(1+elapsed/cfg.vitesse_ramp*0.3,2.5):1;
  let targetVx=VXbase*speedMult;
  // wind N3
  if(cfg.wind){
    const wt=elapsed;
    targetVx+=Math.sin(wt*cfg.wind.freq)*cfg.wind.force;
  }
  vx=targetVx;

  // Gravite (inverse si zone N6)
  let grav=G;
  if(cfg.gravity_zones){
    for(const gz of cfg.gravity_zones){
      if(jx+20>gz.x&&jx+20<gz.x+gz.w){grav=-G;}
    }
  }
  vy=Math.min(Math.max(vy+grav,-22),22);

  jx+=vx;jy+=vy;

  // Bord gauche : le runner ne peut pas aller a gauche du camX
  if(jx<camX){jx=camX;vx=0;}
  // Fin du monde = victoire
  if(jx>=MONDE_W-50){running=false;setTimeout(()=>fin(true),300);return;}

  // Plateformes mobiles
  plates.forEach(p=>{
    if(!p.mobile||!p.range)return;
    p.mt=(p.mt||0)+0.016;
    if(p.axis==='x'){p.x=p.mx0+Math.sin(p.mt*(p.speed||1))*p.range;p.e.style.left=p.x+'px';}
    else{p.y=p.my0+Math.sin(p.mt*(p.speed||1))*p.range;p.e.style.top=p.y+'px';}
  });

  // Plateformes fragiles tombantes
  plates.forEach(p=>{
    if(!p.fragile||!p.falling)return;
    p.alpha=(p.alpha||0)+0.04;
    p.e.style.opacity=Math.max(0,1-p.alpha);
    p.y+=p.alpha*2.5;p.e.style.top=p.y+'px';
  });

  // Collisions platforms
  air=true;
  for(const p of plates){
    if(p.fragile&&p.falling&&(p.alpha||0)>1)continue;
    if(p.invisible&&!p.visible)continue;
    const cx=jx+20,foot=jy+52,head=jy;
    if(cx>p.x+4&&cx<p.x+p.w-4){
      if(vy>=0&&foot>=p.y&&foot<=p.y+p.h+Math.abs(vy)+4){
        jy=p.y-52;vy=0;air=false;
        const maxS=doubleJumpActive?2:(DOUBLE_SAUT?2:1);
        sauts_restants=maxS;
        if(p.fragile&&!p.falling)setTimeout(()=>{p.falling=true;},300);
        if(p.glissante)vx*=1.05; // glissade
      } else if(vy<0&&head<=p.y+p.h&&head>=p.y-10){vy=Math.abs(vy)*0.3;}
    }
  }

  // Chute = perdre
  if(jy>H+120){perdre();return;}

  // Ennemis
  if(!invincible&&!shieldActive){
    for(const s of slimes){
      s.x+=s.vx;
      if(s.x<s.bx||s.x+38>s.bx+s.bw)s.vx*=-1;
      s.e.style.left=s.x+'px';
      const dx=(jx+20)-(s.x+19),dy=(jy+26)-(s.y+15);
      if(Math.sqrt(dx*dx+dy*dy)<30){perdre();return;}
    }
    for(const l of lasers){
      if(l.phase==='actif'){
        const cx=jx+20,cy=jy+26;
        if(cx>l.x&&cx<l.x+l.w&&cy>l.y-4&&cy<l.y+10){perdre();return;}
      }
    }
    for(const p of pics){
      const dx=(jx+20)-(p.x+11),dy=(jy+52)-(p.y+9);
      if(Math.sqrt(dx*dx+dy*dy)<22){perdre();return;}
    }
  }

  // Collecte poussieres
  for(const p of pds){
    if(p.col)continue;
    const dx=(jx+20)-(p.x+11),dy=(jy+26)-(p.y+11);
    if(Math.sqrt(dx*dx+dy*dy)<30){
      p.col=true;p.e.style.display='none';etoiles++;
      sfx('collecte_poussiere');
      const el=document.getElementById('mj-e');if(el)el.textContent=etoiles+'/'+TOTAL+' \u2728';
    }
  }

  // Collecte power-ups
  for(const p of powerups){
    if(p.col)continue;
    const dx=(jx+20)-(p.x+16),dy=(jy+26)-(p.y+18);
    if(Math.sqrt(dx*dx+dy*dy)<36){
      p.col=true;p.e.style.display='none';
      if(p.type==='shield'){shieldActive=true;sfx('zone_detectee');lune('\uD83D\uDEE1 Bouclier actif !');setTimeout(()=>{shieldActive=false;},5000);}
      else{doubleJumpActive=true;const maxS=2;sauts_restants=maxS;sfx('zone_detectee');lune('\u26A1 Double saut !');setTimeout(()=>{doubleJumpActive=false;},7000);}
    }
  }

  // Effet ténèbres : update position centre lumineux autour du joueur N4
  if(cfg.darkness){
    const ov=document.getElementById('dark-ov');
    if(ov){
      const sx=MONDE_W>W?Math.round(jx-camX):jx;
      const pct_x=Math.round((sx/W)*100);const pct_y=Math.round(((jy+26)/H)*100);
      ov.style.background='radial-gradient(circle at '+pct_x+'% '+pct_y+'%,transparent 100px,rgba(0,0,5,0.93) 240px)';
    }
  }

  // Camera
  if(MONDE_W>W){
    const tgt=Math.max(0,Math.min(jx-W*0.35,MONDE_W-W));
    camX+=(tgt-camX)*0.10;
    monde.style.transform='translateX('+(-Math.round(camX))+'px)';
  }
  const sx=MONDE_W>W?Math.round(jx-camX):jx;
  const jEl=document.getElementById('joueur');
  if(jEl){jEl.style.left=sx+'px';jEl.style.top=jy+'px';}
}

function tickLasers(dt){
  lasers.forEach(l=>{
    l.t+=dt;
    const cycle=l.warn_dur+l.on_dur+l.off_dur,tp=l.t%cycle;
    const np=tp<l.warn_dur?'warn':tp<l.warn_dur+l.on_dur?'actif':'off';
    if(np!==l.phase){l.phase=np;l.e.className='laser-h '+(np!=='off'?np:'');if(np==='warn')sfx('laser_warning');}
  });
}

function perdre(){
  if(invincible||shieldActive)return;
  invincible=true;sfx('ennemi_touche');vies--;
  const vm=[,'','\u2764\uFE0F','\u2764\uFE0F\u2764\uFE0F','\u2764\uFE0F\u2764\uFE0F\u2764\uFE0F'];
  const vel=document.getElementById('mj-v');if(vel)vel.textContent=vm[Math.max(0,vies)]||'';
  lune(vies===1?'Dernière chance !':(vies===0?'...':'Aie, attention !'));
  if(vies<=0){running=false;setTimeout(()=>fin(false),400);return;}
  jx=cfg.spawn_x||80;jy=cfg.spawn_y||(H-120);
  vx=0;vy=0;camX=0;
  if(MONDE_W>W)monde.style.transform='translateX(0px)';
  setTimeout(()=>{invincible=false;},1200);
}

function fin(ok){
  if(ok)sfx('boss_hit');
  const ov=document.getElementById('ov'),ot=document.getElementById('ot');
  if(!ov||!ot)return;
  ot.textContent=ok?'Victoire !':'Perdu...';
  ot.className=ok?'win':'lose';
  const btnR=document.getElementById('br'),btnC=document.getElementById('bc'),btnB=document.getElementById('bb');
  const wrap=btnC?.parentElement||btnR?.parentElement;
  if(wrap){wrap.style.flexDirection='column';wrap.style.alignItems='stretch';wrap.style.width='min(300px,90vw)';}
  if(btnR){btnR.style.display='block';btnR.textContent='\uD83D\uDD04 Recommencer';}
  if(btnB){btnB.style.display='block';btnB.textContent='\u274C Abandonner';}
  if(btnC){
    if(ok){
      btnC.style.display='block';
      btnC.textContent='\uD83C\uDF81 Prendre '+etoiles+' poussières';
      if(wrap)wrap.insertBefore(btnC,wrap.firstChild);
      btnC.onclick=()=>{try{window.parent.postMessage({source:'gps0_minijeu',success:true,niveau:cfg.niveau,poussieres:etoiles,etoiles:3},'*');}catch(e){}};
    }else{btnC.style.display='none';}
  }
  ov.classList.add('v');
}

let _luneLastMs = 0;
const _luneTaunt = ['🌚 T\'as du mal, hein ? 😏','🌝 Encore raté ! 😏','🌚 La lune te regarde... badly 😏','🌝 Presque ! (non) 😏','🌚 C\'est long pour toi 😏'];
function lune(txt){
  const now=Date.now();
  if(now-_luneLastMs<60000)return;
  _luneLastMs=now;
  const e=document.getElementById('lune');
  if(e){
    const msg=txt||_luneTaunt[Math.floor(Math.random()*_luneTaunt.length)];
    e.textContent=msg;
    e.classList.add('v');
    setTimeout(()=>e.classList.remove('v'),12000);
  }
}
function sfx(n){try{window.parent.GPS0_Audio&&window.parent.GPS0_Audio.playSFX(n);}catch(e){}}
function demarrerMusiqueNiveau(){try{const a=window.parent.GPS0_Audio;if(a&&a.isEnabled&&a.isEnabled())a.playMusiqueExploration();}catch(e){}}

function ctls(){
  // AUTO-RUNNER : seulement le bouton saut #bs + tap sur monde
  const doJumpStart=()=>{jumpStartMs=Date.now();};
  const doJumpEnd=()=>{tryJump();};
  const bs=document.getElementById('bs');
  if(bs){
    bs.addEventListener('touchstart',e=>{e.preventDefault();doJumpStart();},{passive:false});
    bs.addEventListener('touchend',e=>{e.preventDefault();doJumpEnd();},{passive:false});
    bs.addEventListener('mousedown',e=>{doJumpStart();});
    bs.addEventListener('mouseup',e=>{doJumpEnd();});
  }
  // Tap partout sur l'ecran (hors HUD)
  const m=document.getElementById('monde');
  if(m){
    m.addEventListener('touchstart',e=>{e.preventDefault();doJumpStart();},{passive:false});
    m.addEventListener('touchend',e=>{e.preventDefault();doJumpEnd();},{passive:false});
  }
  // Clavier
  const keyDown={};
  window.addEventListener('keydown',e=>{
    if((e.key==='ArrowUp'||e.key===' '||e.key==='z'||e.key==='Z')&&!keyDown[e.key]){
      keyDown[e.key]=true;doJumpStart();e.preventDefault();
    }
  });
  window.addEventListener('keyup',e=>{
    if(e.key==='ArrowUp'||e.key===' '||e.key==='z'||e.key==='Z'){
      delete keyDown[e.key];doJumpEnd();
    }
  });
}

let prev=0;
function loop(ts){
  const dt=Math.min((ts-prev)||16,50);prev=ts;
  if(running){
    totalMs+=dt;
    timerMs+=dt;
    if(timerMs>=1000){
      timerMs-=1000;tempsRestant=Math.max(0,tempsRestant-1);
      const m=Math.floor(tempsRestant/60),s=tempsRestant%60;
      if(timerEl)timerEl.textContent=m+':'+(s<10?'0':'')+s;
      if(tempsRestant===30)lune('30 secondes !');
      if(tempsRestant<=0){running=false;setTimeout(()=>fin(true),300);}
    }
    fisica();tickLasers(dt);
  }
  requestAnimationFrame(loop);
}

build();ctls();requestAnimationFrame(loop);

document.getElementById('btn-st').addEventListener('click',()=>{
  document.getElementById('tuto').style.display='none';
  running=true;demarrerMusiqueNiveau();
  if(cfg.lune_start)setTimeout(()=>lune(cfg.lune_start),1500);
});
document.getElementById('br').addEventListener('click',()=>location.reload());
document.getElementById('bb').addEventListener('click',()=>{try{window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:cfg.niveau},'*');}catch(e){}});
document.getElementById('btn-q').addEventListener('click',()=>{if(confirm('Quitter ?'))try{window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:cfg.niveau},'*');}catch(e){}});
window.GPS0_MJ_LUNE=lune;
})(window.GPS0_NIVEAU_CFG);
