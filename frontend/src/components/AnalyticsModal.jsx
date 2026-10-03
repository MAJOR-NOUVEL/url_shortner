import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function AnalyticsModal({ urlId, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!urlId) return;
    setLoading(true);
    api.getUrlAnalytics(urlId)
      .then(res => setData(res))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [urlId]);

  if (!urlId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-kraft-900/40 backdrop-blur-xs">
      <div className="bg-kraft-50 border border-kraft-borderDark rounded-2xl p-6 max-w-xl w-full cardboard-shadow space-y-5 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between border-b border-kraft-border pb-3">
          <div>
            <span className="text-[10px] font-mono uppercase tracking-wider text-amberAccent-700 font-bold">Link Performance</span>
            <h3 className="text-base font-bold text-kraft-900 font-mono">
              {data ? `/${data.short_code}` : 'Loading...'}
            </h3>
            {data && <p className="text-xs text-kraft-600 truncate max-w-md font-mono">{data.original_url}</p>}
          </div>
          <button onClick={onClose} className="text-kraft-500 hover:text-kraft-900 text-sm">
            ✕
          </button>
        </div>

        {loading && <div className="p-8 text-center text-kraft-500 text-xs font-mono">Loading statistics...</div>}
        {error && <div className="p-3 bg-red-100 border border-red-300 text-red-900 text-xs rounded-xl">{error}</div>}

        {data && (
          <div className="space-y-5">
            {/* KPI Cards */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-kraft-100 p-4 rounded-xl border border-kraft-border">
                <span className="text-[10px] uppercase tracking-wider text-kraft-600 font-semibold font-mono">Total Clicks</span>
                <div className="text-2xl font-bold text-kraft-900 font-mono mt-0.5">{data.total_clicks}</div>
              </div>
              <div className="bg-kraft-100 p-4 rounded-xl border border-kraft-border">
                <span className="text-[10px] uppercase tracking-wider text-kraft-600 font-semibold font-mono">Unique Visitors</span>
                <div className="text-2xl font-bold text-amberAccent-700 font-mono mt-0.5">{data.unique_visitors}</div>
              </div>
            </div>

            {/* Referrers & Devices */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-kraft-100 p-4 rounded-xl border border-kraft-border space-y-2.5">
                <h4 className="text-xs font-bold text-kraft-800">Top Referrers</h4>
                <div className="space-y-2">
                  {data.top_referrers.length === 0 ? (
                    <p className="text-xs text-kraft-500">No clicks recorded</p>
                  ) : (
                    data.top_referrers.map((item, i) => (
                      <div key={i} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-kraft-800">{item.name}</span>
                          <span className="text-kraft-600 font-mono">{item.count} ({item.percentage}%)</span>
                        </div>
                        <div className="w-full bg-kraft-200 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-amberAccent-500 h-full rounded-full" style={{ width: `${item.percentage}%` }}></div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="bg-kraft-100 p-4 rounded-xl border border-kraft-border space-y-2.5">
                <h4 className="text-xs font-bold text-kraft-800">Devices</h4>
                <div className="space-y-2">
                  {data.devices.length === 0 ? (
                    <p className="text-xs text-kraft-500">No clicks recorded</p>
                  ) : (
                    data.devices.map((item, i) => (
                      <div key={i} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-kraft-800">{item.name}</span>
                          <span className="text-kraft-600 font-mono">{item.count} ({item.percentage}%)</span>
                        </div>
                        <div className="w-full bg-kraft-200 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-amberAccent-600 h-full rounded-full" style={{ width: `${item.percentage}%` }}></div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
