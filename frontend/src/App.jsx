import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import UrlShortener from './components/UrlShortener';
import UrlTable from './components/UrlTable';
import AnalyticsModal from './components/AnalyticsModal';
import AuthModal from './components/AuthModal';
import RedirectPage from './components/RedirectPage';
import { api, getAuthToken, removeAuthToken } from './services/api';

const getShortCodeFromPath = () => {
  if (typeof window === 'undefined') return null;
  const path = window.location.pathname.replace(/^\/+|\/+$/g, '');
  if (!path) return null;
  const reserved = ['health', 'favicon.ico', 'robots.txt', 'static', 'api'];
  if (reserved.includes(path.toLowerCase())) return null;
  return path;
};

export default function App() {
  const [shortCode, setShortCode] = useState(() => getShortCodeFromPath());
  const [user, setUser] = useState(null);
  const [urls, setUrls] = useState([]);
  const [selectedAnalyticsId, setSelectedAnalyticsId] = useState(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  // If visiting a shortened URL path (e.g. /my-slug or /x7K9pQ), render RedirectPage
  if (shortCode) {
    return <RedirectPage shortCode={shortCode} />;
  }

  // Load user on mount if token exists
  useEffect(() => {
    if (getAuthToken()) {
      api.getCurrentUser()
        .then(res => setUser(res.user))
        .catch(() => removeAuthToken());
    }
  }, []);

  // Fetch URLs when user changes
  const fetchUrls = () => {
    if (user) {
      api.getMyUrls()
        .then(res => setUrls(res))
        .catch(() => {});
    } else {
      setUrls([]);
    }
  };

  useEffect(() => {
    fetchUrls();
  }, [user]);

  const handleUrlCreated = async (url, customAlias, expiresIn) => {
    const newLink = await api.createUrl(url, customAlias, expiresIn);
    if (user) {
      fetchUrls();
    }
    return newLink;
  };

  const handleDeleteUrl = async (id) => {
    if (confirm("Delete this link? It will stop redirecting immediately.")) {
      await api.deleteUrl(id);
      fetchUrls();
    }
  };

  const handleLogout = () => {
    removeAuthToken();
    setUser(null);
    setUrls([]);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between font-sans selection:bg-amber-300/40 selection:text-amber-950">
      <Navbar
        user={user}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
      />

      {/* Middle Section with Illustration Background */}
      <div 
        className="flex-1 w-full bg-cover bg-center bg-no-repeat relative flex flex-col justify-start"
        style={{ 
          backgroundImage: "url('/bg-bitroot.png')"
        }}
      >
        {/* Subtle warm tint overlay */}
        <div className="absolute inset-0 bg-[#f1ebd9]/30 pointer-events-none"></div>

        <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-10 space-y-8 relative z-10">
          {/* Hero Heading on Translucent Cardboard Plate */}
          <div className="text-center space-y-2 bg-kraft-50/90 backdrop-blur-sm border border-kraft-border/80 rounded-2xl py-6 px-6 max-w-lg mx-auto cardboard-shadow">
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-kraft-900">
              Smart links, simplified.
            </h1>
            <p className="text-kraft-700 text-sm sm:text-base">
              Transform long, cluttered URLs into clean, fast links with real-time analytics.
            </p>
          </div>

          {/* Shortener Form */}
          <UrlShortener onUrlCreated={handleUrlCreated} />

          {/* Saved Links Section */}
          {user ? (
            <UrlTable
              urls={urls}
              onSelectAnalytics={(id) => setSelectedAnalyticsId(id)}
              onDeleteUrl={handleDeleteUrl}
            />
          ) : (
            <div className="p-6 bg-kraft-50/95 backdrop-blur-md border border-kraft-border rounded-2xl text-center space-y-2 cardboard-shadow">
              <p className="text-xs text-kraft-700">
                Want to track click analytics and manage your links?{' '}
                <button onClick={() => setIsAuthOpen(true)} className="text-amberAccent-700 hover:underline font-semibold">
                  Sign in or create an account
                </button>
              </p>
            </div>
          )}
        </main>
      </div>

      {/* Footer with Prominent Tech Stack */}
      <footer className="border-t border-kraft-border bg-kraft-100/95 backdrop-blur-sm py-6 text-xs text-kraft-700 relative z-20">
        <div className="max-w-4xl mx-auto px-4 space-y-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-kraft-800">
            <div className="flex items-center gap-2">
              <img 
                src="/logo-bitroot.png" 
                alt="BitRoot logo" 
                className="w-5 h-5 object-contain" 
              />
              <span className="font-bold text-sm tracking-tight text-kraft-900">BitRoot</span>
              <span className="text-kraft-400">|</span>
              <span className="text-xs text-kraft-600">Fast, privacy-friendly URL shortener</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-kraft-600">
              <a href="/health" target="_blank" className="hover:text-kraft-900 underline transition-colors">System Diagnostics</a>
              <span>&bull;</span>
              <span>Active</span>
            </div>
          </div>

          {/* Tech Stack Mention */}
          <div className="pt-3 border-t border-kraft-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-[11px]">
            <span className="font-bold text-kraft-900 uppercase tracking-wider text-[10px]">Tech Stack:</span>
            <div className="flex flex-wrap items-center gap-1.5 font-mono text-[11px]">
              <span className="px-2 py-0.5 rounded bg-kraft-50 border border-kraft-border text-kraft-800">Python 3.12 (Flask)</span>
              <span className="px-2 py-0.5 rounded bg-kraft-50 border border-kraft-border text-kraft-800">PostgreSQL + SQLAlchemy</span>
              <span className="px-2 py-0.5 rounded bg-kraft-50 border border-kraft-border text-kraft-800">Redis 7 (Cache & Limiter)</span>
              <span className="px-2 py-0.5 rounded bg-kraft-50 border border-kraft-border text-kraft-800">Celery Async Worker</span>
              <span className="px-2 py-0.5 rounded bg-kraft-50 border border-kraft-border text-kraft-800">React 18 + Tailwind</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={(u) => setUser(u)}
      />

      <AnalyticsModal
        urlId={selectedAnalyticsId}
        onClose={() => setSelectedAnalyticsId(null)}
      />
    </div>
  );
}
