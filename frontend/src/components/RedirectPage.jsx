import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function RedirectPage({ shortCode }) {
  const [status, setStatus] = useState('loading'); // 'loading' | 'redirecting' | 'not_found' | 'expired' | 'error'
  const [destinationUrl, setDestinationUrl] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isWakingUp, setIsWakingUp] = useState(false);

  useEffect(() => {
    let isMounted = true;

    // Show server cold-start notice if backend takes more than 3.5 seconds to respond
    const wakeTimer = setTimeout(() => {
      if (isMounted) {
        setIsWakingUp(true);
      }
    }, 3500);

    const resolveLink = async () => {
      try {
        const data = await api.resolveUrl(shortCode);
        if (!isMounted) return;

        clearTimeout(wakeTimer);
        setDestinationUrl(data.original_url);
        setStatus('redirecting');

        // Immediately trigger navigation to the destination
        window.location.replace(data.original_url);
      } catch (err) {
        if (!isMounted) return;
        clearTimeout(wakeTimer);

        if (err.status === 404) {
          setStatus('not_found');
          setErrorMessage(err.message || 'This shortened link does not exist or was removed.');
        } else if (err.status === 410) {
          setStatus('expired');
          setErrorMessage(err.message || 'This shortened link has expired and is no longer available.');
        } else {
          setStatus('error');
          setErrorMessage(err.message || 'Failed to reach the redirect server. Please try again.');
        }
      }
    };

    resolveLink();

    return () => {
      isMounted = false;
      clearTimeout(wakeTimer);
    };
  }, [shortCode]);

  const handleGoHome = () => {
    window.location.href = '/';
  };

  return (
    <div className="min-h-screen flex flex-col justify-between font-sans selection:bg-amber-300/40 selection:text-amber-950 bg-[#e8deca]">
      {/* Background illustration overlay */}
      <div 
        className="flex-1 w-full bg-cover bg-center bg-no-repeat relative flex flex-col justify-center items-center px-4 py-12"
        style={{ backgroundImage: "url('/bg-bitroot.png')" }}
      >
        <div className="absolute inset-0 bg-[#f1ebd9]/40 pointer-events-none"></div>

        <div className="max-w-md w-full relative z-10 space-y-6">
          {/* Main Card */}
          <div className="bg-kraft-50 border border-kraft-border rounded-2xl p-6 sm:p-8 cardboard-shadow text-center space-y-5">
            {/* Logo */}
            <div className="flex items-center justify-center gap-2.5">
              <img 
                src="/logo-bitroot.png" 
                alt="BitRoot logo" 
                className="w-8 h-8 object-contain" 
              />
              <span className="font-extrabold text-xl tracking-tight text-kraft-900">BitRoot</span>
            </div>

            {/* Short slug badge */}
            <div className="inline-block px-3 py-1 bg-kraft-150 border border-kraft-border rounded-full text-xs font-mono text-kraft-700">
              /{shortCode}
            </div>

            {/* Status: Loading */}
            {status === 'loading' && (
              <div className="space-y-4 py-4">
                <div className="flex justify-center">
                  <div className="w-9 h-9 border-3 border-amberAccent-300 border-t-amberAccent-600 rounded-full animate-spin"></div>
                </div>
                <div className="space-y-1">
                  <h3 className="text-base font-bold text-kraft-900">Resolving Link...</h3>
                  <p className="text-xs text-kraft-600">Connecting to BitRoot routing engine</p>
                </div>
                {isWakingUp && (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 space-y-1 text-left">
                    <p className="font-semibold flex items-center gap-1.5">
                      <span>⏳</span> Free server instance waking up
                    </p>
                    <p className="text-[11px] text-amber-800">
                      On free tier hosting (Render), idle services may take up to 30–50 seconds to initialize. Please wait a moment.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Status: Redirecting */}
            {status === 'redirecting' && (
              <div className="space-y-4 py-2">
                <div className="flex justify-center">
                  <div className="w-10 h-10 rounded-full bg-emerald-100 border border-emerald-300 flex items-center justify-center text-emerald-700">
                    <svg className="w-6 h-6 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </div>
                </div>

                <div className="space-y-1">
                  <h3 className="text-base font-bold text-kraft-900">Redirecting to destination...</h3>
                  <p className="text-xs text-kraft-600 break-all font-mono px-2 py-1 bg-kraft-100 rounded-lg border border-kraft-border">
                    {destinationUrl}
                  </p>
                </div>

                <div className="pt-2">
                  <a
                    href={destinationUrl}
                    className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-gradient-to-b from-amberAccent-400 to-amberAccent-600 hover:from-amberAccent-500 hover:to-amberAccent-700 text-kraft-950 font-bold text-xs rounded-xl border border-amberAccent-700/60 tactile-btn shadow-sm"
                  >
                    <span>Click here if not redirected</span>
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            )}

            {/* Status: Not Found (404) */}
            {status === 'not_found' && (
              <div className="space-y-4 py-2">
                <div className="flex justify-center">
                  <div className="w-10 h-10 rounded-full bg-red-100 border border-red-300 flex items-center justify-center text-red-700">
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                </div>
                <div className="space-y-1">
                  <h3 className="text-base font-bold text-kraft-900">Link Not Found</h3>
                  <p className="text-xs text-kraft-600">{errorMessage}</p>
                </div>
                <div className="pt-2">
                  <button
                    onClick={handleGoHome}
                    className="px-5 py-2.5 bg-kraft-100 hover:bg-kraft-200 border border-kraft-border text-kraft-900 font-semibold text-xs rounded-xl tactile-btn transition-colors"
                  >
                    Go to BitRoot Home
                  </button>
                </div>
              </div>
            )}

            {/* Status: Expired (410) */}
            {status === 'expired' && (
              <div className="space-y-4 py-2">
                <div className="flex justify-center">
                  <div className="w-10 h-10 rounded-full bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-700">
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="space-y-1">
                  <h3 className="text-base font-bold text-kraft-900">Link Expired</h3>
                  <p className="text-xs text-kraft-600">{errorMessage}</p>
                </div>
                <div className="pt-2">
                  <button
                    onClick={handleGoHome}
                    className="px-5 py-2.5 bg-kraft-100 hover:bg-kraft-200 border border-kraft-border text-kraft-900 font-semibold text-xs rounded-xl tactile-btn transition-colors"
                  >
                    Go to BitRoot Home
                  </button>
                </div>
              </div>
            )}

            {/* Status: Error */}
            {status === 'error' && (
              <div className="space-y-4 py-2">
                <div className="flex justify-center">
                  <div className="w-10 h-10 rounded-full bg-red-100 border border-red-300 flex items-center justify-center text-red-700">
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                </div>
                <div className="space-y-1">
                  <h3 className="text-base font-bold text-kraft-900">Could Not Open Link</h3>
                  <p className="text-xs text-kraft-600">{errorMessage}</p>
                </div>
                <div className="pt-2 flex items-center justify-center gap-3">
                  <button
                    onClick={() => window.location.reload()}
                    className="px-4 py-2 bg-gradient-to-b from-amberAccent-400 to-amberAccent-600 text-kraft-950 font-semibold text-xs rounded-xl border border-amberAccent-700/60 tactile-btn"
                  >
                    Try Again
                  </button>
                  <button
                    onClick={handleGoHome}
                    className="px-4 py-2 bg-kraft-100 hover:bg-kraft-200 border border-kraft-border text-kraft-800 text-xs rounded-xl tactile-btn"
                  >
                    Go Home
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
