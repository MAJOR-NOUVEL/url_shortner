import React, { useState } from 'react';
import { api, setAuthToken } from '../services/api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isRegister) {
        await api.register(email, password);
        const loginData = await api.login(email, password);
        setAuthToken(loginData.access_token);
        onAuthSuccess(loginData.user);
      } else {
        const loginData = await api.login(email, password);
        setAuthToken(loginData.access_token);
        onAuthSuccess(loginData.user);
      }
      onClose();
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-kraft-900/40 backdrop-blur-xs">
      <div className="bg-kraft-50 border border-kraft-borderDark rounded-2xl p-6 max-w-sm w-full cardboard-shadow space-y-4">
        <div className="flex items-center justify-between border-b border-kraft-border pb-2.5">
          <h3 className="text-xs font-bold text-kraft-900 uppercase tracking-wide">
            {isRegister ? 'Create BitRoot Account' : 'Sign in to BitRoot'}
          </h3>
          <button onClick={onClose} className="text-kraft-500 hover:text-kraft-900 text-xs">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-kraft-800 mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@domain.com"
              className="w-full px-3 py-2 bg-kraft-100/60 border border-kraft-border rounded-lg text-kraft-900 text-xs font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-kraft-800 mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              className="w-full px-3 py-2 bg-kraft-100/60 border border-kraft-border rounded-lg text-kraft-900 text-xs font-mono"
            />
          </div>

          {error && (
            <div className="p-2 bg-red-100 border border-red-300 text-red-900 text-xs rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-gradient-to-b from-amberAccent-400 to-amberAccent-600 hover:from-amberAccent-500 hover:to-amberAccent-700 text-kraft-950 font-semibold text-xs rounded-xl border border-amberAccent-700/60 tactile-btn transition-colors disabled:opacity-50 shadow-sm"
          >
            {loading ? 'Processing...' : (isRegister ? 'Sign Up' : 'Sign In')}
          </button>
        </form>

        <div className="text-center pt-2 border-t border-kraft-border">
          <button
            type="button"
            onClick={() => { setIsRegister(!isRegister); setError(''); }}
            className="text-xs text-amberAccent-700 hover:underline"
          >
            {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Sign up"}
          </button>
        </div>
      </div>
    </div>
  );
}
