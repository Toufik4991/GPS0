'use strict';
window.GPS0_Avatar = (() => {
  let stream = null;

  function getSelfie() { return localStorage.getItem('gps0_avatar_selfie_base64'); }
  function setSelfie(b64) { localStorage.setItem('gps0_avatar_selfie_base64', b64); }

  async function demarrerCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 640 } },
        audio: false
      });
      const v = document.getElementById('selfie-video');
      if (v) {
        v.setAttribute('autoplay', '');
        v.setAttribute('playsinline', '');
        v.setAttribute('muted', '');
        v.srcObject = stream;
        // iOS Safari : attendre loadedmetadata avant d'afficher
        await new Promise(r => {
          v.addEventListener('loadedmetadata', r, { once: true });
          setTimeout(r, 3000); // Fallback timeout
        });
        try { await v.play(); } catch (_) {}
      }
      return true;
    } catch (e) { console.warn('Camera:', e.message); return false; }
  }

  function arreterCamera() {
    if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
    const v = document.getElementById('selfie-video');
    if (v) v.srcObject = null;
  }

  function capturer() {
    const video = document.getElementById('selfie-video');
    const c32 = document.getElementById('selfie-canvas');
    const prev = document.getElementById('selfie-preview');
    if (!video || !c32) return null;
    const ctx32 = c32.getContext('2d', { willReadFrequently: true });
    ctx32.drawImage(video, 0, 0, 32, 32);
    if (prev) {
      const cp = prev.getContext('2d');
      cp.imageSmoothingEnabled = false;
      cp.clearRect(0, 0, 200, 200);
      cp.drawImage(c32, 0, 0, 200, 200);
    }
    return c32.toDataURL('image/png');
  }

  function injecterDansJeux(b64) {
    document.documentElement.style.setProperty('--selfie-url', 'url(' + b64 + ')');
    const hublot = document.getElementById('selfie-hublot');
    if (hublot) hublot.setAttribute('href', b64);
  }

  return { getSelfie, setSelfie, demarrerCamera, arreterCamera, capturer, injecterDansJeux };
})();
