const CACHE_NAME = "ttl-archival-v1";
const STATIC_CACHE = "ttl-archival-static-v1";
const API_CACHE = "ttl-archival-api-v1";

// Static assets to cache immediately
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/manifest.json",
  // Add other static assets as needed
];

// API endpoints to cache
const API_ENDPOINTS = [
  "/api/dashboard",
  "/api/policies",
  "/api/archives",
  "/api/blockchain",
  "/api/settings",
];

// Install event - cache static assets
self.addEventListener("install", (event) => {
  console.log("Service Worker: Installing...");

  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => {
        console.log("Service Worker: Caching static assets");
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting()),
  );
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  console.log("Service Worker: Activating...");

  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== API_CACHE) {
              console.log("Service Worker: Deleting old cache:", cacheName);
              return caches.delete(cacheName);
            }
          }),
        );
      })
      .then(() => self.clients.claim()),
  );
});

// Fetch event - implement caching strategies
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-HTTP requests
  if (!request.url.startsWith("http")) {
    return;
  }

  // Strategy 1: Cache First for static assets
  if (isStaticAsset(request)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
  }
  // Strategy 2: Network First for API calls
  else if (isAPIRequest(request)) {
    event.respondWith(networkFirst(request, API_CACHE));
  }
  // Strategy 3: Stale While Revalidate for navigation requests
  else if (request.mode === "navigate") {
    event.respondWith(staleWhileRevalidate(request, STATIC_CACHE));
  }
  // Default: Network only
  else {
    event.respondWith(fetch(request));
  }
});

// Cache First strategy
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);

  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.error("Cache First strategy failed:", error);
    throw error;
  }
}

// Network First strategy
async function networkFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);

  try {
    const networkResponse = await fetch(request);

    // Cache successful responses
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log("Network failed, serving from cache:", error);

    if (cachedResponse) {
      return cachedResponse;
    }

    // Return offline fallback for API requests
    if (isAPIRequest(request)) {
      return new Response(
        JSON.stringify({
          error: "Offline",
          message: "No network connection and no cached data available",
        }),
        {
          status: 503,
          headers: { "Content-Type": "application/json" },
        },
      );
    }

    throw error;
  }
}

// Stale While Revalidate strategy
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);

  // Always try to update the cache in the background
  const fetchPromise = fetch(request)
    .then((networkResponse) => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    })
    .catch((error) => {
      console.error("Background fetch failed:", error);
    });

  // Return cached version immediately if available
  if (cachedResponse) {
    return cachedResponse;
  }

  // Otherwise wait for the network
  return fetchPromise;
}

// Helper functions
function isStaticAsset(request) {
  const url = new URL(request.url);
  return (
    request.destination === "script" ||
    request.destination === "style" ||
    request.destination === "image" ||
    url.pathname.includes("/assets/") ||
    url.pathname.includes("/static/")
  );
}

function isAPIRequest(request) {
  const url = new URL(request.url);
  return url.pathname.startsWith("/api/");
}

// Background sync for offline actions
self.addEventListener("sync", (event) => {
  if (event.tag === "background-sync") {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Handle offline actions that need to be synced
  console.log("Service Worker: Background sync started");

  // Get all pending requests from IndexedDB and retry them
  // This would require implementing IndexedDB storage for offline actions
}

// Push notification handling
self.addEventListener("push", (event) => {
  if (event.data) {
    const options = {
      body: event.data.text(),
      icon: "/icon-192x192.png",
      badge: "/badge-72x72.png",
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: 1,
      },
    };

    event.waitUntil(
      self.registration.showNotification("TTL Archival Service", options),
    );
  }
});

// Notification click handling
self.addEventListener("notificationclick", (event) => {
  console.log("Notification click received.");
  event.notification.close();
  event.waitUntil(clients.openWindow("/"));
});
