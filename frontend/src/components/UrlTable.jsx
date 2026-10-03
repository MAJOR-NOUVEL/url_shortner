import React from 'react';

export default function UrlTable({ urls, onSelectAnalytics, onDeleteUrl }) {
  if (!urls || urls.length === 0) {
    return (
      <div className="bg-kraft-50 border border-kraft-border rounded-2xl p-8 text-center space-y-2 cardboard-shadow">
        <p className="text-xs text-kraft-500">You haven't created any links yet. Paste a URL above to start.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between px-1">
        <h3 className="text-sm font-bold text-kraft-900">Your Links ({urls.length})</h3>
      </div>

      <div className="bg-kraft-50 border border-kraft-border rounded-2xl overflow-hidden cardboard-shadow">
        <div className="divide-y divide-kraft-border">
          {urls.map((item) => (
            <div key={item.id} className="p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 hover:bg-kraft-100/60 transition-colors">
              <div className="space-y-1 min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <a
                    href={item.short_url}
                    target="_blank"
                    rel="noreferrer"
                    className="font-mono font-semibold text-amberAccent-700 hover:underline text-sm"
                  >
                    /{item.short_code}
                  </a>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-kraft-150 border border-kraft-border text-kraft-700">
                    {item.click_count} {item.click_count === 1 ? 'click' : 'clicks'}
                  </span>
                  {item.is_expired && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-100 text-red-800 border border-red-200">
                      Expired
                    </span>
                  )}
                </div>
                <p className="text-xs text-kraft-600 truncate max-w-md font-mono">
                  {item.original_url}
                </p>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-center">
                <button
                  onClick={() => onSelectAnalytics(item.id)}
                  className="px-3 py-1.5 rounded-lg bg-kraft-100 hover:bg-kraft-150 border border-kraft-border text-xs text-kraft-800 flex items-center gap-1.5 tactile-btn transition-colors"
                >
                  <svg className="w-3.5 h-3.5 text-amberAccent-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <span>Analytics</span>
                </button>
                <button
                  onClick={() => onDeleteUrl(item.id)}
                  className="p-2 rounded-lg bg-kraft-100 hover:bg-red-100 border border-kraft-border hover:border-red-300 text-kraft-600 hover:text-red-700 text-xs tactile-btn transition-colors"
                  title="Delete link"
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
