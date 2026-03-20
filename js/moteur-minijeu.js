'use strict';
(function(cfg){
const W=window.innerWidth,H=window.innerHeight;
const MONDE_W=Math.round(W*(cfg.monde_w||1));
const G=cfg.gravite||0.46,JF=cfg.saut_force||-11,VXmax=cfg.vitesse||3.6;
const TOTAL=cfg.total_poussieres||8;
const DOUBLE_SAUT=!!cfg.double_saut;
let jx=cfg.spawn_x||80,jy=cfg.spawn_y||(H-120);
let vx=0,vy=0,air=true,sauts_restants=DOUBLE_SAUT?2:1;
let gauche=false,droite=false,vouloir_sauter=false;
let vies=cfg.vies||3,etoiles=0,running=false,invincible=false;
let camX=0;
const monde=document.getElementById('monde');
const plates=[],slimes=[],pds=[],lasers=[],pics=[];
try{const b=window.parent.GPS0_Avatar&&window.parent.GPS0_Avatar.getSelfie();if(b){const el=document.getElementById('ts');if(el)el.style.backgroundImage='url('+b+')';}}catch(e){}
function mkEl(cls,x,y,w,h){const e=document.createElement('div');e.className=cls;e.style.position='absolute';e.style.left=x+'px';e.style.top=y+'px';e.style.width=w+'px';e.style.height=h+'px';monde.appendChild(e);return e;}
function mkPlate(c){const t='plate'+(c.sol?' sol':c.mobile?' mobile':c.fragile?' fragile':'');const e=mkEl(t,c.x,c.y,c.w,c.h);const obj=Object.assign({},c,{e,sol:!!c.sol,mobile:!!c.mobile,fragile:!!c.fragile,mx0:c.x,my0:c.y,mt:0,alpha:0,falling:false});plates.push(obj);return obj;}
function build(){
  if(MONDE_W>W){monde.style.width=MONDE_W+'px';monde.style.right='auto';}
  (cfg.plateformes||[]).forEach(c=>mkPlate(c));
  (cfg.slimes||[]).forEach(c=>{const p=plates[c.pi];if(!p)return;const e=mkEl('slime',p.x+p.w/2-19,p.y-32,38,30);const col=c.col||'#69FF47';const darks={'#69FF47':'#22aa22','#ff9944':'#aa5500','#ff3a3a':'#aa0000'};const dark=darks[col]||'#226622';e.style.background='radial-gradient(circle at 40% 35%,'+col+','+dark+')';e.style.boxShadow='0 0 14px '+col+'88';e.textContent=String.fromCodePoint(0x1F47E);e.style.display='flex';e.style.alignItems='center';e.style.justifyContent='center';e.style.fontSize='.9rem';e.style.borderRadius='50% 50% 40% 40%';slimes.push({e,x:p.x+p.w/2-19,y:p.y-32,bx:p.x,bw:p.w,vx:(c.speed||1.2)*(c.dir||1)});});
  (cfg.poussieres||[]).forEach((c,i)=>{const p=plates[c.pi];if(!p)return;const cnt=(cfg.poussieres||[]).filter(d=>d.pi===c.pi).length;const idx=(cfg.poussieres||[]).slice(0,i).filter(d=>d.pi===c.pi).length;const ox=p.w/(cnt+1)*(idx+1);const e=mkEl('pdiere',p.x+ox-9,p.y-28,18,18);pds.push({e,x:p.x+ox-9,y:p.y-28,col:false});});
  (cfg.lasers||[]).forEach(c=>{const e=mkEl('laser-h',c.x,c.y,c.w,6);lasers.push(Object.assign({},c,{e,t:c.offset||0,warn_dur:c.warn||1500,on_dur:c.on||2000,off_dur:c.off||2000,phase:'off'}));});
  (cfg.pics||[]).forEach(c=>{let px=c.x!=null?c.x:0,py=c.y!=null?c.y:0;if(c.pi!=null&&plates[c.pi]){const p=plates[c.pi];px=p.x+p.w/2-11;py=p.y-(c.h||16);}const e=mkEl('pic',px,py,22,c.h||18);e.style.clipPath='polygon(50% 0%,100% 100%,0% 100%)';e.style.background=c.col||'linear-gradient(180deg,#FF6B6B,#CC0000)';pics.push({e,x:px,y:py});});
}
function fisica(){
  if(gauche)vx=-VXmax;else if(droite)vx=VXmax;else vx*=0.7;
  if(vouloir_sauter&&sauts_restants>0){vy=JF*(sauts_restants<2?0.85:1);sauts_restants--;air=true;sfx('saut_cosmonaute');}
  vouloir_sauter=false;
  vy=Math.min(vy+G,18);jx+=vx;jy+=vy;
  jx=Math.max(0,Math.min(MONDE_W-40,jx));
  plates.forEach(p=>{if(!p.mobile||!p.range)return;p.mt=(p.mt||0)+0.016;if(p.axis==='x'){p.x=p.mx0+Math.sin(p.mt*p.speed)*p.range;p.e.style.left=p.x+'px';}else{p.y=p.my0+Math.sin(p.mt*p.speed)*p.range;p.e.style.top=p.y+'px';}});
  plates.forEach(p=>{if(!p.fragile||!p.falling)return;p.alpha=(p.alpha||0)+0.05;p.e.style.opacity=Math.max(0,1-p.alpha);p.y+=p.alpha*2;p.e.style.top=p.y+'px';});
  air=true;
  for(const p of plates){if(p.fragile&&p.falling&&p.alpha>1)continue;const cx=jx+20,foot=jy+52;if(cx>p.x+4&&cx<p.x+p.w-4){if(vy>=0&&foot>=p.y&&foot<=p.y+p.h+Math.abs(vy)+3){jy=p.y-52;vy=0;air=false;sauts_restants=DOUBLE_SAUT?2:1;if(p.fragile&&!p.falling)setTimeout(()=>{p.falling=true;},400);if(p.mobile&&air)sfx('plateforme_active');}else if(vy<0&&jy<=p.y+p.h&&jy>=p.y-8)vy=0;}}
  if(jy>H+80){perdre();return;}
  if(!invincible){
    for(const s of slimes){s.x+=s.vx;if(s.x<s.bx||s.x+38>s.bx+s.bw)s.vx*=-1;s.e.style.left=s.x+'px';const dx=(jx+20)-(s.x+19),dy=(jy+26)-(s.y+15);if(Math.sqrt(dx*dx+dy*dy)<30){perdre();return;}}
    for(const l of lasers){if(l.phase==='actif'){const dx=jx+20,dy=jy+26;if(dx>l.x&&dx<l.x+l.w&&dy>l.y-4&&dy<l.y+10){perdre();return;}}}
    for(const p of pics){const dx=(jx+20)-(p.x+11),dy=(jy+52)-(p.y+9);if(Math.sqrt(dx*dx+dy*dy)<22){perdre();return;}}
  }
  for(const p of pds){if(p.col)continue;const dx=(jx+20)-(p.x+9),dy=(jy+26)-(p.y+9);if(Math.sqrt(dx*dx+dy*dy)<28){p.col=true;p.e.style.display='none';etoiles++;sfx('collecte_poussiere');document.getElementById('mj-e').textContent=etoiles+'/'+TOTAL+' \u2728';if(etoiles>=TOTAL){running=false;setTimeout(()=>fin(true),300);}}}
  if(MONDE_W>W){const tgt=Math.max(0,Math.min(jx-W*0.35,MONDE_W-W));camX+=(tgt-camX)*0.12;monde.style.transform='translateX('+(-Math.round(camX))+'px)';}
  const sx=MONDE_W>W?Math.round(jx-camX):jx;
  const jEl=document.getElementById('joueur');if(jEl){jEl.style.left=sx+'px';jEl.style.top=jy+'px';}
}
let lt=0;
function tickLasers(dt){lasers.forEach(l=>{l.t+=dt;const cycle=l.warn_dur+l.on_dur+l.off_dur,tp=l.t%cycle;const np=tp<l.warn_dur?'warn':tp<l.warn_dur+l.on_dur?'actif':'off';if(np!==l.phase){l.phase=np;l.e.className='laser-h '+(np!=='off'?np:'');if(np==='warn')sfx('laser_warning');}});}
function perdre(){if(invincible)return;invincible=true;sfx('ennemi_touche');vies--;const vm=['','\u2764\uFE0F','\u2764\uFE0F\u2764\uFE0F','\u2764\uFE0F\u2764\uFE0F\u2764\uFE0F'];document.getElementById('mj-v').textContent=vm[Math.max(0,vies)]||'';lune(vies===1?'Derni\u00e8re chance !':(vies===0?'...':'Aie !'));if(vies<=0){running=false;setTimeout(()=>fin(false),400);return;}jx=cfg.spawn_x||80;jy=cfg.spawn_y||(H-120);vx=0;vy=0;camX=0;if(MONDE_W>W)monde.style.transform='translateX(0px)';setTimeout(()=>{invincible=false;},1200);}
// ── OVERLAY FIN: choix joueur ───────────────────────────────────
function fin(ok){
  if(ok)sfx('boss_hit');
  const ov=document.getElementById('ov'),ot=document.getElementById('ot');
  ot.textContent=ok?'Victoire !':'Perdu...';
  ot.className=ok?'win':'lose';
  document.getElementById('os').textContent=ok?cfg.msg_win||'Bien joy\u00e9 !':cfg.msg_lose||'La Lune te juge.';
  const pEl=document.getElementById('op');
  if(pEl)pEl.textContent=(ok?'+ '+TOTAL:etoiles)+' \u2728 Poussi\u00e8res';
  // Afficher seulement les boutons pertinents
  const btnRecommencer=document.getElementById('br');
  const btnRecompense=document.getElementById('bc');
  const btnAbandon=document.getElementById('bb');
  if(btnRecommencer)btnRecommencer.style.display='inline-block';
  if(btnAbandon)btnAbandon.style.display='inline-block';
  // Bouton recompense = seulement si victoire
  if(btnRecompense){
    btnRecompense.style.display=ok?'inline-block':'none';
    if(ok){
      btnRecompense.textContent='\u2728 Prendre les '+TOTAL+' poussi\u00e8res';
      btnRecompense.onclick=()=>{
        try{window.parent.postMessage({source:'gps0_minijeu',success:true,niveau:cfg.niveau,poussieres:TOTAL,etoiles:3},'*');}catch(e){}
      };
    }
  }
  ov.classList.add('v');
}
function lune(txt){const e=document.getElementById('lune');if(e){e.textContent='\uD83C\uDF19 '+txt;e.classList.add('v');setTimeout(()=>e.classList.remove('v'),4500);}}
function sfx(n){try{window.parent.GPS0_Audio&&window.parent.GPS0_Audio.playSFX(n);}catch(e){}}
function demarrerMusiqueNiveau(){
  try{
    const audio=window.parent.GPS0_Audio;
    if(audio&&audio.isEnabled&&audio.isEnabled()){
      // Relancer une piste exploration aléatoire pour ce niveau
      audio.playMusiqueExploration();
    }
  }catch(e){}
}
function ctls(){
  const zg=document.getElementById('zg'),zd=document.getElementById('zd'),bs=document.getElementById('bs');
  if(zg){zg.addEventListener('touchstart',e=>{e.preventDefault();gauche=true},{passive:false});zg.addEventListener('touchend',e=>{e.preventDefault();gauche=false},{passive:false});}
  if(zd){zd.addEventListener('touchstart',e=>{e.preventDefault();droite=true},{passive:false});zd.addEventListener('touchend',e=>{e.preventDefault();droite=false},{passive:false});}
  if(bs){bs.addEventListener('touchstart',e=>{e.preventDefault();vouloir_sauter=true},{passive:false});}
  window.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='q')gauche=true;if(e.key==='ArrowRight'||e.key==='d')droite=true;if(e.key==='ArrowUp'||e.key===' '||e.key==='z'){vouloir_sauter=true;e.preventDefault();}});
  window.addEventListener('keyup',e=>{if(e.key==='ArrowLeft'||e.key==='q')gauche=false;if(e.key==='ArrowRight'||e.key==='d')droite=false;});
}
let prev=0;
function loop(ts){const dt=Math.min((ts-prev)||16,50);prev=ts;if(running){fisica();tickLasers(dt);}requestAnimationFrame(loop);}
build();ctls();requestAnimationFrame(loop);
document.getElementById('btn-st').addEventListener('click',()=>{document.getElementById('tuto').style.display='none';running=true;demarrerMusiqueNiveau();if(cfg.lune_start)setTimeout(()=>lune(cfg.lune_start),1500);});
// Recommencer = simple reload, SANS recompense
document.getElementById('br').addEventListener('click',()=>location.reload());
// Abandon = retour GPS sans recompense
document.getElementById('bb').addEventListener('click',()=>{try{window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:cfg.niveau},'*');}catch(e){}});
// Quitter en cours de jeu
document.getElementById('btn-q').addEventListener('click',()=>{if(confirm('Quitter ?'))try{window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:cfg.niveau},'*');}catch(e){}});
window.GPS0_MJ_LUNE=lune;
})(window.GPS0_NIVEAU_CFG);