"""
Progressive Web App (PWA) configuration and mobile optimizations
"""
import streamlit as st
import json

def create_pwa_manifest():
    """Create PWA manifest for mobile app experience"""
    manifest = {
        "name": "GitHub Leaderboard Pro",
        "short_name": "GitLeaderboard",
        "description": "Next-generation developer community platform with real-time analytics",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#764ba2",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTkyIiBoZWlnaHQ9IjE5MiIgdmlld0JveD0iMCAwIDE5MiAxOTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxOTIiIGhlaWdodD0iMTkyIiByeD0iMjQiIGZpbGw9InVybCgjZ3JhZGllbnQwX2xpbmVhcl8xXzEpIi8+CjxkZWZzPgo8bGluZWFyR3JhZGllbnQgaWQ9ImdyYWRpZW50MF9saW5lYXJfMV8xIiB4MT0iMCIgeTE9IjAiIHgyPSIxOTIiIHkyPSIxOTIiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4KPHN0b3Agc3RvcC1jb2xvcj0iIzY2N2VlYSIvPgo8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM3NjRiYTIiLz4KPC9saW5lYXJHcmFkaWVudD4KPC9kZWZzPgo8dGV4dCB4PSI5NiIgeT0iMTEwIiBmb250LWZhbWlseT0iLWFwcGxlLXN5c3RlbSwgQmxpbmtNYWNTeXN0ZW1Gb250LCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjcyIiBmb250LXdlaWdodD0iYm9sZCIgZmlsbD0iI2ZmZmZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+8J+PhzwvdGV4dD4KPC9zdmc+",
                "sizes": "192x192",
                "type": "image/svg+xml"
            },
            {
                "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgdmlld0JveD0iMCAwIDUxMiA1MTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiByeD0iNjQiIGZpbGw9InVybCgjZ3JhZGllbnQwX2xpbmVhcl8xXzEpIi8+CjxkZWZzPgo8bGluZWFyR3JhZGllbnQgaWQ9ImdyYWRpZW50MF9saW5lYXJfMV8xIiB4MT0iMCIgeTE9IjAiIHgyPSI1MTIiIHkyPSI1MTIiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4KPHN0b3Agc3RvcC1jb2xvcj0iIzY2N2VlYSIvPgo8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM3NjRiYTIiLz4KPC9saW5lYXJHcmFkaWVudD4KPC9kZWZzPgo8dGV4dCB4PSIyNTYiIHk9IjMwMCIgZm9udC1mYW1pbHk9Ii1hcHBsZS1zeXN0ZW0sIEJsaW5rTWFjU3lzdGVtRm9udCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOTIiIGZvbnQtd2VpZ2h0PSJib2xkIiBmaWxsPSIjZmZmZmZmIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7wn4+HPC90ZXh0Pgo8L3N2Zz4=",
                "sizes": "512x512",
                "type": "image/svg+xml"
            }
        ],
        "categories": ["productivity", "developer", "social"],
        "lang": "en",
        "scope": "/",
        "prefer_related_applications": False
    }
    
    return json.dumps(manifest, indent=2)

def create_service_worker():
    """Create service worker for offline functionality"""
    service_worker = """
const CACHE_NAME = 'github-leaderboard-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
  'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

// Background sync for score updates
self.addEventListener('sync', function(event) {
  if (event.tag === 'background-sync-scores') {
    event.waitUntil(updateScoresInBackground());
  }
});

async function updateScoresInBackground() {
  try {
    const response = await fetch('/api/update-scores', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ action: 'update_all' })
    });
    return response.json();
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

// Push notification handling
self.addEventListener('push', function(event) {
  const options = {
    body: event.data ? event.data.text() : 'New activity on GitHub Leaderboard!',
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '2'
    },
    actions: [
      {
        action: 'explore',
        title: 'View Details',
        icon: '/icon-explore.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icon-close.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('GitHub Leaderboard Pro', options)
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});
"""
    return service_worker

