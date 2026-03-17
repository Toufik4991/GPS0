window.GPS0_App = {
  startTime: Date.now(),
  async init() {
    await this.showSplash();
    await this.ensurePseudo();
    await this.ensureDifficulte();
    const parcours = await this.ensureParcours();
    await window.GPS0_GPS.chargerConfig();
    const zones = window.GPS0_GPS.appliquerParcours(parcours);
    document.getElementById("objectif").textContent = zones[0] ? zones[0].nom : "Aucun objectif";
    this.bindUI();
    this.startClock();
    this.showApp();
  },
  showSplash() { return new Promise((resolve) => setTimeout(resolve, 2000)); },
  ensurePseudo() {
    if (localStorage.getItem("gps0_pseudo")) return Promise.resolve();
    const modal = document.getElementById("modal-pseudo");
    modal.showModal();
    return new Promise((resolve) => modal.addEventListener("close", () => {
      const v = document.getElementById("pseudo-input").value.trim() || "Explorateur";
      localStorage.setItem("gps0_pseudo", v);
      resolve();
    }, { once: true }));
  },
  ensureDifficulte() {
    if (localStorage.getItem("gps0_difficulte")) return Promise.resolve();
    const modal = document.getElementById("modal-difficulte");
    modal.showModal();
    return new Promise((resolve) => modal.addEventListener("close", () => {
      localStorage.setItem("gps0_difficulte", document.getElementById("difficulte-select").value);
      resolve();
    }, { once: true }));
  },
  ensureParcours() {
    const modal = document.getElementById("modal-parcours");
    modal.showModal();
    return new Promise((resolve) => modal.addEventListener("close", () => resolve(document.getElementById("parcours-select").value), { once: true }));
  },
  bindUI() {
    document.getElementById("toggle-boussole").addEventListener("click", () => {
      const active = window.GPS0_Boussole.toggle();
      document.getElementById("toggle-boussole").textContent = active ? "Boussole ON" : "Boussole OFF";
    });
  },
  startClock() {
    const tick = () => {
      const sec = Math.floor((Date.now() - this.startTime) / 1000);
      const mm = String(Math.floor(sec / 60)).padStart(2, "0");
      const ss = String(sec % 60).padStart(2, "0");
      document.getElementById("chrono").textContent = mm + ":" + ss;
      requestAnimationFrame(tick);
    };
    tick();
  },
  showApp() {
    document.getElementById("splash").classList.remove("visible");
    document.getElementById("app").classList.add("visible");
  }
};
window.addEventListener("DOMContentLoaded", () => window.GPS0_App.init());
if ("serviceWorker" in navigator) { navigator.serviceWorker.register("service-worker.js"); }
