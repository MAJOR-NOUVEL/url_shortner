import React from 'react';

export default function Navbar({ user, onOpenAuth, onLogout }) {
  return (
    <header className="border-b border-kraft-border bg-kraft-100/90 backdrop-blur-sm sticky top-0 z-30">
      <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
        {/* BitRoot Logo */}
        <a href="/" className="flex items-center gap-2.5 text-kraft-900 hover:opacity-90 transition-opacity">
          <img 
            src="/logo-bitroot.png" 
            alt="BitRoot logo" 
            className="w-8 h-8 sm:w-9 sm:h-9 object-contain drop-shadow-xs" 
          />
          <span className="font-bold text-lg tracking-tight text-kraft-900">
            Bit<span className="text-amberAccent-700">Root</span>
          </span>
        </a>

        {/* User Navigation Controls */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <span className="hidden sm:inline font-mono text-xs text-kraft-700 bg-kraft-150 px-2.5 py-1 rounded-md border border-kraft-border">
                {user.email}
              </span>
              <button
                onClick={onLogout}
                className="px-3 py-1.5 rounded-lg bg-kraft-150 hover:bg-kraft-200 border border-kraft-border text-kraft-800 text-xs tactile-btn transition-colors"
              >
                Sign out
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="px-4 py-1.5 rounded-lg bg-gradient-to-b from-amberAccent-400 to-amberAccent-600 hover:from-amberAccent-500 hover:to-amberAccent-700 text-kraft-950 font-semibold text-xs border border-amberAccent-700/60 tactile-btn transition-colors shadow-sm"
            >
              Sign in
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
