window.GPS0_Avatar = {
  getSelfie() { return localStorage.getItem("gps0_avatar_selfie_base64"); },
  setSelfie(base64) { localStorage.setItem("gps0_avatar_selfie_base64", base64); }
};
