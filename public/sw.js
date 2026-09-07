/* Minimal service worker: its presence (with a fetch handler) is what makes
   the site installable as an app. Deliberately no caching — the site deploys
   as static files and a stale-cache bug is worse than no cache. */
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", () => {});
