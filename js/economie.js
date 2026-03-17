window.GPS0_Economie = {
  get() { return JSON.parse(localStorage.getItem("gps0_economie") || '{"poussieres":0,"energie":{"actuelle":100,"max":100}}'); },
  save(v) { localStorage.setItem("gps0_economie", JSON.stringify(v)); }
};
