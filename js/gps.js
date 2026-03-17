window.GPS0_GPS = {
  config: null,
  zonesActives: [],
  async chargerConfig() {
    const res = await fetch("gps_config.json");
    this.config = await res.json();
    return this.config;
  },
  appliquerParcours(parcoursId) {
    const ordre = this.config.parcours[parcoursId].ordre;
    this.zonesActives = ordre.map((id) => this.config.zones_fixes.find((z) => z.id === id));
    localStorage.setItem("gps0_zones_actives", JSON.stringify(this.zonesActives));
    return this.zonesActives;
  }
};
