import React, { useState } from 'react';
import { getFullShortUrl } from '../services/api';

export default function UrlShortener({ onUrlCreated }) {
  const [url, setUrl] = useState('');
  const [customAlias, setCustomAlias] = useState('');
  const [expiresIn, setExpiresIn] = useState('');
  const [showOptions, setShowOptions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastCreated, setLastCreated] = useState(null);
  const [copied, setCopied] = useState(false);

  const displayShortUrl = lastCreated ? getFullShortUrl(lastCreated.short_url, lastCreated.short_code) : '';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError('');

    try {
      const data = await onUrlCreated(url, customAlias, expiresIn);
      setLastCreated(data);
      setUrl('');
      setCustomAlias('');
      setExpiresIn('');
      setShowOptions(false);
    } catch (err) {
      setError(err.message || 'Failed to shorten URL');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!displayShortUrl) return;
    try {
      await navigator.clipboard.writeText(displayShortUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      // Fallback
    }
  };

  return (
    <div className="space-y-4">
      {/* Shortener Box (Cardboard Panel) */}
      <div className="bg-kraft-50 border border-kraft-border rounded-2xl p-5 sm:p-7 cardboard-shadow space-y-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-2.5">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-kraft-400">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste your link here (https://...)"
                className="w-full pl-10 pr-4 py-3 bg-kraft-100/60 border border-kraft-border rounded-xl text-kraft-900 placeholder-kraft-400 text-sm font-mono shadow-inner transition-colors"
              />
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setShowOptions(!showOptions)}
                className={`px-3 py-3 rounded-xl border text-xs font-medium transition-colors flex items-center gap-1.5 tactile-btn ${
                  showOptions 
                    ? 'bg-kraft-200 border-kraft-borderDark text-kraft-900 font-semibold' 
                    : 'bg-kraft-100 hover:bg-kraft-150 border-kraft-border text-kraft-700'
                }`}
              >
                <svg className="w-3.5 h-3.5 text-kraft-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
                <span>Options</span>
              </button>

              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-gradient-to-b from-amberAccent-400 to-amberAccent-600 hover:from-amberAccent-500 hover:to-amberAccent-700 text-kraft-950 font-semibold text-sm rounded-xl border border-amberAccent-700/60 tactile-btn transition-all disabled:opacity-50 whitespace-nowrap shadow-sm"
              >
                {loading ? 'Shortening...' : 'Shorten URL'}
              </button>
            </div>
          </div>

          {/* Collapsible Options */}
          {showOptions && (
            <div className="pt-3 border-t border-kraft-border grid grid-cols-1 sm:grid-cols-2 gap-4 bg-kraft-100/50 p-3.5 rounded-xl border border-kraft-border/60">
              <div>
                <label className="block text-xs font-medium text-kraft-800 mb-1">
                  Custom alias (optional)
                </label>
                <div className="relative flex items-center">
                  <span className="absolute left-3 text-xs font-mono text-kraft-500">/</span>
                  <input
                    type="text"
                    value={customAlias}
                    onChange={(e) => setCustomAlias(e.target.value)}
                    placeholder="custom-slug"
                    maxLength={32}
                    className="w-full pl-7 pr-3 py-2 bg-kraft-50 border border-kraft-border rounded-lg text-kraft-900 text-xs font-mono"
                  />
                </div>
                <p className="text-[11px] text-kraft-500 mt-1">Letters, numbers, and hyphens.</p>
              </div>

              <div>
                <label className="block text-xs font-medium text-kraft-800 mb-1">
                  Link expiration
                </label>
                <select
                  value={expiresIn}
                  onChange={(e) => setExpiresIn(e.target.value)}
                  className="w-full px-3 py-2 bg-kraft-50 border border-kraft-border rounded-lg text-kraft-800 text-xs"
                >
                  <option value="">Never (Permanent)</option>
                  <option value="1">1 Hour</option>
                  <option value="24">24 Hours</option>
                  <option value="168">7 Days</option>
                  <option value="720">30 Days</option>
                </select>
                <p className="text-[11px] text-kraft-500 mt-1">Link will stop redirecting after expiration.</p>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-100 border border-red-300 text-red-900 text-xs rounded-xl flex items-center gap-2">
              <svg className="w-4 h-4 flex-shrink-0 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>{error}</span>
            </div>
          )}
        </form>

        {/* Result Card */}
        {lastCreated && (
          <div className="bg-kraft-150 border border-kraft-borderDark rounded-xl p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="space-y-1 min-w-0 flex-1">
              <div className="flex items-center gap-1.5">
                <svg className="w-4 h-4 text-emerald-700" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                <span className="text-[11px] font-semibold text-emerald-800">
                  Link ready to share
                </span>
              </div>
              <div className="text-lg font-bold font-mono text-kraft-900 truncate">
                <a href={displayShortUrl} target="_blank" rel="noreferrer" className="text-amberAccent-700 hover:underline">
                  {displayShortUrl}
                </a>
              </div>
              <p className="text-xs text-kraft-600 truncate max-w-md font-mono">
                {lastCreated.original_url}
              </p>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              <button
                onClick={handleCopy}
                className="px-3.5 py-2 bg-gradient-to-b from-amberAccent-400 to-amberAccent-600 hover:from-amberAccent-500 hover:to-amberAccent-700 text-kraft-950 font-semibold text-xs rounded-lg border border-amberAccent-700/60 tactile-btn transition-colors flex items-center gap-1.5 shadow-sm"
              >
                {copied ? (
                  <>
                    <svg className="w-3.5 h-3.5 text-kraft-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <svg className="w-3.5 h-3.5 text-kraft-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <span>Copy link</span>
                  </>
                )}
              </button>
              <a
                href={displayShortUrl}
                target="_blank"
                rel="noreferrer"
                className="p-2 bg-kraft-100 hover:bg-kraft-200 border border-kraft-border text-kraft-700 rounded-lg tactile-btn text-xs transition-colors"
                title="Open link"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
