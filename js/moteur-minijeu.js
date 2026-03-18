'use strict';
(function(cfg){
const W=window.innerWidth,H=window.innerHeight;
const G=cfg.gravite||0.46,JF=cfg.saut_force||-11,VXmax=cfg.vitesse||3.6;
const TOTAL=cfg.total_poussieres||8;
const DOUBLE_SAUT=!!cfg.double_saut;
let jx=cfg.spawn_x||60,jy=cfg.spawn_y||(H-120);
let vx=0,vy=0,air=true,sauts_restants=DOUBLE_SAUT?2:1;
let gauche=false,droite=false,vouloir_sauter=false;
let vies=3,etoiles=0,running=false,invincible=false;
const monde=document.getElementById('monde');
const plates=[],slimes=[],pds=[],lasers=[],mobiles=[],fragiles=[],pics=[];

// --- Selfie ---
try{const b=window.parent.GPS0_Avatar&&window.parent.GPS0_Avatar.getSelfie();if(b){const el=document.getElementById('ts');el.style.backgroundImage='url('+b+')';}else{try{const b2=window.parent.GPS0_Avatar.getSelfie();if(b2){document.getElementById('ts').style.backgroundImage='url('+b2+')';}}catch{}}}catch{}

// --- Construction ---
function mkEl(cls,x,y,w,h,extra){
  const e=document.createElement('div');e.className=cls;
  e.style.cssText='position:absolute;left:'+x+'px;top:'+y+'px;width:'+w+'px;height:'+h+'px'+(extra||'');
  monde.appendChild(e);return e;
}
function mkPlate(c,sol,mobile,fragile){
  const e=mkEl('plate'+(sol?' sol':mobile?' mobile':fragile?' fragile':''),c.x,c.y,c.w,c.h);
  const obj={...c,e,sol:!!sol,mobile:!!mobile,fragile:!!fragile,mx0:c.x,my0:c.y,mt:0,alpha:0,falling:false};
  plates.push(obj);
  if(mobile&&c.range){obj.range=c.range;obj.speed=c.ms||1.2;obj.axis=c.axis||'x';}
  return obj;
}
function build(){
  (cfg.plateformes||[]).forEach(c=>{mkPlate(c,c.sol,c.mobile,c.fragile);});
  (cfg.slimes||[]).forEach(c=>{
    const p=plates[c.pi];if(!p)return;
    const e=mkEl('slime',p.x+p.w/2-19,p.y-32,38,30);e.style.borderRadius='50% 50% 40% 40%';
    const col=c.col||'#69FF47';e.style.background='radial-gradient(circle at 40% 35%,'+col+','+col.replace('#69FF47','#22aa22').replace('#FF3333','#aa0000').replace('#FF8C00','#aa5500')+')';
    e.style.boxShadow='0 0 14px '+col+'88';e.textContent='👾';e.style.display='flex';e.style.alignItems='center';e.style.justifyContent='center';e.style.fontSize='.9rem';
    slimes.push({e,x:p.x+p.w/2-19,y:p.y-32,bx:p.x,bw:p.w,vx:(c.speed||1.2)*(c.dir||1),by:p.y-32});
  });
  (cfg.poussieres||[]).forEach((c,i)=>{
    const p=plates[c.pi];if(!p)return;
    const cnt=(cfg.poussieres||[]).filter(d=>d.pi===c.pi).length;
    const idx=(cfg.poussieres||[]).slice(0,i).filter(d=>d.pi===c.pi).length;
    const ox=p.w/(cnt+1)*(idx+1);
    const px=p.x+ox-9,py=p.y-28;
    const e=mkEl('pdiere',px,py,18,18);
    pds.push({e,x:px,y:py,col:false});
  });
  (cfg.lasers||[]).forEach(c=>{
    const e=mkEl('laser-h',c.x,c.y,c.w,6);
    lasers.push({e,...c,t:c.offset||0,warn_dur:c.warn||1500,on_dur:c.on||2000,off_dur:c.off||2000,phase:'off'});
  });
  (cfg.pics||[]).forEach(c=>{
    const e=mkEl('pic',c.x,c.y,20,c.h||16);
    e.style.clipPath='polygon(50% 0%,100% 100%,0% 100%)';
    e.style.background='linear-gradient(180deg,#FF6B6B,#CC0000)';
    pics.push({e,...c});
  });
}

// --- Physique ---
function fisica(ts){
  if(gauche)vx=-VXmax;else if(droite)vx=VXmax;else vx*=0.7;
  if(vouloir_sauter&&sauts_restants>0){vy=JF*(sauts_restants<2?0.85:1);sauts_restants--;air=true;sfx('saut_cosmonaute');}
  vouloir_sauter=false;
  vy=Math.min(vy+G,18);jx+=vx;jy+=vy;
  jx=Math.max(0,Math.min(W-40,jx));

  // Plateformes mobiles
  plates.forEach(p=>{
    if(!p.mobile||!p.range)return;
    p.mt=(p.mt||0)+0.016;
    if(p.axis==='x'){p.x=p.mx0+Math.sin(p.mt*p.speed)*p.range;p.e.style.left=p.x+'px';}
    else{p.y=p.my0+Math.sin(p.mt*p.speed)*p.range;p.e.style.top=p.y+'px';}
  });
  // Plateformes fragiles
  plates.forEach(p=>{
    if(!p.fragile||!p.falling)return;
    p.alpha=(p.alpha||0)+0.05;p.e.style.opacity=Math.max(0,1-p.alpha);
    p.y+=p.alpha*2;p.e.style.top=p.y+'px';
  });

  air=true;
  for(const p of plates){
    if(p.fragile&&p.falling&&p.alpha>1)continue;
    const cx=jx+20,foot=jy+52;
    if(cx>p.x+4&&cx<p.x+p.w-4){
      if(vy>=0&&foot>=p.y&&foot<=p.y+p.h+Math.abs(vy)+3){
        jy=p.y-52;vy=0;air=false;sauts_restants=DOUBLE_SAUT?2:1;
        if(p.fragile&&!p.falling){setTimeout(()=>{p.falling=true;},400);}
      } else if(vy<0&&jy<=p.y+p.h&&jy>=p.y-8){vy=0;}
    }
  }
  if(jy>H+80){perdre();return;}

  if(!invincible){
    for(const s of slimes){
      s.x+=s.vx;if(s.x<s.bx||s.x+38>s.bx+s.bw)s.vx*=-1;
      s.e.style.left=s.x+'px';
      const dx=(jx+20)-(s.x+19),dy=(jy+26)-(s.y+15);
      if(Math.sqrt(dx*dx+dy*dy)<30){perdre();return;}
    }
    for(const l of lasers){
      if(l.phase==='actif'){
        const dx=jx+20,dy=jy+26;
        if(dx>l.x&&dx<l.x+l.w&&dy>l.y-4&&dy<l.y+10){perdre();return;}
      }
    }
    for(const p of pics){
      const dx=(jx+20)-(p.x+10),dy=(jy+52)-(p.y+8);
      if(Math.sqrt(dx*dx+dy*dy)<20){perdre();return;}
    }
  }

  for(const p of pds){
    if(p.col)continue;
    const dx=(jx+20)-(p.x+9),dy=(jy+26)-(p.y+9);
    if(Math.sqrt(dx*dx+dy*dy)<28){p.col=true;p.e.style.display='none';etoiles++;sfx('collecte_poussiere');
      document.getElementById('mj-e').textContent=etoiles+'/'+TOTAL+' ✨';
      if(etoiles>=TOTAL){running=false;setTimeout(()=>fin(true),300);}
    }
  }
  document.getElementById('joueur').style.cssText='position:absolute;left:'+jx+'px;top:'+jy+'px;width:40px;height:52px;display:flex;flex-direction:column;align-items:center;pointer-events:none;will-change:transform';
}

// --- Lasers ---
let lt=0;
function tickLasers(dt){
  lasers.forEach(l=>{
    l.t+=dt;
    const cycle=l.warn_dur+l.on_dur+l.off_dur;
    const tp=l.t%cycle;
    let np;
    if(tp<l.warn_dur)np='warn';else if(tp<l.warn_dur+l.on_dur)np='actif';else np='off';
    if(np!==l.phase){l.phase=np;l.e.className='laser-h '+(np!=='off'?np:'');if(np==='warn')sfx('laser_warning');}
  });
}

function perdre(){
  if(invincible)return;
  invincible=true;vies--;
  const vmap=['','❤️','❤️❤️','❤️❤️❤️'];
  document.getElementById('mj-v').textContent=vmap[Math.max(0,vies)]||'';
  lune(vies===1?'Dernière chance cosmonaute !':(vies===0?'...':'Aie ! Maladroit !'));
  if(vies<=0){running=false;setTimeout(()=>fin(false),400);return;}
  jx=cfg.spawn_x||60;jy=cfg.spawn_y||(H-120);vx=0;vy=0;
  setTimeout(()=>{invincible=false;},1200);
}

function fin(ok){
  const ov=document.getElementById('ov'),ot=document.getElementById('ot');
  ot.textContent=ok?'Victoire ! 🎉':'Perdu... 💫';ot.className=ok?'win':'lose';
  document.getElementById('os').textContent=ok?cfg.msg_win||'Bien joué !':cfg.msg_lose||'La Lune te juge.';
  document.getElementById('op').textContent=(ok?'+ '+TOTAL:etoiles)+' ✨ Poussières';
  ov.classList.add('v');
  try{window.parent.postMessage({source:'gps0_minijeu',success:ok,niveau:cfg.niveau,poussieres:ok?TOTAL:etoiles,etoiles:ok?3:1},'*');}catch{}
}

function lune(txt){const e=document.getElementById('lune');e.textContent='🌙 '+txt;e.classList.add('v');setTimeout(()=>e.classList.remove('v'),4500);}
function sfx(n){try{window.parent.GPS0_Audio&&window.parent.GPS0_Audio.playSFX(n);}catch{}}

function ctls(){
  document.getElementById('zg').addEventListener('touchstart',e=>{e.preventDefault();gauche=true},{passive:false});
  document.getElementById('zg').addEventListener('touchend',e=>{e.preventDefault();gauche=false},{passive:false});
  document.getElementById('zd').addEventListener('touchstart',e=>{e.preventDefault();droite=true},{passive:false});
  document.getElementById('zd').addEventListener('touchend',e=>{e.preventDefault();droite=false},{passive:false});
  document.getElementById('bs').addEventListener('touchstart',e=>{e.preventDefault();vouloir_sauter=true},{passive:false});
  window.addEventListener('keydown',e=>{
    if(e.key==='ArrowLeft'||e.key==='q')gauche=true;
    if(e.key==='ArrowRight'||e.key==='d')droite=true;
    if(e.key==='ArrowUp'||e.key===' '||e.key==='z'){vouloir_sauter=true;e.preventDefault();}
  });
  window.addEventListener('keyup',e=>{
    if(e.key==='ArrowLeft'||e.key==='q')gauche=false;
    if(e.key==='ArrowRight'||e.key==='d')droite=false;
  });
}

let prev=0;
function loop(ts){
  const dt=Math.min((ts-prev)||16,50);prev=ts;
  if(running){fisica(ts);tickLasers(dt);}
  requestAnimationFrame(loop);
}

build();ctls();requestAnimationFrame(loop);

document.getElementById('btn-st').addEventListener('click',()=>{
  document.getElementById('tuto').style.display='none';running=true;
  if(cfg.lune_start)setTimeout(()=>lune(cfg.lune_start),1500);
});
document.getElementById('bb').addEventListener('click',()=>{try{window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:cfg.niveau},'*');}catch{}});
document.getElementById('br').addEventListener('click',()=>location.reload());
document.getElementById('btn-q').addEventListener('click',()=>{if(confirm('Quitter ce niveau ?'))try{window.parent.postMessage({source:'gps0_minijeu',success:false,niveau:cfg.niveau},'*');}catch{}});

window.GPS0_MJ_LUNE=lune;
})(window.GPS0_NIVEAU_CFG);