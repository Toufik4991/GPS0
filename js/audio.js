window.GPS0_Audio = {
  enabled: true,
  toggle() { this.enabled = !this.enabled; localStorage.setItem("gps0_audio_enabled", this.enabled ? "1" : "0"); }
};
