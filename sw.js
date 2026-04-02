const CACHE_NAME = "bible-web-v2";
const ASSETS_TO_CACHE = [
    "./index.html",
    "./bible_structured.json",
    "./favicon.png",
];

async function cacheResponse(cacheKey, response) {
    const cache = await caches.open(CACHE_NAME);
    await cache.put(cacheKey, response.clone());
    return response;
}

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE)),
    );
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                    return undefined;
                }),
            ),
        ),
    );
    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    const { request } = event;

    if (request.method !== "GET") return;

    const url = new URL(request.url);
    if (url.origin !== self.location.origin) return;

    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    if (response && response.status === 200) {
                        return cacheResponse("./index.html", response);
                    }
                    return response;
                })
                .catch(() => caches.match("./index.html")),
        );
        return;
    }

    if (!url.pathname.endsWith("/bible_structured.json")) return;

    event.respondWith(
        caches.match(request).then((cachedResponse) => {
            if (cachedResponse) return cachedResponse;

            return fetch(request).then((networkResponse) => {
                if (!networkResponse || networkResponse.status !== 200) {
                    return networkResponse;
                }

                const responseToCache = networkResponse.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(request, responseToCache);
                });

                return networkResponse;
            });
        }),
    );
});
