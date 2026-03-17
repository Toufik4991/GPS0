const CACHE = "gps0-v1";
const CORE = ["/", "/index.html", "/css/main.css", "/js/app.js", "/gps_config.json"];
self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)));
});
self.addEventListener("fetch", (event) => {
  event.respondWith(caches.match(event.request).then((res) => res || fetch(event.request)));
});