def inject_pwa_tags():
    """Inject PWA meta tags and manifest"""
    pwa_html = f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="GitLeaderboard">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#667eea">
    
    <link rel="manifest" href="data:application/json;base64,{create_pwa_manifest().encode('utf-8').hex()}">
    <link rel="apple-touch-icon" href="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgwIiBoZWlnaHQ9IjE4MCIgdmlld0JveD0iMCAwIDE4MCAxODAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxODAiIGhlaWdodD0iMTgwIiByeD0iMjAiIGZpbGw9InVybCgjZ3JhZGllbnQpIi8+CjxkZWZzPgo8bGluZWFyR3JhZGllbnQgaWQ9ImdyYWRpZW50IiB4MT0iMCIgeTE9IjAiIHgyPSIxODAiIHkyPSIxODAiPgo8c3RvcCBzdG9wLWNvbG9yPSIjNjY3ZWVhIi8+CjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iIzc2NGJhMiIvPgo8L2xpbmVhckdyYWRpZW50Pgo8L2RlZnM+Cjx0ZXh0IHg9IjkwIiB5PSIxMDAiIGZvbnQtZmFtaWx5PSJzYW5zLXNlcmlmIiBmb250LXNpemU9IjY0IiBmb250LXdlaWdodD0iYm9sZCIgZmlsbD0iI2ZmZmZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+8J+PhzwvdGV4dD4KPC9zdmc+">
    
    <script>
    if ('serviceWorker' in navigator) {{
      window.addEventListener('load', function() {{
        navigator.serviceWorker.register('data:text/javascript;base64,{service_worker.encode('utf-8').hex()}')
          .then(function(registration) {{
            console.log('SW registered: ', registration);
          }}, function(registrationError) {{
            console.log('SW registration failed: ', registrationError);
          }});
      }});
    }}
    
    // Install prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {{
      e.preventDefault();
      deferredPrompt = e;
      showInstallPromotion();
    }});
    
    function showInstallPromotion() {{
      const installBtn = document.createElement('button');
      installBtn.innerHTML = '📱 Install App';
      installBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 20px;
        font-weight: 600;
        cursor: pointer;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
      `;
      
      installBtn.addEventListener('click', () => {{
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {{
          if (choiceResult.outcome === 'accepted') {{
            console.log('User accepted the install prompt');
          }}
          deferredPrompt = null;
        }});
        installBtn.remove();
      }});
      
      document.body.appendChild(installBtn);
      
      // Auto-hide after 10 seconds
      setTimeout(() => {{
        if (installBtn.parentNode) {{
          installBtn.remove();
        }}
      }}, 10000);
    }}
    
    // Request notification permission
    if ('Notification' in window && navigator.serviceWorker) {{
      if (Notification.permission === 'default') {{
        setTimeout(() => {{
          Notification.requestPermission().then(permission => {{
            console.log('Notification permission:', permission);
          }});
        }}, 5000);
      }}
    }}
    </script>
    """
    
    st.markdown(pwa_html, unsafe_allow_html=True)

def create_mobile_optimized_css():
    """Create mobile-optimized CSS"""
    mobile_css = """
    <style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .stApp {
            padding: 0 !important;
        }
        
        .main-container {
            margin: 0.5rem !important;
            padding: 1rem !important;
            border-radius: 15px !important;
        }
        
        .app-title {
            font-size: 2.2rem !important;
        }
        
        .leaderboard-item {
            flex-direction: column !important;
            text-align: center !important;
            gap: 1rem !important;
            padding: 1rem !important;
        }
        
        .user-info {
            margin-left: 0 !important;
        }
        
        .stats-grid {
            grid-template-columns: 1fr !important;
            gap: 1rem !important;
        }
        
        .metric-card {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Mobile navigation */
        .stSidebar {
            width: 100% !important;
        }
        
        /* Touch-friendly buttons */
        .stButton > button {
            min-height: 48px !important;
            font-size: 1rem !important;
            padding: 12px 24px !important;
        }
        
        /* Mobile input optimization */
        .stTextInput > div > div > input {
            font-size: 16px !important; /* Prevents zoom on iOS */
            padding: 12px !important;
        }
        
        /* Swipe gestures for leaderboard */
        .leaderboard-item {
            touch-action: pan-x !important;
        }
        
        /* Pull-to-refresh indicator */
        .refresh-indicator {
            position: fixed;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            background: var(--primary-color);
            color: white;
            padding: 8px 16px;
            border-radius: 0 0 10px 10px;
            font-size: 0.9rem;
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        /* Bottom navigation for mobile */
        .mobile-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-top: 1px solid var(--border-color);
            padding: 8px;
            display: flex;
            justify-content: space-around;
            z-index: 1000;
        }
        
        .mobile-nav-item {
            flex: 1;
            text-align: center;
            padding: 8px;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .mobile-nav-item.active {
            background: var(--primary-color);
            color: white;
        }
        
        .mobile-nav-icon {
            font-size: 1.2rem;
            display: block;
            margin-bottom: 2px;
        }
        
        .mobile-nav-label {
            font-size: 0.7rem;
            font-weight: 500;
        }
    }
    
    /* Tablet optimizations */
    @media (min-width: 769px) and (max-width: 1024px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr) !important;
        }
        
        .leaderboard-item {
            padding: 1.2rem !important;
        }
    }
    
    /* High DPI displays */
    @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
        .rank-badge {
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .metric-card {
            border: 1px solid var(--border-color);
        }
    }
    
    /* Dark mode media query */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-gradient: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            --card-bg: rgba(25, 25, 25, 0.95);
            --text-color: #ffffff;
            --text-secondary: #b0b0b0;
        }
    }
    
    /* Reduced motion for accessibility */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* High contrast mode */
    @media (prefers-contrast: high) {
        .metric-card, .leaderboard-item {
            border: 2px solid var(--text-color) !important;
        }
        
        .stButton > button {
            border: 2px solid white !important;
        }
    }
    
    /* Landscape phone optimization */
    @media (max-height: 500px) and (orientation: landscape) {
        .app-title {
            font-size: 1.8rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        .header-container {
            margin-bottom: 1rem !important;
        }
    }
    </style>
    """
    
    st.markdown(mobile_css, unsafe_allow_html=True)

def add_mobile_gestures():
    """Add mobile gesture support"""
    gesture_js = """
    <script>
    // Pull-to-refresh functionality
    let startY = 0;
    let currentY = 0;
    let isRefreshing = false;
    
    document.addEventListener('touchstart', function(e) {
        startY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchmove', function(e) {
        currentY = e.touches[0].clientY;
        const pullDistance = currentY - startY;
        
        if (window.scrollY === 0 && pullDistance > 0 && !isRefreshing) {
            if (pullDistance > 100) {
                showRefreshIndicator();
            }
        }
    });
    
    document.addEventListener('touchend', function(e) {
        const pullDistance = currentY - startY;
        
        if (window.scrollY === 0 && pullDistance > 100 && !isRefreshing) {
            triggerRefresh();
        }
        
        hideRefreshIndicator();
    });
    
    function showRefreshIndicator() {
        let indicator = document.querySelector('.refresh-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'refresh-indicator';
            indicator.innerHTML = '⬇️ Release to refresh';
            document.body.appendChild(indicator);
        }
        indicator.style.transform = 'translateX(-50%) translateY(0)';
    }
    
    function hideRefreshIndicator() {
        const indicator = document.querySelector('.refresh-indicator');
        if (indicator) {
            indicator.style.transform = 'translateX(-50%) translateY(-100%)';
            setTimeout(() => indicator.remove(), 300);
        }
    }
    
    function triggerRefresh() {
        isRefreshing = true;
        // Trigger Streamlit rerun
        window.parent.location.reload();
    }
    
    // Swipe navigation for leaderboard items
    let startX = 0;
    let startTime = 0;
    
    document.addEventListener('touchstart', function(e) {
        if (e.target.closest('.leaderboard-item')) {
            startX = e.touches[0].clientX;
            startTime = Date.now();
        }
    });
    
    document.addEventListener('touchend', function(e) {
        if (e.target.closest('.leaderboard-item')) {
            const endX = e.changedTouches[0].clientX;
            const endTime = Date.now();
            const distance = endX - startX;
            const duration = endTime - startTime;
            
            // Swipe right to view profile
            if (distance > 100 && duration < 300) {
                const username = e.target.closest('.leaderboard-item').querySelector('.username').textContent.replace('@', '');
                // Could trigger profile view here
                console.log('Swipe to view profile:', username);
            }
        }
    });
    
    // Haptic feedback for supported devices
    function hapticFeedback(type = 'light') {
        if (navigator.vibrate) {
            switch(type) {
                case 'light':
                    navigator.vibrate(10);
                    break;
                case 'medium':
                    navigator.vibrate(50);
                    break;
                case 'heavy':
                    navigator.vibrate([100, 30, 100]);
                    break;
            }
        }
    }
    
    // Add haptic feedback to buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('button, .stButton > button')) {
            hapticFeedback('light');
        }
    });
    
    // Create mobile bottom navigation
    function createMobileNav() {
        if (window.innerWidth <= 768) {
            const nav = document.createElement('div');
            nav.className = 'mobile-nav';
            nav.innerHTML = `
                <div class="mobile-nav-item" data-page="Dashboard">
                    <div class="mobile-nav-icon">🏠</div>
                    <div class="mobile-nav-label">Home</div>
                </div>
                <div class="mobile-nav-item" data-page="Profile">
                    <div class="mobile-nav-icon">👤</div>
                    <div class="mobile-nav-label">Profile</div>
                </div>
                <div class="mobile-nav-item" data-page="Analytics">
                    <div class="mobile-nav-icon">📊</div>
                    <div class="mobile-nav-label">Analytics</div>
                </div>
                <div class="mobile-nav-item" data-page="LiveFeed">
                    <div class="mobile-nav-icon">📡</div>
                    <div class="mobile-nav-label">Live</div>
                </div>
            `;
            
            nav.addEventListener('click', function(e) {
                const item = e.target.closest('.mobile-nav-item');
                if (item) {
                    const page = item.dataset.page;
                    hapticFeedback('medium');
                    // Update active state
                    document.querySelectorAll('.mobile-nav-item').forEach(i => i.classList.remove('active'));
                    item.classList.add('active');
                    // Navigate to page (would integrate with Streamlit state)
                    console.log('Navigate to:', page);
                }
            });
            
            document.body.appendChild(nav);
            
            // Add padding to prevent content from being hidden behind nav
            document.body.style.paddingBottom = '70px';
        }
    }
    
    // Initialize mobile features
    if (window.innerWidth <= 768) {
        createMobileNav();
    }
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            // Recalculate layout
            window.scrollTo(0, 0);
        }, 100);
    });
    </script>
    """
    
    st.markdown(gesture_js, unsafe_allow_html=True)
